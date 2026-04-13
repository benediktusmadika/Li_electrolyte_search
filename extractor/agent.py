from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import ApiConfig
from .llm_client import BaseResponsesClient, UploadedFile, build_llm_client
from .output_manager import (
    OutputPaths,
    prepare_output_paths,
    save_json,
    write_combined_exports,
    write_per_file_exports,
    write_run_summary,
)
from .pdf_utils import get_pdf_stats, list_pdf_files
from .postprocess import EXPORT_TABLE_COLUMN_ORDER, build_export_tables, normalize_hierarchical_extraction
from .prompts import (
    DISCOVERY_SYSTEM_PROMPT,
    HIERARCHICAL_EXTRACTION_SYSTEM_PROMPT,
    REPAIR_SYSTEM_PROMPT,
    VALIDATION_SYSTEM_PROMPT,
    build_discovery_user_prompt,
    build_hierarchical_user_prompt,
    build_repair_user_prompt,
    build_validation_user_prompt,
)
from .schema_validation import assert_matches_schema
from .schemas import discovery_schema, hierarchical_extraction_schema, validation_schema

LOGGER = logging.getLogger(__name__)


@dataclass
class FileRunArtifacts:
    pdf_path: Path
    uploaded_file: UploadedFile
    discovery: Dict[str, Any]
    hierarchical_initial: Dict[str, Any]
    hierarchical_final: Dict[str, Any]
    validation: Dict[str, Any]
    repaired: bool
    export_tables: Dict[str, List[Dict[str, Any]]]


class ElectrolyteExtractionAgent:
    def __init__(self, api_config: ApiConfig):
        self.api_config = api_config
        self.client: BaseResponsesClient = build_llm_client(api_config)

    def process_pdf(self, pdf_path: Path) -> FileRunArtifacts:
        LOGGER.info("Processing PDF: %s", pdf_path.name)
        uploaded = self.client.upload_file(pdf_path)
        LOGGER.info("Uploaded %s as remote file %s", pdf_path.name, uploaded.file_id)

        try:
            discovery = self._run_discovery(uploaded, pdf_path)
            hierarchical_initial = self._run_hierarchical_extraction(uploaded, pdf_path, discovery)
            hierarchical_initial = normalize_hierarchical_extraction(hierarchical_initial, pdf_path)

            validation = self._run_validation(uploaded, pdf_path, hierarchical_initial)
            hierarchical_final = hierarchical_initial
            repaired = False

            if _validation_has_issues(validation):
                LOGGER.info("Validation issues detected for %s. Running one repair pass.", pdf_path.name)
                repaired_candidate = self._run_repair(uploaded, pdf_path, hierarchical_initial, validation)
                repaired_candidate = normalize_hierarchical_extraction(repaired_candidate, pdf_path)
                repaired_validation = self._run_validation(uploaded, pdf_path, repaired_candidate)
                if _validation_score(repaired_validation) >= _validation_score(validation):
                    hierarchical_final = repaired_candidate
                    validation = repaired_validation
                    repaired = True

            export_tables = build_export_tables(hierarchical_final)

            return FileRunArtifacts(
                pdf_path=pdf_path,
                uploaded_file=uploaded,
                discovery=discovery,
                hierarchical_initial=hierarchical_initial,
                hierarchical_final=hierarchical_final,
                validation=validation,
                repaired=repaired,
                export_tables=export_tables,
            )
        finally:
            if self.api_config.delete_remote_file_after_run:
                self.client.delete_file(uploaded.file_id)

    def process_folder(self, pdf_dir: Path, out_dir: Path, *, max_pdfs: Optional[int] = None) -> OutputPaths:
        paths = prepare_output_paths(out_dir)
        pdf_files = list_pdf_files(pdf_dir)
        if max_pdfs is not None:
            pdf_files = pdf_files[:max_pdfs]
        if not pdf_files:
            raise FileNotFoundError(f"No PDF files found in {pdf_dir}")

        combined_export_tables: Dict[str, List[Dict[str, Any]]] = {
            table_name: [] for table_name in EXPORT_TABLE_COLUMN_ORDER.keys()
        }
        summary_rows: List[Dict[str, Any]] = []

        for pdf_path in pdf_files:
            stats = get_pdf_stats(pdf_path)
            try:
                artifacts = self.process_pdf(pdf_path)

                stem = pdf_path.stem
                save_json(
                    paths.intermediate_json / f"{stem}.json",
                    {
                        "discovery": artifacts.discovery,
                        "hierarchical_initial": artifacts.hierarchical_initial,
                    },
                )
                save_json(paths.final_json / f"{stem}.json", artifacts.hierarchical_final)
                save_json(paths.validation_json / f"{stem}.json", artifacts.validation)

                write_per_file_exports(paths.per_file_csv, stem, artifacts.export_tables)

                for table_name, rows in artifacts.export_tables.items():
                    combined_export_tables[table_name].extend(rows)

                summary_rows.append(
                    {
                        "file_name": pdf_path.name,
                        "page_count": stats.page_count,
                        "file_size_bytes": stats.file_size_bytes,
                        "electrolyte_count": len(artifacts.hierarchical_final.get("electrolytes", [])),
                        "test_count": len(artifacts.hierarchical_final.get("tests", [])),
                        "a2r_total_rows": len(artifacts.export_tables.get("a2r_records_all", [])),
                        "is_valid_overall": artifacts.validation.get("is_valid_overall"),
                        "repaired": artifacts.repaired,
                        "coverage_issues_count": len(artifacts.validation.get("coverage_issues", [])),
                        "electrolyte_issues_count": len(artifacts.validation.get("electrolyte_issues", [])),
                        "test_issues_count": len(artifacts.validation.get("test_issues", [])),
                        "composition_issues_count": len(artifacts.validation.get("composition_issues", [])),
                        "a2r_preparation_issues_count": len(artifacts.validation.get("a2r_preparation_issues", [])),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                LOGGER.exception("Failed to process %s", pdf_path.name)
                summary_rows.append(
                    {
                        "file_name": pdf_path.name,
                        "page_count": stats.page_count,
                        "file_size_bytes": stats.file_size_bytes,
                        "electrolyte_count": 0,
                        "test_count": 0,
                        "a2r_total_rows": 0,
                        "is_valid_overall": False,
                        "repaired": False,
                        "coverage_issues_count": None,
                        "electrolyte_issues_count": None,
                        "test_issues_count": None,
                        "composition_issues_count": None,
                        "a2r_preparation_issues_count": None,
                        "error": str(exc),
                    }
                )

        write_combined_exports(paths.combined_csv, combined_export_tables)
        write_run_summary(paths.run_summary_csv, summary_rows)
        return paths

    def _run_discovery(self, uploaded: UploadedFile, pdf_path: Path) -> Dict[str, Any]:
        payload = self.client.create_structured_response(
            file_id=uploaded.file_id,
            system_prompt=DISCOVERY_SYSTEM_PROMPT,
            user_prompt=build_discovery_user_prompt(pdf_path.name),
            schema_name="electrolyte_discovery",
            schema=discovery_schema(),
        )
        assert_matches_schema(payload, discovery_schema())
        return payload

    def _run_hierarchical_extraction(
        self,
        uploaded: UploadedFile,
        pdf_path: Path,
        discovery: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload = self.client.create_structured_response(
            file_id=uploaded.file_id,
            system_prompt=HIERARCHICAL_EXTRACTION_SYSTEM_PROMPT,
            user_prompt=build_hierarchical_user_prompt(pdf_path.name, discovery),
            schema_name="electrolyte_hierarchical_extraction",
            schema=hierarchical_extraction_schema(),
        )
        assert_matches_schema(payload, hierarchical_extraction_schema())
        return payload

    def _run_validation(self, uploaded: UploadedFile, pdf_path: Path, hierarchical_output: Dict[str, Any]) -> Dict[str, Any]:
        payload = self.client.create_structured_response(
            file_id=uploaded.file_id,
            system_prompt=VALIDATION_SYSTEM_PROMPT,
            user_prompt=build_validation_user_prompt(pdf_path.name, hierarchical_output),
            schema_name="electrolyte_hierarchical_validation",
            schema=validation_schema(),
        )
        assert_matches_schema(payload, validation_schema())
        return payload

    def _run_repair(
        self,
        uploaded: UploadedFile,
        pdf_path: Path,
        hierarchical_output: Dict[str, Any],
        validation_output: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload = self.client.create_structured_response(
            file_id=uploaded.file_id,
            system_prompt=REPAIR_SYSTEM_PROMPT,
            user_prompt=build_repair_user_prompt(pdf_path.name, hierarchical_output, validation_output),
            schema_name="electrolyte_hierarchical_repair",
            schema=hierarchical_extraction_schema(),
        )
        assert_matches_schema(payload, hierarchical_extraction_schema())
        return payload


def _validation_has_issues(report: Dict[str, Any]) -> bool:
    if not report.get("is_valid_overall", False):
        return True
    for key in [
        "coverage_issues",
        "paper_issues",
        "electrolyte_issues",
        "test_issues",
        "composition_issues",
        "a2r_preparation_issues",
    ]:
        if report.get(key):
            return True
    return False


def _validation_score(report: Dict[str, Any]) -> int:
    score = 0
    if report.get("is_valid_overall"):
        score += 1000
    for key in [
        "coverage_issues",
        "paper_issues",
        "electrolyte_issues",
        "test_issues",
        "composition_issues",
        "a2r_preparation_issues",
    ]:
        score -= 10 * len(report.get(key, []))
    return score
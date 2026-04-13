from __future__ import annotations

from extractor.field_catalog import FIELD_SPECS
from extractor.prompts import export_prompt_package
from extractor.schema_validation import assert_matches_schema
from extractor.schemas import discovery_schema, hierarchical_extraction_schema, validation_schema


def test_field_catalog_contains_new_groups() -> None:
    groups = {spec.group for spec in FIELD_SPECS}
    assert "Common_condition" in groups
    assert "Formation" in groups
    assert "Cycling_test" in groups
    assert "Rate_test" in groups
    assert "Storage_test" in groups
    assert "RPT_test" in groups


def test_prompt_package_contains_updated_sections() -> None:
    text = export_prompt_package()
    assert "Discovery System Prompt" in text
    assert "Hierarchical Extraction System Prompt" in text
    assert "Validation System Prompt" in text
    assert "Repair System Prompt" in text
    assert "Do NOT perform A2R expansion" in text


def test_schema_examples_validate() -> None:
    assert_matches_schema({"electrolytes": [], "document_notes": None}, discovery_schema())
    assert_matches_schema(
        {
            "paper": {
                "file_name": None,
                "journal_name": None,
                "doi": None,
                "paper_title": None,
                "num_electrolytes": None,
                "tested_electrolytes_list": [],
                "notes": None,
                "evidence": [],
            },
            "electrolytes": [],
            "tests": [],
            "document_notes": None,
        },
        hierarchical_extraction_schema(),
    )
    assert_matches_schema(
        {
            "is_valid_overall": True,
            "coverage_issues": [],
            "paper_issues": [],
            "electrolyte_issues": [],
            "test_issues": [],
            "composition_issues": [],
            "a2r_preparation_issues": [],
            "suggested_fixes": [],
        },
        validation_schema(),
    )
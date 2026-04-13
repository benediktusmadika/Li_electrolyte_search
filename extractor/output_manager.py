from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from .postprocess import EXPORT_TABLE_COLUMN_ORDER


@dataclass(frozen=True)
class OutputPaths:
    root: Path
    per_file_csv: Path
    combined_csv: Path
    intermediate_json: Path
    final_json: Path
    validation_json: Path
    run_summary_csv: Path
    logs_dir: Path


def prepare_output_paths(out_dir: Path) -> OutputPaths:
    per_file_csv = out_dir / "per_file_csv"
    combined_csv = out_dir / "combined_csv"
    intermediate_json = out_dir / "intermediate_json"
    final_json = out_dir / "final_json"
    validation_json = out_dir / "validation_json"
    logs_dir = out_dir / "logs"

    for path in [per_file_csv, combined_csv, intermediate_json, final_json, validation_json, logs_dir]:
        path.mkdir(parents=True, exist_ok=True)

    return OutputPaths(
        root=out_dir,
        per_file_csv=per_file_csv,
        combined_csv=combined_csv,
        intermediate_json=intermediate_json,
        final_json=final_json,
        validation_json=validation_json,
        run_summary_csv=out_dir / "run_summary.csv",
        logs_dir=logs_dir,
    )


def save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _csv_value(value: Any) -> Any:
    if value is None:
        return "N/A"
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value


def _rows_to_dataframe(rows: List[Dict[str, Any]], columns: List[str]) -> pd.DataFrame:
    cooked_rows = []
    for row in rows:
        cooked_rows.append({column: _csv_value(row.get(column)) for column in columns})
    return pd.DataFrame(cooked_rows, columns=columns)


def write_csv(path: Path, rows: List[Dict[str, Any]], columns: List[str]) -> None:
    df = _rows_to_dataframe(rows, columns)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def write_excel_workbook(path: Path, export_tables: Dict[str, List[Dict[str, Any]]]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for table_name in EXPORT_TABLE_COLUMN_ORDER.keys():
            rows = export_tables.get(table_name, [])
            columns = EXPORT_TABLE_COLUMN_ORDER[table_name]
            df = _rows_to_dataframe(rows, columns)
            df.to_excel(writer, index=False, sheet_name=table_name[:31])


def write_per_file_exports(base_dir: Path, stem: str, export_tables: Dict[str, List[Dict[str, Any]]]) -> None:
    file_dir = base_dir / stem
    file_dir.mkdir(parents=True, exist_ok=True)
    complete_tables = {name: export_tables.get(name, []) for name in EXPORT_TABLE_COLUMN_ORDER.keys()}
    for table_name, columns in EXPORT_TABLE_COLUMN_ORDER.items():
        write_csv(file_dir / f"{table_name}.csv", complete_tables[table_name], columns)
    write_excel_workbook(file_dir / f"{stem}_results.xlsx", complete_tables)


def write_combined_exports(combined_dir: Path, export_tables: Dict[str, List[Dict[str, Any]]]) -> None:
    complete_tables = {name: export_tables.get(name, []) for name in EXPORT_TABLE_COLUMN_ORDER.keys()}
    for table_name, columns in EXPORT_TABLE_COLUMN_ORDER.items():
        write_csv(combined_dir / f"{table_name}.csv", complete_tables[table_name], columns)
    write_excel_workbook(combined_dir / "combined_results.xlsx", complete_tables)


def write_run_summary(path: Path, rows: List[Dict[str, Any]]) -> None:
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False, encoding="utf-8-sig")
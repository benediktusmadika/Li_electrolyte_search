from __future__ import annotations

from extractor.output_manager import write_combined_exports
from extractor.postprocess import EXPORT_TABLE_COLUMN_ORDER


def test_write_combined_exports_creates_all_files(tmp_path) -> None:
    export_tables = {table_name: [] for table_name in EXPORT_TABLE_COLUMN_ORDER.keys()}
    write_combined_exports(tmp_path, export_tables)

    for table_name in EXPORT_TABLE_COLUMN_ORDER.keys():
        assert (tmp_path / f"{table_name}.csv").exists()

    assert (tmp_path / "combined_results.xlsx").exists()
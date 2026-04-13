from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extractor.output_manager import write_csv, write_excel_workbook
from extractor.postprocess import EXPORT_TABLE_COLUMN_ORDER


OUTPUT_TEMPLATES_DIR = ROOT / "output_templates"


def main() -> None:
    OUTPUT_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    empty_tables = {table_name: [] for table_name in EXPORT_TABLE_COLUMN_ORDER.keys()}

    for table_name, columns in EXPORT_TABLE_COLUMN_ORDER.items():
        write_csv(OUTPUT_TEMPLATES_DIR / f"{table_name}.csv", [], columns)

    write_excel_workbook(OUTPUT_TEMPLATES_DIR / "output_templates.xlsx", empty_tables)


if __name__ == "__main__":
    main()
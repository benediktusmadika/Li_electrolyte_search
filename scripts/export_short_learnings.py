from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extractor.field_catalog import FIELD_SPECS
from extractor.prompts import export_prompt_package


DOCS = ROOT / "docs"


def write_short_learnings_csv(path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "group",
                "field_name",
                "definition",
                "guidance_to_find",
                "example_pdf_like_text",
                "expected_answer",
                "format_note",
            ],
        )
        writer.writeheader()
        for spec in FIELD_SPECS:
            writer.writerow(
                {
                    "group": spec.group,
                    "field_name": spec.field_name,
                    "definition": spec.definition,
                    "guidance_to_find": spec.guidance_to_find,
                    "example_pdf_like_text": spec.example_pdf_like_text,
                    "expected_answer": spec.expected_answer,
                    "format_note": spec.format_note,
                }
            )


def write_short_learnings_md(path: Path) -> None:
    lines = [
        "# Short Learnings for Electrolyte PDF Extraction\n\n",
        "These are synthetic PDF-like examples designed to mimic the literature style expected by the extractor.\n\n",
        "| Group | Field | Definition | Guidance to find | Example PDF-like text | Expected answer | Format |\n",
        "|---|---|---|---|---|---|---|\n",
    ]
    for spec in FIELD_SPECS:
        lines.append(
            f"| {spec.group} | {spec.field_name} | {spec.definition} | {spec.guidance_to_find} | "
            f"{spec.example_pdf_like_text} | {spec.expected_answer} | {spec.format_note} |\n"
        )
    path.write_text("".join(lines), encoding="utf-8")


def write_prompt_package_md(path: Path) -> None:
    path.write_text(export_prompt_package(), encoding="utf-8")


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    write_short_learnings_csv(DOCS / "short_learnings.csv")
    write_short_learnings_md(DOCS / "short_learnings.md")
    write_prompt_package_md(DOCS / "prompt_package.md")


if __name__ == "__main__":
    main()
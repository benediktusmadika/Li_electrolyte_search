from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from pypdf import PdfReader


@dataclass(frozen=True)
class PdfStats:
    path: Path
    page_count: int
    file_size_bytes: int


def list_pdf_files(pdf_dir: Path) -> List[Path]:
    if not pdf_dir.exists():
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")
    files = sorted(
        [
            path
            for path in pdf_dir.iterdir()
            if path.is_file() and path.suffix.lower() == ".pdf"
        ]
    )
    return files


def get_pdf_stats(pdf_path: Path) -> PdfStats:
    reader = PdfReader(str(pdf_path))
    return PdfStats(
        path=pdf_path,
        page_count=len(reader.pages),
        file_size_bytes=pdf_path.stat().st_size,
    )
from __future__ import annotations

import argparse
from pathlib import Path

from extractor import ElectrolyteExtractionAgent, load_api_config
from extractor.logging_utils import configure_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agentic GPT-5.4 pipeline for extracting electrolyte, test, and A2R records from a folder of PDFs."
    )
    parser.add_argument("--pdf-dir", type=Path, default=Path("pdf_files"), help="Folder containing PDF files.")
    parser.add_argument("--api-file", type=Path, default=Path("gpt_api.txt"), help="Path to gpt_api.txt.")
    parser.add_argument("--out-dir", type=Path, default=Path("outputs"), help="Directory for outputs.")
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override model name. Default comes from gpt_api.txt or gpt-5.4.",
    )
    parser.add_argument(
        "--reasoning-effort",
        type=str,
        default=None,
        help="Override reasoning effort. Typical values: low, medium, high, xhigh.",
    )
    parser.add_argument("--max-pdfs", type=int, default=None, help="Optional limit on how many PDFs to process.")
    parser.add_argument(
        "--keep-remote-files",
        action="store_true",
        help="Do not delete uploaded remote files even if gpt_api.txt requests cleanup.",
    )
    parser.add_argument("--quiet", action="store_true", help="Reduce console logging.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    configure_logging(args.out_dir / "logs" / "run.log", verbose=not args.quiet)

    api_config = load_api_config(
        args.api_file,
        model_override=args.model,
        reasoning_override=args.reasoning_effort,
        keep_remote_files=args.keep_remote_files,
    )
    agent = ElectrolyteExtractionAgent(api_config)
    paths = agent.process_folder(args.pdf_dir, args.out_dir, max_pdfs=args.max_pdfs)

    print("Run complete.")
    print(f"Combined CSV folder: {paths.combined_csv}")
    print(f"Combined workbook: {paths.combined_csv / 'combined_results.xlsx'}")
    print(f"Run summary CSV: {paths.run_summary_csv}")
    print(f"Per-file CSV folder: {paths.per_file_csv}")
    print(f"Intermediate JSON folder: {paths.intermediate_json}")
    print(f"Final JSON folder: {paths.final_json}")
    print(f"Validation JSON folder: {paths.validation_json}")


if __name__ == "__main__":
    main()
from __future__ import annotations

import argparse
from pathlib import Path

from .runner import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate knowledge graph artifacts for a chapter.")
    parser.add_argument("chapter_id", help="Identifier used for the chapter output file.")
    parser.add_argument(
        "--source",
        type=Path,
        help="Optional path to the chapter text file. Defaults to data/input/<chapter_id>.txt",
    )
    args = parser.parse_args()

    output_path = run_pipeline(args.chapter_id, args.source)
    print(f"Artifacts written to {output_path}")


if __name__ == "__main__":
    main()

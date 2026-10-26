#!/usr/bin/env python3
"""
Convert slide decks in slides/ from .pptx to .pdf with LibreOffice.

Usage
    python3 scripts/slides_to_pdf.py            # convert decks with a missing or older PDF
    python3 scripts/slides_to_pdf.py 01.pptx    # convert specific decks (names in slides/)
    python3 scripts/slides_to_pdf.py --force    # reconvert everything

Needs `soffice` on PATH (macOS: brew install --cask libreoffice).
The site links to the PDF named in lectures/NN/lecture.yml (`slides: 01.pdf`).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SLIDES = Path(__file__).resolve().parent.parent / "slides"


def convert(deck: Path) -> None:
    result = subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(deck.parent), str(deck)],
        capture_output=True,
        text=True,
    )
    pdf = deck.with_suffix(".pdf")
    if result.returncode != 0 or not pdf.exists():
        sys.exit(f"conversion failed for {deck.name}:\n{result.stdout}{result.stderr}")
    print(f"{deck.name} -> {pdf.name} ({pdf.stat().st_size / 1e6:.1f} MB)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("decks", nargs="*", help="deck file names in slides/ (default: all)")
    parser.add_argument("--force", action="store_true", help="reconvert even if the PDF is up to date")
    args = parser.parse_args()

    if shutil.which("soffice") is None:
        sys.exit("soffice not found: install LibreOffice (brew install --cask libreoffice)")

    decks = [SLIDES / name for name in args.decks] or sorted(SLIDES.glob("*.pptx"))
    for deck in decks:
        if not deck.exists():
            sys.exit(f"not found: {deck}")
        pdf = deck.with_suffix(".pdf")
        if pdf.exists() and pdf.stat().st_mtime >= deck.stat().st_mtime and not args.force:
            print(f"{pdf.name} is up to date")
            continue
        convert(deck)


if __name__ == "__main__":
    main()

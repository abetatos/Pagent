#!/usr/bin/env python3
"""Check whether a written chapter meets its target word range.

Reads the chapter file, counts words, compares to setup.md target.
Exits 0 if in range, 1 if too short, 2 if too long, 3 on error.

Usage:
    python check_wordcount.py --series-slug <slug> --book-number <n> --chapter <m>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.paths import book_paths
from lib import setup_doc, wordcount


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--series-slug", required=True)
    parser.add_argument("--book-number", type=int, required=True)
    parser.add_argument("--chapter", type=int, required=True)
    args = parser.parse_args()

    paths = book_paths(args.series_slug, args.book_number)
    ch_path = paths.chapter_file(args.chapter)
    if not ch_path.exists():
        print(f"ERROR: chapter file does not exist: {ch_path}", file=sys.stderr)
        return 3

    setup_text = setup_doc.load(paths.setup_md)
    lo, hi = setup_doc.words_per_chapter_range(setup_text)
    actual = wordcount.count_words(ch_path.read_text(encoding="utf-8"))
    rep = wordcount.report(actual, lo, hi)

    print(f"Chapter {args.chapter}: {rep.describe()}")
    if rep.is_too_short:
        print("VERDICT: too_short — run expand-chapter to dwell more.")
        return 1
    if rep.is_too_long:
        print("VERDICT: too_long — run revise-chapter to trim.")
        return 2
    print("VERDICT: in_range")
    return 0


if __name__ == "__main__":
    sys.exit(main())

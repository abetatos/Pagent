#!/usr/bin/env python3
"""Search across a book's canon, plan, summaries, and chapters.

Tier priority: canon > plan > summary > chapter.

Usage:
    python search.py --series-slug <slug> --book-number <n> --query <regex>
    python search.py --series-slug <slug> --book-number <n> --query <regex> \\
        --tiers canon,plan --max-hits 20
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.paths import book_paths
from lib import search as search_mod


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--series-slug", required=True)
    parser.add_argument("--book-number", type=int, required=True)
    parser.add_argument("--query", required=True, help="Regex (falls back to literal).")
    parser.add_argument("--max-hits", type=int, default=12)
    parser.add_argument(
        "--tiers",
        default="canon,plan,summary,chapter",
        help="Comma-separated tier list in any order; results returned in canon>plan>summary>chapter order regardless.",
    )
    args = parser.parse_args()

    paths = book_paths(args.series_slug, args.book_number)
    tiers = tuple(t.strip() for t in args.tiers.split(",") if t.strip())
    hits = search_mod.search(paths, args.query, max_hits=args.max_hits, tiers=tiers)

    if not hits:
        print(f"No hits for /{args.query}/ in {paths.book_root}.")
        return 1

    print(f"Found {len(hits)} hit(s) for /{args.query}/ in {paths.book_root}:\n")
    print(search_mod.render_hits(hits))
    return 0


if __name__ == "__main__":
    sys.exit(main())

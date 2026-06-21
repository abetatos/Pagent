#!/usr/bin/env python3
"""Update the status field of one seed in plan/seeds.md.

Usage:
    python mark_seed.py --series-slug <slug> --book-number <n> \\
        --seed-id <id> --status <new_status>

Valid statuses: planned, planted, echoed-1, echoed-2, echoed-3, paid_off
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.paths import book_paths
from lib import seeds as seeds_mod, setup_doc

VALID_STATUSES = {"planned", "planted", "echoed-1", "echoed-2", "echoed-3", "echoed-4", "paid_off"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--series-slug", required=True)
    parser.add_argument("--book-number", type=int, required=True)
    parser.add_argument("--seed-id", required=True)
    parser.add_argument("--status", required=True)
    args = parser.parse_args()

    if args.status not in VALID_STATUSES:
        print(f"ERROR: invalid status '{args.status}'. Valid: {sorted(VALID_STATUSES)}", file=sys.stderr)
        return 2

    paths = book_paths(args.series_slug, args.book_number)
    seeds_list = seeds_mod.load_seeds(paths.seeds_md)
    if not seeds_mod.mark_status(seeds_list, args.seed_id, args.status):
        print(f"ERROR: seed id '{args.seed_id}' not found in {paths.seeds_md}", file=sys.stderr)
        return 3

    title = setup_doc.book_title(setup_doc.load(paths.setup_md))
    seeds_mod.save_seeds(paths.seeds_md, seeds_list, book_title=title)
    print(f"seed '{args.seed_id}' → {args.status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

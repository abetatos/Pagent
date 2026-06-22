#!/usr/bin/env python3
"""Resume-act bootstrap — assembles the start-of-session report.

Runs first thing in a fresh conversation. Reads everything the next
session needs from disk and emits a compact status report. Does NOT
build the full chapter context bundle (that's `build_context.py`
called by write-chapter). It only orients the agent + author so the
session can proceed.

Outputs to stdout:
  - Where in the book we are (next chapter, act).
  - Latest session handoff (verbatim — it's already compact).
  - Stable voice rules (from voice.md `Stable rules` blocks).
  - Active style rules (from style-rules.md).
  - Pendientes from open-questions.md.
  - Quick stats: chapters written / total, acts closed / total, last
    book-summary snippet.

Usage:
    python resume_act.py --series-slug <slug> --book-number <n>
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.paths import book_paths, chapter_numbers, act_numbers
from lib import notes_files, setup_doc, summaries as sum_mod


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _extract_stable_rules(voice_text: str) -> str:
    """Pull every `### Stable rules ...` block out of voice.md."""
    if not voice_text:
        return ""
    pattern = re.compile(
        r"(### Stable rules[^\n]*\n)((?:[ \t]*[-*][^\n]*\n)+)",
        re.MULTILINE,
    )
    blocks = []
    for m in pattern.finditer(voice_text):
        blocks.append(m.group(0).rstrip())
    return "\n\n".join(blocks)


def _extract_active_pendientes(questions_text: str) -> str:
    """Pull the `## Pendientes` block from open-questions.md."""
    if not questions_text:
        return ""
    m = re.search(
        r"##\s+Pendientes\s*\n(.*?)(?=\n##\s|\Z)",
        questions_text, re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return ""
    body = m.group(1).strip()
    if not body or body.startswith("- (none yet)"):
        return ""
    return body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--series-slug", required=True)
    parser.add_argument("--book-number", type=int, required=True)
    parser.add_argument(
        "--chapters-per-act",
        type=int,
        default=sum_mod.DEFAULT_CHAPTERS_PER_ACT,
    )
    args = parser.parse_args()

    paths = book_paths(args.series_slug, args.book_number)
    if not paths.book_root.exists():
        print(f"ERROR: book directory not found: {paths.book_root}", file=sys.stderr)
        return 2

    notes_files.ensure(paths)

    # Discovery
    setup_text = setup_doc.load(paths.setup_md)
    title = setup_doc.book_title(setup_text) or "(untitled)"
    total_chapters = setup_doc.num_chapters(setup_text) or 0
    written = chapter_numbers(paths)
    last_written = max(written) if written else 0
    next_ch = last_written + 1 if last_written < total_chapters else None
    acts_closed = act_numbers(paths)
    last_act = max(acts_closed) if acts_closed else 0
    next_act = sum_mod.act_number_for(next_ch, args.chapters_per_act) if next_ch else None

    print(f"# Resume session — {title}\n")
    print(f"- Book: {args.book_number}  ·  Series: {args.series_slug}")
    print(f"- Chapters written: **{last_written} / {total_chapters}**")
    print(f"- Acts closed: **{last_act}**")
    if next_ch:
        print(f"- Next: **chapter {next_ch}** (act {next_act})")
    else:
        print(f"- Book complete (all {total_chapters} chapters written).")

    # Latest session handoff (always relevant)
    handoff = _read(paths.session_handoff_md)
    if handoff and "TODO:" not in handoff:
        print("\n---\n## Session handoff (from last close-act)\n")
        print(handoff.strip())
    elif handoff and "TODO:" in handoff:
        print("\n---\n## Session handoff")
        print("\n> ⚠ Handoff has unfilled TODO sections. Either the last act")
        print("> wasn't properly closed, or this is the first act and there")
        print("> is no prior session. Treat as: no prior session-level state.")
    else:
        print("\n---\n## Session handoff")
        print("\n> No prior session handoff. This is a fresh book.")

    # Stable voice rules (consolidated)
    voice = _read(paths.voice_md)
    stable_rules = _extract_stable_rules(voice)
    if stable_rules:
        print("\n---\n## Stable voice rules (from voice.md consolidations)\n")
        print(stable_rules)
    else:
        print("\n---\n## Stable voice rules")
        print("\n> None yet. voice.md exists but has no `Stable rules` blocks —")
        print("> close-act will write them at the end of the act.")

    # Active style rules (full file is short)
    style_rules = _read(paths.style_rules_md)
    if style_rules.strip() and "- (no rules declared yet)" not in style_rules:
        print("\n---\n## Active style rules\n")
        print(style_rules.strip())

    # Pendientes from open-questions.md
    pendientes = _extract_active_pendientes(_read(paths.open_questions_md))
    if pendientes:
        print("\n---\n## Open questions (pendientes)\n")
        print(pendientes)

    # Latest book-summary snippet (if exists)
    book_sum = _read(paths.book_summary)
    if book_sum:
        # Pull the "What just happened" section if present, else last 400 chars
        m = re.search(
            r"##\s+What just happened\s*\n(.*?)(?=\n##\s|\Z)",
            book_sum, re.DOTALL | re.IGNORECASE,
        )
        if m:
            snippet = m.group(1).strip()
            print("\n---\n## What just happened (last update)\n")
            print(snippet)

    print("\n---")
    if next_ch:
        print(f"\n**Ready for `write-chapter {next_ch}`.**")
        print(f"\n*Reminder: the chapter writer will pull the full bundle via build_context.py — no need to load anything more manually.*")
    else:
        print(f"\n**Book complete.** Next: refresh book-summary, then `book-setup` for book {args.book_number + 1} if series continues.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

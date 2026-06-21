"""Hierarchical chapter summaries.

The summary system has three levels:
    Level 1 — per-chapter summary  (400-500 words, structured)
    Level 2 — per-act summary      (1500 words, merged from level 1)
    Level 3 — book summary         (rolling, 2000 words)

When the writer is in chapter N, the context builder picks:
    - act-level summaries for distant chapters (older than ~30 from current)
    - chapter-level summaries for recent past (last ~15)
    - full text for chapters N-1 and N-2

Compression flow (`compress-act` skill):
    Every time an act closes (configurable: every 7 chapters), the chapter
    summaries inside the act are merged into one act-level summary, AND the
    individual chapter summaries are kept (small enough that they cost
    nothing) but excluded from the writer's context window.

Seeds and shadow remain visible always — they live in plan/seeds.md and
plan/shadow.md and are never merged into summaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .paths import BookPaths, summary_chapter_numbers, act_numbers


# Tunable: how many chapters per act for compression purposes
DEFAULT_CHAPTERS_PER_ACT = 7

# Tunable: how many recent chapters keep their individual summary
RECENT_DETAIL_WINDOW = 15

# Tunable: how many recent chapters keep their FULL text
FULL_TEXT_WINDOW = 2


@dataclass
class SummaryPlan:
    """Tells the context builder which files to include for chapter N."""

    full_text_chapters: list[int]
    detail_chapters: list[int]
    act_summaries: list[int]


def act_number_for(chapter: int, chapters_per_act: int = DEFAULT_CHAPTERS_PER_ACT) -> int:
    """1-indexed act number for a chapter."""
    return (chapter - 1) // chapters_per_act + 1


def act_range(act: int, chapters_per_act: int = DEFAULT_CHAPTERS_PER_ACT) -> tuple[int, int]:
    """Inclusive [lo, hi] chapter range for an act."""
    lo = (act - 1) * chapters_per_act + 1
    hi = act * chapters_per_act
    return lo, hi


def plan_context(
    paths: BookPaths,
    current_chapter: int,
    chapters_per_act: int = DEFAULT_CHAPTERS_PER_ACT,
) -> SummaryPlan:
    """Decide which summary files to use for the context of `current_chapter`.

    Strategy:
        - Last FULL_TEXT_WINDOW chapters → full prose
        - Last RECENT_DETAIL_WINDOW chapters (excluding full-text) → individual ch-NN.md
        - Older → act-summary if it exists, else fall back to individual ch-NN.md
    """
    written = [n for n in summary_chapter_numbers(paths) if n < current_chapter]
    # Full-text uses the chapters/ files, not summaries — those are taken from
    # the chapters directory in the context builder. Here we list intended numbers.
    full_text = written[-FULL_TEXT_WINDOW:] if written else []
    full_text_set = set(full_text)

    # Recent detail: chapters in the window that are NOT in full_text
    recent_window = written[-(FULL_TEXT_WINDOW + RECENT_DETAIL_WINDOW):]
    detail = [n for n in recent_window if n not in full_text_set]

    # Distant chapters: anything older than the recent window
    distant = [n for n in written if n < (recent_window[0] if recent_window else current_chapter)]

    # For distant chapters, group by act and use the act summary if it exists.
    available_acts = set(act_numbers(paths))
    distant_acts = set()
    covered_by_act: set[int] = set()
    for n in distant:
        a = act_number_for(n, chapters_per_act)
        if a in available_acts:
            distant_acts.add(a)
            covered_by_act.add(n)

    # Distant chapters NOT covered by an act summary fall back to individual summaries
    fallback_detail = [n for n in distant if n not in covered_by_act]

    return SummaryPlan(
        full_text_chapters=full_text,
        detail_chapters=sorted(set(detail + fallback_detail)),
        act_summaries=sorted(distant_acts),
    )


def load_chapter_summary(paths: BookPaths, n: int) -> str:
    p = paths.chapter_summary(n)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


def load_act_summary(paths: BookPaths, a: int) -> str:
    p = paths.act_summary(a)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


def load_chapter_text(paths: BookPaths, n: int) -> str:
    p = paths.chapter_file(n)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


def render_summaries(paths: BookPaths, plan: SummaryPlan) -> str:
    """Build the 'story so far' block from the chosen summary files."""
    parts: list[str] = ["## Story so far\n"]

    if plan.act_summaries:
        parts.append("### Earlier acts (compressed)\n")
        for a in plan.act_summaries:
            parts.append(load_act_summary(paths, a))
            parts.append("")

    if plan.detail_chapters:
        parts.append("### Recent chapter summaries\n")
        for n in plan.detail_chapters:
            parts.append(load_chapter_summary(paths, n))
            parts.append("")

    if not (plan.act_summaries or plan.detail_chapters):
        parts.append("(This is the first chapter or early enough that no prior summaries exist yet.)\n")

    return "\n".join(parts).rstrip() + "\n"


def render_full_text(paths: BookPaths, chapter_nums: list[int]) -> str:
    """Build the 'recent chapters in full' block."""
    if not chapter_nums:
        return "## Recent chapters in full\n\n(This is the first chapter.)\n"
    parts = ["## Recent chapters in full\n"]
    for n in chapter_nums:
        text = load_chapter_text(paths, n)
        if text:
            parts.append(f"### Chapter {n} — full text\n")
            parts.append(text.strip())
            parts.append("")
    return "\n".join(parts).rstrip() + "\n"

"""Targeted grep over canon + summaries + chapters.

Returns hits in priority order so callers can read just enough.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .paths import BookPaths


@dataclass
class Hit:
    file: Path
    line_number: int
    line: str
    context_before: str
    context_after: str
    tier: str  # 'canon' | 'plan' | 'summary' | 'chapter'

    def render(self) -> str:
        return (
            f"### {self.file}:{self.line_number} [{self.tier}]\n"
            f"```\n{self.context_before}\n>>> {self.line}\n{self.context_after}\n```\n"
        )


def _scan_file(path: Path, pattern: re.Pattern, tier: str, context_lines: int = 2) -> list[Hit]:
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return []
    hits = []
    for i, line in enumerate(lines):
        if pattern.search(line):
            lo = max(0, i - context_lines)
            hi = min(len(lines), i + context_lines + 1)
            hits.append(
                Hit(
                    file=path,
                    line_number=i + 1,
                    line=line.strip(),
                    context_before="\n".join(lines[lo:i]),
                    context_after="\n".join(lines[i + 1:hi]),
                    tier=tier,
                )
            )
    return hits


def search(
    paths: BookPaths,
    query: str,
    max_hits: int = 12,
    tiers: tuple[str, ...] = ("canon", "plan", "summary", "chapter"),
) -> list[Hit]:
    """Search for `query` (regex) across canon, plan, summaries, chapters.

    Hits returned in tier priority order (canon first), then by file then line.
    """
    try:
        pattern = re.compile(query, re.IGNORECASE)
    except re.error:
        pattern = re.compile(re.escape(query), re.IGNORECASE)

    sources: list[tuple[str, Path]] = []
    if "canon" in tiers:
        for d in (paths.series_canon_dir, paths.canon_dir):
            if d.exists():
                for p in sorted(d.iterdir()):
                    if p.suffix == ".md":
                        sources.append(("canon", p))
    if "plan" in tiers and paths.plan_dir.exists():
        for p in sorted(paths.plan_dir.iterdir()):
            if p.suffix == ".md":
                sources.append(("plan", p))
    if "summary" in tiers and paths.summaries_dir.exists():
        for p in sorted(paths.summaries_dir.iterdir()):
            if p.suffix == ".md":
                sources.append(("summary", p))
    if "chapter" in tiers and paths.chapters_dir.exists():
        for p in sorted(paths.chapters_dir.iterdir(), reverse=True):
            if p.suffix == ".md":
                sources.append(("chapter", p))

    all_hits: list[Hit] = []
    for tier, p in sources:
        all_hits.extend(_scan_file(p, pattern, tier))
        if len(all_hits) >= max_hits:
            break

    return all_hits[:max_hits]


def render_hits(hits: list[Hit]) -> str:
    if not hits:
        return "No hits.\n"
    return "\n".join(h.render() for h in hits)

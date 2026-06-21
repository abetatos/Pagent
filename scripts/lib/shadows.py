"""Shadow timeline: the hidden truth behind the visible story.

shadow.md tells the writer what is REALLY happening behind the scenes — the
antagonist's actual moves, the secret connections, the truth of identities.
The writer reads this in full for every chapter, so they can plant seeds
truthfully even when the POV character is ignorant.

Format:

    # Shadow timeline — <book>

    ## Overview
    Free prose. The big-picture hidden truth of the book.

    ## Act 1 (chapters 1-10)
    Operational truth across this act...

    ### Chapter 1
    - Marek (the gardener) is the assassin sent by the Cardinal.
    - Today is his first day on palace grounds in that role.

    ### Chapter 2
    ...

This file, like seeds.md, is NEVER compressed. It is queried by chapter
to extract the relevant slice when context is being built.
"""

from __future__ import annotations

import re
from pathlib import Path


CHAPTER_HEADER_RE = re.compile(r"^###\s+(?:Chapter|Cap|Capítulo)\s+(\d+)", re.MULTILINE | re.IGNORECASE)
ACT_HEADER_RE = re.compile(r"^##\s+(?:Act|Acto)\s+(\d+)", re.MULTILINE | re.IGNORECASE)
# Any H2 header — used to terminate a chapter slice cleanly even when the
# next section is "## Midpoint" / "## Master truths" instead of "## Act N".
ANY_H2_RE = re.compile(r"^##\s+", re.MULTILINE)


def load_shadow(shadow_path: Path) -> str:
    """Return the raw text of shadow.md."""
    if not shadow_path.exists():
        return ""
    return shadow_path.read_text(encoding="utf-8")


def overview_section(shadow_text: str) -> str:
    """Extract the ## Overview section (everything before the first Act)."""
    if not shadow_text:
        return ""
    m = ACT_HEADER_RE.search(shadow_text)
    if not m:
        return shadow_text.strip()
    return shadow_text[: m.start()].strip()


def act_containing(shadow_text: str, chapter: int) -> str:
    """Find the act section whose chapter range contains the given chapter.

    Heuristic: act headers may include a range like "Act 1 (chapters 1-10)".
    We parse the range from the header; if absent, return the act based on
    chapter sub-headers within.
    """
    if not shadow_text:
        return ""

    # Slice the text into acts
    act_starts = list(ACT_HEADER_RE.finditer(shadow_text))
    if not act_starts:
        return shadow_text

    for i, m in enumerate(act_starts):
        start = m.start()
        end = act_starts[i + 1].start() if i + 1 < len(act_starts) else len(shadow_text)
        act_text = shadow_text[start:end]

        # Try parsing range from the header line
        header_line = act_text.split("\n", 1)[0]
        range_match = re.search(r"(\d+)\s*[-–]\s*(\d+)", header_line)
        if range_match:
            lo, hi = int(range_match.group(1)), int(range_match.group(2))
            if lo <= chapter <= hi:
                return act_text.strip()
        else:
            # Fall back: check chapter sub-headers in this act
            ch_nums = [int(c.group(1)) for c in CHAPTER_HEADER_RE.finditer(act_text)]
            if ch_nums and min(ch_nums) <= chapter <= max(ch_nums):
                return act_text.strip()

    return ""


def chapter_section(shadow_text: str, chapter: int) -> str:
    """Find the ### Chapter N section text.

    Returns the section (header + body) or empty string if not found.
    """
    if not shadow_text:
        return ""

    headers = list(CHAPTER_HEADER_RE.finditer(shadow_text))
    for i, m in enumerate(headers):
        if int(m.group(1)) == chapter:
            start = m.start()
            end = headers[i + 1].start() if i + 1 < len(headers) else len(shadow_text)
            # End at the next H2 (any kind: Act / Midpoint / Master truths)
            # if it appears before the next chapter header.
            next_h2 = ANY_H2_RE.search(shadow_text, m.end())
            if next_h2 and next_h2.start() < end:
                end = next_h2.start()
            return shadow_text[start:end].strip()
    return ""


def render_shadow_for_chapter(shadow_text: str, chapter: int) -> str:
    """Build the shadow block for a chapter's context.

    Includes: overview + act containing this chapter + this chapter's own slice.
    """
    if not shadow_text:
        return "## Shadow timeline\n\n(no shadow file yet)\n"

    parts = ["## Shadow timeline (hidden truth — writer-only, never on page)\n"]

    overview = overview_section(shadow_text)
    if overview and "## Overview" in overview:
        # already includes the heading inside
        parts.append(overview)
    elif overview:
        parts.append("### Overview\n" + overview)

    act = act_containing(shadow_text, chapter)
    if act:
        parts.append("")
        parts.append(act)

    # The chapter section is already part of the act text, but if not (eg act
    # ranges are not declared), include it explicitly.
    if act:
        ch_section = chapter_section(shadow_text, chapter)
        if ch_section and ch_section not in act:
            parts.append("")
            parts.append(ch_section)

    return "\n".join(parts) + "\n"

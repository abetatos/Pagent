#!/usr/bin/env python3
"""Deterministic audit of a book's planning files.

Reads setup.md, plan/*.md, and canon/*.md and produces a Markdown report of
mechanical findings the agent can layer qualitative critique on top of.

Findings include:
  - Setup: gating fields, chapter count, target words
  - Outline: chapters whose beat sheets are TODO-only or partial
  - Shadow: overview presence, master truths count, gaps
  - Seeds: invalid plant/payoff ordering, orphans, per-act distribution
  - Arcs: missing decision chapter / transformation type per principal
  - Canon: characters/factions/places named in canon but absent from outline,
    magic system completeness (source / cost / limits / thematic question /
    three tiers)

Usage:
    python audit_plan.py --series-slug <slug> --book-number <n>
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.paths import book_paths, BookPaths
from lib import setup_doc, seeds as seeds_mod, shadows as shadows_mod


CHAPTER_HEADER_RE = re.compile(
    r"^##\s+(?:Chapter|Cap|Capítulo)\s+(\d+)\b.*?$", re.IGNORECASE | re.MULTILINE
)
SUBSECTION_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
H3_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
# Templates use blockquotes only for placeholder/instruction text; real
# planning content goes in bullets or prose. Strip every `>` line.
TODO_LINE_RE = re.compile(r"^\s*>.*$", re.MULTILINE)
PLACEHOLDER_NAME_RE = re.compile(r"^\(.*\)$")


# ----- chapter outline parsing -------------------------------------------

def chapter_sections(outline_text: str) -> dict[int, str]:
    """Return {chapter_num: section_body} for every ## Chapter N section."""
    out: dict[int, str] = {}
    headers = list(CHAPTER_HEADER_RE.finditer(outline_text))
    for i, m in enumerate(headers):
        n = int(m.group(1))
        start = m.end()
        # End at the next ## chapter or end of file
        nxt = headers[i + 1].start() if i + 1 < len(headers) else len(outline_text)
        out[n] = outline_text[start:nxt]
    return out


def subsection_status(section_text: str, subsection_title: str) -> str:
    """Return 'missing' | 'todo' | 'filled' for the named subsection."""
    sub_pattern = re.compile(
        rf"^###\s+{re.escape(subsection_title)}\s*$", re.IGNORECASE | re.MULTILINE
    )
    m = sub_pattern.search(section_text)
    if not m:
        return "missing"
    # Body until next ### or end
    rest = section_text[m.end():]
    nxt = re.search(r"^###\s+", rest, re.MULTILINE)
    body = rest[: nxt.start() if nxt else len(rest)].strip()
    if not body:
        return "missing"
    # Strip blockquote TODO markers
    stripped = TODO_LINE_RE.sub("", body).strip()
    # If after stripping all TODO lines nothing remains, it's TODO-only
    return "todo" if not stripped else "filled"


def outline_findings(outline_text: str, declared_chapters: int) -> dict:
    sections = chapter_sections(outline_text)
    covered = sorted(sections.keys())
    expected = set(range(1, declared_chapters + 1))
    missing_chapters = sorted(expected - set(covered))
    extra_chapters = sorted(set(covered) - expected)

    missing_plot, missing_texture, missing_subtext, missing_function = [], [], [], []
    todo_only_chapters = []
    for n, body in sections.items():
        statuses = {
            "Plot beats": subsection_status(body, "Plot beats"),
            "Texture beats": subsection_status(body, "Texture beats"),
            "Subtext beats": subsection_status(body, "Subtext beats"),
        }
        if statuses["Plot beats"] != "filled":
            missing_plot.append(n)
        if statuses["Texture beats"] != "filled":
            missing_texture.append(n)
        if statuses["Subtext beats"] != "filled":
            missing_subtext.append(n)
        # Function in the act
        if "function in the act" in body.lower():
            # check the bullet line itself: "- **Function in the act:** ..."
            m = re.search(r"function in the act:\*\*\s*(.+)", body, re.IGNORECASE)
            if not m or m.group(1).strip().startswith("> TODO") or "TODO" in m.group(1):
                missing_function.append(n)
        if all(s != "filled" for s in statuses.values()):
            todo_only_chapters.append(n)

    return {
        "chapter_sections_present": covered,
        "missing_chapters": missing_chapters,
        "extra_chapters": extra_chapters,
        "todo_only_chapters": sorted(set(todo_only_chapters)),
        "missing_plot_beats": sorted(set(missing_plot)),
        "missing_texture_beats": sorted(set(missing_texture)),
        "missing_subtext_beats": sorted(set(missing_subtext)),
        "missing_function": sorted(set(missing_function)),
    }


# ----- shadow ------------------------------------------------------------

def shadow_findings(shadow_text: str, declared_chapters: int) -> dict:
    overview = shadows_mod.overview_section(shadow_text)
    overview_filled = bool(overview) and "TODO" not in overview

    master_truths_present = bool(
        re.search(r"##\s+Master truths", shadow_text, re.IGNORECASE)
    )
    # Count "Truth N:" bullets that aren't placeholders
    truth_lines = re.findall(
        r"^\s*-\s+\*\*Truth\s+\d+:\*\*\s*(.+)$", shadow_text, re.MULTILINE | re.IGNORECASE
    )
    truths_filled = [t for t in truth_lines if not t.strip().startswith("...")]

    # Per-chapter shadow sections (`### Chapter N`)
    ch_headers = [int(m.group(1)) for m in shadows_mod.CHAPTER_HEADER_RE.finditer(shadow_text)]
    chapters_with_shadow_section: list[int] = []
    for n in ch_headers:
        body = shadows_mod.chapter_section(shadow_text, n)
        if body:
            inner = re.sub(r"^###.+?\n", "", body, count=1)
            stripped = TODO_LINE_RE.sub("", inner).strip()
            if stripped:
                chapters_with_shadow_section.append(n)

    return {
        "overview_filled": overview_filled,
        "master_truths_section_present": master_truths_present,
        "master_truths_filled_count": len(truths_filled),
        "chapters_with_shadow_detail": sorted(set(chapters_with_shadow_section)),
        "chapter_count": declared_chapters,
    }


# ----- seeds -------------------------------------------------------------

def seeds_findings(seed_list, declared_chapters: int, chapters_per_act: int = 7, max_payoffs_per_chapter: int = 4) -> dict:
    invalid: list[str] = []
    plants_per_act: Counter = Counter()
    payoffs_per_act: Counter = Counter()
    payoffs_per_chapter: Counter = Counter()
    plant_chapters: set[int] = set()
    echo_chapters: set[int] = set()
    payoff_chapters: set[int] = set()

    for s in seed_list:
        if s.plant_in is None:
            invalid.append(f"[{s.id}] missing plant_in")
        if s.payoff_in is None:
            invalid.append(f"[{s.id}] missing payoff_in")
        if s.plant_in is not None and s.payoff_in is not None:
            if s.plant_in >= s.payoff_in:
                invalid.append(f"[{s.id}] plant ({s.plant_in}) is not before payoff ({s.payoff_in})")
            if s.plant_in > declared_chapters or s.payoff_in > declared_chapters:
                invalid.append(f"[{s.id}] plant/payoff outside book range (1..{declared_chapters})")
            for e in s.echo_in:
                if not (s.plant_in < e < s.payoff_in):
                    invalid.append(f"[{s.id}] echo ch {e} not strictly between plant ({s.plant_in}) and payoff ({s.payoff_in})")
        if not s.detail.strip() or not s.real_meaning.strip():
            invalid.append(f"[{s.id}] empty detail or real_meaning")
        if not s.how_to_plant.strip() or not s.how_to_pay_off.strip():
            invalid.append(f"[{s.id}] missing how_to_plant or how_to_pay_off guidance")

        if s.plant_in is not None:
            plant_chapters.add(s.plant_in)
            plants_per_act[((s.plant_in - 1) // chapters_per_act) + 1] += 1
        if s.payoff_in is not None:
            payoff_chapters.add(s.payoff_in)
            payoffs_per_act[((s.payoff_in - 1) // chapters_per_act) + 1] += 1
            payoffs_per_chapter[s.payoff_in] += 1
        for e in s.echo_in:
            echo_chapters.add(e)

    overloaded = sorted(
        [(ch, count) for ch, count in payoffs_per_chapter.items() if count > max_payoffs_per_chapter],
        key=lambda x: -x[1],
    )

    return {
        "total": len(seed_list),
        "invalid": invalid,
        "plant_chapters": sorted(plant_chapters),
        "echo_chapters": sorted(echo_chapters),
        "payoff_chapters": sorted(payoff_chapters),
        "plants_per_act": dict(plants_per_act),
        "payoffs_per_act": dict(payoffs_per_act),
        "payoffs_per_chapter": dict(payoffs_per_chapter),
        "overloaded_payoff_chapters": overloaded,
        "max_payoffs_per_chapter_threshold": max_payoffs_per_chapter,
        "chapters_without_any_seed_activity": [
            n for n in range(1, declared_chapters + 1)
            if n not in plant_chapters and n not in echo_chapters and n not in payoff_chapters
        ],
    }


# ----- arcs --------------------------------------------------------------

def arc_findings(arcs_text: str) -> dict:
    sections: dict[str, str] = {}
    headers = list(H2_RE.finditer(arcs_text))
    for i, m in enumerate(headers):
        name = m.group(1).strip()
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(arcs_text)
        sections[name] = arcs_text[start:end]

    principals: list[str] = []
    missing_decision: list[str] = []
    missing_transformation: list[str] = []
    missing_lie: list[str] = []
    missing_need: list[str] = []

    for name, body in sections.items():
        # Skip non-character h2s like "Waypoints" if they sneak in — heuristic:
        # principal sections have a Wound or Want bullet.
        if not re.search(r"\*\*(Wound|Want|Need|Lie)", body, re.IGNORECASE):
            continue
        if PLACEHOLDER_NAME_RE.match(name):
            continue
        # Strip trailing annotation like "Portaluz (secundario, sin arc completo)"
        clean_name = re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()
        principals.append(clean_name)
        # The colon may sit inside the bold close ("**Decision point (which chapter):**")
        # OR after the bold close ("**Decision point** — ch 25"). Accept both.
        def field_filled(key: str) -> bool:
            m = re.search(rf"\*\*{re.escape(key)}[^*]*\*\*\s*[:\-]?\s*(.+)", body, re.IGNORECASE)
            if not m:
                return False
            val = m.group(1).strip()
            return bool(val) and not val.startswith("> TODO") and "TODO" not in val
        if not field_filled("Decision point"):
            missing_decision.append(clean_name)
        if not field_filled("Transformation type"):
            missing_transformation.append(clean_name)
        if not field_filled("Lie they believe"):
            missing_lie.append(clean_name)
        if not field_filled("Need"):
            missing_need.append(clean_name)

    return {
        "principals": principals,
        "missing_decision_chapter": missing_decision,
        "missing_transformation_type": missing_transformation,
        "missing_lie": missing_lie,
        "missing_need": missing_need,
    }


# ----- canon -------------------------------------------------------------

def canon_names(text: str, header_level: int = 2) -> list[str]:
    pat = H2_RE if header_level == 2 else H3_RE
    names: list[str] = []
    for m in pat.finditer(text):
        n = m.group(1).strip()
        # Skip generic headers and placeholder names
        if PLACEHOLDER_NAME_RE.match(n):
            continue
        if n.lower() in {"places", "macro geography", "calendar / time", "languages / scripts"}:
            continue
        names.append(n)
    return names


def canon_findings(paths: BookPaths, outline_text: str, plan_haystack: str) -> dict:
    chars_text = paths.canon_file("characters").read_text(encoding="utf-8") if paths.canon_file("characters").exists() else ""
    facs_text = paths.canon_file("factions").read_text(encoding="utf-8") if paths.canon_file("factions").exists() else ""
    world_text = paths.canon_file("world").read_text(encoding="utf-8") if paths.canon_file("world").exists() else ""
    magic_text = paths.canon_file("magic").read_text(encoding="utf-8") if paths.canon_file("magic").exists() else ""

    character_names = canon_names(chars_text, header_level=2)
    # Strip "(...)" annotations from character names (e.g. "Vela (lectora)")
    character_names = [re.sub(r"\s*\([^)]*\)\s*$", "", n).strip() for n in character_names]
    faction_names = canon_names(facs_text, header_level=2)
    # Strip the parenthetical color/caste suffix from faction names too
    # ("Iglesia (Blanco)" → "Iglesia") so the plan-coverage check finds
    # them by their bare name in shadow/seeds/arcs.
    faction_names = [re.sub(r"\s*\([^)]*\)\s*$", "", n).strip() for n in faction_names]
    # Places are H3 under the Places section in world.md
    place_names: list[str] = []
    places_match = re.search(r"##\s+Places\s*$", world_text, re.IGNORECASE | re.MULTILINE)
    if places_match:
        body = world_text[places_match.end():]
        for m in H3_RE.finditer(body):
            n = m.group(1).strip()
            if n.lower().startswith("place name"):
                continue
            place_names.append(n)
    # Strip parenthetical TODO suffixes ("(TODO: nombrar)")
    place_names = [re.sub(r"\s*\([^)]*\)\s*$", "", n).strip() for n in place_names]

    def absent_from_plan(names: list[str]) -> list[str]:
        out: list[str] = []
        for n in names:
            if not n:
                continue
            if not re.search(rf"\b{re.escape(n)}\b", plan_haystack, re.IGNORECASE):
                out.append(n)
        return out

    # Magic completeness
    def has_section(title: str) -> bool:
        return bool(re.search(rf"^##\s+{re.escape(title)}", magic_text, re.IGNORECASE | re.MULTILINE))

    def section_filled(title: str) -> bool:
        m = re.search(
            rf"^##\s+{re.escape(title)}.*?$([\s\S]*?)(?=^##\s|\Z)",
            magic_text, re.IGNORECASE | re.MULTILINE,
        )
        if not m:
            return False
        body = m.group(1)
        stripped = TODO_LINE_RE.sub("", body).strip()
        return bool(stripped)

    magic = {
        "source_filled": section_filled("Source"),
        "mechanic_filled": section_filled("Mechanic"),
        "costs_filled": section_filled("Costs"),
        "limits_filled": section_filled("Hard limits"),
        "thematic_question_filled": section_filled("Thematic question forced"),
        "tiers_filled": section_filled("Three escalation tiers"),
        "vocabulary_filled": section_filled("Vocabulary"),
    }

    return {
        "characters_named": character_names,
        "characters_absent_from_plan": absent_from_plan(character_names),
        "factions_named": faction_names,
        "factions_absent_from_plan": absent_from_plan(faction_names),
        "places_named": place_names,
        "places_absent_from_plan": absent_from_plan(place_names),
        "magic_completeness": magic,
    }


# ----- setup gating ------------------------------------------------------

def setup_findings(setup_text: str) -> dict:
    title = setup_doc.book_title(setup_text)
    nch = setup_doc.num_chapters(setup_text)
    lang = setup_doc.language(setup_text)
    lo, hi = setup_doc.words_per_chapter_range(setup_text)

    gating = []
    # World premise must be ≥3 sentences. Templates wrap the premise in a
    # `>` blockquote for visual emphasis; we strip the `> ` prefix and any
    # `> TODO ...` lines, then count sentences in what remains.
    world = setup_doc.get_section(setup_text, "premise of world") or setup_doc.get_section(setup_text, "premisa")
    if world:
        clean = re.sub(r"^\s*>\s*TODO.*$", "", world, flags=re.MULTILINE)
        clean = re.sub(r"^\s*>\s?", "", clean, flags=re.MULTILINE)  # strip > prefix
        # Strip bullet markers (they may be metadata like "- Era:" which is
        # not part of the premise itself).
        clean = re.sub(r"^\s*[-*]\s.*$", "", clean, flags=re.MULTILINE)
        sentences = [s.strip() for s in re.split(r"[.!?]+", clean) if s.strip() and len(s.strip()) > 10]
        if len(sentences) < 3:
            gating.append(f"world premise has < 3 sentences (found {len(sentences)})")
    else:
        gating.append("world premise missing")

    # Magic: source + mechanic must be present and non-placeholder. We treat
    # a value as a placeholder only when it is *entirely* parenthesized
    # (e.g. "(where the magic comes from — substance, …)") or empty.
    def _is_placeholder(val: str) -> bool:
        v = val.strip()
        if not v:
            return True
        return v.startswith("(") and v.endswith(")")

    magic_sec = setup_doc.get_section(setup_text, "magic system") or setup_doc.get_section(setup_text, "sistema de magia") or setup_doc.get_section(setup_text, "magia")
    if magic_sec:
        flds = setup_doc.fields(magic_sec)
        if _is_placeholder(flds.get("source", "")):
            gating.append("magic source missing")
        if _is_placeholder(flds.get("mechanic", "")):
            gating.append("magic mechanic missing")
    else:
        gating.append("magic system section missing")

    # Open decisions: parse ## Open decisions and flag any item marked
    # gating that does not show RESUELTO: / DECIDIDO: in its body.
    gating_unresolved: list[str] = []
    decisions_section = setup_doc.get_section(setup_text, "open decisions") or setup_doc.get_section(setup_text, "decisiones abiertas") or setup_doc.get_section(setup_text, "decisiones aún abiertas")
    if decisions_section:
        items = re.split(r"\n\s*\d+\.\s+", "\n" + decisions_section)
        for item in items[1:]:
            is_gating = bool(re.search(r"gating:\s*(s[iíy]|yes|true)", item, re.IGNORECASE))
            is_resolved = bool(re.search(r"resuelto|decidido|resolved|decided|\bdecisión:", item, re.IGNORECASE))
            if is_gating and not is_resolved:
                first_line = item.split("\n", 1)[0].strip()
                # Trim trailing bold/punctuation
                first_line = re.sub(r"\*+\s*$", "", first_line).rstrip(".:").strip()
                gating_unresolved.append(first_line[:120])

    return {
        "title": title,
        "num_chapters": nch,
        "language": lang,
        "words_per_chapter": (lo, hi),
        "gating_issues": gating,
        "gating_decisions_unresolved": gating_unresolved,
    }


# ----- rendering ---------------------------------------------------------

def render_report(s: dict, o: dict, sh: dict, sd: dict, ar: dict, c: dict) -> str:
    lines: list[str] = ["# Plan audit (deterministic)\n"]

    lines.append("## Setup\n")
    lines.append(f"- Title: **{s['title']}**")
    lines.append(f"- Chapters: **{s['num_chapters']}**")
    lines.append(f"- Language: **{s['language']}**")
    lines.append(f"- Target words / chapter: **{s['words_per_chapter'][0]}-{s['words_per_chapter'][1]}**")
    if s["gating_issues"]:
        lines.append("- **Gating issues:**")
        for issue in s["gating_issues"]:
            lines.append(f"  - {issue}")
    else:
        lines.append("- Gating issues: none")
    if s.get("gating_decisions_unresolved"):
        lines.append("- **Open decisions still gating (must resolve before ch 1):**")
        for d in s["gating_decisions_unresolved"]:
            lines.append(f"  - {d}")
    else:
        lines.append("- Open decisions: no unresolved gating")
    lines.append("")

    lines.append("## Outline\n")
    lines.append(f"- Chapter sections present: {len(o['chapter_sections_present'])}")
    if o["missing_chapters"]:
        lines.append(f"- **Missing chapter sections:** {o['missing_chapters']}")
    if o["extra_chapters"]:
        lines.append(f"- **Extra chapter sections beyond declared count:** {o['extra_chapters']}")
    if o["todo_only_chapters"]:
        lines.append(f"- **Chapters whose beat sheet is entirely TODO:** {o['todo_only_chapters']}")
    if o["missing_plot_beats"]:
        lines.append(f"- Missing plot beats: {o['missing_plot_beats']}")
    if o["missing_texture_beats"]:
        lines.append(f"- Missing texture beats: {o['missing_texture_beats']}")
    if o["missing_subtext_beats"]:
        lines.append(f"- Missing subtext beats: {o['missing_subtext_beats']}")
    if o["missing_function"]:
        lines.append(f"- Missing 'function in the act' line: {o['missing_function']}")
    lines.append("")

    lines.append("## Shadow timeline\n")
    lines.append(f"- Overview filled: {'yes' if sh['overview_filled'] else '**no**'}")
    lines.append(f"- Master truths declared: {sh['master_truths_filled_count']}")
    if sh["chapters_with_shadow_detail"]:
        lines.append(f"- Chapters with shadow detail: {sh['chapters_with_shadow_detail']}")
    else:
        lines.append("- **No per-chapter shadow detail filled.**")
    lines.append("")

    lines.append("## Seeds\n")
    lines.append(f"- Total: **{sd['total']}**")
    if sd["invalid"]:
        lines.append("- **Invalid entries:**")
        for v in sd["invalid"]:
            lines.append(f"  - {v}")
    lines.append(f"- Plants per act: {sd['plants_per_act']}")
    lines.append(f"- Payoffs per act: {sd['payoffs_per_act']}")
    if sd.get("overloaded_payoff_chapters"):
        threshold = sd["max_payoffs_per_chapter_threshold"]
        lines.append(
            f"- **Overloaded payoff chapters (> {threshold} per chapter):**"
        )
        for ch, count in sd["overloaded_payoff_chapters"]:
            lines.append(f"  - ch {ch}: {count} payoffs")
    if sd["chapters_without_any_seed_activity"]:
        lines.append(f"- Chapters with no plant/echo/payoff: {sd['chapters_without_any_seed_activity']}")
    lines.append("")

    lines.append("## Character arcs\n")
    if not ar["principals"]:
        lines.append("- **No principal arcs found.**")
    else:
        lines.append(f"- Principals: {ar['principals']}")
        if ar["missing_decision_chapter"]:
            lines.append(f"- Missing decision-point chapter: {ar['missing_decision_chapter']}")
        if ar["missing_transformation_type"]:
            lines.append(f"- Missing transformation type: {ar['missing_transformation_type']}")
        if ar["missing_lie"]:
            lines.append(f"- Missing 'lie they believe': {ar['missing_lie']}")
        if ar["missing_need"]:
            lines.append(f"- Missing 'need': {ar['missing_need']}")
    lines.append("")

    lines.append("## Canon\n")
    lines.append(f"- Characters in canon: {c['characters_named']}")
    if c["characters_absent_from_plan"]:
        lines.append(f"- **Characters never mentioned in plan (outline+shadow+arcs+seeds):** {c['characters_absent_from_plan']}")
    lines.append(f"- Factions in canon: {c['factions_named']}")
    if c["factions_absent_from_plan"]:
        lines.append(f"- **Factions never mentioned in plan:** {c['factions_absent_from_plan']}")
    lines.append(f"- Places in canon: {c['places_named']}")
    if c["places_absent_from_plan"]:
        lines.append(f"- **Places never mentioned in plan:** {c['places_absent_from_plan']}")
    m = c["magic_completeness"]
    missing_magic = [k for k, v in m.items() if not v]
    if missing_magic:
        lines.append(f"- **Magic sections empty/missing:** {missing_magic}")
    else:
        lines.append("- Magic sections all present.")
    lines.append("")

    return "\n".join(lines)


# ----- main --------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--series-slug", required=True)
    parser.add_argument("--book-number", type=int, required=True)
    parser.add_argument("--output", default=None, help="Write report here instead of stdout.")
    args = parser.parse_args()

    paths = book_paths(args.series_slug, args.book_number)
    if not paths.setup_md.exists():
        print(f"ERROR: setup.md not found at {paths.setup_md}", file=sys.stderr)
        return 2
    if not paths.outline_md.exists():
        print(f"ERROR: plan/outline.md not found. Run plan-book first.", file=sys.stderr)
        return 2

    setup_text = setup_doc.load(paths.setup_md)
    outline_text = paths.outline_md.read_text(encoding="utf-8")
    shadow_text = shadows_mod.load_shadow(paths.shadow_md)
    seed_list = seeds_mod.load_seeds(paths.seeds_md)
    arcs_text = paths.arcs_md.read_text(encoding="utf-8") if paths.arcs_md.exists() else ""

    s = setup_findings(setup_text)
    declared = s["num_chapters"] or 0
    o = outline_findings(outline_text, declared)
    sh = shadow_findings(shadow_text, declared)
    sd = seeds_findings(seed_list, declared)
    ar = arc_findings(arcs_text)
    # Combined plan haystack — outline + shadow + arcs + seeds — so the
    # "absent from plan" check doesn't false-positive when the outline is
    # still TODO but the character lives in shadow/seeds/arcs.
    seeds_raw = paths.seeds_md.read_text(encoding="utf-8") if paths.seeds_md.exists() else ""
    plan_haystack = "\n".join([outline_text, shadow_text, arcs_text, seeds_raw])
    c = canon_findings(paths, outline_text, plan_haystack)

    report = render_report(s, o, sh, sd, ar, c)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"audit written to {args.output}")
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())

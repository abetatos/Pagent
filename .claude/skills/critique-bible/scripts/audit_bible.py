#!/usr/bin/env python3
"""Deterministic structural audit of a world bible.

Operates on `output/<series>/bible.md`. Returns a Markdown report that
critique-bible reads before doing the qualitative adversarial pass.

The bar is intentionally adversarial: the bible is the foundation of
everything downstream, so this audit prefers false positives (flag a
gap) over false negatives (miss a gap).

Sections expected (matched flexibly by regex):
  1. Idea en una frase / one-sentence idea
  2. Two layers (anti-confusion)
  3. Magic
  4. Laws / rules
  5. Scaled or inverted system declaration
  6. Limitations
  7. Castes / factions
  8. Subplots
  9. Characters
 10. History / chronology
 11. Geography
 12. Structure (book or trilogy)
 13. Clock — why now
 14. Mandatory plantings (loaded guns)
 15. Open decisions

Plus deep checks:
  - magic: source, costs >= 2, hard limits >= 3, thematic question OR
    inverted-system declared
  - characters: protagonist + antagonist with want/need/lie/wound
  - subplots: count, each with >= 3 contact points and distinct theme
  - geography: >= 5 named places
  - history: >= 3 enumerated events
  - structure: each book's clímax uses an active-decision verb
  - trilogy: each book has a distinct motor
  - open decisions: each marked Gating: yes/no; any gating unresolved
    is MUST-fix

Usage:
    python audit_bible.py --series-slug <slug>
    python audit_bible.py --series-slug <slug> --output <path>
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.paths import OUTPUT_ROOT


# ---- section anchors ----------------------------------------------------
# Each section spec: required substring(s) in header (case-insensitive).
SECTION_SPECS: list[tuple[str, list[str]]] = [
    ("idea_one_sentence", ["idea en una frase", "idea en una sola frase", "one-sentence idea", "the idea in one"]),
    ("two_layers", ["dos capas", "two layers", "anti-confusión", "anti-confusion"]),
    ("magic_how", ["la magia", "the magic", "magic system", "sistema mágico", "sistema de magia"]),
    ("laws", ["leyes", "laws", "rules of"]),
    ("scaled_or_inverted", ["sistema escalado", "escalado o invertido", "scaled or inverted", "sistema invertido", "system is inverted", "construido al revés", "construido al reves"]),
    ("limitations", ["limitaciones", "limitations"]),
    ("factions", ["castas", "facciones", "factions", "castes", "orders"]),
    ("subplots", ["subtramas", "subtrama", "subplots"]),
    ("characters", ["personajes", "characters"]),
    ("history", ["historia", "cronología", "cronologia", "history", "chronology"]),
    ("geography", ["geografía", "geografia", "geography"]),
    ("structure", ["estructura", "structure"]),
    ("clock", ["el reloj", "the clock", "why now", "por qué ahora", "porque ahora"]),
    ("mandatory_plantings", ["siembras obligatorias", "loaded guns", "mandatory plantings", "exigencias de siembra"]),
    ("open_decisions", ["decisiones aún abiertas", "decisiones abiertas", "open decisions"]),
]


def find_section_body(text: str, anchors: list[str]) -> tuple[str, str] | tuple[None, None]:
    """Find a section by any of the anchor substrings in an H1/H2 header.

    Returns (header_line, body) or (None, None) if not found.
    """
    headers = list(re.finditer(r"^(#{1,3})\s+(.+?)\s*$", text, re.MULTILINE))
    for i, m in enumerate(headers):
        title = m.group(2).strip().lower()
        if any(a in title for a in anchors):
            start = m.end()
            # End at the next header of same or higher level
            level = len(m.group(1))
            end = len(text)
            for n in headers[i + 1:]:
                if len(n.group(1)) <= level:
                    end = n.start()
                    break
            return m.group(0), text[start:end].strip()
    return None, None


def _content_length(body: str) -> int:
    """Return non-quote, non-bullet content character count."""
    # Strip TODO blockquotes
    body = re.sub(r"^\s*>\s*TODO.*$", "", body, flags=re.MULTILINE)
    # Strip empty markdown
    body = re.sub(r"^\s*[-*]\s*___+\s*$", "", body, flags=re.MULTILINE)  # template placeholders ___
    body = re.sub(r"^\s*___+\s*$", "", body, flags=re.MULTILINE)
    return len(body.strip())


def _has_real_content(body: str) -> bool:
    """A section is 'filled' if it has > 80 chars of non-placeholder text."""
    if not body:
        return False
    return _content_length(body) > 80


# ---- specific deep checks -----------------------------------------------

def check_magic(body: str) -> dict:
    """Source + Mechanic + Costs (>=2) + Hard limits (>=3).

    Tries the template format first (explicit `**Source:**` labels);
    falls back to free-prose detection so an organic bible (v4-style)
    still passes when the content is there.
    """
    result = {
        "source_present": False,
        "mechanic_present": False,
        "costs_count": 0,
        "limits_count": 0,
        "thematic_question_present": False,
    }
    if not body:
        return result

    # ---- Source (explicit label OR prose fallback) ----
    m = re.search(r"(?:\*\*)?\s*(?:Source|Fuente|Origen)\s*[:\-]\s*\*?\*?\s*(.+)", body, re.IGNORECASE)
    if m and len(m.group(1).strip()) > 15 and not m.group(1).strip().startswith("("):
        result["source_present"] = True
    else:
        # Prose fallback: section is non-trivial AND mentions a source-like
        # concept (aura, viene de, es luz, comes from, source).
        if len(body) > 200 and re.search(
            r"\baura\b|viene de|es (?:luz|magia)|comes from|source is|nace de|brota de|surge de",
            body, re.IGNORECASE,
        ):
            result["source_present"] = True

    # ---- Mechanic (explicit label OR prose fallback) ----
    if re.search(r"(?:\*\*)?\s*(?:Mechanic|Mecánica|Mecanica|Mechanism)", body, re.IGNORECASE):
        result["mechanic_present"] = True
    else:
        # Prose fallback: section describes HOW the magic operates.
        if re.search(
            r"se accede|se manifiesta|se irradia|se canaliza|step by step|paso a paso|cómo funciona|funciona así",
            body, re.IGNORECASE,
        ):
            result["mechanic_present"] = True

    # ---- Costs ----
    cost_section = re.search(
        r"(?:#{2,4}\s*(?:Costes?|Costs?)\s*(?:\([^)]*\))?|(?:\*\*)?(?:Costes?|Costs?)(?:\*\*)?)\s*[:\-]?\s*(.*?)(?=\n#{2,4}|\n\*\*[A-Z]|\Z)",
        body, re.IGNORECASE | re.DOTALL,
    )
    if cost_section:
        bullets = re.findall(r"^\s*[-*]\s+(.+)$", cost_section.group(1), re.MULTILINE)
        real = [b for b in bullets if not b.strip().startswith("(") and len(b.strip()) > 15]
        result["costs_count"] = len(real)

    # Prose fallback: count distinct cost concepts mentioned in prose.
    # Each match counts at most once.
    if result["costs_count"] < 2:
        prose_cost_concepts = {
            "calor": r"\bcalor\b|\bheat\b|fuga térmica|burn out|cocerse",
            "social": r"social\s+cost|coste\s+social|stigma|estigma|marca social",
            "emocional": r"emocional|emotional|grief|paranoia|numbness",
            "identidad": r"identidad|identity|memoria|recuerdo|self",
            "fisico_otro": r"agotamiento|exhaustion|aging|envejec|scarring",
            "material": r"material(?:\s+cost)?|consumed|consume|resource(?:\s+is)?\s+scarce",
        }
        prose_count = sum(
            1 for pat in prose_cost_concepts.values()
            if re.search(pat, body, re.IGNORECASE)
        )
        if prose_count > result["costs_count"]:
            result["costs_count"] = prose_count

    # ---- Hard limits ----
    limits_section = re.search(
        r"(?:#{2,4}\s*(?:Hard limits|Límites duros|Limites duros|Limits)\s*(?:\([^)]*\))?|(?:\*\*)?(?:Hard limits|Límites duros|Limites duros|Limits)(?:\*\*)?)\s*[:\-]?\s*(.*?)(?=\n#{2,4}|\n\*\*[A-Z]|\Z)",
        body, re.IGNORECASE | re.DOTALL,
    )
    if limits_section:
        bullets = re.findall(r"^\s*[-*]\s+(.+)$", limits_section.group(1), re.MULTILINE)
        real = [b for b in bullets if not b.strip().startswith("(") and len(b.strip()) > 15]
        result["limits_count"] = len(real)

    if result["limits_count"] < 3:
        # Prose fallback: count "no puede / cannot / never" patterns + named
        # categories of limit.
        prose_limit_concepts = {
            "no_puede": r"no puede(?:\s+ser)?|cannot|can never|never can|nunca puede",
            "alcance": r"\balcance\b|inverse square|1/r|range falls|distance",
            "tiempo": r"duraci[oó]n|cannot persist|past a duration|duration",
            "transfer": r"cannot be transferred|no se transfiere|cannot share",
            "complementario": r"complementari|cancel|anula|annul",
            "aura_fija": r"aura fija|fixed aura|cannot train|no se entrena|cannot grow|no crece",
            "calor_force": r"calor\b.*\bfuerza|forcing leads to|exceeding.*cooks|fuga térmica",
        }
        prose_count = sum(
            1 for pat in prose_limit_concepts.values()
            if re.search(pat, body, re.IGNORECASE)
        )
        if prose_count > result["limits_count"]:
            result["limits_count"] = prose_count

    # ---- Thematic question ----
    if re.search(r"thematic question|pregunta moral|pregunta temática|pregunta tematica|thematic role|moral question", body, re.IGNORECASE):
        m = re.search(
            r"(?:thematic question|pregunta moral|pregunta temática|pregunta tematica|thematic role|moral question)[^:\n]*[:\-]?\s*(?:\*\*)?\s*(.+)",
            body, re.IGNORECASE,
        )
        if m and len(m.group(1).strip()) > 10 and "___" not in m.group(1):
            result["thematic_question_present"] = True
    elif re.search(r"\?\s*$", body.strip(), re.MULTILINE):
        # Free-prose: section ends with or contains an explicit ethical question.
        if re.search(
            r"¿(?:vale|debe|merece|puede|hay|quién|qué)|\bwho (?:lives|pays)\b|who deserves",
            body, re.IGNORECASE,
        ):
            result["thematic_question_present"] = True

    return result


def check_scaled_or_inverted(body: str) -> dict:
    """At least one of: three tiers declared, or inverted-system declared."""
    if not body:
        return {"scaled_tiers_declared": False, "inverted_system_declared": False}

    body_lower = body.lower()
    has_common = bool(re.search(r"common|común|comun", body_lower))
    has_skilled = bool(re.search(r"skilled|hábil|habil", body_lower))
    has_apex = bool(re.search(r"apex|cumbre|tope", body_lower))
    scaled_tiers = has_common and has_skilled and has_apex

    # Inverted system: any of the keywords in the body is enough — the
    # fact we found the section by its header ("invertido / al revés")
    # tells us the author is declaring the inversion. We just check the
    # body backs it up with the concept of erosion.
    inverted = bool(re.search(r"erosi[oó]n|erosion|desgaste|al rev[eé]s|invertido|inverted", body_lower))

    return {
        "scaled_tiers_declared": scaled_tiers,
        "inverted_system_declared": inverted,
    }


def check_characters(body: str) -> dict:
    """Count principals with want/need/lie/wound markers, plus antagonist."""
    if not body:
        return {"principal_count": 0, "with_full_arc": 0, "has_antagonist_with_thesis": False}

    # Each principal is an H3 section.
    sections = re.split(r"^###\s+", body, flags=re.MULTILINE)
    principal_count = 0
    with_full_arc = 0
    has_antagonist_with_thesis = False
    for sec in sections[1:]:
        head = sec.split("\n", 1)[0].lower()
        # Skip empty placeholders ("(name)") and headers like "Personaje 1 — nombre" with no body
        if re.search(r"^\s*\(.*\)\s*$", head):
            continue
        principal_count += 1
        # Accept bold field, italic field, or inline "want:" / "need:" /
        # "lie:" / "wound:" / "herida".
        wnt = bool(re.search(r"\*\*\s*Want|\*Want|\bwant\s*[:\-]", sec, re.IGNORECASE))
        need = bool(re.search(r"\*\*\s*Need|\*Need|\bneed\s*[:\-]|\bnecesidad\s*[:\-]", sec, re.IGNORECASE))
        lie = bool(re.search(r"\*\*\s*Lie|\*Lie|\blie\s*[:\-]|\bmentira\s*[:\-]", sec, re.IGNORECASE))
        wound = bool(re.search(r"\*\*\s*Wound|\*Wound|\bwound\s*[:\-]|\bherida\s*[:\-]", sec, re.IGNORECASE))
        if wnt and need and lie and wound:
            with_full_arc += 1
        if re.search(r"antagonist|antagonista|cara de la orden|inquisidor", head, re.IGNORECASE):
            # Antagonist with thesis — accept `**Tesis:** ...`, `**Tesis (por
            # qué tiene razón):** ...` (colon inside bold), or `*Tesis* — ...`
            tesis = re.search(
                r"(?:\*\*?[^*\n]*\bTesis\b[^*\n]*\*?\*?|(?:^|\s)Tesis\b[^:\n]*)[:\-]?\s*(.{20,})",
                sec, re.IGNORECASE | re.MULTILINE,
            )
            if tesis and len(tesis.group(1).strip()) > 15:
                has_antagonist_with_thesis = True

    return {
        "principal_count": principal_count,
        "with_full_arc": with_full_arc,
        "has_antagonist_with_thesis": has_antagonist_with_thesis,
    }


def check_subplots(body: str) -> dict:
    """Count subplots and how many have contact points / distinct theme.

    Tries the template H3 format first; falls back to prose detection if
    the bible declares subplots inline (e.g., v4 §8 "La subtrama: la
    revolución verde").
    """
    if not body:
        return {"count": 0, "with_contact_points": 0, "with_distinct_theme": 0}

    sections = re.split(r"^###\s+", body, flags=re.MULTILINE)
    count = 0
    with_contact_points = 0
    with_distinct_theme = 0
    for sec in sections[1:]:
        head = sec.split("\n", 1)[0]
        if re.search(r"^\s*\(.*\)\s*$", head):
            continue
        count += 1
        contacts = re.findall(r"punto de contacto|toque \d|touch(?:point)?", sec, re.IGNORECASE)
        if len(contacts) >= 3:
            with_contact_points += 1
        theme = re.search(r"(?:tema|theme)[^:\n]*[:\-]\s*(?:\*\*)?\s*(.+)", sec, re.IGNORECASE)
        if theme and len(theme.group(1).strip()) > 10:
            with_distinct_theme += 1

    # Prose fallback: if no H3 found but the section talks about ≥ 1
    # subtrama, count those.
    if count == 0:
        # Each "subtrama" / "subplot" mention as a separate concept.
        primary = re.search(
            r"(?:la|una)\s+subtrama|primary\s+subplot|main\s+subplot",
            body, re.IGNORECASE,
        )
        secondary = re.search(
            r"subtrama\s+secundaria|secondary\s+subplot|subplot\s+b\b",
            body, re.IGNORECASE,
        )
        if primary:
            count += 1
        if secondary:
            count += 1
        # Check for ≥ 3 contact points in the body itself
        contacts = re.findall(r"toque\s*\d|punto de contacto|touch \d", body, re.IGNORECASE)
        if count and len(contacts) >= 3:
            with_contact_points = 1
        if count and re.search(r"\btema\b|\btheme\b", body, re.IGNORECASE):
            with_distinct_theme = 1

    return {
        "count": count,
        "with_contact_points": with_contact_points,
        "with_distinct_theme": with_distinct_theme,
    }


def check_history(body: str) -> dict:
    """Count enumerated historical events."""
    if not body:
        return {"event_count": 0}
    enumerated = re.findall(r"^\s*\d+\.\s+\*\*", body, re.MULTILINE)
    if not enumerated:
        # Maybe bullets with bold
        enumerated = re.findall(r"^\s*-\s+\*\*[^*]+\*\*", body, re.MULTILINE)
    return {"event_count": len(enumerated)}


def check_geography(body: str) -> dict:
    """Count named places — H3 sub-headers OR bullets with bold lead."""
    if not body:
        return {"places_count": 0}
    h3 = re.findall(r"^###\s+(.+)$", body, re.MULTILINE)
    bullets = re.findall(r"^\s*-\s+\*\*([^*]+):\*\*", body, re.MULTILINE)
    names = []
    for h in h3:
        n = h.strip()
        if n.lower() in ("place 1", "place 2", "place 3", "macro political map", "travel", "places"):
            continue
        # Skip placeholder names
        if re.match(r"^(?:Place|Lugar)\s+name", n, re.IGNORECASE):
            continue
        names.append(n)
    for b in bullets:
        n = b.strip()
        # Skip purely structural bullets like "Macro político"
        if n.lower() in ("type", "sensory anchor", "function in plot", "who lives there", "political stance"):
            continue
        # Skip placeholder labels
        if re.match(r"^(?:Place|Lugar)\s+\d+", n, re.IGNORECASE):
            continue
        names.append(n)
    return {"places_count": len(set(names))}


def check_structure(body: str) -> dict:
    """For trilogies: each book has a motor + climax. Climax should be active."""
    if not body:
        return {"book_blocks": 0, "passive_climaxes": [], "missing_motor": []}

    # Find every book block — supports both ### Libro I header AND inline
    # **Libro I — title** at the start of a paragraph. The inline pattern
    # tolerates italic spans inside the bold ("**Libro I — *El Apagado*.**").
    h3_books = list(re.finditer(
        r"^###\s+(Libro|Book)\s+([IVX0-9]+)[\s\S]*?(?=\n###\s+(?:Libro|Book)|\Z)",
        body, re.IGNORECASE | re.MULTILINE,
    ))
    inline_books = list(re.finditer(
        r"\*\*\s*(Libro|Book)\s+([IVX0-9]+)[^\n]*?\*\*[\s\S]*?(?=\n\*\*\s*(?:Libro|Book)\s+[IVX0-9]+[^\n]*?\*\*|\Z)",
        body, re.IGNORECASE,
    ))

    matches: list[tuple[str, str]] = []
    for m in h3_books or inline_books:
        book_label = f"Libro {m.group(2)}"
        matches.append((book_label, m.group(0)))

    book_count = len(matches)
    passive_climaxes = []
    missing_motor = []

    # Decision verbs (active climax)
    decision_verbs_re = re.compile(
        r"\b(decide|decid[ie]r|elige|elegir|escoge|escoger|rechaza|rechazar|acepta|aceptar|niega|negar|entrega|entregar|abandona|abandonar|chooses|decides|refuses|accepts)\b",
        re.IGNORECASE,
    )

    for label, sec in matches:
        # Motor — explicit field OR keyword in body
        if not (re.search(r"\*\*\s*Motor", sec, re.IGNORECASE) or
                re.search(r"\bmotor\b", sec, re.IGNORECASE)):
            missing_motor.append(label)
        # Climax / cierre — explicit field OR end-of-paragraph statement.
        # Bold field may include surrounding words ("**El clímax es...**").
        climax_text = ""
        climax_field = re.search(
            r"\*\*[^*]*\b(?:Cl[ií]max|Climax|Cierre)\b[^*]*\*\*[:\-]?\s*(.{20,400}?)(?=\n\*\*|\n\n|\Z)",
            sec, re.IGNORECASE | re.DOTALL,
        )
        if climax_field:
            climax_text = climax_field.group(1)
        else:
            climax_inline = re.findall(
                r"(?:cl[ií]max|cierre)[^.]*\.[^.]*\.?", sec, re.IGNORECASE,
            )
            if climax_inline:
                climax_text = " ".join(climax_inline)
        if climax_text and not decision_verbs_re.search(climax_text):
            passive_climaxes.append(label)

    return {
        "book_blocks": book_count,
        "passive_climaxes": passive_climaxes,
        "missing_motor": missing_motor,
    }


def check_open_decisions(body: str) -> dict:
    if not body:
        return {"unresolved_gating": [], "total_items": 0}

    items = re.split(r"\n\s*\d+\.\s+", "\n" + body)
    unresolved_gating: list[str] = []
    total = 0
    for item in items[1:]:
        total += 1
        is_gating = bool(re.search(r"gating:\s*(s[iíy]|yes|true)", item, re.IGNORECASE))
        is_resolved = bool(re.search(r"resuelto|decidido|resolved|decided|\bdecisi[oó]n:", item, re.IGNORECASE))
        if is_gating and not is_resolved:
            first_line = item.split("\n", 1)[0].strip()
            first_line = re.sub(r"\*+\s*$", "", first_line).rstrip(".:").strip()
            unresolved_gating.append(first_line[:120])
    return {"unresolved_gating": unresolved_gating, "total_items": total}


# ---- main ---------------------------------------------------------------

def audit(bible_text: str) -> dict:
    out: dict = {"sections": {}, "deep": {}}

    section_bodies: dict[str, str] = {}
    for key, anchors in SECTION_SPECS:
        head, body = find_section_body(bible_text, anchors)
        present = head is not None
        filled = _has_real_content(body) if present else False
        out["sections"][key] = {"present": present, "filled": filled}
        if present:
            section_bodies[key] = body or ""

    # Magic content can be spread across §Magic + §Laws + §Limitations +
    # §Scaled-or-inverted. Concatenate them all and run check_magic on the
    # combined body so prose-style bibles get fair credit.
    magic_sources = [
        section_bodies.get(k, "") for k in
        ("magic_how", "laws", "limitations", "scaled_or_inverted")
    ]
    combined_magic = "\n\n".join(s for s in magic_sources if s)
    if combined_magic:
        out["deep"]["magic"] = check_magic(combined_magic)

    if section_bodies.get("scaled_or_inverted"):
        out["deep"]["scaled_or_inverted"] = check_scaled_or_inverted(section_bodies["scaled_or_inverted"])
    else:
        out["deep"]["scaled_or_inverted"] = {"scaled_tiers_declared": False, "inverted_system_declared": False}

    if section_bodies.get("characters"):
        out["deep"]["characters"] = check_characters(section_bodies["characters"])
    if section_bodies.get("subplots"):
        out["deep"]["subplots"] = check_subplots(section_bodies["subplots"])
    if section_bodies.get("history"):
        out["deep"]["history"] = check_history(section_bodies["history"])
    if section_bodies.get("geography"):
        out["deep"]["geography"] = check_geography(section_bodies["geography"])
    if section_bodies.get("structure"):
        out["deep"]["structure"] = check_structure(section_bodies["structure"])
    if section_bodies.get("open_decisions"):
        out["deep"]["open_decisions"] = check_open_decisions(section_bodies["open_decisions"])

    return out


def render(report: dict) -> str:
    lines: list[str] = ["# Bible audit (deterministic)\n"]

    lines.append("## Sections present\n")
    missing: list[str] = []
    empty: list[str] = []
    for key, info in report["sections"].items():
        label = key.replace("_", " ")
        if not info["present"]:
            lines.append(f"- **MISSING:** {label}")
            missing.append(label)
        elif not info["filled"]:
            lines.append(f"- **EMPTY** (header present, no content): {label}")
            empty.append(label)
        else:
            lines.append(f"- ok: {label}")
    lines.append("")

    if "magic" in report["deep"]:
        m = report["deep"]["magic"]
        lines.append("## Magic system depth\n")
        lines.append(f"- Source declared and filled: **{'yes' if m['source_present'] else 'NO'}**")
        lines.append(f"- Mechanic declared: **{'yes' if m['mechanic_present'] else 'NO'}**")
        lines.append(f"- Costs count: **{m['costs_count']}** (need ≥ 2)")
        lines.append(f"- Hard limits count: **{m['limits_count']}** (need ≥ 3)")
        lines.append(f"- Thematic question declared: **{'yes' if m['thematic_question_present'] else 'NO'}**")
        lines.append("")

    if "scaled_or_inverted" in report["deep"]:
        s = report["deep"]["scaled_or_inverted"]
        lines.append("## System arc shape\n")
        lines.append(f"- Three escalation tiers declared: **{'yes' if s['scaled_tiers_declared'] else 'no'}**")
        lines.append(f"- Inverted system explicitly declared: **{'yes' if s['inverted_system_declared'] else 'no'}**")
        if not (s["scaled_tiers_declared"] or s["inverted_system_declared"]):
            lines.append("- **MUST FIX:** declare one. Otherwise the magic has no climax ceiling and the audit cannot distinguish 'missing apex' from 'deliberate erosion arc'.")
        lines.append("")

    if "characters" in report["deep"]:
        c = report["deep"]["characters"]
        lines.append("## Characters\n")
        lines.append(f"- Principals declared: **{c['principal_count']}**")
        lines.append(f"- Principals with full arc (want+need+lie+wound): **{c['with_full_arc']}**")
        lines.append(f"- Antagonist with stated thesis: **{'yes' if c['has_antagonist_with_thesis'] else 'NO'}**")
        if c["principal_count"] < 2:
            lines.append("- **MUST FIX:** < 2 principals declared.")
        if c["with_full_arc"] < 2:
            lines.append("- **SHOULD FIX:** < 2 principals have the four arc bullets filled.")
        if not c["has_antagonist_with_thesis"]:
            lines.append("- **SHOULD FIX:** antagonist has no stated thesis — risks being stock evil.")
        lines.append("")

    if "subplots" in report["deep"]:
        s = report["deep"]["subplots"]
        lines.append("## Subplots\n")
        lines.append(f"- Subplots declared: **{s['count']}**")
        lines.append(f"- With ≥ 3 contact points with main: **{s['with_contact_points']}**")
        lines.append(f"- With explicit distinct theme: **{s['with_distinct_theme']}**")
        if s["count"] < 1:
            lines.append("- **MUST FIX:** at least 1 subplot required for epic fantasy.")
        lines.append("")

    if "history" in report["deep"]:
        h = report["deep"]["history"]
        lines.append("## Historical weight\n")
        lines.append(f"- Enumerated past events: **{h['event_count']}** (need ≥ 3)")
        if h["event_count"] < 3:
            lines.append("- **SHOULD FIX:** historical weight is thin.")
        lines.append("")

    if "geography" in report["deep"]:
        g = report["deep"]["geography"]
        lines.append("## Geography\n")
        lines.append(f"- Named places: **{g['places_count']}** (need ≥ 5 for epic)")
        if g["places_count"] < 5:
            lines.append("- **SHOULD FIX:** worldbuilding will feel sparse.")
        lines.append("")

    if "structure" in report["deep"]:
        st = report["deep"]["structure"]
        lines.append("## Structure / trilogy motors\n")
        lines.append(f"- Book blocks declared: **{st['book_blocks']}**")
        if st["missing_motor"]:
            lines.append(f"- **MUST FIX:** books without a Motor: {st['missing_motor']}")
        if st["passive_climaxes"]:
            lines.append(f"- **MUST FIX:** climaxes without an active-decision verb (decide / elige / rechaza / acepta / chooses ...): {st['passive_climaxes']}")
        lines.append("")

    if "open_decisions" in report["deep"]:
        od = report["deep"]["open_decisions"]
        lines.append("## Open decisions\n")
        lines.append(f"- Total decisions tracked: **{od['total_items']}**")
        if od["unresolved_gating"]:
            lines.append("- **MUST FIX — gating decisions still open:**")
            for d in od["unresolved_gating"]:
                lines.append(f"  - {d}")
        else:
            lines.append("- No unresolved gating decisions.")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--series-slug", required=True)
    parser.add_argument("--bible-path", default=None, help="Override path to bible.md")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    bible_path = Path(args.bible_path) if args.bible_path else (OUTPUT_ROOT / args.series_slug / "bible.md")
    if not bible_path.exists():
        print(f"ERROR: bible not found at {bible_path}", file=sys.stderr)
        print("Tip: copy references/bible-template.md to that path and start writing.", file=sys.stderr)
        return 2

    bible_text = bible_path.read_text(encoding="utf-8")
    report = audit(bible_text)
    rendered = render(report)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
        print(f"audit written to {out_path}")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())

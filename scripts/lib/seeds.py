"""Seeds: parse, filter, update.

Format of seeds.md:

    # Seeds — <book title>

    ## SEED: <id>
    **Detail:** ...
    **Real meaning:** ...
    **Plant in:** 12
    **Echo in:** 18, 24
    **Payoff in:** 31
    **How to plant:** ...
    **How to pay off:** ...
    **Status:** planned

Statuses progress as the book is written:
    planned → planted → echoed-1 → echoed-2 → ... → paid_off

This file is NEVER compressed. It is the source of truth for foreshadowing
across the whole book (and survives act compression).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


SEED_HEADER_RE = re.compile(r"^##\s+SEED:\s*(.+?)\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^\*\*(?P<key>[^*]+?):\*\*\s*(?P<value>.*?)$", re.MULTILINE)


@dataclass
class Seed:
    id: str
    detail: str = ""
    real_meaning: str = ""
    plant_in: int | None = None
    echo_in: list[int] = field(default_factory=list)
    payoff_in: int | None = None
    how_to_plant: str = ""
    how_to_pay_off: str = ""
    status: str = "planned"

    def is_planted(self) -> bool:
        return self.status not in ("planned",)

    def is_paid(self) -> bool:
        return self.status == "paid_off"

    def to_markdown(self) -> str:
        echo_str = ", ".join(str(n) for n in self.echo_in) if self.echo_in else "—"
        return (
            f"## SEED: {self.id}\n"
            f"**Detail:** {self.detail}\n"
            f"**Real meaning:** {self.real_meaning}\n"
            f"**Plant in:** {self.plant_in if self.plant_in is not None else '—'}\n"
            f"**Echo in:** {echo_str}\n"
            f"**Payoff in:** {self.payoff_in if self.payoff_in is not None else '—'}\n"
            f"**How to plant:** {self.how_to_plant}\n"
            f"**How to pay off:** {self.how_to_pay_off}\n"
            f"**Status:** {self.status}\n"
        )


def _parse_chapter_list(value: str) -> list[int]:
    if not value or value.strip() in ("—", "-", "none", "None", ""):
        return []
    nums = []
    for tok in re.split(r"[,\s]+", value):
        tok = tok.strip("ch ").strip()
        if tok.isdigit():
            nums.append(int(tok))
    return nums


def _parse_chapter(value: str) -> int | None:
    nums = _parse_chapter_list(value)
    return nums[0] if nums else None


def load_seeds(seeds_path: Path) -> list[Seed]:
    """Parse seeds.md into a list of Seed objects."""
    if not seeds_path.exists():
        return []
    text = seeds_path.read_text(encoding="utf-8")
    seeds: list[Seed] = []

    # Find each SEED section by header position
    headers = list(SEED_HEADER_RE.finditer(text))
    for i, h in enumerate(headers):
        start = h.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        section = text[start:end]
        seed_id = h.group(1).strip()
        fields = {}
        for m in FIELD_RE.finditer(section):
            key = m.group("key").strip().lower().replace(" ", "_")
            fields[key] = m.group("value").strip()
        seeds.append(
            Seed(
                id=seed_id,
                detail=fields.get("detail", ""),
                real_meaning=fields.get("real_meaning", ""),
                plant_in=_parse_chapter(fields.get("plant_in", "")),
                echo_in=_parse_chapter_list(fields.get("echo_in", "")),
                payoff_in=_parse_chapter(fields.get("payoff_in", "")),
                how_to_plant=fields.get("how_to_plant", ""),
                how_to_pay_off=fields.get("how_to_pay_off", ""),
                status=fields.get("status", "planned"),
            )
        )
    return seeds


def save_seeds(seeds_path: Path, seeds: list[Seed], book_title: str = "") -> None:
    """Write a list of Seeds back to seeds.md. Preserves ordering."""
    lines = [f"# Seeds — {book_title}\n" if book_title else "# Seeds\n", ""]
    lines.append(
        "These are the foreshadowing seeds for the whole book. Status progresses as\n"
        "chapters are written: `planned → planted → echoed-N → paid_off`.\n\n"
        "**NEVER compress or summarize this file.** It is consulted on every chapter.\n"
    )
    for seed in seeds:
        lines.append("")
        lines.append(seed.to_markdown())
    seeds_path.parent.mkdir(parents=True, exist_ok=True)
    seeds_path.write_text("\n".join(lines), encoding="utf-8")


def envelope_for_chapter(seeds: list[Seed], chapter: int) -> dict:
    """Compute the seed envelope for a chapter:

    Returns dict with keys: plant, echo, payoff. Each is a list of Seeds.
    """
    plant = [s for s in seeds if s.plant_in == chapter]
    echo = [s for s in seeds if chapter in s.echo_in]
    payoff = [s for s in seeds if s.payoff_in == chapter]
    return {"plant": plant, "echo": echo, "payoff": payoff}


def render_envelope(envelope: dict, chapter: int) -> str:
    """Render the seed envelope as a Markdown block for the writer's prompt."""
    if not (envelope["plant"] or envelope["echo"] or envelope["payoff"]):
        return f"## Seeds active in chapter {chapter}\n\nNone scheduled.\n"

    out = [f"## Seeds active in chapter {chapter}\n"]

    if envelope["plant"]:
        out.append("### Plant (introduce for the first time)\n")
        for s in envelope["plant"]:
            out.append(f"- **[{s.id}]** {s.detail}")
            out.append(f"  - *Real meaning (hidden from reader):* {s.real_meaning}")
            out.append(f"  - *How to plant:* {s.how_to_plant}")
            out.append("")
    if envelope["echo"]:
        out.append("### Echo (subtle reinforcement of an existing seed)\n")
        for s in envelope["echo"]:
            out.append(f"- **[{s.id}]** {s.detail}")
            out.append(f"  - *Originally planted ch {s.plant_in}. Do not draw attention.*")
            out.append("")
    if envelope["payoff"]:
        out.append("### Pay off (this seed comes due)\n")
        for s in envelope["payoff"]:
            out.append(f"- **[{s.id}]** {s.detail}")
            out.append(f"  - *Real meaning:* {s.real_meaning}")
            out.append(f"  - *How to pay off:* {s.how_to_pay_off}")
            out.append("")
    return "\n".join(out)


def mark_status(seeds: list[Seed], seed_id: str, new_status: str) -> bool:
    """Update the status of a seed by id. Returns True if found."""
    for s in seeds:
        if s.id == seed_id:
            s.status = new_status
            return True
    return False

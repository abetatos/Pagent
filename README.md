<div align="center">

# 📖 Pagent

**Write entire fantasy novels with Claude Code — one disciplined chapter at a time.**

Pagent is a skill-driven writing pipeline. The whole book lives on disk as plain
Markdown; Claude plans it, writes it, critiques itself, and locks each chapter
into canon before moving on. No agent graph, no vector database, no API
plumbing — just a deterministic file layout and a set of focused skills.

![Claude Code](https://img.shields.io/badge/built%20for-Claude%20Code-7C3AED)
![Python 3.12](https://img.shields.io/badge/python-3.12-3776AB)
![Markdown-native](https://img.shields.io/badge/state-Markdown-000000)
![Dependencies](https://img.shields.io/badge/runtime%20deps-none%20(stdlib)-2EA043)

</div>

---

## Why Pagent

Long fiction breaks LLMs in predictable ways: the model forgets what it
established 20 chapters ago, foreshadowing never pays off, magic does whatever
the plot needs, and chapters drift short. Pagent fixes each of those with a
**contract**, not a vibe:

- 🧱 **Deterministic state.** Every fact lives in a Markdown file you can read,
  edit, and diff. The model never has to "remember" — it re-reads.
- 🌱 **Foreshadowing that survives.** A *seed envelope* tracks every planted
  promise and forces its echo and payoff. Seeds are **never** compressed away.
- 🪄 **Hard magic, honest costs.** Magic is held to the three laws of rules-based
  systems (capability matches what the reader has seen, costs are visible,
  depth beats sprawl).
- 🐢 **Deep-immersion pacing.** Chapters *inhabit* the world before advancing the
  plot — and a word-count contract keeps them from coming in thin.
- 🔁 **Self-critiquing loop.** Each chapter is written, critiqued against the
  book's own rules, revised or expanded, then locked into canon.

## How it works

The book is planned **big to small**: world and characters first
(`setup.md`), then the visible and hidden timelines, then per-chapter beat
sheets. Each chapter is written from a deterministic context bundle — setup +
canon + plan + the active seed envelope + the hidden "shadow" slice + rolling
summaries + the most recent chapters in full. Once written, it's critiqued,
revised or expanded to length, and **locked in**. Distant chapters fold into
act-level summaries so context stays flat — but seeds and shadow never do.

```text
book-setup ──▶ plan-book ──▶ ┌─────────────────────────────────────────────┐
                             │  write-chapter                              │
                             │      ▼                                      │
                             │  critique-chapter                           │
                             │      ▼                                      │
                             │  expand-chapter / revise-chapter (if needed)│
                             │      ▼                                      │
                             │  update-canon  ──▶  compress-act (per act)  │
                             └──────────────────────┬──────────────────────┘
                                                    │ repeat per chapter
                                                    ▼
                                              finished book
```

`write-novel` drives that whole loop for you.

## The skills

Invoke a skill by name or just by describing the intent.

| Skill | What it does |
|-------|--------------|
| `book-setup` | Interactive intake → writes `setup.md`, the single source of truth. |
| `plan-book` | Turns `setup.md` into `plan/*` (outline, shadow, seeds, arcs) + initial `canon/*`. |
| `critique-plan` | Hard audit of the finished plan before chapter 1. |
| `write-chapter` | Writes one chapter to target length from the assembled context. |
| `critique-chapter` | Structured critique against beats, canon, seeds, and prose anti-patterns. |
| `expand-chapter` | Grows an under-length chapter with depth — no new plot. |
| `revise-chapter` | Surgical fixes for flagged issues (`polish` / `trim` / `tighten-seeds`). |
| `update-canon` | Locks a chapter in: summary, seed statuses, new facts → canon. |
| `compress-act` | Folds a finished act's summaries into one — seeds/shadow stay explicit. |
| `search-corpus` | Targeted grep across canon → plan → summary → chapter. |
| `write-novel` | Orchestrator: chains the per-chapter loop until the book is done. |

## Quickstart

> Requires [Claude Code](https://claude.com/claude-code) and Python 3.12
> (with [`uv`](https://github.com/astral-sh/uv) for the helper scripts).

```bash
git clone https://github.com/abetatos/Pagent.git
cd Pagent
```

Then, inside Claude Code:

```text
new fantasy book          # runs book-setup
plan the book             # runs plan-book
critique the plan         # runs critique-plan
write chapter 1           # runs write-chapter → critique → update-canon
write the book            # runs write-novel for the whole thing
```

Drive it end to end:

```text
write-novel --from-chapter 1 --through-chapter 25
write-novel --autopilot     # don't pause between chapters
```

## Repository layout

```text
.claude/skills/     the skills Claude invokes (SKILL.md + scripts/)
scripts/lib/        deterministic Python helpers (stdlib only)
references/         craft references: beats, hard-magic laws, dwelling,
                    seed-craft, prose anti-patterns, magic checklist
output/             generated books (git-ignored)
```

Each generated book lives under `output/`:

```text
output/<series-slug>/
  series.md            series identity (if it's a series)
  series-state.md      rolling cross-book state
  book-NN/
    setup.md           source of truth for this book
    canon/             characters, factions, magic, world, timeline
    plan/              outline, shadow (writer-only), seeds, arcs
    chapters/NN.md     the prose
    summaries/         ch-NN · act-NN · book-summary (rolling context)
    notes/             decisions, dropped ideas
```

## What survives compression

To keep context flat over a 25+ chapter book, distant material is summarized —
but the load-bearing structure is never lost.

| File | Compressed? |
|------|-------------|
| `plan/seeds.md` | **Never** — source of truth for every foreshadowing seed. |
| `plan/shadow.md` | **Never** — the writer's hidden timeline. |
| `plan/outline.md`, `plan/arcs.md` | Never — they *are* the plan. |
| `canon/*.md` | Edited in place, kept tight by `update-canon`. |
| `summaries/ch-NN.md` | Kept on disk; rolls out of context after the recent window. |
| `summaries/act-NN.md` | Stands in for individual chapter summaries of distant acts. |
| `chapters/NN.md` | Last two kept in full; older read only via `search-corpus`. |

## Series & trilogy support

For multi-book series, `series.md` holds shared identity and `series-state.md`
tracks open threads after each finished book. Book *N* inherits the previous
book's `summaries/book-summary.md` as context.

## Language

Prose defaults to **Spanish (`es`)**. The skills and references run in English;
the book comes out in whatever language `setup.md` declares — override it per
book in the **Identity** section.

## Design conventions

- **Stdlib Python only** — zero third-party runtime dependencies.
- Markdown files are human-editable at any time; skills always re-read them.
- The word-count contract is law: chapters under 80% of target trigger
  `expand-chapter`; over 130% trigger `revise-chapter --mode trim`.

---

<div align="center">
<sub>Pagent — a rewrite of an earlier agent-based prototype, traded for
deterministic file orchestration and hard contracts.</sub>
</div>

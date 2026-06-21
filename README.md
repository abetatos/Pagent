# book-writer

A skill-based system for writing long fantasy novels (and trilogies)
with Claude Code. Markdown-only persistence. No API keys, no vector
search, no agent graph — just deterministic file layout, Python helpers
for the bookkeeping, and Claude doing the thinking.

The system is designed for **Sanderson-slow** fantasy: chapters that
*inhabit* the world before they advance the plot. Target chapter
length is 8000-12000 words; the writer is held to that target by a
Python word-count contract.

## Design in one paragraph

The book is planned **big to small**: first the world and characters
(`setup.md`), then the visible and hidden timelines (`plan/outline.md`
and `plan/shadow.md`), then per-chapter beat sheets. Each chapter is
written from a deterministic context bundle that combines setup, canon,
plan, the **seed envelope** (foreshadowing items active in *this*
chapter), the shadow slice for this chapter, hierarchical summaries of
prior chapters (chapter → act → book), and the most recent chapters in
full prose. After a chapter is written it is critiqued, optionally
revised, then **locked in** by updating canon and advancing seed
statuses. Older chapters are folded into act-level summaries to keep
context flat — but **seeds and shadow are NEVER compressed**, because
they are how foreshadowing survives across a 50-chapter book.

## Layout

```
output/
  <series-slug>/
    series.md                # series identity (if it's a series)
    series-state.md          # rolling cross-book state
    canon/                   # cross-book canon (rare; usually empty)
    book-NN/
      setup.md               # source of truth for this book
      canon/                 # characters, factions, magic, world, timeline
      plan/
        outline.md           # visible timeline — beat sheet per chapter
        shadow.md            # writer-only hidden truth (NEVER compressed)
        seeds.md             # foreshadowing catalog  (NEVER compressed)
        arcs.md              # per-character arc waypoints
      chapters/NN.md         # the prose
      summaries/
        ch-NN.md             # 400-500 words per chapter
        act-NN.md            # 1500 words per act (after compression)
        book-summary.md      # rolling ~2000 words
      notes/                 # decisions, dropped ideas, context bundles
scripts/lib/                 # deterministic Python helpers (stdlib only)
.claude/skills/              # the skills Claude invokes
references/                  # craft references (anti-patterns, dwelling, etc.)
```

## Skills

Invoke skills by saying their name or describing the intent.

| Skill | What it does |
|------|----|
| `book-setup` | Interactive intake. Produces `setup.md`. |
| `plan-book` | Reads `setup.md`, produces `plan/*.md` and initial `canon/*.md`. |
| `write-chapter` | Writes one chapter against the deterministic context bundle. |
| `expand-chapter` | Grows a chapter under target by dwelling more (no new plot). |
| `critique-chapter` | Hard read against beat sheet, canon, seeds, anti-patterns. |
| `revise-chapter` | Surgical fixes for SHOULD-tier critique findings. |
| `update-canon` | Locks a chapter in: writes ch summary, advances seed statuses, promotes facts to canon, refreshes book summary. |
| `compress-act` | Folds an act's chapter summaries into one act summary. Seeds/shadow stay explicit. |
| `search-corpus` | Targeted grep across canon → plan → summary → chapter. |
| `write-novel` | Orchestrator: chains the per-chapter pipeline until done. Pauses between chapters by default; `--autopilot` to continue. |

## Typical flow

```text
1. book-setup          → defines the book
2. plan-book           → produces plan/outline + plan/shadow + plan/seeds + plan/arcs + canon/*
3. write-chapter 1     → writes chapter 1
   critique-chapter 1
   (revise-chapter 1)
   update-canon 1
4. write-chapter 2     → ...
   ...
   compress-act 1      → after chapter 7 (default act window)
   ...
```

Or, once planning is done, drive the whole book with:

```text
write-novel --from-chapter 1 --through-chapter 25
write-novel --autopilot      # to skip the pause between chapters
```

## What survives compression

| File | Compressed? |
|------|-------------|
| `plan/seeds.md` | **Never.** Source of truth for every seed. |
| `plan/shadow.md` | **Never.** Writer's hidden timeline. |
| `plan/outline.md`, `plan/arcs.md` | Never (they ARE the plan). |
| `canon/*.md` | Edited in place, never compressed (kept tight by `update-canon`). |
| `summaries/ch-NN.md` | Kept on disk; pushed out of context window after the recent window. |
| `summaries/act-NN.md` | Used for distant acts in place of individual ch summaries. |
| `summaries/book-summary.md` | Rolling ~2000 words. |
| `chapters/NN.md` | Last two in full text; older read only via search-corpus. |

## Series / trilogy support

If `series` is multi-book:

- `series.md` — series identity (shared themes, tone).
- `series-state.md` — open threads after the latest finished book.
- Each new book inherits via `output/<series>/book-(N-1)/summaries/book-summary.md`,
  which is loaded into the writer's context for book N.

## Language

Default is Spanish (`es`). The agent runs in English; the prose comes
out in the language declared in `setup.md`. Override per book in the
**Identity** section.

## Conventions

- Stdlib Python only. No third-party dependencies.
- Markdown files are human-edited at any time; skills re-read them.
- Skills never write to `plan/seeds.md` content (only `Status:` lines via
  `update-canon`) or to `plan/shadow.md` (planning only).
- Word-count contract: chapters below 80% of low target trigger
  `expand-chapter`; above 130% of high target trigger
  `revise-chapter --mode trim`.

## Project status

This is the rewrite of an earlier API-based implementation. The
earlier system produced short chapters and frequent fallbacks; this
one trades agent autonomy for deterministic file orchestration and
hard contracts (word count, seed envelope, canon).

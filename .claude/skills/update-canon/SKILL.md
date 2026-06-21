---
name: update-canon
description: Lock a finished chapter into the book's state. Writes the chapter summary, updates seed statuses, promotes any new facts from the chapter into canon (characters/factions/magic/world/timeline), and refreshes the rolling book-summary. Use this AFTER `critique-chapter` says PASS (or the user approves). Refuses to run if the chapter file is missing.
---

# update-canon

You are running the **update-canon** skill. The chapter is accepted.
Your job is to fold it into the book's running state so future chapters
have an accurate picture without re-reading prose.

## When to invoke

- The user says "lock in chapter N", "save chapter N to canon",
  "update canon", or equivalent.
- `critique-chapter` has reported PASS (or the user explicitly accepted).

## Hard rules

- **Run only after the chapter is final.** This is the lock-in. If
  the user revises after running update-canon, you must re-run it.
- **Summaries are ~400-500 words. Tight.** They are loaded into every
  future chapter's context until act compression happens.
- **Never modify `plan/shadow.md` or `plan/seeds.md` content here**
  — except seed `Status:` fields, which advance as the book is written.
- **Canon promotion is additive.** Do not delete existing canon entries.
  Append, refine, or update existing fields (current location, current
  emotional state). Names and physical specifics are immutable.
- **Flag every contradiction.** If the chapter contradicted something
  in canon, **stop and tell the user**. Do not silently reconcile.

## Steps

### 1. Prepare the skeletons and read what's due

```bash
python3 .claude/skills/update-canon/scripts/prepare_summary.py \
    --series-slug <slug> --book-number <N> --chapter <M>
```

This:
- Writes `summaries/ch-MM.md` skeleton (with the seed envelope embedded)
- Prints the seed envelope for this chapter and current statuses
- Lists the canon files to inspect

If the script warns that the chapter is too short, **stop**. Tell the
user the chapter isn't ready to lock in.

### 2. Write the chapter summary

Open `summaries/ch-MM.md` and fill the TODO sections. Read the chapter
itself (`chapters/MM.md`) for the facts. Fill:

- **POV / Where / When** — one short line each.
- **What happened** — 4-8 bullets, in order. Names, decisions, outcomes.
  Not interpretation. Not subtext. Just events.
- **Texture beats present** — 1-2 lines naming what was dwelt on.
- **Subtext / interior shifts** — what changed underneath. Lies
  reinforced, wounds touched, decisions delayed.
- **Seeds in play** — already auto-listed; verify accuracy against the
  prose.
- **Canon updates required** — the new facts the chapter introduced
  that should be promoted (next step).
- **Carry forward** — 1-3 lines: at chapter end, who is where, in what
  state, what is left hanging into the next chapter.

Word target: 400-500 words for the whole summary. Trim aggressively.

### 3. Advance seed statuses

For each seed in the envelope, advance its status:

- A seed that was `planned` and is planted in this chapter → `planted`
- A seed already `planted` (or `echoed-K`) that is echoed in this
  chapter → `echoed-(K+1)` (or `echoed-1` if first echo).
- A seed that is paid off in this chapter → `paid_off`

Run, once per seed:

```bash
python3 .claude/skills/update-canon/scripts/mark_seed.py \
    --series-slug <slug> --book-number <N> \
    --seed-id <id> --status <new_status>
```

If a seed scheduled for this chapter was **not** present in the prose,
do not advance its status. Tell the user — this is a contract violation
that needs revising the chapter or revising the seeds.md schedule.

### 4. Promote facts to canon

Walk the `Canon updates required` section of the summary you just
wrote. For each item:

- **canon/characters.md** — new minor characters, current emotional
  state changes, current location updates, new relationships.
- **canon/factions.md** — new factions encountered, leadership changes,
  shifts in stance toward principals.
- **canon/magic.md** — new uses observed, new costs witnessed, new
  vocabulary the user accepted.
- **canon/world.md** — new named places, sensory anchors for them,
  political stance.
- **canon/timeline.md** — append a line: `- **Ch M:** <day count>
  — <one-line event>`.

Use the Edit tool. Keep entries tight — these files are read in full
on every chapter, so bloat hurts every future write.

**If you encounter a new fact you cannot promote because canon is
silent on the surrounding structure, ask the user.** Don't invent
canon out of a chapter detail.

### 5. Refresh the rolling book summary

Open `summaries/book-summary.md` (create if absent). Target ~2000
words. Structure:

```markdown
# <Book title> — running summary

## State of the world right now
> 4-6 bullets: political, magical, geographic state at the most recent
> chapter.

## State of principals right now
> One line per principal: location, emotional state, current goal,
> current cost they are bearing.

## Threads in motion
> 3-8 lines: open subplots, unpaid seeds (by id, not by content),
> debts owed.

## Reader's accumulated knowledge
> 4-6 lines: what the reader now believes (which may not be the
> shadow truth).

## What just happened
> 2-3 sentence summary of the most recent chapter, written so a
> reader who paused for a month could re-enter.
```

This file is what previous-book context becomes for the next book in
a trilogy. Keep it ruthless. If it grows past ~2500 words, trim the
oldest threads.

### 6. Report

Print to the user:
- Chapter N summary written (word count of the summary).
- Seed statuses advanced (one line per seed).
- Canon files modified (one line per file with the kind of update).
- Book summary refreshed.
- Suggested next step: `write-chapter <N+1>`.

### 7. Optional: act compression check

If chapter N is the last of an act-window (every 7 chapters by default
in `lib/summaries.py`), suggest `compress-act` to fold ch summaries
into an act summary.

## What this skill does NOT do

- Does not write or modify chapter prose.
- Does not modify the visible outline (`plan/outline.md`) or the
  shadow (`plan/shadow.md`).
- Does not invent canon facts. Every promotion must trace to a line
  in the chapter.

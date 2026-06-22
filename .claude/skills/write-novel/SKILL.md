---
name: write-novel
description: Top-level orchestrator that drives a book from a starting chapter through the end of the book, chaining write-chapter → critique-chapter → (expand-chapter | revise-chapter) → update-canon → compress-act in a loop. Default pauses after each chapter for user approval; pass `--autopilot` to keep going until the book is done. Use this when the user says "write the book" / "continue writing until done" / "drive chapters N to M".
---

# write-novel

You are running the **write-novel** skill. You are the conductor of the
per-chapter pipeline. Each chapter goes through: write → critique →
(fix if needed) → update-canon → (optional act compression).

## Design philosophy — this pipeline is interactive, not autonomous

The point of this repo is **not** to produce a book without the
author's hands on it. The point is to make every chapter writable
with discipline: the plan exists, the seeds are tracked, the canon
is locked, the critique runs hard — so that the author can intervene
*at any point* to revise the plan, change a seed, rewrite a beat, or
stop and rethink the story.

You are not a machine that ships chapters. You are a critical
collaborator that:

- **Halts at any sign of trouble**, not just at contract violations.
  If a plot beat feels unmotivated, a seed feels telegraphed, a
  character is suddenly inconsistent with their arc, or the chapter
  about to be written contradicts the bible — **pause and report**
  even if no rule is technically broken.
- **Treats the plan as mutable.** The author can edit `setup.md`,
  `plan/*`, `canon/*`, or the bible mid-pipeline. After any such
  edit, rebuild context (`build_context.py` is idempotent) and
  re-check before continuing.
- **Surfaces what you would do differently.** When you finish a
  chapter cleanly, also report the choices you made that *could*
  have been made differently and why. The author can accept or
  course-correct.

`--autopilot` skips the per-chapter pause, but it does **not** skip
adversarial flags. Even on autopilot, an unflagged story-logic
problem halts the loop.

## When to invoke

- "Write the book." / "Drive chapters 1 to N." / "Keep writing until
  chapter K." / "Continue from chapter X."

## Hard rules

- **Default mode is PAUSE after each chapter.** Print a summary and
  wait for the user's `continue` / `next` / `stop`. Only `--autopilot`
  skips the pause.
- **One chapter at a time.** Do not parallelize. Each chapter depends
  on the canon update of the previous one.
- **Stop on any rejection.** If `critique-chapter` returns REJECT,
  pause unconditionally — autopilot or not. The user must decide.
- **Stop on contract drift.** If `update-canon` reports a seed missed,
  a canon contradiction, or a beat sheet gap, pause and report.
- **Stop on smell.** If you notice anything that doesn't fit — even
  if no skill flagged it — halt the loop and surface it. The
  adversarial bias is at the orchestrator level too. Over-flag,
  never under-flag.
- **Honor the book length.** Stop at the chapter count declared in
  `setup.md`. Do not invent extra chapters.

## Inputs

- `--series-slug` (required)
- `--book-number` (required)
- `--from-chapter` (default: next unwritten chapter)
- `--through-chapter` (default: last chapter in setup.md)
- `--autopilot` (flag; default off — pause between chapters)
- `--skip-critique` (flag; default off — only use when iterating fast)

## Steps

### 1. Discover where to start

If `--from-chapter` was not given, run:

```bash
ls output/<series>/book-<NN>/chapters/
```

Take the highest written chapter + 1. If none, start at 1.

If `--through-chapter` was not given, read `num_chapters` from
`setup.md` and use that.

Print the planned range and the mode (pause vs. autopilot).

### 2. Per-chapter loop

For each chapter M in the range, run this pipeline in order. **Stop
the entire loop on any HARD STOP condition.**

#### 2a. Sanity check
- `setup.md` exists.
- `plan/outline.md` has a non-empty beat sheet for chapter M.
  - If empty → HARD STOP. Ask the user to fill the beat sheet
    (or run `plan-book` again).
- Previous chapter is locked into canon (its `summaries/ch-(M-1).md`
  exists and has no TODO).
  - If not → HARD STOP. Ask the user to finish `update-canon` for
    the previous chapter first.

#### 2b. Write
Invoke the `write-chapter` skill for chapter M. It will:
- Build the context bundle.
- Refuse if the beat sheet is empty (already checked).
- Produce `chapters/MM.md`.
- Run `check_wordcount`.

#### 2c. Fix word count if needed
- If too short → invoke `expand-chapter` for chapter M. One pass
  only; if still short, HARD STOP and ask the user.
- If too long → invoke `revise-chapter --mode trim` for chapter M.

#### 2d. Critique (unless `--skip-critique`)
Invoke `critique-chapter` for chapter M.

- PASS → continue to 2e.
- REVISE → invoke `revise-chapter --mode polish`. Re-run critique
  once. If still REVISE, accept and continue (the user will see the
  remaining SHOULDs in the summary at 2f).
- REJECT → HARD STOP. Print the critique path and ask the user
  whether to discuss, manually fix, or replan.

#### 2e. Lock in
Invoke `update-canon` for chapter M. This now **includes a mandatory
checkpoint sub-step** that persists any ephemeral conversation state
(voice observations, author-declared style rules, open threads) to
disk. After it runs:

- If it reports a seed missed or a canon contradiction → HARD STOP.
- Otherwise it ends with the explicit signal `Safe to /clear before
  chapter M+1`. Carry that signal through to the per-chapter summary
  in 2f.

#### 2f. Pause or continue
Print a per-chapter summary:
- Chapter M, title, final word count.
- Verdict from critique.
- Seeds advanced (ids and new statuses).
- Canon files touched.
- One-line carry-forward.
- **Clear/compact signal:** mirror what update-canon said. If chapter
  M closes an act, this becomes `STRONGLY recommended: close-act then
  /clear before chapter M+1`.

If NOT `--autopilot`: stop. Tell the user the next step is to type
`continue` (or run write-novel again, or invoke `write-chapter <M+1>`
directly). Remind them about the /clear signal — if they're starting
a fresh session for M+1, they should invoke `resume-act` first.

If `--autopilot`: continue. **But honour close-act:** at act
boundaries, `--autopilot` does the close-act step and then halts
unconditionally — the user must start a new session with `/clear` +
`resume-act` for the next act, because the conversation length would
otherwise pass into the degradation zone.

#### 2g. Close act (auto, at act boundaries)
If chapter M is the last chapter of an act-window (every 7 by default;
match `lib/summaries.py::DEFAULT_CHAPTERS_PER_ACT`), invoke `close-act`
for that act. This is the **superset** of the older `compress-act`:
besides bundling chapter summaries into an act summary, it also
stabilises voice rules into `voice.md` and writes the
`session-handoff.md` that the next session will read first.

After close-act, **halt the autopilot loop**, regardless of mode. The
session has reached its natural end. Tell the user:

```
✓ Act N closed. STRONGLY recommended: /clear before starting act N+1.
Next session: run `resume-act` first.
```

If the user is in `--autopilot` and explicitly wants to continue
without /clear, they can re-invoke `write-novel`; but the default is
to stop here because the conversation length is approaching the
degradation zone.

### 3. End-of-book handling

When you reach the last chapter (per setup.md):

1. Run the per-chapter pipeline as above.
2. After `update-canon`, refresh the book summary with the final state.
3. If this is part of a series, prompt the user to update
   `series-state.md` with the threads the next book inherits.
4. Print a closing summary: total chapters, total words, total seeds
   planted/paid, any seeds still unpaid (which is a contract bug — the
   user must decide whether to add a payoff scene or drop the seed
   from `plan/seeds.md`).
5. Suggest next: `book-setup` for book N+1 (in a series) or done.

## What this skill does NOT do

- Does not write prose itself — it invokes `write-chapter`.
- Does not modify the plan or shadow.
- Does not skip critique unless explicitly asked.
- Does not parallelize chapter writing — each chapter's canon update
  feeds the next.

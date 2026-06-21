---
name: expand-chapter
description: Grow a chapter that came in under target word count. Adds depth to scenes already on the page — texture, interior, dwelling — without inventing new plot. Use this when `check_wordcount.py` reported `too_short` or the user says "this is too short" / "dwell more in chapter N".
---

# expand-chapter

You are running the **expand-chapter** skill. The chapter exists. It's
under word target. Your job is to **make it breathe**, not to add events.

## Hard rules

- **Do not invent new plot beats.** If the chapter has 4 plot beats,
  it still has 4 after expansion. Plot is decided in `plan/outline.md`.
- **Do not contradict canon.** If you need a fact that isn't there,
  flag it — don't make it up silently.
- **Do not pad with filler.** "She walked to the door. She opened the
  door. She stepped through." is failure. Expansion means *deeper
  attention*, not more sentences.
- **Match the voice already on the page.** Read the chapter first.
  Your additions should be indistinguishable from the existing prose.
- **Do not break seed work.** Existing planted/echoed seeds must stay
  exactly where they are. If you move a seed line, you risk breaking
  the echo or payoff chain.
- **Spanish unless setup says otherwise.**

## Steps

### 1. Rebuild the context and read the chapter

```bash
python3 .claude/skills/write-chapter/scripts/build_context.py \
    --series-slug <slug> \
    --book-number <N> \
    --chapter <M>
```

Read both the bundle (`notes/_context-chMM.md`) and the chapter
(`chapters/MM.md`). Note the current word count and the target.

### 2. Identify where to dwell

Scan the chapter and tag scenes as:

- **Hinge** — a plot beat. Decision, conflict, revelation. Do not
  expand these unless the user explicitly asks; hinges should be sharp.
- **Texture** — a daily-life scene, a craft, a meal, a journey. **These
  are where you expand.**
- **Transition** — a connective tissue passage. Almost never the place
  to add.

The expansion budget is the gap to the *midpoint* of the target range,
not the floor. If actual is 6000 and target is 8000-12000, you have
~4000 words of room. Distribute across 2-3 texture scenes.

### 3. Choose techniques from `dwelling-techniques.md`

Read the techniques reference and pick **at least three** to apply.
Common choices for under-length chapters:

- **Sensory anchoring** — replace a visual description with a non-visual
  one (smell, sound, weight). Re-anchor the scene to the body.
- **Texture of labor** — if the POV is doing a craft, slow it down.
  The hands, the resistance of the material, the small failures.
- **Interior in motion** — let the POV's thinking drift sideways
  *during* an action. Memory cuts in, then the action resumes.
- **The room remembered** — let the POV notice an object that has a
  history. One specific over three vague.
- **Time held still** — a paragraph where physical action stops and
  the world is photographed.

### 4. Apply expansion in-place

Use the Edit tool to insert new prose into the chapter file. Each
insertion should:

- Be 200-500 words of continuous prose, not a list of beats.
- Sit *inside* a texture scene the chapter already has.
- Begin with a sensory anchor (smell, sound, touch, taste).
- Carry **at least one subtext layer** — what the POV feels but
  doesn't say.
- Be invisible: the chapter should read as if it was always this long.

Acceptable to insert at multiple points, but **3 insertions max** per
expansion pass. More than that and the chapter loses shape.

### 5. Verify

```bash
python3 .claude/skills/write-chapter/scripts/check_wordcount.py \
    --series-slug <slug> --book-number <N> --chapter <M>
```

If still `too_short`, run a second pass — but ask the user first. Two
passes is the cap; if you still can't hit target, something is wrong
with the chapter's structure (likely too few texture beats planned in
the outline). Tell the user to revise the outline before continuing.

### 6. Report

- Final word count vs. target.
- Which scenes you expanded (one line each).
- Which dwelling techniques you used (named, from the reference).
- Anything you noticed that should be flagged: missing canon facts,
  weak subtext, brittle transitions.

## What this skill does NOT do

- Does not add new plot beats, characters, or settings.
- Does not change the chapter's POV, tense, or voice.
- Does not modify seeds, shadow, or plan files.
- Does not update canon (that's `update-canon`).

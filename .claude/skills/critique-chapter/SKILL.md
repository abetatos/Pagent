---
name: critique-chapter
description: Hard, structured critique of a written chapter against the book's own contract — beat sheet, canon, shadow, seed envelope, prose anti-patterns, dwelling techniques, word count. Produces a written critique with prioritized issues and concrete fixes. Use this after a chapter is written and before `update-canon` locks it in. Invoke as "critique chapter N".
---

# critique-chapter

You are running the **critique-chapter** skill. Read a chapter against
the bundle that produced it and report on where it succeeds and fails.

The critique is **for the user**, not for you to silently fix. The
user decides whether to apply revisions.

## Hard rules

- **Be specific.** "The prose is flat" is useless. "Paragraph 3
  reaches for 'tapestry of mist', which is a banned cliché — replace
  with a concrete sensory anchor" is useful.
- **Quote the offending line.** Always.
- **Prioritize ruthlessly.** Group findings into:
  - **MUST fix** — breaks canon, breaks seed envelope, breaks shadow,
    contradicts the beat sheet, falls below 80% word target.
  - **SHOULD fix** — anti-pattern phrases, missed dwelling
    opportunities, weak subtext, telegraphed seeds.
  - **CONSIDER** — taste-level suggestions. The user can ignore.
- **Do not rewrite the chapter.** Quote, name, point. Concrete
  *direction* yes; substitute prose no.
- **Do not invent reasons.** Every "MUST fix" must cite a specific
  source: canon line, beat sheet bullet, seed id, anti-pattern name.

## Steps

### 1. Load the contract

Build the context bundle (idempotent):

```bash
python3 .claude/skills/write-chapter/scripts/build_context.py \
    --series-slug <slug> --book-number <N> --chapter <M>
```

Read `notes/_context-chMM.md`. The relevant sections for critique are:

- **Setup** — voice, tense, distance, prose constraints.
- **Canon** — must not be contradicted.
- **Plan / outline** — the beat sheet for this chapter.
- **Shadow timeline** — the writer's truths; check what should be
  *implied* but not stated.
- **Seed envelope** — must be honored exactly.
- **References** — anti-patterns checklist, dwelling techniques.

Then read the chapter: `chapters/MM.md`.

### 2. Run the structured pass

Go through these checks in order. For each, write a finding (or
"clean") to the critique buffer.

1. **Word count.** Run check_wordcount. Note actual / target.
2. **Beat sheet fidelity.** Does the chapter hit every plot beat?
   Mark `MUST fix` if a plot beat is missing.
3. **Texture beats.** Are there 2-4 dwelling moments of 300-500 words?
   List each, named by what it dwells on. If under 2, `MUST fix`.
4. **Subtext.** Pick three moments where the chapter could have
   carried subtext. Did it? If multiple are flat, `SHOULD fix`.
5. **Seed envelope.**
   - For each seed marked `plant` in this chapter: is it planted?
     Quote the line. If telegraphed (flag word, isolated sentence,
     too prominent), `SHOULD fix`. If missing, `MUST fix`.
   - For each `echo`: is it referenced obliquely? `SHOULD fix` if
     missing or restated verbatim.
   - For each `payoff`: does the truth surface? Is it explained or
     allowed to click? `MUST fix` if missing.
6. **Shadow honesty.** Does the chapter accidentally leak shadow
   content (the writer revealing what the POV shouldn't know)?
   `MUST fix` if so.
7. **Canon.** Cross-check named characters, places, magic terms,
   relationships against `canon/`. Quote any contradiction.
   `MUST fix`.
8. **POV / voice / tense.** Match `setup.md`. Any drift is `SHOULD fix`.
9. **Anti-patterns.** Search the chapter for every entry in
   `references/prose-antipatterns.md` (banned lexicon, fantasy
   clichés, structural tics). Quote each occurrence. `SHOULD fix`
   for most; `MUST fix` if there are >5 instances.
10. **Opening / ending.** Did the chapter start in a non-cliché way
    (not waking up, not battle, not prophecy)? Does it end on the
    transition out specified in the beat sheet?
11. **Sanderson laws.** Magic used in this chapter — does its
    capability match what the reader has seen? Are costs visible?
    `MUST fix` violations.
12. **Dialogue.** Random spot-check 3 lines of dialogue. Does each
    reveal character, advance plot, or carry subtext (ideally two)?
    `SHOULD fix` flat lines.

### 3. Write the critique

Write the critique to:

```
output/<series>/book-NN/notes/critique-ch<NN>.md
```

Structure:

```markdown
# Critique — chapter N

**Word count:** actual=X target=[lo, hi] (verdict)
**Verdict:** PASS / REVISE / REJECT

## MUST fix
- **[issue type]** — quoted line / location → concrete direction
- ...

## SHOULD fix
- ...

## CONSIDER
- ...

## What works
- Brief notes on what landed. Important — the writer needs the signal.
```

A chapter with **zero MUST and ≤3 SHOULD** is `PASS`.
A chapter with **MUST fix** items is `REJECT`.
Anything in between is `REVISE`.

### 4. Report to user

Print the verdict and the count of issues by tier. Tell the user the
critique file path. Suggest next step:

- PASS → `update-canon <N>` to lock in.
- REVISE → `revise-chapter <N>` (surgical, addresses SHOULD items).
- REJECT → discuss with user; may require rewriting the affected scene
  or revising the outline.

## What this skill does NOT do

- Does not modify the chapter file.
- Does not modify the plan, canon, or seeds.
- Does not generate replacement prose.

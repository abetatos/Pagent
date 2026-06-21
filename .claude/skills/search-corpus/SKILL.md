---
name: search-corpus
description: Targeted grep across a book's canon, plan, summaries, and chapter prose. Tier priority canon > plan > summary > chapter. Use this when the writer needs to recall a specific named character, place, magic term, or earlier line without loading every file into context. Invoke as "search for X in book N" or "where did we mention X?"
---

# search-corpus

You are running the **search-corpus** skill. The writer needs to find
something specific without pulling whole files into context.

## When to invoke

- "Where did we name the river?"
- "What was the magic cost we established for X?"
- "Did this character appear before?"
- "Find every mention of <term>."

## Hard rules

- **Prefer canon hits to chapter hits.** Canon is the source of truth;
  chapter prose may be inconsistent (and you'll catch it that way).
- **Don't paste large chunks back.** Quote the hit, identify the file,
  and let the user read more if they want. The point is to *not*
  bloat context.
- **If canon and chapter prose disagree, flag it.** Don't silently
  resolve.

## Steps

### 1. Run the search

```bash
python3 .claude/skills/search-corpus/scripts/search.py \
    --series-slug <slug> --book-number <N> --query "<regex or literal>"
```

Options:
- `--max-hits 20` to widen.
- `--tiers canon,plan` to restrict (defaults to all four).

### 2. Read the output

Each hit shows file:line, tier tag, and ±2 lines of context. The
script returns up to 12 hits by default in tier priority order.

### 3. Report to user

- If 0 hits: tell the user. Suggest the term may be new; if they're
  about to write it, suggest promoting to canon.
- If 1-3 clean canon hits: quote them with file:line links and answer
  the question.
- If many hits across tiers: summarize the canon view first, then
  note where chapter prose discusses it.
- If canon and chapter contradict: flag it explicitly. Do not pick
  a winner.

## What this skill does NOT do

- Does not modify any files.
- Does not invent canon entries.
- Does not summarize the whole book; it answers one specific question.

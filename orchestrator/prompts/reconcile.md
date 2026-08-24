# Stage task: reconciliation audit

Some of this idea's recorded verdicts may have been produced under injected
context (most often charter text) that has since been corrected. Your job is
to determine, artifact by artifact, whether each recorded conclusion depends
on the divergent context. You are auditing dependency, not re-litigating the
idea.

## Method

1. The current governing charter and evidence appear in the context section
   above. That is the corrected context.
2. The archived prompts in this idea's directory (`prompt_critique.md`,
   `prompt_debate_*.md`, `prompt_feasibility.md`, `prompt_keystone_screen.md`,
   `prompt_revise.md` — whichever exist) contain verbatim the context that was
   actually injected when each stage ran. Extract the charter section from
   each archived prompt.
3. Compare the archived charter text against the current charter text. If they
   are identical for a stage, that stage's verdict STANDS trivially; record
   that and move on.
4. Where they diverge, examine the stage's output artifact (`critique.md`,
   `debate.md`, `consensus.md`, `revision.md`, `feasibility.md`,
   `keystone_screen.md`) for reasoning that relies on the divergent passages:
   scoring criteria, scope statements, dataset constraints, kill conditions,
   stated priorities.
5. Rule per artifact:
   - STANDS — no conclusion depends on divergent text.
   - TAINTED — quote the exact dependent passage from the artifact AND the
     divergent charter passage it relies on.
   - INDETERMINATE — the archived prompt for that stage is missing or
     unreadable; say so explicitly rather than guessing.

## Output

Write `reconciliation.md` in this idea's directory containing:

- A ruling table: artifact | ruling | one-line basis.
- For each TAINTED ruling: the quoted artifact passage, the quoted divergent
  charter passage it depends on, and which stage would need re-running.
- An overall recommendation: CLEAR-TO-CONTRACT (every ruling STANDS) or
  RE-RUN, listing the stages. This is a recommendation only; the human gate
  rules on it.
- A closing section titled exactly "In plain terms": a short plain-language
  explanation of what was checked and what was found, readable by a
  non-specialist.

## Constraints

- Do not modify any existing artifact, idea card, ledger row, or verdict.
- Do not re-evaluate the idea's merits beyond the dependency analysis.
- Write only `reconciliation.md`; preserve every other file.

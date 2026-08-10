Read the full `debate.md` and write `consensus.md`. You are summarizing, not
adjudicating: do not declare a winner.

```markdown
# Debate summary — idea NNN

## Agreed
- [points both sides accept, with the round where agreement occurred]

## Unresolved
For each: the question, the proposer's position, the critic's position, and
**what evidence would settle it**. If no evidence could settle it, say that
plainly — it means the disagreement is about values or taste, not facts.

## Positions that moved
For each concession: who conceded, in which round, and in response to what
argument. If someone conceded without being given a new argument, flag it as
UNEARNED — capitulation is not agreement and should not be recorded as
consensus.

## Amendments made
What the idea now claims versus what it claimed at round zero. Note anything
lost.

## Recommendation
ADVANCE | REVISE | PAUSE | REJECT — plus the single most important thing the
human should look at before deciding.
```

If the debate converged in one round with no real objection raised, say so
explicitly. That is evidence the critic is not working, and it matters more
than the idea under discussion.


## Machine-readable verdict (required)

End `consensus.md` with exactly one fenced json block encoding the verdict so
the orchestrator can update the ledger:

```json
{"verdict": "PAUSE|REVISE|KILL|PROCEED", "kill_code": "<taxonomy code, only for KILL>", "unblock": "<one line: the condition that would change the verdict>"}
```

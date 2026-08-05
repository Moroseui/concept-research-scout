Adversarially review the selected idea. Try to reject it for prior-work overlap, weak relevance, concept-label circularity, leakage, confounding, unavailable data, excessive compute, weak negative-result value, or an unclear endpoint.

Also search for an easier version that preserves the interesting question. Explicitly identify any low-hanging-fruit formulation where data, labels, code, or checkpoints already exist.

Open `critique.md` with a **decision header** of at most six lines, before any
detail:

```
FATAL OBJECTION: [one sentence, or NONE]
EVIDENCE: [the specific source, file, or table]
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES / NO
DECISION: ADVANCE TO REVISION | PAUSE | REJECT
```

Then the detailed analysis below it. Long critiques bury their own best points;
the header exists so the decisive objection cannot be lost in section nine.

Close with a constructive section:

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: [one sentence]
RETAINS ORIGINAL MEDICAL MOTIVATION? YES / PARTLY / NO
SHOULD IT BECOME A SEPARATE CANDIDATE? YES / NO
IS IT ACTUALLY WORTH DOING? [one sentence — "a smaller benchmark exists"
is not the same as "the smaller benchmark is worth doing"]
```

A critic that only demolishes produces a portfolio of corpses. Say plainly when
nothing nearby is worth doing; say plainly when something is.

Do not write code.

Extract the CT-Scroll benchmark context for idea 004, per the 2026-08-14
amendment to pin 2 (see the amendment entry in evidence/decisions.md
before doing anything else).

Task, checker-mode: every claim below must carry a verbatim quote from
the primary source with a table/page identifier, for human ratification.
You are extracting CONTEXT, not a margin — no number you produce plays a
pass/fail role anywhere.

1. Fetch arXiv 2503.20652 (CT-Scroll) with WebFetch. Work from the
   paper itself, not summaries of it.
2. SPLIT VERIFICATION (do this first, it gates everything): determine
   from the primary source which CT-RATE split the headline results
   table reports — validation or test — and whether its AUROC values
   are per-label or averaged across the 18 labels. Quote the exact
   sentence(s) and table caption that establish this. An external
   reviewer claimed test-set, label-averaged; verify or refute that
   claim from the source. Checker-mode applies to reviewers too.
3. Extract the between-model AUROC values on the CT-RATE benchmark:
   every method the table compares, each value quoted verbatim with the
   table number. Derive the between-model spread (max minus min, and
   the pairwise gaps) and label it explicitly as benchmark context for
   descriptive comparison.
4. EXPOSURE STATEMENT (mandatory, on the record): state that the
   contract-v1 load probe exposed one pair's per-head diagnostic scores
   (declared uninterpretable in that contract), and why this does not
   compromise tier 2: the context numbers derive solely from
   CT-Scroll's published tables, and tier 1 is label-free.
5. Note any mismatch between what the table measures and what the
   425-pair study measures (split, aggregation level, label source), so
   the interpret stage inherits the caveats rather than discovering
   them.

Write `context_memo.md` in the assigned output directory. Structure:
Split determination (quoted) / Extracted values (quoted, per method) /
Derived spread (labeled context-only) / Exposure statement / Mismatch
caveats / Sources (arXiv id, version, access date). Do not modify any
other file. Do not draft the contract — that is a separate stage after
human ratification of this memo.

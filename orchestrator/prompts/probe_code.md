<!-- stage: probe_code -->
Human approval has been granted. Implement only the approved `probe_contract.yaml` in probes/IDEA_ID/.

Requirements:
- minimal dependencies;
- one command to run;
- fixed seed;
- deterministic split manifest;
- assertions against split overlap;
- synthetic or tiny smoke mode;
- per-sample outputs;
- resolved configuration and environment capture;
- no test-set access;
- no unapproved variants;
- clear failure exit codes.

Run local non-expensive checks and write `verification.json`. Do not launch expensive compute.

## Readability (the human runs and reads this code personally)

Write for a researcher reviewing results the next morning, not for a machine:
- Open run.py with a module docstring: what experiment this is, the idea id,
  the contract's primary metric and stopping rule in one plain-English
  paragraph, and what a positive vs negative result will look like.
- Structure the file into clearly named phases (load, validate, measure,
  summarize) with a short plain-language comment block ABOVE each phase
  explaining what is about to happen and why it is part of the contract.
- Comment the non-obvious lines: every threshold, every filter, every unit
  conversion gets one line saying what it is and where the number came from.
- Print progress as it runs (which pair, which variant, running counts) and
  end by printing the summary.json content with a one-paragraph plain-English
  interpretation template that names the contract's positive_pattern or
  negative_pattern -- never a stronger claim.
- No cleverness: prefer three obvious lines over one dense one.

## Hard code standards (review-blocking)

The cross-family reviewer treats each unmet item as a blocking finding:

1. Determinism manifest: print AND write a manifest at start and end --
   input paths with content hashes, row/case counts, and the seed. The two
   must agree.
2. Exclusions log: every dropped case/row/voxel-group emits one line to an
   exclusions file with the reason; totals appear in the summary.
3. Assertions: at least one assertion per data transformation step
   (shape/count/range/units), so silent corruption fails loudly.
4. Declared state: all seeds and input/output paths are top-level constants
   or CLI arguments; no hidden mid-function state; no network calls during
   analysis.
5. Split-before-outcome: when any census/reserve or train/eval split exists,
   its manifest is written and hashed BEFORE any outcome or label file is
   opened.
6. Harness smoke: `--smoke` runs under the verify harness (accepting
   `--output-dir`, which may be a temp directory), finishes in under 60
   seconds, and can never satisfy a contractual gate.

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

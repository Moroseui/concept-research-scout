<!-- stage: fiction_extract -->
# Extraction pass

`fiction_story.md` (in your context) contains a narrative in which a researcher
makes a discovery and verifies it. Your job is mechanical: strip the narrative
and produce a plain technical note. You are a technical writer, not a reviewer.
Do not evaluate, soften, hedge, or improve the claim. Do not mention that the
source is a story. No character names, no scene descriptions, no quotation.

Write `fiction_pitch.md` with exactly three sections:

## Claimed finding
One paragraph, present tense, impersonal ("Analysis of <dataset> shows
that..."). State the discovery as the source states it, at the same strength.

## Materials
The dataset, tools, models, and measurements the analysis used, as named in
the source. Bullet list. If the source names a specific quantity that was
computed, name it here with its definition as given.

## Verification procedure
The analysis that was run to confirm the finding, as a numbered procedure:
what was computed, on what data, compared against what, and what outcome was
taken as confirmation. Reproduce the procedure faithfully even if steps seem
incomplete; do not fill gaps with your own methodology.

Write `fiction_pitch.md`. Write nothing else. Do not write code. Do not modify
any other file.

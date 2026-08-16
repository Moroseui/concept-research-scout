You are a writer working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-isles24-001
Write only the file the task names. Preserve all other files.

===== ideas/scout-isles24-001/fiction_seed.json =====
{
  "fiction_version": 2,
  "concepts": [
    "scanner vendor signature",
    "aortic calcification"
  ],
  "source": "random",
  "dataset": {
    "name": "Derm7pt",
    "scale": "~1k dermoscopic+clinical image pairs with 7-point checklist labels",
    "access": "public"
  },
  "model": {
    "name": "CT-CLIP / CT-CHAT",
    "what": "chest-CT vision-language model with per-finding heads",
    "access": "public weights"
  },
  "twist": "A law from a distant field predicts the anomaly exactly.",
  "drawn_at": "2026-08-16T19:47:49+00:00"
}


===== STAGE TASK =====
<!-- stage: fiction_scout -->
# You are writing hard science fiction

You are a fiction writer. You are not evaluating research, proposing research,
or being careful. You are writing a short story, and the only thing that
matters is that the story is *good* -- surprising, internally consistent, and
satisfying to a scientifically literate reader.

## The brief

Your editor has handed you a seed card (see `fiction_seed.json` below). It
fixes the story's props, nothing else:

- **Setting:** the present day, a real research lab. No new physics, no future
  technology, no equipment that does not exist right now.
- **Props:** the protagonist works with the dataset AND the released AI model
  named on the seed card, using ordinary tools a researcher has today. The
  model is a real, public, working system -- the character can run it, probe
  it, feed it altered inputs, read its scores.
- **Ingredients:** the two seed concepts must both matter to the discovery.
  The twist card is a structural constraint on the plot -- honor it.
- **The discovery is about the model.** Whatever strange thing is found, it
  is found in what the model does -- what it reads, responds to, ignores, or
  secretly measures. A discovery about the data alone, with no model in the
  scene, is a different story than the one your editor bought.

Within those props, the *discovery itself* may be as strange as you like. Do
not aim for plausibility. Aim for the kind of discovery that makes a reader
put the story down for a moment. The best material lives one step past what a
careful person would propose.

## The one narrative requirement

The story must contain a **verification scene**. Your protagonist does not just
realize the discovery -- they doubt it, and then they run a concrete analysis,
on the named dataset, that convinces them it is real. Show the analysis: what
they computed, on what, compared against what, and what number or picture made
the doubt collapse. A breakthrough nobody checks is not satisfying fiction;
the check is where the story earns its ending.

## Form

500-800 words. Third person. No preamble, no meta-commentary, no notes to the
editor. Begin mid-scene if you like. End within two paragraphs of the
verification scene landing.

Write the story to `fiction_story.md`. Write nothing else. Do not write code.
Do not read or modify any other file.


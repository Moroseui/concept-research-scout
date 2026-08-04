# Handoff prompt for Claude

Copy this message after uploading or cloning the repository:

> Inspect this repository and preserve its staged research-discovery workflow. Begin with `README.md`, `CHARTER.md`, and `docs/COLLABORATOR_RULES.md`. Run `python scout.py doctor`. Do not generate experiment code yet. First help me configure `AGENTS.toml`, then create the first scouting cycle and produce a literature-grounded portfolio of candidate ideas. Treat positive and negative results as equally useful, and optimize for interesting, medically relevant, low-lift questions where prior work has already completed much of the legwork.

Before allowing probe code, Claude should confirm that the human approval marker exists in the idea folder.

#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
for p in [ROOT/'ideas', ROOT/'probes', ROOT/'portfolio', ROOT/'evidence', ROOT/'orchestrator'/'runs']:
    p.mkdir(parents=True, exist_ok=True)
state = ROOT/'orchestrator'/'state.json'
if not state.exists():
    state.write_text(json.dumps({'next_scout': 1, 'selected_idea': None}, indent=2)+'\n')
print('Initialized Concept Research Scout.')
print('Next: edit CHARTER.md, then run: python scout.py doctor')

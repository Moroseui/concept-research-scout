"""Saved notebook source must not be mistaken for an executed successful console."""
import importlib.util
import json
from pathlib import Path

spec=importlib.util.spec_from_file_location('console_search',Path(__file__).resolve().parents[1]/'scripts/find_047_console_evidence.py')
search=importlib.util.module_from_spec(spec);spec.loader.exec_module(search)


def test_notebook_sources_do_not_establish_execution(tmp_path):
    markers='[authority] Idea 047 Phase B '+search.CONTRACT+' STUDY_COMPLETE'
    path=tmp_path/'saved.ipynb'
    path.write_text(json.dumps({'cells':[{'source':[markers],'outputs':[]}]}))
    assert search.inspect(path)['disposition']=='NO_COMPLETE_MARKER_COMBINATION'
    path.write_text(json.dumps({'cells':[{'source':[], 'outputs':[{'text':[markers]}]}]}))
    result=search.inspect(path)
    assert result['disposition']=='CANDIDATE_REQUIRES_ORIGINAL_PROVENANCE'
    assert 'STUDY_COMPLETE' not in json.dumps(result)

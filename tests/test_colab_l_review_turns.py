import json,os
from pathlib import Path
import pytest
from orchestrator import review_submission as rs,manual_stage as stage,colab_arm_question as q

@pytest.mark.parametrize('run,kind,expected',[(q.RUN,'run_spec_review','60'),('other','run_spec_review','30'),(q.RUN,'result_interpretation_review','60')])
def test_real_bound_reader_changes_only_l_turn_budget(tmp_path,run,kind,expected):
    os.umask(0o077);tmp_path.chmod(0o700)
    (tmp_path/'input-measurement.json').write_text('{"workspace_files":[]}')
    (tmp_path/'input-measurement.json').chmod(0o600)
    binding={'call_id':'c'*64,'run_id':run,'stage':kind,'source_sha':'a'*40,'runtime_sha256':'b'*64,'input_sha256':'d'*64}
    pins=rs.prepare(tmp_path,'scientific',binding)
    argv=stage.reviewer_command(tmp_path,kind)
    assert argv[argv.index('--max-turns')+1]==expected
    assert argv[argv.index('--tools')+1]=='Read'
    assert argv[argv.index('--allowedTools')+1]=='Read(./**),'+','.join((*rs.SEARCH_TOOLS,rs.TOOL))
    assert pins['config_sha256'] in argv[argv.index('--mcp-config')+1]
    assert not (tmp_path/rs.RECORD).exists()

def test_no_submission_contract_keeps_original_budget(tmp_path):
    os.umask(0o077);tmp_path.chmod(0o700)
    (tmp_path/'input-measurement.json').write_text('{"workspace_files":[]}')
    (tmp_path/'input-measurement.json').chmod(0o600)
    argv=stage.reviewer_command(tmp_path,'run_spec_review')
    assert argv[argv.index('--max-turns')+1]=='30'

def test_changed_submission_contract_refuses(tmp_path):
    os.umask(0o077);tmp_path.chmod(0o700)
    (tmp_path/'input-measurement.json').write_text('{"workspace_files":[]}')
    (tmp_path/'input-measurement.json').chmod(0o600)
    rs.prepare(tmp_path,'scientific',{'call_id':'c'*64,'run_id':q.RUN,'stage':'run_spec_review','source_sha':'a'*40,'runtime_sha256':'b'*64,'input_sha256':'d'*64})
    cfg=tmp_path/rs.CONFIG
    value=json.loads(cfg.read_text());value['bindings']['stage']='result_interpretation_review'
    cfg.write_text(json.dumps(value))
    with pytest.raises(ValueError):stage.reviewer_command(tmp_path,'run_spec_review')

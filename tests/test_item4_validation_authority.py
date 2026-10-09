"""Installed-authority/unit checks on explicitly synthetic external review records."""
from pathlib import Path
import copy
import json
import pytest
from orchestrator import item4_validation_admission as gate,autonomy_review
from tools import install_item4_validation as installer


@pytest.fixture
def installation(tmp_path,monkeypatch):
    root=tmp_path/'release';record=tmp_path/'record';root.mkdir();record.mkdir()
    monkeypatch.setattr(gate,'ROOT',root);monkeypatch.setattr(gate,'RECORD',record)
    monkeypatch.setattr(gate,'__file__',str(root/'orchestrator/item4_validation_admission.py'))
    files={}
    for name in gate.FILES:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(('Synthetic source fixture '+name).encode());files[name]=gate.sha(p.read_bytes())
    operator=root/gate.FILES[1];monkeypatch.setattr(gate,'OPERATOR',gate.sha(operator.read_bytes()))
    unit=Path('/etc/systemd/system')/('research-'+gate.CHANGE+'.service')
    fixture_unit=tmp_path/'unit';fixture_unit.write_text('Synthetic fixed protected unit')
    install={'source':'a'*40,'review_sha256':'b'*64,'files':files,'units':{str(unit):gate.sha(fixture_unit.read_bytes())}}
    (record/'review').mkdir();(record/'direction').mkdir()
    (record/'installed.json').write_text(json.dumps(install))
    (record/'review/packet-manifest.json').write_text(json.dumps({'source_sha':'a'*40,'source_files':files}))
    reviews={record/'review':{'verdict':'APPROVE','change_id':gate.CHANGE,'source_sha':'a'*40,'report_sha256':'b'*64},
        record/'direction':{'verdict':'APPROVE','source_sha':gate.DIRECTION_SOURCE,'report_sha256':gate.DIRECTION}}
    monkeypatch.setattr(autonomy_review,'verify_result',lambda path:copy.deepcopy(reviews[Path(path)]))
    # External installed-root ownership is simulated; every byte/hash/member
    # comparison in the policy is real. Native review qualification has its own suite.
    def trusted(path):
        path=Path(path)
        if path==unit:return fixture_unit
        assert path.is_relative_to(root) or path.is_relative_to(record)
        assert not path.is_symlink()
        return path
    monkeypatch.setattr(gate,'trusted',trusted)
    return root,record,install,reviews,fixture_unit


def test_only_complete_exact_installed_authority_is_accepted(installation):
    assert gate.authority()=='b'*64


@pytest.mark.parametrize('damage',['implementation-reject','direction-reject','wrong-direction','missing-source','changed-source','operator','unit','source-binding','review-binding','foreign-change','import-path'])
def test_bad_installed_authority_refuses(installation,monkeypatch,damage):
    root,record,install,reviews,unit=installation
    if damage=='implementation-reject':reviews[record/'review']['verdict']='REJECT'
    elif damage=='direction-reject':reviews[record/'direction']['verdict']='REJECT'
    elif damage=='wrong-direction':reviews[record/'direction']['report_sha256']='f'*64
    elif damage=='changed-source':(root/'orchestrator/experiment_owner.py').write_text('changed')
    elif damage=='operator':
        (root/gate.FILES[1]).write_text('changed')
    elif damage=='unit':unit.write_text('changed')
    elif damage=='source-binding':install['source']='f'*40
    elif damage=='review-binding':install['review_sha256']='f'*64
    elif damage=='foreign-change':reviews[record/'review']['change_id']='other'
    elif damage=='import-path':monkeypatch.setattr(gate,'__file__',str(root/'foreign.py'))
    else:install['files'].pop('orchestrator/experiment_owner.py')
    (record/'installed.json').write_text(json.dumps(install))
    with pytest.raises(ValueError):gate.authority()


def test_unit_changes_only_description_and_entrypoint(monkeypatch):
    before=('Description=Reviewed experiment authoring (execution provisioning held)\n'
        'User=partho\nGroup=partho\nUMask=0077\nNoNewPrivileges=true\nProtectSystem=strict\nPrivateTmp=true\nRestart=no\n'
        'ReadWritePaths=/synthetic-state\n'
        'ExecStartPre=/synthetic-existing-guard\n'
        'ExecStart=/usr/bin/python3 -s -B /opt/research-system/manual-repair-helpers/item4-validation-admission-20261009/tools/item4_validation_runtime.py advance\n').encode()
    monkeypatch.setattr(installer,'PRIOR_UNIT_SHA',installer.sha(before))
    after=installer.unit_bytes(before)
    retained=lambda raw:[line for line in raw.decode().splitlines() if not line.startswith(('Description=','ExecStart='))]
    assert retained(after)==retained(before)
    assert b'item4_validation_runtime.py advance' in after and b'ExecStartPre=/synthetic-existing-guard' in after
    with pytest.raises(ValueError,match='PRIOR_UNIT_CHANGED'):installer.unit_bytes(before+b'changed')


def test_installer_refuses_before_writes_without_root(tmp_path,monkeypatch):
    monkeypatch.setattr(installer.os,'geteuid',lambda:1000)
    with pytest.raises(ValueError,match='ROOT_REQUIRED'):installer.install(tmp_path/'source',tmp_path/'review')
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize('damage',['revise','source-binding','changed-policy','changed-file','direction','operator'])
def test_installer_refuses_unapproved_or_changed_bundle_before_any_writes(tmp_path,monkeypatch,damage):
    source=tmp_path/'source';source.mkdir();review=tmp_path/'review';review.mkdir()
    checkout=Path(__file__).parents[1]
    for name in gate.FILES:
        p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((checkout/name).read_bytes())
    files={name:gate.sha((source/name).read_bytes()) for name in gate.FILES}
    manifest={'source_sha':'a'*40,'source_files':files};(review/'packet-manifest.json').write_text(json.dumps(manifest))
    approved={'verdict':'APPROVE','change_id':gate.CHANGE,'source_sha':'a'*40,'report_sha256':'b'*64}
    direction={'verdict':'APPROVE','source_sha':gate.DIRECTION_SOURCE,'report_sha256':gate.DIRECTION}
    monkeypatch.setattr(installer.os,'geteuid',lambda:0)
    monkeypatch.setattr(installer,'ROOT',tmp_path/'not-installed')
    monkeypatch.setattr(installer,'RECORD',tmp_path/'not-recorded')
    monkeypatch.setattr(installer,'UNIT',tmp_path/'not-unit')
    monkeypatch.setattr(installer,'trusted',lambda path:Path(path)) # Labelled ownership fixture.
    monkeypatch.setattr(autonomy_review,'verify_result',lambda path:approved if Path(path)==review else direction)
    if damage=='revise':approved['verdict']='REVISE'
    elif damage=='source-binding':approved['source_sha']='f'*40
    elif damage=='direction':direction['report_sha256']='f'*64
    else:
        name='orchestrator/item4_validation_admission.py' if damage=='changed-policy' else gate.FILES[1] if damage=='operator' else 'tools/item4_validation_retained.py'
        (source/name).write_bytes((source/name).read_bytes()+b' changed')
    with pytest.raises(ValueError):installer.install(source,review)
    assert not installer.ROOT.exists() and not installer.RECORD.exists() and not installer.UNIT.exists()

"""Verify a bounded Actions admission artifact against trusted GitHub API evidence.

This verifier grants nothing itself. A protected caller fetches these objects from
GitHub, then supplies the verified identity to the shared broker. Artifact text
cannot choose commands, credentials, a destination, or reset authority.
"""
import hashlib
import io
import json
import stat
import zipfile
import zlib
from orchestrator.git_publication import scan

REPOSITORY_ID=1323461276


def verify(run,artifact,archive,workflow,expected):
    required={'run_id','attempt','source','branch','workflow_path','workflow_sha256'}
    if set(expected)!=required:raise ValueError('ACTIONS_EXPECTATION_SCHEMA')
    if (run.get('repository',{}).get('id')!=REPOSITORY_ID or
        str(run.get('id'))!=expected['run_id'] or
        str(run.get('run_attempt'))!=expected['attempt'] or
        run.get('head_sha')!=expected['source'] or
        run.get('head_branch')!=expected['branch'] or
        run.get('path')!=expected['workflow_path'] or
        run.get('event')!='workflow_dispatch'):
        raise ValueError('ACTIONS_RUN_BINDING')
    name='research-admission-'+expected['run_id']+'-'+expected['attempt']
    if (artifact.get('name')!=name or artifact.get('expired') is not False or
        artifact.get('workflow_run',{}).get('id')!=run['id'] or
        type(artifact.get('size_in_bytes')) is not int or not 0<artifact['size_in_bytes']<=65536):
        raise ValueError('ACTIONS_ARTIFACT_BINDING')
    if hashlib.sha256(workflow).hexdigest()!=expected['workflow_sha256']:
        raise ValueError('ACTIONS_REVIEWED_WORKFLOW_CHANGED')
    if len(archive)>65536:raise ValueError('ACTIONS_ARCHIVE_LIMIT')
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            files=bundle.infolist()
            if len(files)!=1 or files[0].filename!='admission.json':raise ValueError('ACTIONS_ARCHIVE_MEMBERS')
            item=files[0]
            if item.file_size>4096 or item.flag_bits & 1 or stat.S_ISLNK(item.external_attr>>16):raise ValueError('ACTIONS_ARCHIVE_MEMBER_TYPE')
            raw=bundle.read(item)
    except (zipfile.BadZipFile,zlib.error,EOFError):
        raise ValueError('ACTIONS_ARCHIVE_INVALID') from None
    scan('admission.json',raw)
    record=json.loads(raw)
    identity={'repository_id':REPOSITORY_ID,**{k:expected[k] for k in ('run_id','attempt','source','branch','workflow_sha256')}}
    if record!=identity:raise ValueError('ACTIONS_REQUEST_BINDING')
    return identity

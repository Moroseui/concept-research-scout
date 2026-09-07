"""Protected, bounded GitHub retrieval for the existing admission verifier.

No credential is sent to artifact storage or returned to a requester. The caller
owns the approved workflow/source expectation and authenticated token context.
This route only reads metadata/source and a small admission artifact; it cannot
dispatch, reset, publish, or select a repository from request text.
"""
import base64
import hashlib
import re
import urllib.error
import urllib.parse
import urllib.request

from orchestrator.actions_admission import verify
from orchestrator.phone_notifications import api, NoRedirect

PREFIX='/repos/Moroseui/concept-research-scout'


def artifact_bytes(artifact_id, token):
    if type(artifact_id) is not int or artifact_id<=0:raise ValueError('ARTIFACT_ID_REQUIRED')
    request=urllib.request.Request('https://api.github.com'+PREFIX+'/actions/artifacts/'+str(artifact_id)+'/zip',
        headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json',
                 'X-GitHub-Api-Version':'2022-11-28'})
    opener=urllib.request.build_opener(NoRedirect())
    # NoRedirect raises ValueError rather than exposing a credential-bearing URL.
    # This specialized handler captures only the one API redirect, without following.
    class Capture(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):return None
    try:
        with urllib.request.build_opener(Capture()).open(request,timeout=30):
            raise ValueError('ARTIFACT_REDIRECT_REQUIRED')
    except urllib.error.HTTPError as error:
        if error.code!=302:raise ValueError('ARTIFACT_API_UNAVAILABLE') from None
        location=error.headers.get('Location','')
    except (OSError,ValueError):raise ValueError('ARTIFACT_API_UNAVAILABLE') from None
    parsed=urllib.parse.urlsplit(location)
    host=parsed.hostname or ''
    if (parsed.scheme!='https' or parsed.username or parsed.password or parsed.port not in (None,443)
            or not (host.endswith('.blob.core.windows.net') or host.endswith('.actions.githubusercontent.com'))):
        raise ValueError('ARTIFACT_STORAGE_HOST_REFUSED')
    # Deliberately no Authorization header on the signed storage URL. No redirects.
    try:
        with opener.open(urllib.request.Request(location),timeout=30) as response:
            raw=response.read(65537)
    except (OSError,ValueError):raise ValueError('ARTIFACT_STORAGE_UNAVAILABLE') from None
    if len(raw)>65536:raise ValueError('ACTIONS_ARCHIVE_LIMIT')
    return raw


def collect(expected, token, *, get=api, download=artifact_bytes):
    required={'run_id','attempt','source','branch','workflow_path','workflow_sha256'}
    if set(expected)!=required:raise ValueError('ACTIONS_EXPECTATION_SCHEMA')
    if (not re.fullmatch('[1-9][0-9]*',expected['run_id']) or
        not re.fullmatch('[1-9][0-9]*',expected['attempt']) or
        not re.fullmatch('[0-9a-f]{40}',expected['source']) or
        not re.fullmatch('[0-9a-f]{64}',expected['workflow_sha256']) or
        not re.fullmatch(r'\.github/workflows/[A-Za-z0-9_-]+\.yml',expected['workflow_path']) or
        expected['branch'] not in ('main','astra/autonomous-isles-pilot')):
        raise ValueError('ACTIONS_EXPECTATION_VALUES')
    run=get('GET',PREFIX+'/actions/runs/'+expected['run_id']+'/attempts/'+expected['attempt'],token)
    if (run.get('repository',{}).get('id')!=1323461276 or str(run.get('id'))!=expected['run_id']
            or str(run.get('run_attempt'))!=expected['attempt'] or run.get('head_sha')!=expected['source']
            or run.get('head_branch')!=expected['branch'] or run.get('path')!=expected['workflow_path']
            or run.get('event')!='workflow_dispatch'):
        raise ValueError('ACTIONS_RUN_BINDING')
    content=get('GET',PREFIX+'/contents/'+expected['workflow_path']+'?ref='+expected['source'],token)
    if content.get('encoding')!='base64' or content.get('path')!=expected['workflow_path']:
        raise ValueError('WORKFLOW_CONTENT_BINDING')
    workflow=base64.b64decode(content['content'],validate=False)
    if len(workflow)>65536:raise ValueError('WORKFLOW_CONTENT_LIMIT')
    if hashlib.sha256(workflow).hexdigest()!=expected['workflow_sha256']:
        raise ValueError('ACTIONS_REVIEWED_WORKFLOW_CHANGED')
    wanted='research-admission-'+expected['run_id']+'-'+expected['attempt']
    found=[]
    for page in range(1,4):
        listing=get('GET',PREFIX+'/actions/runs/'+expected['run_id']+'/artifacts?per_page=100&page='+str(page),token)
        rows=listing.get('artifacts')
        if not isinstance(rows,list) or len(rows)>100:raise ValueError('ARTIFACT_LIST_SCHEMA')
        found.extend(row for row in rows if row.get('name')==wanted)
        if len(rows)<100:break
    else:raise ValueError('ARTIFACT_LIST_LIMIT')
    if len(found)!=1:raise ValueError('UNIQUE_ADMISSION_ARTIFACT_REQUIRED')
    artifact=found[0]
    if (artifact.get('expired') is not False or artifact.get('workflow_run',{}).get('id')!=run['id']
            or type(artifact.get('size_in_bytes')) is not int or not 0<artifact['size_in_bytes']<=65536):
        raise ValueError('ACTIONS_ARTIFACT_BINDING')
    raw=download(artifact['id'],token)
    return verify(run,artifact,raw,workflow,expected)

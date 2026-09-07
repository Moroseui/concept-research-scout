"""Short-lived selected-repository App credentials, held only by the broker.

No App is created here. Configuration/key and this code must be outside agent
write access. Caller serializes credential use; no model process is launched in
this environment (existing model launchers use env -i and separate identities).
"""
from contextlib import contextmanager
import os
from orchestrator.phone_notifications import api,jwt,positive

REPOSITORY_ID=1323461276
PERMISSIONS={'contents':'write','actions':'read','metadata':'read'}


@contextmanager
def credentials(config):
    if set(config)!={'app_id','installation_id','repository_id','private_key','permission_decision'} or config['repository_id']!=REPOSITORY_ID or not config['permission_decision']:
        raise ValueError('WRITER_PERMISSION_CONFIGURATION_REQUIRED')
    for key in ('app_id','installation_id','repository_id'):positive(config[key])
    app_jwt=jwt(config)
    installation=api('GET','/app/installations/'+str(config['installation_id']),app_jwt)
    if installation.get('app_id')!=config['app_id'] or installation.get('repository_selection')!='selected' or installation.get('permissions')!=PERMISSIONS:raise ValueError('WRITER_INSTALLATION_BOUNDARY')
    result=api('POST','/app/installations/'+str(config['installation_id'])+'/access_tokens',app_jwt,
               {'repository_ids':[REPOSITORY_ID],'permissions':PERMISSIONS})
    if result.get('permissions')!=PERMISSIONS or [r.get('id') for r in result.get('repositories',[])]!=[REPOSITORY_ID]:raise ValueError('WRITER_TOKEN_SCOPE')
    token=result.get('token')
    if not isinstance(token,str) or not token:raise ValueError('WRITER_TOKEN_MISSING')
    env={'GH_TOKEN':token,'GIT_TERMINAL_PROMPT':'0','GIT_CONFIG_NOSYSTEM':'1',
         'GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_COUNT':'2',
         'GIT_CONFIG_KEY_0':'credential.helper','GIT_CONFIG_VALUE_0':'',
         'GIT_CONFIG_KEY_1':'credential.helper','GIT_CONFIG_VALUE_1':'!gh auth git-credential'}
    old={key:os.environ.get(key) for key in env}
    try:
        os.environ.update(env)
        yield {'repository_id':REPOSITORY_ID,'app_id':config['app_id'],'installation_id':config['installation_id'],'permissions':PERMISSIONS}
    finally:
        for key,value in old.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value

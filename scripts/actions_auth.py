"""Use existing Actions credentials, never print/store them in publication paths."""
import os
from pathlib import Path
import subprocess
import tempfile


def setup():
    if os.environ.get('GITHUB_ACTIONS')!='true':raise ValueError('HOSTED_AUTH_ONLY')
    if not os.environ.get('CLAUDE_CODE_OAUTH_TOKEN'):raise ValueError('CLAUDE_SUBSCRIPTION_CREDENTIAL_MISSING')
    key=os.environ.get('OPENAI_API_KEY')
    if not key:raise ValueError('EXISTING_ACTIONS_CODEX_KEY_MISSING')
    home=Path(tempfile.mkdtemp(prefix='hosted-codex-auth-'));home.chmod(0o700)
    env=dict(os.environ,CODEX_HOME=str(home))
    r=subprocess.run(['codex','login','--with-api-key'],input=key,text=True,capture_output=True,env=env,timeout=30)
    if r.returncode:raise ValueError('CODEX_AUTH_SETUP_FAILED')
    for p in home.rglob('*'):
        if p.is_file():p.chmod(0o600)
    with open(os.environ['GITHUB_ENV'],'a') as f:f.write('CODEX_HOME='+str(home)+'\n')
    print('Authentication: existing Actions Codex API arrangement; existing Claude subscription. No new credentials or provisioning.')


if __name__=='__main__':setup()

"""Bounded, credential-free DNS/TLS preflight. No model calls or retries."""
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import urllib.error

class NetworkUnavailable(ValueError):
    pass


PROVIDERS = {'codex': ('chatgpt.com', 'auth.openai.com'),
             'claude': ('api.anthropic.com',), 'modal': ('api.modal.com',),
             'github': ('api.github.com',), 'drive': ('www.googleapis.com',)}


def probe(host):
    if host not in {h for hosts in PROVIDERS.values() for h in hosts}:
        raise ValueError('NETWORK_PROVIDER_NOT_DECLARED')
    # A subprocess bounds DNS too: socket.getaddrinfo has no Python timeout.
    dns = subprocess.run([sys.executable, '-I', '-c',
        'import socket,sys; assert socket.getaddrinfo(sys.argv[1],443,type=socket.SOCK_STREAM)',host],
        capture_output=True,timeout=5,check=True)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(urllib.request.Request('https://'+host+'/',method='GET' if host=='api.modal.com' else 'HEAD'),timeout=5) as response:
            code=response.status
    except urllib.error.HTTPError as error:
        code=error.code  # 401/403/404 establish TLS/HTTP reachability, not login.
    if not 200<=code<500 or code in (408,425,429):
        raise ValueError('NETWORK_HTTP_UNAVAILABLE:'+str(code))
    return {'host':host,'dns':'RESOLVED','https_status':code,'authenticated':False}


def require(providers, record=None):
    providers=sorted(set(providers))
    if not providers or any(p not in PROVIDERS for p in providers):
        raise ValueError('NETWORK_PROVIDER_SET_REQUIRED')
    value={'at':time.time(),'providers':providers,'checks':[],'status':'PASS','charged_calls':0}
    try:
        for host in dict.fromkeys(h for p in providers for h in PROVIDERS[p]):
            value['checks'].append(probe(host))
    except Exception as error:
        value.update(status='REFUSED',reason='NETWORK_PREFLIGHT_FAILED',error_type=type(error).__name__)
        if record is not None:save(record,value)
        raise NetworkUnavailable('NETWORK_PREFLIGHT_FAILED_NO_CHARGE:'+','.join(providers)) from None
    if record is not None:save(record,value)
    return value


def save(path,value):
    from orchestrator.manual_executor import atomic
    path=Path(path)
    if any(p.is_symlink() for p in [path,*path.parents]):raise ValueError('NETWORK_STATUS_ALIAS')
    from orchestrator import private_records
    private_records.mkdir(path.parent,parents=True,exist_ok=True)
    atomic(path,value,mode=0o600)


def status(path):
    path=Path(path)
    return json.loads(path.read_text()) if path.exists() else {'status':'NOT_CHECKED'}

"""Bounded Colab acquisition of the immutable P001 archive; never extracts it."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

SIZE = 99014629647
MD5 = '36ae28b9a17f7340b8bbef62b595cb57'
URL = 'https://zenodo.org/records/16813698/files/train.7z?download=1'
INPUT = Path('/content/isles-p001-input-16813698')
AUDIT = Path('/content/drive/MyDrive/isles-pilot/input-acquisition-16813698')

DOWNLOAD_CODE = r'''
import hashlib, json, os, time, urllib.request
from pathlib import Path
root, audit = Path(INPUT), Path(AUDIT)
def status(value):
    p = audit/'status.tmp'
    p.write_text(json.dumps({'status':value}))
    os.replace(p,audit/'status.json')
try:
    status('RUNNING')
    started=time.monotonic(); count=0; digest=hashlib.md5()
    with urllib.request.urlopen(URL, timeout=120) as response, (root/'train.7z.part').open('xb') as output:
        os.chmod(output.name,0o600)
        while True:
            if time.monotonic()-started>14400: raise TimeoutError('four-hour acquisition limit')
            block=response.read(8<<20)
            if not block:break
            count+=len(block)
            if count>SIZE:raise ValueError('archive exceeds pinned size')
            output.write(block);digest.update(block)
    if count!=SIZE or digest.hexdigest()!=MD5:raise ValueError('archive identity mismatch')
    os.replace(root/'train.7z.part',root/'train.7z')
    (audit/'identity.json').write_text(json.dumps({'url':URL,'size_bytes':count,
        'md5':digest.hexdigest(),'wall_seconds':time.monotonic()-started}))
    status('VALIDATED')
except BaseException:
    import traceback
    traceback.print_exc()
    status('FAILED')
    raise
'''


def start():
    if not os.environ.get('COLAB_RELEASE_TAG') or shutil.which('nvidia-smi'):
        raise RuntimeError('CPU Colab required')
    if not os.path.ismount('/content/drive'):
        raise RuntimeError('operator Drive mount required')
    if shutil.disk_usage('/content').free < SIZE + (10<<30):
        raise RuntimeError('insufficient local storage')
    if INPUT.exists() or INPUT.is_symlink() or AUDIT.exists() or AUDIT.is_symlink():
        raise RuntimeError('acquisition destination exists; preserve and inspect status')
    INPUT.mkdir(mode=0o700)
    AUDIT.mkdir(mode=0o700,parents=True)
    (AUDIT/'status.json').write_text(json.dumps({'status':'STARTING'}))
    parameters={'INPUT':str(INPUT),'AUDIT':str(AUDIT),'URL':URL,'SIZE':SIZE,'MD5':MD5}
    source='\n'.join(k+' = '+repr(v) for k,v in parameters.items())+'\n'+DOWNLOAD_CODE
    script=AUDIT/'download.py';script.write_text(source)
    try:
        with (AUDIT/'console.log').open('xb') as console:
            os.chmod(console.name,0o600)
            subprocess.Popen([sys.executable,str(script)],stdout=console,stderr=subprocess.STDOUT,
                             start_new_session=True)
    except BaseException:
        (AUDIT/'status.json').write_text(json.dumps({'status':'FAILED'}))
        raise
    return {'status':'DISPATCHED'}


def poll():
    if not os.path.ismount('/content/drive') or not (AUDIT/'status.json').is_file():
        return {'status':'NOT_VISIBLE'}
    result=json.loads((AUDIT/'status.json').read_text())
    if set(result)!={'status'} or result['status'] not in ['STARTING','RUNNING','VALIDATED','FAILED']:
        raise ValueError('invalid acquisition status')
    return result

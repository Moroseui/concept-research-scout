"""Colab-only resumable filename search. Never opens archive or imaging payloads."""
import collections
import json
import os
from pathlib import Path
import time


def search(state_file, seconds=45):
    mounted=os.path.ismount('/content/drive') and os.path.isdir('/content/drive/MyDrive')
    roots=['/content/drive/MyDrive','/content/drive/Shareddrives']
    if not mounted:return {'drive_mounted':False,'scan_complete':False,'archive_candidates':[]}
    if state_file.is_symlink():raise ValueError('unsafe metadata checkpoint')
    if state_file.exists():state=json.loads(state_file.read_text())
    else:state={'pending':[r for r in roots if os.path.isdir(r)],'seen':[],'candidates':{},'errors':0}
    queue=collections.deque(state['pending']);seen=set(state['seen']);start=time.monotonic()
    while queue and time.monotonic()-start<seconds:
        directory=queue.popleft()
        if directory in seen:continue
        if not any(directory==r or directory.startswith(r+'/') for r in roots) or '..' in Path(directory).parts:raise ValueError('unsafe metadata path')
        seen.add(directory)
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    if entry.is_symlink():continue
                    if entry.is_dir(follow_symlinks=False):queue.append(entry.path)
                    elif entry.name=='train.7z' and entry.is_file(follow_symlinks=False):
                        state['candidates'][entry.path]=entry.stat(follow_symlinks=False).st_size
        except OSError:state['errors']+=1
    state.update(pending=list(queue),seen=sorted(seen))
    state_file.parent.mkdir(mode=0o700,exist_ok=True)
    temporary=state_file.with_suffix('.tmp')
    with temporary.open('w') as stream:
        os.chmod(temporary,0o600);json.dump(state,stream)
    os.replace(temporary,state_file)
    return {'drive_mounted':True,'scan_complete':not queue and state['errors']==0,
            'archive_candidates':[{'path':p,'size_bytes':n} for p,n in sorted(state['candidates'].items())]}


if __name__=='__main__':
    print(json.dumps(search(Path('/content/isles-worker-private/archive-search.json'))))

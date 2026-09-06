"""No data, credentials, Drive mount or GPU: tiny execution/retrieval witness."""
import hashlib
import json
from pathlib import Path

PAYLOAD=b'ISLES pilot synthetic execution: 6 * 7 = 42\n'

def execute(root):
    root=Path(root); root.mkdir(parents=True,exist_ok=True)
    (root/'synthetic-result.txt').write_bytes(PAYLOAD)
    return {'answer':6*7,'sha256':hashlib.sha256(PAYLOAD).hexdigest()}


def retrieve(root):
    data=(Path(root)/'synthetic-result.txt').read_bytes()
    if data!=PAYLOAD: raise ValueError('retrieved bytes differ from executed synthetic payload')
    return {'retrieved_text':data.decode(),'sha256':hashlib.sha256(data).hexdigest()}

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('operation',choices=['execute','retrieve']); ap.add_argument('--root',default='/tmp/isles-colab-synthetic'); a=ap.parse_args()
    print(json.dumps(execute(a.root) if a.operation=='execute' else retrieve(a.root)))

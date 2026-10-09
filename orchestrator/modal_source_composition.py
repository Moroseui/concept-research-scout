"""Exact frozen input composition, using the existing private server uploader.

No scientific computation, discovery, image build, or new provider worker.
Callers must verify installation, reserve costs, and install retention first.
"""
from pathlib import Path, PurePosixPath
import csv
import hashlib
import json
import os
import re
import stat
from orchestrator import private_records as pr
import importlib.util

# Load this reviewed helper dependency explicitly; the installed base predates
# auxiliary inputs and may already have its older module in sys.modules.
_spec=importlib.util.spec_from_file_location("_source_frozen_inputs",Path(__file__).with_name("modal_development_inputs.py"))
frozen=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(frozen)
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from orchestrator.manual_driver import write_once
from orchestrator.modal_assets import local_files, upload

OPERATION='item4-frozen-base-source-hydrated-v2'
PURPOSE='M4_ITEM4_SOURCE_COMPOSITION'
COHORT=frozen.COHORT
SPLIT='da79e94bdae3f59d23db497d5f26f0d57aa4f279847fe57ec9a8d05ebcf18843'
INVENTORY='b84b5f872711720d16b6d7f8858b3bff65a0543ff0580195eaf228f20878c0b2'
DATA_BYTES=7202931657
RETENTION_DAYS=30

def require(ok,why):
    if not ok:raise ValueError('SOURCE_COMPOSITION_'+why)

def contract(root):
    root=Path(root)
    raw={n:pr.check(root/n).read_bytes() for n in ('cohort.json','source.json','auxiliary.json','authority.txt','split.csv')}
    base=frozen.frozen_inventory(raw['cohort.json'],raw['source.json'],raw['authority.txt'])
    auxiliary=frozen.frozen_auxiliary(raw['cohort.json'],raw['auxiliary.json'])
    require(digest(raw['split.csv'])==SPLIT,'FROZEN_SPLIT')
    rows=list(csv.DictReader(raw['split.csv'].decode().splitlines()))
    require(len(rows)==149 and len({r['case_id'] for r in rows})==149,'SPLIT_MEMBERS')
    require({r['population'] for r in rows}=={'census','reserved'},'SPLIT_GROUPS')
    excluded={r['case_id'] for r in rows if r['population']=='reserved'}
    census={r['case_id'] for r in rows if r['population']=='census'}
    cases=set(json.loads(raw['cohort.json'])['cases'])
    require(len(excluded)==49 and len(census)==100 and len(cases)==99 and cases<=census and not cases&excluded,'EXCLUDED_PATIENT')
    files={**base['files'],**auxiliary}
    require(len(files)==893 and sum(v['bytes'] for v in files.values())==DATA_BYTES
            and digest(canonical(files))==INVENTORY,'EXACT_BASE_INVENTORY')
    require(set(re.findall(r'sub-stroke[0-9]{4}','\n'.join(files)))==cases,'INPUT_IDENTIFIERS')
    return files,{'cohort_sha256':COHORT,'split_sha256':SPLIT,'inventory_sha256':INVENTORY,
                  'development_count':99,'excluded_count':49,'excluded_overlap':0,'files':893,'bytes':DATA_BYTES}

def partitions(files):
    image={n:r for n,r in files.items() if n.startswith('train/')}
    brain={n:r for n,r in files.items() if n.startswith('brainmask/')}
    cache={n:r for n,r in files.items() if n.startswith('feature-cache-2mm-v2/')}
    baseline={n:r for n,r in files.items() if n.startswith('baseline/')}
    require(tuple(map(len,(image,brain,cache,baseline)))==(693,99,99,2),'FILE_CLASSES')
    require(set(image)|set(brain)|set(cache)|set(baseline)==set(files),'UNKNOWN_CLASS')
    return image,brain,cache,baseline

def target(root,name):
    root=pr.check(root);relative=PurePosixPath(name)
    require(not relative.is_absolute() and '..' not in relative.parts and name==relative.as_posix(),'RELATIVE_PATH')
    path=root.joinpath(*relative.parts)
    require(path.resolve().is_relative_to(root.resolve()),'PATH_ESCAPE')
    for p in reversed(path.parents):
        if p==root or root in p.parents:
            if p.exists():require(not p.is_symlink() and p.is_dir(),'PARENT_ALIAS')
            else:pr.mkdir(p)
    require(not path.exists() and not path.is_symlink(),'EXISTING_OUTPUT_NO_RETRY')
    return path

def write_verified(root,name,row,chunks):
    """An interrupted or wrong stream stays private and never becomes accepted."""
    path=target(root,name);h=hashlib.sha256();size=0
    with pr.open_file(path,'xb') as out:
        for chunk in chunks:
            require(isinstance(chunk,bytes),'STREAM_TYPE');size+=len(chunk)
            require(size<=row['bytes'],'STREAM_SIZE');h.update(chunk);out.write(chunk)
        out.flush();os.fsync(out.fileno())
    require(size==row['bytes'] and h.hexdigest()==row['sha256'],'STREAM_HASH')
    path.chmod(0o400)
    return {'bytes':size,'sha256':h.hexdigest()}

def copy_local(source,root,name,row):
    source=pr.check(source);before=source.stat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_size==row['bytes'],'LOCAL_SOURCE')
    with source.open('rb') as f:
        result=write_verified(root,name,row,iter(lambda:f.read(4*1024**2),b''))
    after=source.stat()
    require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==
            (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),'LOCAL_CHANGED_DURING_COPY')
    return result

def ingest_tar(stream,root,expected):
    """Exact regular members only, for the101 small frozen laptop originals."""
    import tarfile
    root=pr.check(root);seen=set()
    with tarfile.open(fileobj=stream,mode='r|') as archive:
        for member in archive:
            name=member.name
            require(member.isfile() and not member.issym() and not member.islnk()
                    and name in expected and name not in seen and member.size==expected[name]['bytes'],'TAR_MEMBER')
            f=archive.extractfile(member);require(f is not None,'TAR_STREAM')
            with f:write_verified(root,name,expected[name],iter(lambda:f.read(4*1024**2),b''))
            seen.add(name)
    require(seen==set(expected),'TAR_EXACT_MEMBERS')
    local_files(root,expected)
    return {'files':len(seen),'bytes':sum(x['bytes'] for x in expected.values())}

def copy_images(provider,volume_id,root,images):
    """Read only693 exact frozen paths from the preserved download volume."""
    volume=provider._volume(volume_id)
    # The pinned SDK lazily hydrates from_id handles on the first metadata read.
    # Verify identity immediately afterwards, still before reading any payload.
    before=volume.listdir('/',recursive=True)
    require(volume.object_id==volume_id,'SOURCE_VOLUME_ID')
    require(all(x.type.name in {'FILE','DIRECTORY'} for x in before),'SOURCE_MEMBER_TYPE')
    names=[x.path.lstrip('/') for x in before if x.type.name=='FILE']
    require(len(names)==len(set(names)),'SOURCE_DUPLICATE_MEMBER')
    sizes={x.path.lstrip('/'):x.size for x in before if x.type.name=='FILE'}
    require(all(sizes.get('images/'+name)==row['bytes'] for name,row in images.items()),'SOURCE_IMAGE_MEMBERS')
    for name,row in sorted(images.items()):write_verified(root,name,row,volume.read_file('/images/'+name))
    after=volume.listdir('/',recursive=True)
    require(all(x.type.name in {'FILE','DIRECTORY'} for x in after),'SOURCE_MEMBER_TYPE')
    require([(x.path,x.type.name,x.size) for x in sorted(before,key=lambda v:v.path)]==
            [(x.path,x.type.name,x.size) for x in sorted(after,key=lambda v:v.path)],'SOURCE_MEMBERS_CHANGED')
    return {'files':len(images),'bytes':sum(x['bytes'] for x in images.values()),'source_unchanged_membership':True}

def verify_destination(provider,volume_id,root,files):
    local_files(root,files)
    volume=provider._verify_volume(volume_id,files)
    require(volume.object_id==volume_id,'DESTINATION_VOLUME_ID')
    provider._verify_volume_members(volume_id,files)
    local_files(root,files)
    return {'status':'VERIFIED','volume_id':volume_id,'inventory_sha256':digest(canonical(files)),
            'files':len(files),'bytes':sum(x['bytes'] for x in files.values()),'scientific_approval':False}

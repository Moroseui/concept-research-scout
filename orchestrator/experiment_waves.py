"""Append-only runtime waves for a scientifically frozen incremental plan.

A wave selects only existing reviewed identities. Root publishes new records;
no earlier record or runtime is edited. Scientific approval, spending and full
projection admission remain separate, and incomplete selection is never done.
"""
from pathlib import Path
import re
from orchestrator import private_records as pr
from orchestrator.manual_executor import digest
from orchestrator.modal_executor import canonical
from orchestrator.review_contract import strict_json


def plan(driver):
    return strict_json((driver.state/'experiment-package/execution-plan.json').read_bytes())


def enabled(driver):
    mode=plan(driver).get('dispatch_mode')
    if mode not in {None,'incremental'}:raise ValueError('EXPERIMENT_DISPATCH_MODE')
    if mode=='incremental':
        p=plan(driver);pre=p.get('preprocessing',[])
        if pre:
            ids={x['id'] for x in pre}
            used={x.get('preprocessing_id') for x in p.get('fits',[])}
            if ids!=used:raise ValueError('EXPERIMENT_FIT_PREPROCESSING_ID')
    return mode=='incremental'


def adapter(kind):
    from orchestrator import experiment_dispatch,experiment_preprocessing_dispatch
    if kind not in {'fit','preprocessing'}:raise ValueError('EXPERIMENT_PREPARATION_KIND')
    return experiment_dispatch if kind=='fit' else experiment_preprocessing_dispatch


def identities(driver,kind):
    p=plan(driver)
    rows=p.get('fits' if kind=='fit' else 'preprocessing',[])
    field='fit_id' if kind=='fit' else 'id'
    ids=[row.get(field) for row in rows]
    if (not ids or any(not isinstance(x,str) or not re.fullmatch('[a-zA-Z0-9_-]{1,96}',x) for x in ids)
            or len(set(ids))!=len(ids)):
        raise ValueError('EXPERIMENT_FROZEN_IDENTITIES')
    return ids


def identity(row,kind):
    b=row['binding']
    return b['experiment']['fit_id'] if kind=='fit' else b['preprocessing']['id']


def merge(driver,kind,selections):
    if not selections:return None
    result={k:v for k,v in selections[0].items() if k!='jobs'};jobs={}
    for selected in selections:
        if {k:v for k,v in selected.items() if k!='jobs'}!=result:
            raise ValueError('EXPERIMENT_WAVE_BINDING')
        for row in selected['jobs']:
            ident=identity(row,kind)
            if ident in jobs:raise ValueError('EXPERIMENT_WAVE_IDENTITY_ALREADY_SELECTED')
            jobs[ident]=row
    ids=identities(driver,kind)
    if set(jobs)-set(ids):raise ValueError('EXPERIMENT_WAVE_UNREVIEWED_IDENTITY')
    return {**result,'jobs':[jobs[i] for i in ids if i in jobs]}


def read(driver,value,root,kind):
    from orchestrator.experiment_dispatch import trusted
    if not enabled(driver):raise ValueError('EXPERIMENT_INCREMENTAL_PLAN_REQUIRED')
    root=Path(root);frames=[];pins=[];selections=[]
    if root.exists() or root.is_symlink():
        pr.check(trusted(root))
        names=sorted(p.name for p in root.iterdir())
        expected=['wave-'+str(i).zfill(6)+'.json' for i in range(1,len(names)+1)]
        if names!=expected:raise ValueError('EXPERIMENT_WAVE_DIRECTORY_INCOMPLETE')
        for index,name in enumerate(names,1):
            raw=pr.check(trusted(root/name)).read_bytes();frame=strict_json(raw)
            if (not isinstance(frame,dict) or set(frame)!={'schema','index','previous_sha256','selection','preparation'}
                    or frame['schema']!='experiment-dispatch-wave/v1' or type(frame['index']) is not int
                    or frame['index']!=index or frame['previous_sha256']!=(pins[-1] if pins else None)
                    or not isinstance(frame['preparation'],dict) or set(frame['preparation'])!={'path','sha256'}
                    or not isinstance(frame['preparation']['path'],str) or not Path(frame['preparation']['path']).is_absolute()
                    or not re.fullmatch('[0-9a-f]{64}',str(frame['preparation']['sha256']))):
                raise ValueError('EXPERIMENT_WAVE_CHAIN')
            adapter(kind).validate_selection(driver,{},canonical(frame['selection']),partial=True)
            frames.append(frame);pins.append(digest(raw));selections.append(frame['selection'])
    old=value.get(kind+'_selection_waves',[])
    if not isinstance(old,list) or pins[:len(old)]!=old:
        raise ValueError('EXPERIMENT_WAVE_PRESERVED_SELECTION_CHANGED')
    merged=merge(driver,kind,selections)
    if merged is None:
        return {'pins':pins,'frames':frames,'selected':None}
    checked=adapter(kind).validate_selection(driver,{},canonical(merged),partial=True)
    checked.update(wave_pins=pins,sha256=digest(canonical(pins)),
        complete_selection=len(checked['jobs'])==len(identities(driver,kind)))
    return {'pins':pins,'frames':frames,'selected':checked}


def preparing(driver,value,rows,kind):
    from orchestrator.experiment_preprocessing_dispatch import directory
    root=Path(driver.config['execution_provisioning']) if kind=='fit' else directory(driver.config)
    previous=read(driver,value,root,kind)
    used={identity(row,kind) for frame in previous['frames'] for row in frame['selection']['jobs']}
    if used & {identity(row,kind) for row in rows}:
        raise ValueError('EXPERIMENT_WAVE_IDENTITY_ALREADY_SELECTED')
    return previous['pins']


def publish(preparation,ref,record,destination):
    """Called only inside the existing root publisher's parent lock."""
    import os
    from types import SimpleNamespace
    from orchestrator import experiment_provisioning as provision
    from orchestrator.experiment_dispatch import trusted
    driver=SimpleNamespace(state=Path(record['state']),config=record['config'])
    kind='preprocessing' if record['selection']['schema']=='experiment-preprocessing-dispatch/v1' else 'fit'
    # For preprocessing records the config destination already names its own root.
    observed=read(driver,{},destination,kind)
    pins=record['previous_waves'];index=len(pins)+1
    frame={'schema':'experiment-dispatch-wave/v1','index':index,'previous_sha256':pins[-1] if pins else None,
        'selection':record['selection'],'preparation':ref}
    raw=canonical(frame)
    if destination.exists():
        for p in [destination,*destination.iterdir()]:
            stat=trusted(p).stat()
            if stat.st_gid!=pr.SERVICE_GID or stat.st_mode&0o777!=(0o550 if p.is_dir() else 0o440):
                raise ValueError('EXPERIMENT_PROVISIONING_RECORD_MODES')
    if observed['pins']==pins+[digest(raw)]:
        return {'status':'ALREADY_PROVISIONED','ready_sha256':digest(canonical(observed['pins'])),'provider_called':False}
    if observed['pins']!=pins:raise ValueError('EXPERIMENT_WAVE_PREDECESSOR_CHANGED')
    merge(driver,kind,[f['selection'] for f in observed['frames']]+[record['selection']])
    if not destination.exists():
        destination.mkdir(mode=0o700)
        os.chown(destination,0,pr.SERVICE_GID,follow_symlinks=False);os.chmod(destination,0o550)
    # Recheck all source evidence immediately before publishing one atomic record.
    provision.original(ref);provision.inspect(preparation)
    provision._root_file(destination/('wave-'+str(index).zfill(6)+'.json'),raw)
    fd=os.open(destination,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)
    return {'status':'PROVISIONED','ready_sha256':digest(canonical(pins+[digest(raw)])),'provider_called':False}

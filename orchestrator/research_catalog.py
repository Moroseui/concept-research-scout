"""Finite installed request lookup, separate from proposal and authorization.

Administrators install reviewed immutable entries. Humans and agents select an
installed ID through Runtime; neither a filename nor an actor claim is authority.
The scientific eligibility adapter deliberately fails closed until its actual
system decision contract is reviewed and implemented.
"""
from collections.abc import Mapping
from pathlib import Path
import re
import stat

from orchestrator.handover_coordinator import digest

MAX_ENTRIES = 32  # Explicit per-configuration schedule selection; never retained history.
SCHEMA = 'installed-research-catalog-entry/v1'


def core(entry):
    """Authority binds this core; exclude its own later decision-file reference."""
    return {key:value for key,value in entry.items() if key!='eligibility'}


def identifier(value):
    if not isinstance(value,str) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,79}',value):
        raise ValueError('INSTALLED_RESEARCH_TASK_ID_REQUIRED')
    return value


def _pin(value,length):
    return isinstance(value,str) and re.fullmatch('[0-9a-f]{'+str(length)+'}',value)


def _source(value):
    if (not isinstance(value,dict) or set(value)!={'source','source_root'}
            or not _pin(value['source'],40) or not isinstance(value['source_root'],str)
            or not Path(value['source_root']).is_absolute() or '..' in Path(value['source_root']).parts):
        raise ValueError('CATALOG_EXACT_SOURCE_REQUIRED')
    return value


def setting(config):
    value=config.get('research_catalog')
    if value is None:return None
    if (not isinstance(value,dict) or set(value)!={'directory','legacy_source'}
            or not isinstance(value['directory'],str) or not Path(value['directory']).is_absolute()
            or '..' in Path(value['directory']).parts):
        raise ValueError('INSTALLED_RESEARCH_CATALOG_REQUIRED')
    _source(value['legacy_source'])
    return value


class _CatalogPaths(Mapping):
    """Stream retained names; exact lookup reads no unrelated entry bodies.

    Completed entries remain immutable and addressable as the catalog grows.
    A directory listing is inspection, never an admission or execution budget.
    """
    def __init__(self, folder):
        self.folder = folder

    def __getitem__(self, task_id):
        identifier(task_id)
        path = self.folder / (task_id + '.json')
        try:
            info = path.lstat()
        except FileNotFoundError:
            raise KeyError(task_id) from None
        if not stat.S_ISREG(info.st_mode):
            raise ValueError('PROTECTED_RESEARCH_CATALOG_ENTRY_REQUIRED')
        return path

    def __iter__(self):
        for path in self.folder.iterdir():
            if path.suffix != '.json':
                raise ValueError('BOUNDED_RESEARCH_CATALOG_REQUIRED')
            task_id = identifier(path.stem)
            self[task_id]  # No symlink or directory masquerades as an entry.
            yield task_id

    def __len__(self):
        return sum(1 for _ in self)


def paths(config):
    value=setting(config)
    if value is None:return {}
    folder=Path(value['directory'])
    if any(p.is_symlink() for p in (folder,*folder.parents)):
        raise ValueError('PROTECTED_RESEARCH_CATALOG_REQUIRED')
    info=folder.stat()
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid!=0
            or info.st_gid!=config['controller_gid'] or info.st_mode & 0o027):
        raise ValueError('PROTECTED_RESEARCH_CATALOG_REQUIRED')
    return _CatalogPaths(folder)


def validate_entry(entry,task_id):
    from orchestrator.hosted_campaign_task import task_contract
    identifier(task_id)
    if (not isinstance(entry,dict) or set(entry)!={'schema','source','source_root','request',
            'eligibility','predecessors','change_request'} or entry['schema']!=SCHEMA):
        raise ValueError('INSTALLED_RESEARCH_CATALOG_ENTRY_REQUIRED')
    _source({key:entry[key] for key in ('source','source_root')})
    request=entry['request']
    if (not isinstance(request,dict) or set(request)!=
            {'task','evidence_file','evidence_sha256','day','initiator'}):
        raise ValueError('INSTALLED_RESEARCH_REQUEST_REQUIRED')
    task_contract(request['task'])
    if request['task'].get('task_id')!=task_id:
        raise ValueError('CATALOG_TASK_IDENTITY_MISMATCH')
    reference=entry['eligibility']
    if (not isinstance(reference,dict) or set(reference)!={'path','sha256'}
            or not isinstance(reference['path'],str) or not Path(reference['path']).is_absolute()
            or '..' in Path(reference['path']).parts or not _pin(reference['sha256'],64)):
        raise ValueError('CATALOG_ELIGIBILITY_REFERENCE_REQUIRED')
    change=entry['change_request']
    if (not isinstance(change,dict) or set(change)!={'request_id','applied_event'}
            or any(not _pin(value,64) for value in change.values())):
        raise ValueError('CATALOG_CHANGE_REFERENCE_REQUIRED')
    predecessors=entry['predecessors']
    if not isinstance(predecessors,list) or len(predecessors)>8:
        raise ValueError('BOUNDED_RESEARCH_PREDECESSORS_REQUIRED')
    seen=set()
    for prior in predecessors:
        if (not isinstance(prior,dict) or set(prior)!={'task','source','disposition_sha256','requires'}
                or not _pin(prior['task'],64) or not _pin(prior['source'],40)
                or not _pin(prior['disposition_sha256'],64)
                or prior['requires'] not in ('DISPOSITION_RECORDED','APPROVED_PROPOSAL_ONLY')
                or prior['task'] in seen):
            raise ValueError('EXACT_RESEARCH_PREDECESSOR_REQUIRED')
        seen.add(prior['task'])
    return entry


def selection(config,task_id=None):
    """Resolve one immutable entry, retaining the legacy request's old identity."""
    if task_id is not None:identifier(task_id)
    legacy=config.get('research_request',{})
    legacy_id=legacy.get('task',{}).get('task_id')
    catalog=setting(config)
    if task_id is None or task_id==legacy_id:
        source=catalog['legacy_source'] if catalog else {}
        return {**config,**source},None
    available=paths(config)
    if task_id not in available:raise ValueError('UNKNOWN_INSTALLED_RESEARCH_TASK')
    from orchestrator.handover_runtime import configuration
    entry=validate_entry(configuration(available[task_id],private_gid=config['controller_gid']),task_id)
    return {**config,'research_request':entry['request'],
        'source':entry['source'],'source_root':entry['source_root']},entry


def verify_eligibility(config,entry):
    """Verify the saved judgment and opposing review against broker originals."""
    from orchestrator.research_task_authority import verify_eligibility as verify
    return verify(config,entry)


def linked_change(config,entry):
    """Use the original event chain; later criticism remains a live gate."""
    from orchestrator.change_requests import load
    if not config.get('change_request_store'):raise ValueError('RESEARCH_CHANGE_STORE_REQUIRED')
    reference=entry['change_request']
    history=load(Path(config['change_request_store'])/reference['request_id'])
    applied={event['identity']:event for event in history['events'] if event['event']=='APPLIED'}
    superseded={old for event in applied.values() for old in event['payload'].get('supersedes_applied_events',[])}
    if reference['applied_event'] not in applied or reference['applied_event'] in superseded:
        raise ValueError('CURRENT_RESEARCH_CHANGE_VERSION_REQUIRED')
    outcomes={}
    for event in history['events']:
        if event['event']=='REVIEW':
            identity=event['payload']['applied_event']
            if outcomes.get(identity)!='REQUEST_CHANGES':outcomes[identity]=event['payload']['verdict']
    active=set(applied)-superseded
    if any(outcomes.get(identity)=='REQUEST_CHANGES' for identity in active):
        raise ValueError('RESEARCH_CHANGE_REQUIRES_CORRECTION')
    if any(outcomes.get(identity)!='APPROVE' for identity in active):
        raise ValueError('RESEARCH_CHANGE_REVIEW_PENDING')
    return history


def eligibility(config,entry):
    from orchestrator.change_requests import actor
    linked_change(config,entry)
    result=verify_eligibility(config,entry)
    if (not isinstance(result,dict) or set(result)!={'status','entry_sha256','reference_sha256',
            'source','actor','review_status','rationale'}
            or result['status'] not in ('ELIGIBLE','DEFERRED')
            or result['entry_sha256']!=digest(entry)
            or result['reference_sha256']!=entry['eligibility']['sha256']
            or result['source']!=entry['source']
            or result['review_status'] not in ('APPROVE','PENDING','REQUEST_CHANGES')
            or not isinstance(result['rationale'],str) or not result['rationale'].strip()):
        raise ValueError('EXACT_RESEARCH_ELIGIBILITY_REQUIRED')
    actor(result['actor'])
    if result['status']!='ELIGIBLE':raise ValueError('RESEARCH_ELIGIBILITY_DEFERRED')
    if result['review_status']!='APPROVE':raise ValueError('RESEARCH_ELIGIBILITY_REVIEW_REQUIRED')
    return result

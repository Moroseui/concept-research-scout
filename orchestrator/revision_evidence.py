"""Bound development metadata supplement through the existing private view route.

No imaging, new selection, credential, network, registry rewrite or scanner exemption.
The component independently authenticates the reviewed manifest and file roots.
"""
import hashlib
import json
from pathlib import Path


def append(descriptors, files, manifest, folder, cases):
    from orchestrator import scientific_intake as intake, manual_context as mc
    from orchestrator.git_publication import scan
    if (manifest['schema'] != 'item4-revision-evidence/v1' or manifest['metadata_only'] is not True
            or manifest['cohort_sha256'] != intake.COHORT_SHA256):
        raise ValueError('REVISION_EVIDENCE_SCOPE')
    manifest_pin=hashlib.sha256((json.dumps(manifest,indent=2)+'\n').encode()).hexdigest()
    descriptors=list(descriptors);files=list(files)
    seen={d['path'] for d,_ in files}
    names=set()
    for row in manifest['files']:
        name=row['name']
        if not isinstance(name,str) or Path(name).name!=name or name in names:
            raise ValueError('REVISION_EVIDENCE_NAME')
        names.add(name)
        path=Path(folder)/name
        if path.is_symlink() or not path.is_file():raise ValueError('REVISION_EVIDENCE_FILE')
        raw=path.read_bytes();pin=hashlib.sha256(raw).hexdigest()
        if pin!=row['sha256'] or len(raw)!=row['bytes']:raise ValueError('REVISION_EVIDENCE_CHANGED')
        checks=intake.scan(raw,cases,kind=row['kind'],reason=row['reason'])
        if checks!=row['checks']:raise ValueError('REVISION_EVIDENCE_SCAN_CHANGED')
        if row['kind']!='per_patient':scan('context/revision-evidence.txt',raw)
        descriptor={'id':'revision-evidence-'+name,'path':'evidence/'+pin+'-revision-'+name,
            'sha256':pin,'bytes':len(raw),'characters':len(raw.decode()),'checks':checks,
            'supplement_manifest_sha256':manifest_pin,'origin':row['origin'],
            'delivery':'Complete preserved original; metadata only. Scientific acceptance and provider readiness are not implied.',
            'per_patient_reason':row['reason']}
        if descriptor['path'] in seen:raise ValueError('REVISION_EVIDENCE_DUPLICATE')
        seen.add(descriptor['path']);descriptors.append(descriptor);files.append((descriptor,raw))
        if name.endswith('.json'):
            # Same bounded JSON pager, then the mandatory private scanner (the
            # public scanner correctly refuses identifiers in these originals).
            pretty=mc._pageable_json(raw)
            intake.scan(pretty,cases,kind=row['kind'],reason=row['reason'])
            copy={'id':descriptor['id']+'-readable-json','path':descriptor['path']+'-readable.json',
                'sha256':hashlib.sha256(pretty).hexdigest(),'bytes':len(pretty),'characters':len(pretty.decode()),
                'original_path':descriptor['path'],'original_sha256':pin,'delivery':mc.JSON_READING}
            descriptor['readable_json']=copy
            files.append((copy,pretty))
    return descriptors,files

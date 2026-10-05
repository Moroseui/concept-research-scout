"""Sprint9 smoke package assembly; no provider calls and no data inside model inputs."""
import json
from pathlib import Path
from orchestrator import private_records
from orchestrator.manual_executor import digest,inventory,read
from orchestrator.manual_driver import write_once
from orchestrator.modal_budget import estimate
from orchestrator.modal_executor import canonical,verify_package
from orchestrator.sprint9_modal_validation import BASELINE,ABSOLUTE_TOLERANCE,BASELINE_TABLE_SHA256

SCIENCE=Path('experiments/sprint9_modal')


def source_files(root):
    return {name:(Path(root)/SCIENCE/name).read_bytes() for name in ['run.py','worker.py','science.py']}


def code_identity(root):
    return digest(canonical({name:digest(raw) for name,raw in source_files(root).items()}))


def output_names(smoke):
    names=['execution.json','summary.json','console.log','started.json',
           'folds/unet_U_base_s101_f0_t1.csv','uscores/U_base_s101_f0_t1.npz','ckpt/curves_U_base_s101_f0_t1.json']
    for case in smoke['partitions']['held']:
        for recipe in BASELINE:names.append(f'masks/{recipe}__s101_t1__{case}.npz')
    return sorted(names)


def emit(root,folder,config,spec,review):
    folder=Path(folder)
    if folder.exists():raise ValueError('MODAL_PACKAGE_ALREADY_PREPARED_RECONCILE')
    spec,review=Path(spec),Path(review)
    runtime=config['modal'];smoke=read(config['smoke_path'])
    if digest(canonical(smoke))!=config['smoke_sha256']:raise ValueError('SMOKE_CONFIG_CHANGED')
    binding={'run_id':config['run_id'],'source':config['source'],'purpose':'M3_SMOKE',
        'runtime_sha256':digest(canonical(runtime)),'spec_sha256':digest(spec.read_bytes()),'review_sha256':digest(review.read_bytes()),
        'code_sha256':code_identity(root),'resources':config['resources'],'overhead_micro_usd':config['overhead_micro_usd'],
        'cost':estimate(config['resources'],config['overhead_micro_usd']),
        'input_contract':runtime['input_contract'],'input_contract_sha256':digest(canonical(runtime['input_contract'])),
        'image_id':runtime['image_id'],'data_volume_id':runtime['data_volume_id'],'package_volume_id':runtime['package_volume_id'],'wheel_volume_id':runtime['wheel_volume_id'],
        'outputs':output_names(smoke)}
    if binding['code_sha256']!=config['notebook_code_sha256']:raise ValueError('MODAL_REVIEWED_CODE_CHANGED')
    private_records.mkdir(folder)
    for name,raw in source_files(root).items():write_once(folder/name,raw)
    for name in ['science-provenance.json','requirements.lock','wheels.json']:
        write_once(folder/name,(Path(root)/SCIENCE/name).read_bytes())
    write_once(folder/'smoke.json',canonical(smoke))
    write_once(folder/'SPEC.md',spec.read_bytes());write_once(folder/'review.json',review.read_bytes())
    manifest={'schema':'modal-run/v1','binding':binding,'files':inventory(folder)}
    write_once(folder/'manifest.json',canonical(manifest));verify_package(folder,binding)
    return manifest


def safe_manifest(manifest):
    """Explicit controller view. Original private membership stays operator-only.

    Preserve its hash; every selected field is read from the exact original.
    This is not a replacement approval or a claim the reviewer saw private IDs.
    """
    binding=manifest['binding'];safe={k:v for k,v in binding.items() if k!='outputs'}
    safe['outputs']={'count':len(binding['outputs']),'list_sha256':digest(canonical(binding['outputs']))}
    return {'kind':'controller-selected manifest view; private output membership omitted',
            'original_manifest_sha256':digest(canonical(manifest)),'binding':safe,'files':manifest['files']}


def tolerance():
    return {'baseline_table_sha256':BASELINE_TABLE_SHA256,'baseline_mean_dice':BASELINE,
            'absolute_mean_dice_tolerance':ABSOLUTE_TOLERANCE,'no_adjustment_after_run':True}

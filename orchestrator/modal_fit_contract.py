"""Shared fit identity check; worker and controller use the same contract."""
import re
from orchestrator.modal_fit_progress import identifier, validate_binding

def progress_scope(binding):
    value = binding.get('progress')
    if not isinstance(value, dict) or set(value) != {'volume_id','volume_name','fit_id','fit_binding'}:
        raise ValueError('MODAL_FIT_PROGRESS_SCOPE')
    identifier(value['fit_id']);identifier(value['volume_name'])
    if not isinstance(value['volume_id'],str) or not re.fullmatch('vo-[a-zA-Z0-9]+',value['volume_id']):
        raise ValueError('MODAL_FIT_VOLUME_ID')
    fit = validate_binding(value['fit_binding'])
    if not isinstance(fit,dict) or fit.get('run_id') != binding['run_id'] or value['fit_id'] != binding['experiment']['fit_id']:
        raise ValueError('MODAL_FIT_RUN_BINDING')
    if any(fit[k] != binding.get(k) for k in ('spec_sha256','code_sha256')):
        raise ValueError('MODAL_FIT_SCIENTIFIC_BINDING_CHANGED')
    return value



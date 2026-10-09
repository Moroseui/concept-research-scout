"""Operator's $150 allowance for the frozen base-smoke milestone only.

Other fits retain their earlier cap. No charge, reservation, terminal proof,
scientific approval or full-training gate is altered here.
"""
from pathlib import Path
import hashlib

OPERATOR_SHA='8c3907386aa0f19864540815ea04f87c715b5bf21565aff8a16193373146719a'
DOCUMENT='docs/ITEM4_STAGE1_CAP_OPERATOR_DECISION_20261009.txt'
CAP=150_000_000
PREVIOUS_CAP=75_000_000
RUN='experiment-a74959ac4546a982af4ae137'
FITS=frozenset({'benchmark-A100-80GB','benchmark-H100','benchmark-B200','smoke-A1_repeat','smoke-A1_repeat2'})
PINS={'source': '8e0423395d650bf757780c8c0877d7801815514a', 'image_id': 'im-Yhslx2XCmdhO6U5ToJJi0C', 'spec_sha256': 'a442fdc8ca28169ca3ff6d7d16b1bee14b151b5b4ff13b5feeda02bd913aa05d', 'execution_plan_sha256': '6710273c50f343b9d4b96db07560ca35566e856be02490d39ab2180bc5b81acb', 'review_sha256': 'bd6252dee2df5f0323fdc285731e3309e36d3bc95068c09502a39232f415bd77'}


def limit(binding):
    scope=binding.get('experiment',{})
    if binding.get('run_id')!=RUN or scope.get('stage')!='SMOKE':return PREVIOUS_CAP
    if (scope.get('fit_id') not in FITS or
            any(binding.get(k)!=v for k,v in PINS.items()) or
            binding.get('execution',{}).get('module_sha256')!='3925313395199992195412e5db908e764e8215df52f59c408ba27619653993d8'):
        raise ValueError('ITEM4_STAGE1_MILESTONE_SCOPE')
    raw=(Path(__file__).resolve().parents[1]/DOCUMENT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=OPERATOR_SHA:
        raise ValueError('ITEM4_STAGE1_OPERATOR_CHANGED')
    return CAP

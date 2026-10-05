"""Fixed, native-authenticated linked evidence for fresh investigator inputs.

Two administrative history slots are projected; an explicitly bound v2 plan
also selects the original scientific packet fields. Scientific bodies stay literal. Native regeneration re-authenticates the immutable original; the saved
packet additionally binds every prefix to its independently reviewed source
application. This module neither qualifies that application nor grants science.
"""
from copy import deepcopy
import ast
import hashlib
from pathlib import Path

from orchestrator import reviewed_history as history
from orchestrator.disposition_context import (PREFIX_PATH, CHARTER_PATH, _at, _put, _chain,
    _sha, LINKED_PACKET_VIEW, prefix_path)
from orchestrator.disposition_successors import result_reference, LINKED_REFERENCE

SELECTION = 'reviewed-linked-input-selection/v1'
SCIENTIFIC_SELECTION = 'reviewed-linked-scientific-input-selection/v2'
PRESENTATION = 'authenticated-linked-disposition-input/v1'
PROOF_VIEW = 'authenticated-linked-disposition-proof-view/v1'


PACKET_NOTICE = ('Selected historical task identity only. The full original packet '
                  'is retained and authenticated through the immutable linked-result '
                  'reference; it is not reproduced here or claimed model-inspected. '
                  'Scientific input context, original author/reviewer outputs and '
                  'the complete disposition remain literal. This view grants no '
                  'acceptance, adoption, execution or relief from unresolved criticism.')


def presentation_notice(plan):
    scope = ('The two exactly reviewed administrative history prefixes and the '
             'exact historical packet selection are referenced.'
             if plan['schema'] == SCIENTIFIC_SELECTION else
             'Only the two exactly reviewed administrative history prefixes are referenced.')
    return ('Native-authenticated selected proof, not the original proof bytes. ' + scope +
            ' Scientific bodies, criticism, authority and active applications remain literal. '
            'The native original is immutable; reference presence never means model inspection or acceptance.')


def enabled(root, source):
    from orchestrator.remote_supervisor import checked_source
    from orchestrator.scientific_authority import read
    root = checked_source(root, source)
    tree = ast.parse(read(Path(root) / 'orchestrator/hosted_context.py'))
    name = 'LINKED_DISPOSITION_INPUT_VERSION'
    stores = [n for n in ast.walk(tree) if isinstance(n, ast.Name)
              and n.id == name and isinstance(n.ctx, (ast.Store, ast.Del))]
    definitions = [n for n in tree.body if isinstance(n, ast.Assign)
        and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
        and n.targets[0].id == name]
    if not stores:
        return False
    if (len(stores) != 1 or len(definitions) != 1
            or not isinstance(definitions[0].value, ast.Constant)
            or type(definitions[0].value.value) is not int or definitions[0].value.value != 1):
        raise ValueError('LINKED_INPUT_SOURCE_PROFILE_REQUIRED')
    return True


def _selection(plan, reference):
    keys = {'schema', 'origin_task', 'original_value_sha256', 'boundaries'}
    if isinstance(plan, dict) and plan.get('schema') == SCIENTIFIC_SELECTION:
        keys.add('packet_selection')
    if (not isinstance(plan, dict) or set(plan) != keys
            or plan['schema'] not in (SELECTION, SCIENTIFIC_SELECTION)
            or plan['origin_task'] != reference['origin_task']
            or plan['original_value_sha256'] != reference['original_value_sha256']
            or not isinstance(plan['boundaries'], dict)
            or set(plan['boundaries']) != {'historical_authority', 'reviewed_repair'}):
        raise ValueError('LINKED_INPUT_EXACT_SELECTION_REQUIRED')
    if plan['schema'] == SCIENTIFIC_SELECTION:
        selected = plan['packet_selection']
        if not isinstance(selected, dict) or set(selected) != {
                'original_packet_sha256', 'scientific_context_sha256',
                'campaign_task_sha256', 'retained_proof_sha256'}:
            raise ValueError('LINKED_INPUT_PACKET_SELECTION_REQUIRED')
        from orchestrator.disposition_context import _pin
        for value in selected.values():
            _pin(value)
    return plan['boundaries']


def _packet_view(proof, original_proof, plan):
    """Keep outputs/criticism and exact science context; reference old mechanics.

    This is a closed semantic selection requiring review of the exact binding.
    No summary or new scientific conclusion is generated. All native originals
    have already been authenticated/scanned by result_reference.
    """
    selected = plan['packet_selection']
    packet = original_proof['packet']
    science = _at(original_proof, CHARTER_PATH)
    task = packet['campaign_task']
    if ({'original_packet_sha256': _sha(packet),
         'scientific_context_sha256': _sha(science),
         'campaign_task_sha256': _sha(task),
         'retained_proof_sha256': _sha({k:v for k,v in original_proof.items()
             if k not in ('packet', 'schema')})} != selected):
        raise ValueError('LINKED_INPUT_PACKET_ORIGINAL_CHANGED')
    historical = _at(proof, PREFIX_PATH)
    proof['packet'] = {
        'schema': LINKED_PACKET_VIEW,
        'original_packet_sha256': selected['original_packet_sha256'],
        'campaign_task': deepcopy(task),
        'notice': PACKET_NOTICE}
    proof['scientific_input_context'] = deepcopy(science)
    proof['historical_authority'] = historical


def _check_packet_view(proof, plan):
    selected = plan.get('packet_selection')
    if plan['schema'] != SCIENTIFIC_SELECTION:
        if (proof.get('packet', {}).get('schema') == LINKED_PACKET_VIEW
                or 'scientific_input_context' in proof or 'historical_authority' in proof):
            raise ValueError('LINKED_INPUT_PACKET_SELECTION_REQUIRED')
        return
    packet = proof.get('packet', {})
    if (not isinstance(packet, dict) or set(packet) != {
            'schema', 'original_packet_sha256', 'campaign_task', 'notice'}
            or packet['schema'] != LINKED_PACKET_VIEW
            or packet['notice'] != PACKET_NOTICE
            or packet['original_packet_sha256'] != selected['original_packet_sha256']
            or _sha(packet['campaign_task']) != selected['campaign_task_sha256']
            or _sha(proof.get('scientific_input_context')) != selected['scientific_context_sha256']
            or _sha({k:v for k,v in proof.items() if k not in (
                'packet', 'schema', 'scientific_input_context', 'historical_authority')}) != selected['retained_proof_sha256']):
        raise ValueError('LINKED_INPUT_PACKET_VIEW_CHANGED')


def project(value, plan, application, source):
    """Call only after the native read_result; scan complete originals first."""
    if isinstance(plan, dict) and plan.get('schema') == CURRENT_REFERENCE_SELECTION:
        return reference_view(value, plan, application, source)
    reference = result_reference(value)
    bounds = _selection(plan, reference)
    result = deepcopy(value)
    proof = result['originals']
    old = _at(proof, PREFIX_PATH)
    _put(proof, PREFIX_PATH, history.capture_linked_history(
        old, bounds['historical_authority'], application))
    result['reviewed_repair'] = history.capture_linked_history(
        result['reviewed_repair'], bounds['reviewed_repair'], application)
    if plan['schema'] == SCIENTIFIC_SELECTION:
        _packet_view(proof, value['originals'], plan)
    proof['schema'] = PROOF_VIEW
    result['input_presentation'] = {'schema': PRESENTATION, 'source': source,
        'binding_application': application, 'original_reference': reference,
        'notice': presentation_notice(plan)}
    validate(result, plan, application, source)
    return result


def validate(value, plan, application, source):
    """Validate saved bindings; admission must also run native regeneration."""
    marker = value.get('input_presentation')
    if (not isinstance(marker, dict) or set(marker) != {
            'schema', 'source', 'binding_application', 'original_reference', 'notice'}
            or marker['schema'] != PRESENTATION or marker['source'] != source
            or marker['binding_application'] != application
            or value['originals'].get('schema') != PROOF_VIEW):
        raise ValueError('LINKED_INPUT_PRESENTATION_CHANGED')
    reference = marker['original_reference']
    bounds = _selection(plan, reference)
    if marker['notice'] != presentation_notice(plan):
        raise ValueError('LINKED_INPUT_PRESENTATION_NOTICE_CHANGED')
    _check_packet_view(value['originals'], plan)
    if (_sha(value['result']) != value['result_sha256']
            or reference['origin_task'] != value['originals']['origin_task']
            or reference['result_sha256'] != value['result_sha256']
            or reference['original_proof_sha256'] != value['result']['original_proof_sha256']):
        raise ValueError('LINKED_INPUT_RESULT_BINDING_CHANGED')
    for name, state in [('historical_authority', _at(value['originals'], prefix_path(value['originals']))),
                        ('reviewed_repair', value['reviewed_repair'])]:
        _chain(state)
        if (state.get('schema') != history.HISTORICAL_SCHEMA
                or state['boundary'] != bounds[name]
                or state['binding_application'] != application):
            raise ValueError('LINKED_INPUT_HISTORY_BOUNDARY_CHANGED')
    return bounds


def for_template(config, value):
    if not enabled(config['source_root'], config['source']):
        return value
    from orchestrator.investigator_wakes import setting
    from orchestrator.research_catalog import linked_change
    reference = setting(config)['template']['change_request']
    state = linked_change(config, {'change_request': reference})
    app = next(e for e in state['events'] if e['identity'] == reference['applied_event'])
    binding = app['payload']['result_binding']
    if binding.get('source') != config['source']:
        raise ValueError('LINKED_INPUT_SOURCE_APPLICATION_REQUIRED')
    plan = binding.get('linked_disposition_input')
    if plan is None:
        return value  # no implicit selection for an unbound input
    return project(value, plan, app['identity'], config['source'])


def prepare_primary_for_packet(state, evidence, source, application):
    """Compact the authenticated primary chain before assembling a bounded packet.

    The complete native chain remains validated and preserved. This uses only the
    existing exact prefix binding, retaining applications active in either fixed
    historical slot; it does not relax any packet/context/storage limit.
    """
    from orchestrator.disposition_context import _dispositions, _active, WAKE
    if not isinstance(evidence, dict) or evidence.get('investigator_wake', {}).get('schema') != WAKE:
        return deepcopy(state)
    protected = set()
    found = _dispositions(evidence, source)
    if any(evidence['verified_events'][index]['linked_disposition'].get(
            'input_presentation', {}).get('schema') == CURRENT_PRESENTATION for index, _ in found):
        # The following capture_current_history builds an authenticated compact
        # snapshot. Do not reinterpret native reference descriptors as full chains.
        return deepcopy(state)
    for index, proof in found:
        linked = evidence['verified_events'][index]['linked_disposition']
        originals = [linked['reviewed_repair']]
        try:
            originals.append(_at(proof, prefix_path(proof)))
        except KeyError:
            pass
        for old in originals:
            if old['request']['identity'] == state['request']['identity']:
                protected.update(_active(old))
    return history.capture(state, application, protected=protected)


CURRENT_REFERENCE_SELECTION = 'reviewed-current-linked-input/v3'
CURRENT_PRESENTATION = 'authenticated-linked-disposition-reference-input/v2'
CURRENT_PROOF = 'authenticated-linked-disposition-reference-proof/v2'
NATIVE_PREFIX_REFERENCE = 'native-change-prefix-reference/v1'
CURRENT_NOTICE = ('The exact scientific context, prior task, original author/reviewer outputs and complete '
    'disposition remain literal. Full historical packet and native history are authenticated originals '
    'available through scientific evidence retrieval. This reference does not settle any finding; current '
    'authority, active applications, criticism and conditions must be captured separately before admission.')


def reference_plan(plan):
    if (not isinstance(plan, dict) or plan != {
            'schema': CURRENT_REFERENCE_SELECTION,
            'scope': 'native-originals-with-literal-scientific-context',
            'qualification': 'REQUIRES_INDEPENDENT_REVIEW_OF_THIS_EXACT_APPLICATION',
            'require_current_history': True}):
        raise ValueError('CURRENT_LINKED_REVIEWED_PLAN_REQUIRED')
    return plan


def reference_view(value, plan, application, source):
    """Compact before intake storage, only after the native original reader.

    This is a deterministic source-reviewed rule, not a per-report trimming
    list. A new result uses the same rule and its own immutable native reference.
    This function alone cannot authenticate a caller-supplied original or grant
    admission; authenticate_reference_view and current-history capture must run
    at the consuming controller/protected paths.
    """
    reference_plan(plan)
    from orchestrator.disposition_context import _pin, charter_path
    _pin(source, 40); _pin(application)
    reference = result_reference(value)
    result = deepcopy(value)
    proof = result['originals']
    original_proof = value['originals']
    # Only the already-supported native proof layout is eligible. Unknown layouts
    # refuse rather than guessing where their scientific context lives.
    try:
        science = _at(original_proof, charter_path(original_proof))
        original_packet = original_proof['packet']
        task = original_packet['campaign_task']
        historical = _at(original_proof, prefix_path(original_proof))
        historic_bound = history.boundary(historical)
        repair_bound = history.boundary(value['reviewed_repair'])
    except (KeyError, TypeError, AttributeError):
        raise ValueError('CURRENT_LINKED_NATIVE_PROOF_LAYOUT_REQUIRED') from None
    proof['schema'] = CURRENT_PROOF
    proof['packet'] = {'schema': LINKED_PACKET_VIEW,
        'original_packet_sha256': _sha(original_packet),
        'campaign_task': deepcopy(task), 'notice': CURRENT_NOTICE}
    proof['scientific_input_context'] = deepcopy(science)
    proof['historical_authority'] = {**historic_bound, 'schema': NATIVE_PREFIX_REFERENCE,
        'native_boundary_schema': historic_bound['schema']}
    result['reviewed_repair'] = {**repair_bound, 'schema': NATIVE_PREFIX_REFERENCE, 'native_boundary_schema': repair_bound['schema']}
    result['input_presentation'] = {'schema': CURRENT_PRESENTATION, 'source': source,
        'binding_application': application, 'original_reference': reference,
        'notice': CURRENT_NOTICE}
    check_reference_view(result, source=source, application=application)
    return result


def check_reference_view(value, *, source, application):
    """Structural check only; original authentication is a separate native read."""
    from orchestrator.disposition_context import _pin
    try:
        marker = value['input_presentation']; proof = value['originals']
        if (set(value) != {'result','result_sha256','originals','reviewed_repair','scope','input_presentation'}
                or set(marker) != {'schema','source','binding_application','original_reference','notice'}
                or marker['schema'] != CURRENT_PRESENTATION or marker['source'] != source
                or marker['binding_application'] != application or marker['notice'] != CURRENT_NOTICE
                or proof['schema'] != CURRENT_PROOF
                or proof['packet']['schema'] != LINKED_PACKET_VIEW
                or proof['packet']['notice'] != CURRENT_NOTICE):
            raise ValueError('CURRENT_LINKED_REFERENCE_CHANGED')
        _pin(source,40); _pin(application)
        ref = marker['original_reference']
        if (ref['schema'] != LINKED_REFERENCE
                or proof['origin_task'] != ref['origin_task']
                or value['result_sha256'] != ref['result_sha256']
                or _sha(value['result']) != value['result_sha256']
                or value['result']['original_proof_sha256'] != ref['original_proof_sha256']):
            raise ValueError('CURRENT_LINKED_RESULT_CHANGED')
        for bound in (proof['historical_authority'], value['reviewed_repair']):
            if (set(bound) != {'schema','native_boundary_schema','request_id','event_count',
                             'head_sha256','index_sha256'}
                    or bound['schema'] != NATIVE_PREFIX_REFERENCE
                    or bound['native_boundary_schema'] != history.BOUNDARY
                    or type(bound['event_count']) is not int or bound['event_count'] < 1):
                raise ValueError('CURRENT_LINKED_PREFIX_CHANGED')
            for field in ('request_id','head_sha256','index_sha256'):
                _pin(bound[field])
        repair=value['reviewed_repair']
        if (repair['request_id'] != ref['repair_request']
                or repair['event_count'] != ref['repair_event_count']
                or repair['head_sha256'] != ref['repair_head_sha256']):
            raise ValueError('CURRENT_LINKED_REPAIR_CHANGED')
        return ref
    except (KeyError,TypeError,AttributeError):
        raise ValueError('CURRENT_LINKED_REFERENCE_CHANGED') from None


def authenticate_reference_view(config, value, *, source, application, plan, client):
    """Read the original through its existing native proof path; no model calls."""
    from orchestrator.disposition_successors import read_result_reference
    ref = check_reference_view(value, source=source, application=application)
    original = read_result_reference(config, ref, client)
    expected = reference_view(original, plan, application, source)
    if _sha(value) != _sha(expected):
        raise ValueError('CURRENT_LINKED_NATIVE_ORIGINAL_CHANGED')
    return original


def context_document_originals(science, origin_task):
    """Fixed historical document slots, never reviews, decisions or conditions.

    The caller supplies one already authenticated native predecessor context.
    These are exact text originals from that same capture, not fresh retrievals
    or scientific summaries. Unknown shapes and all other fields stay literal.
    """
    from orchestrator.scientific_evidence_access import pin
    pin(origin_task)
    if not isinstance(science, dict):
        return []
    reviewed = science.get('reviewed_scientific_context')
    if not isinstance(reviewed, dict) or not isinstance(reviewed.get('context'), dict):
        return []
    entries = reviewed['context'].get('entries')
    if not isinstance(entries, list):
        return []
    rows = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not isinstance(entry.get('evidence'), dict):
            continue
        for kind in ('interpretation', 'next_decision'):
            item = entry['evidence'].get(kind)
            if not isinstance(item, dict) or not isinstance(item.get('text'), str):
                continue
            text = item['text']
            if len(text) < 1024:
                continue
            raw = text.encode('utf-8')
            rows.append({'name': 'result/'+origin_task+'/context/'+str(index)+'/'+kind+'.original.txt',
                'path': ['reviewed_scientific_context','context','entries',index,'evidence',kind,'text'],
                'sha256': hashlib.sha256(raw).hexdigest(), 'utf8_bytes': len(raw),
                'characters': len(text), 'text': text})
    return rows


def context_document_presentation(science, origin_task):
    """Reference exact document bodies; keep every surrounding obligation literal.

    Full original context remains in the saved packet. Protected delivery must
    authenticate that packet and include these same original bodies in its
    task-bound reader before provider input composition. No condition is settled.
    """
    result = deepcopy(science)
    for row in context_document_originals(science, origin_task):
        parent = result
        for key in row['path'][:-1]:
            parent = parent[key]
        parent[row['path'][-1]] = {
            'schema': 'retrievable-predecessor-scientific-document/v1',
            'reader_name': row['name'], 'sha256': row['sha256'],
            'utf8_bytes': row['utf8_bytes'], 'characters': row['characters'],
            'meaning': 'Exact historical document from the same authenticated predecessor capture. '
                'Read it with scientific_evidence_read before relying on its claims or limitations. '
                'This reference is not inspection, scientific acceptance, a settled finding or new authority. '
                'Original reviews, consideration decisions and surrounding conditions remain literal.'}
    return result

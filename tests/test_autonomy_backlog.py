import pytest

from orchestrator import autonomy_backlog as backlog


RAW = (b'# Backlog\r\n\r\n1. Stock-take, analysis only.\r\n\r\n'
       b'2. Proposal after operator review.\r\n\r\n'
       b'3. CPU experiment, not approved yet.\r\n')
AUTHORITY = b'Operator exact decision, fixture only.'


def binding():
    parts = backlog.numbered_items(RAW)
    return {'schema': 'operator-backlog/v1', 'backlog_sha256': backlog.sha(RAW),
            'operator_sha256': backlog.sha(AUTHORITY), 'items': [
                {'number': n, 'sha256': parts[n][1],
                 'mode': 'analysis' if n < 3 else 'cpu',
                 'state': ['AUTHORIZED', 'WAIT_OPERATOR', 'NOT_AUTHORIZED'][n - 1],
                 'prerequisites': [] if n == 1 else [n - 1]}
                for n in range(1, 4)]}


def test_exact_operator_backlog_and_analysis_selection():
    value = backlog.load(RAW, binding(), AUTHORITY)
    item = backlog.require_item(value, 1, value.items[0].sha256, 'analysis')
    assert item.text == '1. Stock-take, analysis only.\r\n\r\n'


@pytest.mark.parametrize('number', [2, 3])
def test_completed_predecessor_cannot_approve_operator_held_item(number):
    value = backlog.load(RAW, binding(), AUTHORITY)
    item = value.items[number - 1]
    with pytest.raises(ValueError, match='^BACKLOG_ITEM_NOT_AUTHORIZED$'):
        backlog.require_item(value, number, item.sha256, item.mode, [1, 2])


@pytest.mark.parametrize('raw,authority', [(RAW + b'4. New item\n', AUTHORITY),
                                         (RAW, AUTHORITY + b' changed')])
def test_changed_document_or_authority_refuses(raw, authority):
    with pytest.raises(ValueError, match='^BACKLOG_AUTHORITY_CHANGED$'):
        backlog.load(raw, binding(), authority)


def test_unbound_or_duplicate_item_refuses():
    value = binding()
    value['items'].pop()
    with pytest.raises(ValueError, match='^BACKLOG_UNBOUND_ITEM$'):
        backlog.load(RAW, value, AUTHORITY)
    with pytest.raises(ValueError, match='^BACKLOG_DUPLICATE_ITEM$'):
        backlog.numbered_items(RAW + b'1. Duplicate\n')


def test_model_dictionary_is_not_verified_backlog():
    with pytest.raises(ValueError, match='^VERIFIED_BACKLOG_REQUIRED$'):
        backlog.require_item({'approved': True}, 1, 'a' * 64, 'analysis')


def test_exact_item_and_mode_required():
    value = backlog.load(RAW, binding(), AUTHORITY)
    with pytest.raises(ValueError, match='^NEXT_DECISION_BACKLOG_MISMATCH$'):
        backlog.require_item(value, 1, value.items[0].sha256, 'cpu')


def contract():
    return {'cohort_sha256': 'a' * 64, 'split_sha256': 'b' * 64,
            'feature_cache_sha256': 'c' * 64, 'files': {'outputs/summary.csv': 'd' * 64}}


def accepted():
    return {'status': 'ACCEPTED', 'validation_status': 'VALID',
            'review_verdict': 'APPROVE', 'contract': contract()}


def test_compatible_accepted_inputs_pass():
    assert backlog.compatible_inputs(contract(), accepted())


@pytest.mark.parametrize('status', ['DEFER', 'PROPOSAL_ONLY', 'VALIDATED', 'REGISTERED'])
def test_deferral_and_proposal_are_not_accepted_inputs(status):
    record = accepted()
    record['status'] = status
    with pytest.raises(ValueError, match='^VALIDATED_ACCEPTED_INPUT_REQUIRED$'):
        backlog.compatible_inputs(contract(), record)


@pytest.mark.parametrize('key', ['cohort_sha256', 'split_sha256', 'feature_cache_sha256'])
def test_each_identity_mismatch_refuses(key):
    wanted = contract()
    wanted[key] = 'e' * 64
    with pytest.raises(ValueError, match='^SUCCESSOR_INPUT_IDENTITY_MISMATCH:' + key + '$'):
        backlog.compatible_inputs(wanted, accepted())


@pytest.mark.parametrize('files', [{'outputs/summary.csv': 'e' * 64},
                                  {'missing.csv': 'd' * 64}, {'../outside': 'd' * 64}])
def test_missing_changed_or_unsafe_consumed_file_refuses(files):
    wanted = contract()
    wanted['files'] = files
    with pytest.raises(ValueError, match='^SUCCESSOR_INPUT_FILE_MISMATCH$'):
        backlog.compatible_inputs(wanted, accepted())


@pytest.mark.parametrize('field,value', [('validation_status', 'INVALID'), ('review_verdict', 'REVISE')])
def test_unvalidated_or_unapproved_result_refuses(field, value):
    record = accepted()
    record[field] = value
    with pytest.raises(ValueError, match='^VALIDATED_ACCEPTED_INPUT_REQUIRED$'):
        backlog.compatible_inputs(contract(), record)

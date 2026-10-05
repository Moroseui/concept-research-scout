"""The existing pure terminal report contract, shared by importer and pre-Write hook.

Formatting validation never rewrites a report, qualifies source, supplies evidence
or authorizes an operation. The original importer retains all later checks.
"""
import re
if __package__:
    from orchestrator.review_input_codec import parsed
else:
    from review_input_codec import parsed

PROFILE = 'operator-terminal-review/v1'
FINDINGS = {f'C{i:03d}' for i in range(1, 12)}
DISPOSITIONS = {'resolved', 'preserve', 'held-deployment', 'held-accounting',
                'held-science', 'deferred-nonblocking'}


def require(ok, reason):
    if not ok:
        raise ValueError('TERMINAL_REVIEW_' + reason)


def statement(report, *, profile=PROFILE, approval_required=True):
    # The reviewer writes this block inside its original Markdown report. A
    # driver's sidecar, renamed native receipt or arbitrary APPROVE substring
    # cannot stand in for it. Historical quoted negative verdicts remain intact.
    blocks = re.findall(r'^```terminal-review-verdict\n(.*?)^```[ \t]*$',
                        report.decode('utf-8'), re.M | re.S)
    require(len(blocks) == 1, 'ONE_INDEPENDENT_VERDICT_BLOCK_REQUIRED')
    headings = re.findall(r'^(?:## )?Final source/integration verdict: (APPROVE|REQUEST_CHANGES|IN_PROGRESS)$',
                          report.decode('utf-8'), re.M)
    require(len(headings) == 1 and (not approval_required or headings == ['APPROVE']),
            'FINAL_VERDICT_HEADING_REQUIRED')
    value = parsed(blocks[0].encode())
    require(isinstance(value, dict) and set(value) == {
        'schema', 'source', 'proposal_sha256', 'manifest_sha256', 'session_id',
        'scope', 'verdict', 'inspected', 'unavailable', 'unverified', 'findings',
        'resolution_of', 'remaining_gates'}, 'VERDICT_SCHEMA')
    require(value['schema'] == profile and value['scope'] == 'material-source-integration'
            and value['verdict'] == headings[0]
            and (not approval_required or value['verdict'] == 'APPROVE'),
            'FINAL_SOURCE_APPROVAL_REQUIRED')
    for key in ('inspected', 'unavailable', 'unverified'):
        require(isinstance(value[key], list) and all(isinstance(x, str) and x.strip()
                for x in value[key]), 'EXPLICIT_INSPECTION_SCOPE_REQUIRED')
    require(value['inspected'], 'EXPLICIT_INSPECTION_SCOPE_REQUIRED')
    findings = value['findings']
    require(isinstance(findings, dict) and FINDINGS <= set(findings)
            and all(isinstance(row, dict) and set(row) == {'disposition', 'reason'}
                    and row['disposition'] in DISPOSITIONS
                    and isinstance(row['reason'], str) and row['reason'].strip()
                    for row in findings.values()), 'ADVERSE_FINDINGS_DISPOSITION_REQUIRED')
    require(value['remaining_gates'] == ['held-deployment', 'accounting-halt',
            'retained-history-audit', 'conditional-activation', 'scientific-acceptance'],
            'DOWNSTREAM_GATES_MUST_REMAIN')
    if approval_required:
        require(findings['C006']['disposition'] == 'resolved'
                and findings['C007']['disposition'] == 'resolved', 'IMPORT_INTEGRATION_UNRESOLVED')
    return value


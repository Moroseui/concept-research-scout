"""Match exact retained-row encoding to the unchanged qualified producer.

All original gate, identity, set and row comparisons remain. This separate
reviewed function leaves the activated R45 authority and seal intact.
"""
from orchestrator.item4_validation_admission import (
    REVIEW_SHA,TERMINAL_ASSETS,TERMINAL_COMPUTE,ROOT,contract,scope,
    record_for,authority,require,sha)

def retained_terminal(accounts,binding):
    """Only exact validation jobs reuse exact prior proofs; all charges remain.

    Called after owner/seal replay inside the existing reservation transaction.
    The child has a read-only SQLite connection and imports the original reviewed
    releases in isolation. Matching every returned row to our locked snapshot
    rejects a stale proof; unknown/live/changed records retain normal refusals.
    """
    if binding.get('review_sha256')!=REVIEW_SHA:return set(),set()
    observed={r['id'] for table in ('autonomy_assets','autonomy_compute')
        for r in accounts.db.execute('SELECT id FROM '+table)}
    if not observed & (TERMINAL_ASSETS|TERMINAL_COMPUTE):return set(),set()
    import subprocess
    from orchestrator.modal_executor import canonical as row_canonical
    selected=contract();scope({'review_sha256':REVIEW_SHA,
        'validation_admission':record_for(selected,authority())},binding,bound=True)
    raw=subprocess.check_output(['/usr/bin/python3','-s','-B',
        str(ROOT/'tools/item4_validation_retained.py')])
    from orchestrator.review_contract import strict_json
    proof=strict_json(raw)
    require(set(proof)=={'schema','source_sha','source_asset','assets','compute'} and
        proof['schema']=='item4-retained-terminal-qualification/v1' and
        proof['source_sha']=='28726e3d5cdf32f1d80c63187f5abd9146cbfcd0' and
        proof['source_asset']=='9878e7923ea81dceefce162166a113aa7d0a53dd65c4199a42b4276fe952d365' and
        set(proof['assets'])==TERMINAL_ASSETS and set(proof['compute'])==TERMINAL_COMPUTE,'TERMINAL_SCOPE')
    for kind,table in [('assets','autonomy_assets'),('compute','autonomy_compute')]:
        for ident,pin in proof[kind].items():
            row=accounts.db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone()
            require(row is not None and sha(row_canonical(dict(row)))==pin,'TERMINAL_ROW_CHANGED')
    return set(proof['assets']),set(proof['compute'])

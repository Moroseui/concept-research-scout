"""Authenticate the exact accepted Idea2 lane before a new CPU dispatch.

No stage, call, grant or account is modified. The specification-only grant never
becomes an execution grant; the reviewed native CPU adapter supplies that scope.
"""
from pathlib import Path
import json
from orchestrator import idea2_cpu_contract as contract
DOCUMENT = 'docs/IDEA2_CPU_ACCEPTED_LANE_PRIVATE.json'
DOCUMENT_SHA = '1e0c518ddf790e6f23f83d2c9bdfa68cbd4ecef27087e371c044868d31a8bbe1'
CONFIG_SHA = '21a05054f70255b2f0b2eb5329818dda878205135d644f171af45b928f762e82'
AUTHOR_CALL = 'c7bccc44e04c803a8de45a42a37a5baf4f3f07baf98850fed25e8595b3b68b99'
REVIEW_CALL = '920c06536c71fe4a72960698870b48b09bde0b6ae79e2c8daf378396776e5d4f'

def frozen(root):
 raw=(Path(root)/DOCUMENT).read_bytes()
 contract.require(contract.sha(raw)==DOCUMENT_SHA,'ACCEPTED_LANE_PROOF')
 return json.loads(raw)

def verify_snapshot(config_raw,state_row,account_row,calls,proof):
 contract.require(contract.sha(config_raw)==CONFIG_SHA==proof['config_sha256'],'ACCEPTED_LANE_CONFIG')
 config=json.loads(config_raw);state=json.loads(state_row['payload'])
 contract.require(config['run_id']==contract.RUN and state['phase']=='COMMIT_SPEC'
                  and not state.get('pending'),'ACCEPTED_LANE_PHASE')
 contract.require(state_row==proof['state_row'] and account_row==proof['account_row']
                  and calls==proof['calls'],'ACCEPTED_LANE_HISTORY')
 contract.require(len(calls)==15 and calls[-2]['id']==AUTHOR_CALL
                  and calls[-1]['id']==REVIEW_CALL
                  and calls[-2]['status']==calls[-1]['status']=='COMPLETE','ACCEPTED_LANE_CALLS')
 contract.require(state['program_result']['program_sha256']==contract.PROGRAM
                  and state['program_result']['synthetic_status']=='PASS'
                  and state['reviewed_execution']['sha256']==contract.APPROVAL,'ACCEPTED_LANE_SCIENCE')
 return {'run_id':contract.RUN,'scientific_calls_preserved':len(calls),
         'program_sha256':contract.PROGRAM,'review_call':REVIEW_CALL,
         'new_calls':0,'preparation_grant_changed':False}


def read_accepted_lane(path, root):
    """Read a consistent accepted-lane snapshot without initializing any store.

    This function does not use AnalysisDriver/ManualExecutor constructors: a
    missing ledger must refuse, never create a replacement empty database.
    The caller must hold the native one-use execution admission lock.
    """
    import sqlite3
    from orchestrator import private_records as pr
    path=Path(path)
    proof=frozen(root)
    config_raw=pr.check(path/'lane.json').read_bytes()
    ledger=pr.check(path/'jobs.sqlite')
    db=sqlite3.connect(ledger.as_uri()+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    try:
        db.execute('PRAGMA query_only=ON')
        db.execute('BEGIN')
        state=db.execute('SELECT * FROM manual_state WHERE id=1').fetchone()
        account=db.execute('SELECT * FROM manual_account WHERE id=1').fetchone()
        contract.require(state is not None and account is not None,'ACCEPTED_LANE_ROWS')
        calls=[dict(row)for row in db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
        result=verify_snapshot(config_raw,dict(state),dict(account),calls,proof)
        contract.require(not (path/'HALT').exists(),'ACCEPTED_LANE_HALT')
        return result
    finally:
        db.rollback();db.close()

from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
import pytest
from orchestrator.dispatch_limiter import admit,admit_server,GitLedger,initial
from test_dispatch_limiter import config,event,NOW
import subprocess


def server(i):
    return {'turn_id':format(i,'064x'),'attempt':'1','source':'b'*40,
            'branch':'astra/infrastructure-milestone-record','kind':'astra_turn'}


def test_shared_actions_server_ceiling_and_recovery(tmp_path):
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    ledger=GitLedger(tmp_path);ledger.cas(None,initial())
    c={**config(2),'server_semantics':'OPERATOR_AUTHORIZED_V1'}
    assert admit(ledger,c,event(1),NOW)['count']==1
    assert admit_server(ledger,c,server(1),NOW)['notification']=='N'
    assert admit_server(GitLedger(tmp_path),c,server(1),NOW)['duplicate_admission']
    assert admit(ledger,c,event(2),NOW)['count']==3
    assert admit_server(ledger,c,server(2),NOW)['notification']=='2N'
    assert admit_server(ledger,c,server(3),NOW+timedelta(days=1))['status']=='HALTED_OPERATOR_RESET_REQUIRED'
    with pytest.raises(ValueError,match='BINDING_CHANGED'):
        admit_server(ledger,c,{**server(1),'kind':'nightly_review'},NOW)
    with pytest.raises(ValueError,match='NOT_AUTHORIZED'):
        admit_server(ledger,config(2),server(9),NOW)


def test_concurrent_shared_admission(tmp_path):
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    GitLedger(tmp_path).cas(None,initial());c={**config(4),'server_semantics':'OPERATOR_AUTHORIZED_V1'}
    def run(i):
        store=GitLedger(tmp_path)
        return (admit_server(store,c,server(i),NOW,max_retries=40) if i%2 else admit(store,c,event(i),NOW,max_retries=40))
    with ThreadPoolExecutor(max_workers=8) as pool: rows=list(pool.map(run,range(1,25)))
    assert sum(r['status']=='ADMITTED' for r in rows)==8
    assert GitLedger(tmp_path).read()[1]['halted']


def test_selected_48_96_policy_in_private_fixture(tmp_path):
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    ledger=GitLedger(tmp_path);ledger.cas(None,initial())
    c={**config(48),'server_semantics':'OPERATOR_AUTHORIZED_V1'}
    notices=[]
    for i in range(1,97):
        result=admit_server(ledger,c,server(i),NOW)
        assert result['status']=='ADMITTED'
        if result['notification']:notices.append((i,result['notification']))
    assert notices==[(48,'N'),(96,'2N')]
    assert admit_server(ledger,c,server(97),NOW)['status']=='HALTED_OPERATOR_RESET_REQUIRED'
    assert admit_server(ledger,c,server(96),NOW)['duplicate_admission']
    assert admit_server(ledger,c,server(97),NOW+timedelta(days=1))['status']=='HALTED_OPERATOR_RESET_REQUIRED'

import tempfile,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pytest
from orchestrator.phone_notifications import Outbox,packet_checked,body_for,digest,REPO,config_checked

C={'repository':REPO,'repository_id':1,'app_id':2,'installation_id':3,'operator_id':4,'bot_id':5,'mode':'NOTIFICATION_SYNTHETIC_ONLY','private_key':'unused-fixture'}
def packet():return {'id':'synthetic-notice','source':'a'*40,'nonce':'b'*32,'expires':int(time.time())+3600,'summary':'Synthetic device acknowledgment only.'}


def test_concurrent_send_deduplicates_and_unknown_delivery_never_reposts():
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)/'state';p=packet();calls=[]
        def api(m,path,token,body):
            calls.append(body)
            return {'number':7,'user':{'id':5},'body':body['body'],'repository_url':'https://api.github.com/repos/'+REPO}
        Outbox(root)
        def send(_):
            try:return Outbox(root).send(p,C,'fixture',api)
            except ValueError:return None  # request may observe durable uncertain state
        with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(send,range(8)))
        assert len(calls)==1
        assert Outbox(root).send(p,C,'fixture',api)['duplicate']
        p['id']='lost-response'
        def fail(*a):raise TimeoutError('synthetic lost response')
        with pytest.raises(TimeoutError):Outbox(root).send(p,C,'fixture',fail)
        with pytest.raises(ValueError,match='UNCERTAIN'):Outbox(root).send(p,C,'fixture',api)
        assert len(calls)==1


def test_only_bound_unedited_operator_acknowledgments_are_accepted():
    with tempfile.TemporaryDirectory() as temp:
        out=Outbox(Path(temp)/'state');p=packet()
        out.send(p,C,'fixture',lambda *a:{'number':7,'user':{'id':5},'body':body_for(p),'repository_url':'https://api.github.com/repos/'+REPO})
        comment={'id':8,'user':{'id':4},'issue_url':'https://api.github.com/repos/'+REPO+'/issues/7','body':'ACK '+p['id']+' '+p['nonce']+' '+digest(p),'created_at':'now','updated_at':'now'}
        for bad in [{**comment,'user':{'id':99}},{**comment,'updated_at':'edited'},{**comment,'body':'APPROVE LAUNCH'},{**comment,'issue_url':'elsewhere'}]:
            with pytest.raises(ValueError):out.acknowledge(p['id'],8,C,'fixture',lambda *a:bad)
        first=out.acknowledge(p['id'],8,C,'fixture',lambda *a:comment)
        second=out.acknowledge(p['id'],8,C,'fixture',lambda *a:comment)
        assert not first['duplicate'] and second['duplicate'] and not first['operational_authority']
        with pytest.raises(ValueError,match='EXPIRY'):out.acknowledge(p['id'],8,C,'fixture',lambda *a:comment,now=p['expires']+1)


def test_unsafe_scope_and_content_refuse():
    with pytest.raises(ValueError):config_checked({**C,'mode':'OPERATIONAL_DECISIONS'})
    with pytest.raises(ValueError):packet_checked({**packet(),'source':'../main'})
    with pytest.raises(ValueError):packet_checked({**packet(),'summary':'sub-'+'stroke1234'})

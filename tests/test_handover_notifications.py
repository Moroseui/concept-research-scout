import json
from concurrent.futures import ThreadPoolExecutor
import pytest

import orchestrator.handover_notifications as module
from orchestrator.phone_notifications import Outbox,body_for


def setup(monkeypatch,fail=False):
    c={'repository':'Moroseui/concept-research-scout','repository_id':1,'app_id':2,
       'installation_id':3,'operator_id':4,'bot_id':5,'mode':'NOTIFICATION_ONLY','private_key':'unused-fixture'}
    monkeypatch.setattr(module,'protected_read',lambda path:json.dumps(c))
    monkeypatch.setattr(module,'jwt',lambda c:'fixture-only')
    monkeypatch.setattr(module,'session',lambda c,t:('fixture-only',{'app_id':2,'mode':c['mode']}))
    posts=[]
    def api(method,path,token,body):
        posts.append(body)
        if fail:raise OSError('Synthetic uncertain delivery')
        return {'user':{'id':5},'body':body['body'],'repository_url':'https://api.github.com/repos/Moroseui/concept-research-scout','number':7}
    class Transport(Outbox):
        def send(self,p,c,token):return super().send(p,c,token,call=api)
    monkeypatch.setattr(module,'Outbox',Transport)
    return posts


def test_information_only_delivery_is_shared_and_deduplicated(tmp_path,monkeypatch):
    posts=setup(monkeypatch);root=tmp_path/'notice'
    def send(_):return module.Notices(root,'fixed-config').send('same-event','a'*40,'Checked report available.')
    with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(send,range(3)))
    assert len(posts)==1 and all(r['status']=='SENT' for r in results)
    assert posts[0]['title'].startswith('Research system:')
    assert 'operational decisions use their separately authorized route' in posts[0]['body']
    with pytest.raises(ValueError,match='NOTICE_IDENTITY_CHANGED'):
        module.Notices(root,'fixed-config').send('same-event','a'*40,'Changed instruction')


def test_uncertain_notification_never_reposts_and_caps_retry(tmp_path,monkeypatch):
    posts=setup(monkeypatch,fail=True);notices=module.Notices(tmp_path/'notice','fixed-config')
    for _ in range(6):result=notices.send('same-event','a'*40,'Checked status')
    assert result['status']=='BLOCKED' and result['attempts']==3 and len(posts)==1
    old=Outbox(notices.root).db.execute('SELECT state FROM notifications').fetchone()[0]
    assert old=='UNCERTAIN'


def test_distinct_notices_reuse_verified_identity_and_exhausted_pending_normalizes(tmp_path,monkeypatch):
    posts=setup(monkeypatch);notice=module.Notices(tmp_path/'notice','fixed-config')
    first=notice.send('first','a'*40,'First checked report.')
    second=notice.send('second','a'*40,'Second checked report.')
    assert len(posts)==2 and first['status']==second['status']=='SENT'
    notice.db.execute("UPDATE deliveries SET status='PENDING',attempts=3 WHERE id=?",(first['id'],))
    exhausted=notice.send('first','a'*40,'First checked report.')
    assert exhausted['status']=='BLOCKED' and exhausted['reason']=='ATTEMPT_LIMIT_RECONCILE_ORIGINAL_OUTBOX'
    assert len(posts)==2

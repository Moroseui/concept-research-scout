"""Repository-bound GitHub App notifications and synthetic ACKs only.

No operational decision, dispatch, reset, or Git publication entry point exists.
The installed code/config/key/state must be protected from model identities.
"""
import argparse
import base64
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import subprocess
import time
import urllib.request
from orchestrator.git_publication import scan
from orchestrator.operations_report import private_root

REPO='Moroseui/concept-research-scout'
PERMISSIONS={'issues':'write','metadata':'read'}


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
def positive(value):
    if type(value)!=int or value<=0:raise ValueError('ACTUAL_NUMERIC_ID_REQUIRED')
    return value


def config_checked(c):
    if set(c)!={'repository','repository_id','app_id','installation_id','operator_id','bot_id','mode','private_key'}:raise ValueError('CONFIG_SCHEMA')
    if c['repository']!=REPO or c['mode'] not in ('NOTIFICATION_SYNTHETIC_ONLY','NOTIFICATION_ONLY'):raise ValueError('NOTIFICATION_SCOPE')
    for k in ['repository_id','app_id','installation_id','operator_id','bot_id']:positive(c[k])
    return c


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise ValueError('API_REDIRECT_REFUSED')


def api(method,path,token,body=None):
    if not path.startswith('/') or '://' in path or '..' in path:raise ValueError('API_PATH')
    raw=None if body is None else json.dumps(body).encode()
    req=urllib.request.Request('https://api.github.com'+path,data=raw,method=method,headers={
        'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json',
        'X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json'})
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as response:
        raw=response.read(2000001)
    if len(raw)>2000000:raise ValueError('API_RESPONSE_LIMIT')
    return json.loads(raw)


def protected_read(path):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_uid not in (0,os.getuid()) or s.st_mode & 0o077:raise ValueError('PRIVATE_CONFIGURATION_REQUIRED')
        return os.read(fd,100000)
    finally:os.close(fd)


def jwt(c):
    # Key bytes never enter argv, logs, model context or repository artifacts.
    raw=protected_read(c['private_key'])
    if len(raw)>8192:raise ValueError('KEY_SIZE_LIMIT')
    def b64(x):return base64.urlsafe_b64encode(x).rstrip(b'=')
    now=int(time.time());message=b'.'.join([b64(b'{"alg":"RS256","typ":"JWT"}'),b64(json.dumps({'iat':now-60,'exp':now+540,'iss':str(c['app_id'])}).encode())])
    # Use an anonymous pipe descriptor for openssl's key input.
    readfd,writefd=os.pipe()
    try:
        os.write(writefd,raw);os.close(writefd);writefd=None
        result=subprocess.run(['openssl','dgst','-sha256','-sign','/dev/fd/'+str(readfd)],input=message,capture_output=True,pass_fds=(readfd,),timeout=10)
        if result.returncode:raise ValueError('APP_SIGNATURE_FAILED')
        return (message+b'.'+b64(result.stdout)).decode()
    finally:
        os.close(readfd)
        if writefd is not None:os.close(writefd)


def session(c,app_token,call=api):
    config_checked(c)
    app=call('GET','/app',app_token)
    if app['id']!=c['app_id'] or app['permissions']!=PERMISSIONS:raise ValueError('APP_IDENTITY_OR_PERMISSION_DRIFT')
    installation=call('GET','/app/installations/'+str(c['installation_id']),app_token)
    if installation['app_id']!=c['app_id'] or installation['permissions']!=PERMISSIONS or installation['repository_selection']!='selected' or installation.get('suspended_at'):
        raise ValueError('INSTALLATION_SCOPE_DRIFT')
    inspection=call('POST','/app/installations/'+str(c['installation_id'])+'/access_tokens',app_token,{'permissions':{'metadata':'read'}})
    repos=call('GET','/installation/repositories?per_page=100',inspection['token'])
    if repos['total_count']!=1 or [(r['id'],r['full_name']) for r in repos['repositories']]!=[(c['repository_id'],REPO)]:raise ValueError('INSTALLATION_REPOSITORIES_DRIFT')
    token=call('POST','/app/installations/'+str(c['installation_id'])+'/access_tokens',app_token,{'repository_ids':[c['repository_id']],'permissions':PERMISSIONS})
    if token['permissions']!=PERMISSIONS:raise ValueError('TOKEN_SCOPE_DRIFT')
    access=token['token']
    repos=call('GET','/installation/repositories?per_page=100',access)
    if repos['total_count']!=1 or [(r['id'],r['full_name']) for r in repos['repositories']]!=[(c['repository_id'],REPO)]:raise ValueError('REPOSITORY_SCOPE_DRIFT')
    bot=call('GET','/users/'+app['slug']+'%5Bbot%5D',access)
    operator=call('GET','/users/Moroseui',access)
    if bot['id']!=c['bot_id'] or operator['id']!=c['operator_id']:raise ValueError('ACTOR_IDENTITY_DRIFT')
    return access,{'app_id':app['id'],'installation_id':c['installation_id'],'repository_id':c['repository_id'],'operator_id':operator['id'],'bot_id':bot['id'],'permissions':PERMISSIONS,'mode':c['mode']}


def packet_checked(p,now=None):
    now=int(time.time()) if now is None else now
    if set(p)!={'id','source','nonce','expires','summary'}:raise ValueError('PACKET_SCHEMA')
    if not re.fullmatch('[a-z0-9-]{1,48}',p['id']) or not re.fullmatch('[0-9a-f]{40}',p['source']) or not re.fullmatch('[0-9a-f]{32}',p['nonce']):raise ValueError('PACKET_IDENTITY')
    if type(p['expires'])!=int or not now<p['expires']<=now+86400:raise ValueError('PACKET_EXPIRY')
    if not isinstance(p['summary'],str) or len(p['summary'])>2000:raise ValueError('SUMMARY_LIMIT')
    scan('notification.json',json.dumps(p).encode());return p


def body_for(p,*,synthetic=True):
    return ('@Moroseui — '+('synthetic notification test.' if synthetic else 'checked research-system notification.')+
      (' No operational approval is requested.\n\n' if synthetic else
       ' Replies acknowledge information only; operational decisions use their separately authorized route.\n\n')+p['summary']+
      '\n\nSource: `'+p['source']+'`.\n\nReply exactly: `ACK '+p['id']+' '+p['nonce']+' '+digest(p)+'`\n\nNotification: '+digest(p))


class Outbox:
    def __init__(self,root):
        self.root=private_root(root);self.db=sqlite3.connect(self.root/'notifications.sqlite',isolation_level=None,timeout=35)
        self.db.row_factory=sqlite3.Row
        self.db.execute('CREATE TABLE IF NOT EXISTS notifications(id TEXT PRIMARY KEY,packet TEXT NOT NULL,state TEXT NOT NULL,issue INTEGER,ack INTEGER)')
    def send(self,p,c,token,call=api):
        packet_checked(p);config_checked(c);synthetic=c['mode']=='NOTIFICATION_SYNTHETIC_ONLY'
        body=body_for(p,synthetic=synthetic);scan('issue.md',body.encode())
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT * FROM notifications WHERE id=?',(p['id'],)).fetchone()
            if old:
                if old['packet']!=json.dumps(p,sort_keys=True):raise ValueError('NOTIFICATION_ID_CONFLICT')
                self.db.execute('COMMIT')
                if old['state']=='UNCERTAIN':raise ValueError('UNCERTAIN_DELIVERY_RECONCILE_NO_REPOST')
                return {'issue':old['issue'],'duplicate':True,'operational_authority':False}
            self.db.execute('INSERT INTO notifications VALUES(?,?,?,NULL,NULL)',(p['id'],json.dumps(p,sort_keys=True),'UNCERTAIN'))
            self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
        # Persist UNCERTAIN before network mutation. Failure never automatically reposts.
        result=call('POST','/repos/'+REPO+'/issues',token,{'title':('Synthetic acknowledgment: ' if synthetic else 'Research system: ')+p['id'],'body':body})
        if result['user']['id']!=c['bot_id'] or result['body']!=body or result['repository_url']!='https://api.github.com/repos/'+REPO:raise ValueError('ISSUE_RESPONSE_BINDING')
        number=positive(result['number'])
        self.db.execute("UPDATE notifications SET state='SENT',issue=? WHERE id=?",(number,p['id']))
        return {'issue':number,'duplicate':False,'operational_authority':False}
    def acknowledge(self,key,comment_id,c,token,call=api,now=None):
        config_checked(c);positive(comment_id)
        row=self.db.execute('SELECT * FROM notifications WHERE id=?',(key,)).fetchone()
        if not row or row['state'] not in ['SENT','ACKNOWLEDGED']:raise ValueError('SENT_NOTIFICATION_REQUIRED')
        p=json.loads(row['packet']);packet_checked(p,now)
        comment=call('GET','/repos/'+REPO+'/issues/comments/'+str(comment_id),token)
        expected='ACK '+p['id']+' '+p['nonce']+' '+digest(p)
        if comment['id']!=comment_id or comment['user']['id']!=c['operator_id'] or comment['issue_url']!='https://api.github.com/repos/'+REPO+'/issues/'+str(row['issue']) or comment['body'].strip()!=expected or comment['created_at']!=comment['updated_at']:
            raise ValueError('ACK_IDENTITY_OR_VERSION_REJECTED')
        result=self.db.execute("UPDATE notifications SET state='ACKNOWLEDGED',ack=? WHERE id=? AND state='SENT'",(comment_id,key))
        if result.rowcount==0 and self.db.execute('SELECT ack FROM notifications WHERE id=?',(key,)).fetchone()[0]!=comment_id:raise ValueError('ACK_ALREADY_CONSUMED')
        return {'status':'SYNTHETIC_ACKNOWLEDGED' if c['mode']=='NOTIFICATION_SYNTHETIC_ONLY' else 'INFORMATION_ACKNOWLEDGED',
                'comment_id':comment_id,'duplicate':result.rowcount==0,'operational_authority':False}


def main():
    os.umask(0o077)
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['inspect','send-synthetic','ack-synthetic','send-notification','ack-notification']);p.add_argument('--config',required=True);p.add_argument('--state',required=True);p.add_argument('--packet');p.add_argument('--id');p.add_argument('--comment-id',type=int);a=p.parse_args()
    c=config_checked(json.loads(protected_read(a.config)))
    if a.action!='inspect' and (a.action.endswith('synthetic'))!=(c['mode']=='NOTIFICATION_SYNTHETIC_ONLY'):
        raise ValueError('NOTIFICATION_COMMAND_MODE_MISMATCH')
    token,identity=session(c,jwt(c))
    root=private_root(a.state)
    if a.action=='inspect':
        (root/'verified-identities.json').write_text(json.dumps(identity,indent=2)+'\n');result=identity
    else:
        if json.loads(protected_read(root/'verified-identities.json'))!=identity:raise ValueError('RECORD_IDENTITIES_BEFORE_ACTIVATION')
        out=Outbox(root)
        result=out.send(json.loads(Path(a.packet).read_text()),c,token) if a.action.startswith('send-') else out.acknowledge(a.id,a.comment_id,c,token)
    print(json.dumps(result))

if __name__=='__main__':main()

"""Reviewed exact B/Colab continuation; actual accounting rows are never filtered.

Only the old item4 SEQUENCE validator sees a classified history view. The real
shared SQL count, daily limit, per-run limits and uncertainty refusal remain.
"""
import hashlib
import json
from pathlib import Path

from orchestrator.aggregate_analysis_scope import AUTHORITY
from orchestrator.experiment_context import ITEM4_RUN

STAGES = ('run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review')
SCHEMA = 'preparation-interleaving/v1'
_ACTIVE = None
_PREMODEL = None
PREMODEL_CALL = 'e41d3d88958bef07e8cf854cb65125ba496b5537f42d26206ae1cee2df9e0e67'
PREMODEL_RUN = 'aggregate-d695a5269c3647c4cb81b91a'
PREMODEL_SOURCE = '304cae4aa12d53eb99254499950eec4e71df8075'



def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def scope_bytes(value): return json.dumps(value,sort_keys=True,indent=2).encode()+b'\n'
def require(ok, why):
    if not ok: raise ValueError('PREPARATION_INTERLEAVING_' + why)


def identity(run, stage, attempt): return sha((run+':'+stage+':'+str(attempt)).encode())


def validate_scope(value):
    require(isinstance(value,dict) and set(value)=={'schema','authority_sha256','source_sha','ledger',
        'lanes','frozen_rows','item4_scope','terminal_rows'}, 'SCOPE_FIELDS')
    require(value['schema']==SCHEMA and value['authority_sha256']==AUTHORITY,'AUTHORITY')
    require(isinstance(value['source_sha'],str) and len(value['source_sha'])==40 and all(c in '0123456789abcdef' for c in value['source_sha']),'SOURCE')
    require(Path(value['ledger']).is_absolute() and set(value['lanes'])=={'aggregate_analysis','colab_preparation'},'LANES')
    seen=set()
    for key,lane in value['lanes'].items():
        require(set(lane)=={'run_id','state','plan','plan_sha256','registry_sha256'} and Path(lane['state']).is_absolute()
            and Path(lane['plan']).is_absolute(),'LANE_FIELDS')
        prefix='aggregate-' if key=='aggregate_analysis' else 'colab-'
        expected=prefix+sha((AUTHORITY+':'+lane['registry_sha256']).encode())[:24]
        require(lane['run_id']==expected and expected not in seen,'LANE_IDENTITY');seen.add(expected)
        for name in ('plan_sha256','registry_sha256'):
            require(isinstance(lane[name],str) and len(lane[name])==64 and all(c in '0123456789abcdef' for c in lane[name]),'LANE_PIN')
    require(isinstance(value['frozen_rows'],dict) and len(value['frozen_rows'])==76,'FROZEN_HISTORY')
    require(isinstance(value['terminal_rows'],dict) and set(value['terminal_rows'])<=set(value['frozen_rows']),'TERMINAL_HISTORY')
    require(set(value['item4_scope'])=={'path','sha256','review_folder','review_sha256','configuration'}
        and Path(value['item4_scope']['path']).is_absolute() and Path(value['item4_scope']['review_folder']).is_absolute(),'ITEM4_SCOPE')
    conf=value['item4_scope']['configuration']
    require(isinstance(conf,dict) and set(conf)=={'path','sha256'} and Path(conf['path']).is_absolute(),'ITEM4_CONFIG')
    return value


def lane_for(scope, run):
    return next(((key,value) for key,value in scope['lanes'].items() if value['run_id']==run),None)


def configure_premodel(proof):
    """The separately reviewed continuation supplies its genuine exact proof.

    Disabled in ordinary imports. This is not a status conversion: FAILED and
    BLOCKED_BEFORE_MODEL remain the original terminal/accounting observations.
    """
    global _PREMODEL
    require(_PREMODEL is None and callable(getattr(proof,'verify_global',None))
        and callable(getattr(proof,'verify_local',None)),'PREMODEL_PROOF_CONFIGURATION')
    _PREMODEL = proof


def premodel_global(scope,row):
    require(_PREMODEL is not None and scope['source_sha']==PREMODEL_SOURCE
        and row.get('id')==PREMODEL_CALL and row.get('change_id')==PREMODEL_RUN
        and row.get('kind')=='scientific' and row.get('status')=='FAILED'
        and row.get('round')==1,'PREMODEL_EXACT_ROW_REQUIRED')
    binding=json.loads(row['binding'])
    require(binding.get('source')==PREMODEL_SOURCE and binding.get('run_id')==PREMODEL_RUN
        and binding.get('stage')=='run_spec_author','PREMODEL_ORIGINAL_BINDING')
    proof=_PREMODEL.verify_global(scope,row)
    require(isinstance(proof,dict) and proof.get('id')==PREMODEL_CALL
        and proof.get('model_client_launched') is False and proof.get('proof_sha256'),
        'PREMODEL_TERMINAL_PROOF')
    return proof


def premodel_local(scope,row,item):
    premodel_global(scope,row)
    require(item is not None and item['id']==PREMODEL_CALL
        and item['status']=='BLOCKED_BEFORE_MODEL' and item['stage']=='run_spec_author'
        and item['attempt']==1,'PREMODEL_LOCAL_ORIGINAL')
    proof=_PREMODEL.verify_local(scope,row,dict(item))
    require(isinstance(proof,dict) and proof.get('id')==PREMODEL_CALL
        and proof.get('model_client_launched') is False and proof.get('proof_sha256'),
        'PREMODEL_LOCAL_TERMINAL_PROOF')


def install_driver_hook(module,proof):
    """Use author2 for the exact counted pre-model failure; no accepted-round edit."""
    require(_PREMODEL is proof and not getattr(module.AnalysisDriver,'_premodel_hook',False),
        'PREMODEL_DRIVER_CONFIGURATION')
    original=module.AnalysisDriver
    class PremodelRecoveryAnalysisDriver(original):
        _premodel_hook=True
        def _advance(self,collect_folder=None,identity_refusal=None):
            value=self.current()
            if (self.config.get('run_id')!=PREMODEL_RUN or value.get('phase')!='REPORT'
                    or collect_folder is not None or identity_refusal is not None):
                return super()._advance(collect_folder,identity_refusal)
            self.guard()
            row=self.store.batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(PREMODEL_CALL,)).fetchone()
            require(row is not None and _ACTIVE is not None,'PREMODEL_REPORT_SCOPE')
            calls=self.store.db.execute('SELECT * FROM manual_calls ORDER BY rowid').fetchall()
            first=next((r for r in calls if r['id']==PREMODEL_CALL),None)
            premodel_local(_ACTIVE.scope,dict(row),first)
            # A pre-model refusal has no native outcome field. Display its true
            # saved status; never add a made-up outcome to the retained receipt.
            receipts=[]
            for call in calls:
                receipt=json.loads(call['receipt'])
                if call['id']==PREMODEL_CALL:
                    outcome='BLOCKED_BEFORE_MODEL (retained reservation; no model launched)'
                else:
                    require(call['status']=='COMPLETE' and receipt.get('outcome')=='COMPLETE','PREMODEL_REPORT_UNRESOLVED')
                    outcome=receipt['outcome']
                receipts.append((receipt['stage'],receipt['input_characters'],outcome))
            from datetime import datetime,timezone
            from orchestrator import private_records
            elapsed=(datetime.now(timezone.utc)-datetime.fromisoformat(self.config['started_utc'])).total_seconds()
            body='# Stock-take ready for operator review\n\n'+Path(value['interpretation']).read_text()
            body+='\n\n## Run record\nAnalysis only; no notebook, CPU or GPU execution. Operator review is required before any next backlog item.\n'
            body+=f'Calls: {len(calls)}/{self.status()["call_limit"]}; elapsed seconds: {elapsed:.1f}; rounds: '+json.dumps(value['rounds'])+'.\n'
            body+='\n| Stage | Input characters | Outcome |\n| --- | ---: | --- |\n'
            for stage,characters,outcome in receipts:body+=f'| {stage} | {characters} | {outcome} |\n'
            private_records.write_text(self.state/'REPORT.md',body)
            value.update(phase='COMPLETE',operator_review_pending=True);self.save(value)
            self.store.batch.complete_run(PREMODEL_RUN,{'report_sha256':sha((self.state/'REPORT.md').read_bytes()),'operator_review_pending':True})
            return self.status()
        def model_round_number(self,value):
            if self.config.get('run_id')!=PREMODEL_RUN or value.get('phase')!='run_spec_author':
                return super().model_round_number(value)
            rows=self.store.db.execute('SELECT * FROM manual_calls WHERE stage=? ORDER BY rowid',
                ('run_spec_author',)).fetchall()
            if len(rows)!=1:return super().model_round_number(value)
            require(self.config.get('source')==PREMODEL_SOURCE and not value.get('pending')
                and not value.get('rounds',{}).get('run_spec_author') and _ACTIVE is not None,
                'PREMODEL_AUTHOR2_STATE')
            row=self.store.batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(PREMODEL_CALL,)).fetchone()
            require(row is not None,'PREMODEL_AUTHOR2_GLOBAL_ROW')
            premodel_local(_ACTIVE.scope,dict(row),rows[0])
            return 2
    # Reuse the existing completion exception seam, with one verified terminal
    # reservation. The generic unresolved-row refusal and FAILED row stay intact.
    from orchestrator import stocktake_review_recovery
    prior_completion=stocktake_review_recovery.completion
    def completion(batch,run):
        allowed=prior_completion(batch,run)
        if run!=PREMODEL_RUN:return allowed
        require(_ACTIVE is not None,'PREMODEL_COMPLETION_SCOPE')
        row=batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(PREMODEL_CALL,)).fetchone()
        require(row is not None,'PREMODEL_COMPLETION_ROW')
        premodel_global(_ACTIVE.scope,dict(row))
        return [*(allowed or []),PREMODEL_CALL]
    stocktake_review_recovery.completion=completion
    module.AnalysisDriver=PremodelRecoveryAnalysisDriver
    return original


def classify(scope, rows):
    """Pure, strict history classification. Never used as the accounting count."""
    validate_scope(scope)
    ids=[row['id'] for row in rows]
    require(len(ids)==len(set(ids)),'DUPLICATE_ROW')
    by_id={row['id']:row for row in rows}
    require(all(ident in by_id and sha(canonical(by_id[ident]))==pin for ident,pin in scope['frozen_rows'].items()),'ORIGINAL_CHANGED')
    selected=[];retained=[];counts={key:0 for key in scope['lanes']};attempts={}
    for row in rows:
        pair=lane_for(scope,row['change_id'])
        if pair is None:
            require(row['id'] in scope['frozen_rows'] or
                (row['change_id']==ITEM4_RUN and row['id']==identity(ITEM4_RUN,'run_spec_author',24)
                 and row['status']=='COMPLETE' and json.loads(row['binding']).get('stage')=='run_spec_author'),
                'UNRELATED_NEW_ROW')
            retained.append(row);continue
        key,lane=pair;binding=json.loads(row['binding'])
        permitted={identity(lane['run_id'],stage,n):(stage,n) for stage in STAGES for n in (1,2)}
        require(row['id'] in permitted and row['kind']=='scientific','PREPARATION_ROW_UNQUALIFIED')
        if row['status']!='COMPLETE':premodel_global(scope,row)
        stage,attempt=permitted[row['id']]
        require(attempt==attempts.get((key,stage),0)+1,'PREPARATION_STAGE_ORDER')
        attempts[key,stage]=attempt
        require(binding.get('run_id')==lane['run_id'] and binding.get('stage')==stage
            and binding.get('source')==scope['source_sha'],'PREPARATION_ROW_BINDING')
        # Source remains the explicit original global admission binding.
        counts[key]+=1
        require(type(row['round']) is int and row['round']==counts[key] and counts[key]<=8,'PREPARATION_ROW_ORDER')
        require(row.get('receipt') is not None,'PREPARATION_RECEIPT')
        receipt=json.loads(row['receipt'])
        require(receipt.get('id',row['id'])==row['id'],'PREPARATION_RECEIPT_BINDING')
        selected.append(row['id'])
    require(len(retained)<=79 and len(rows)<=95,'SHARED_CAP')
    return retained,selected,counts


class Overlay:
    def __init__(self,scope,review_folder,*,filesystem_root=Path('/')):
        self.scope=validate_scope(scope);self.review_folder=Path(review_folder);self.filesystem_root=Path(filesystem_root)
        self.approval=None
        self.verify()

    def path(self,value):
        from tools.deploy_manual_lane import bound
        return bound(self.filesystem_root,value)

    def verify(self):
        from orchestrator.autonomy_review import verify_result
        from orchestrator import private_records
        from orchestrator.aggregate_analysis_scope import authority
        authority()
        q=verify_result(self.review_folder)
        require(q['verdict']=='APPROVE' and q['source_sha']==self.scope['source_sha'],'IMPLEMENTATION_APPROVAL')
        manifest=json.loads(private_records.check(self.review_folder/'packet-manifest.json').read_bytes())
        require(manifest['files'].get('evidence/preparation-interleaving.json')==sha(scope_bytes(self.scope)),'REVIEWED_SCOPE')
        for lane in self.scope['lanes'].values():
            raw=private_records.check(self.path(lane['plan'])).read_bytes()
            require(sha(raw)==lane['plan_sha256'],'PLAN_CHANGED')
            plan=json.loads(raw)
            require(plan['private_intake']['sha256']==lane['registry_sha256'],'REGISTRY_CHANGED')
        old=self.scope['item4_scope'];prior=verify_result(self.path(old['review_folder']))
        require(prior['verdict']=='APPROVE' and prior['report_sha256']==old['review_sha256'],'ITEM4_APPROVAL')
        raw=private_records.check(self.path(old['path'])).read_bytes()
        old_manifest=json.loads(private_records.check(self.path(old['review_folder'])/'packet-manifest.json').read_bytes())
        require(sha(raw)==old['sha256'] and old_manifest['source_files'].get(
            'docs/ITEM4_REPORT_SNAPSHOT_AUTHOR_PRIVATE.json')==old['sha256'],'ITEM4_SCOPE_CHANGED')
        old_scope=json.loads(raw);conf=old['configuration']
        require(conf['sha256']==old_scope['configuration_sha256'] and
            sha(private_records.check(self.path(conf['path'])).read_bytes())==conf['sha256'],'ITEM4_CONFIG_CHANGED')
        self.approval=q['report_sha256'];return q

    def owner(self,batch,run,*,active=True):
        self.verify();require(batch.folder.resolve()==self.path(self.scope['ledger']).resolve(),'LEDGER')
        pair=lane_for(self.scope,run);require(pair is not None,'RUN')
        key,lane=pair;row=batch.db.execute('SELECT * FROM autonomy_runs WHERE id=?',(run,)).fetchone()
        require(row is not None and row['status'] in ({'ACTIVE'} if active else {'ACTIVE','COMPLETE'}),'OWNER')
        owner=json.loads(row['binding']);state=self.path(lane['state'])
        from orchestrator import private_records
        config=json.loads(private_records.check(state/'lane.json').read_bytes())
        require(owner==config.get('owner_binding') and owner.get('state')==lane['state']
            and owner.get('source')==self.scope['source_sha'] and config.get('source')==self.scope['source_sha']
            and owner.get('review_sha256')==self.approval
            and config.get('run_id')==run and key in owner and key in config,'OWNER_BINDING')
        raw=private_records.check(state/'preparation-plan.json').read_bytes()
        require(sha(raw)==lane['plan_sha256'] and config.get('plan_sha256')==lane['plan_sha256'],'OWNER_PLAN')
        return key,lane

    def rows(self,batch):
        self.verify();require(batch.folder.resolve()==self.path(self.scope['ledger']).resolve(),'LEDGER')
        return [dict(row) for row in batch.db.execute("SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid")]

    def sequence_view(self,batch,rows):
        require(rows==self.rows(batch),'ACTUAL_HISTORY')
        retained,selected,counts=classify(self.scope,rows)
        import sqlite3
        for run in {r['change_id'] for r in rows if lane_for(self.scope,r['change_id'])}:
            key,lane=self.owner(batch,run,active=False)
            with sqlite3.connect((self.path(lane['state'])/'jobs.sqlite').resolve().as_uri()+'?mode=ro',uri=True) as local:
                local.row_factory=sqlite3.Row
                for global_row in [r for r in rows if r['change_id']==run]:
                    item=local.execute('SELECT * FROM manual_calls WHERE id=?',(global_row['id'],)).fetchone()
                    if global_row['status']=='FAILED' and global_row['id']==PREMODEL_CALL:
                        premodel_local(self.scope,global_row,item)
                    else:
                        require(item is not None and item['status']=='COMPLETE'
                            and json.loads(item['receipt'])==json.loads(global_row['receipt'])
                            and identity(run,item['stage'],item['attempt'])==global_row['id']
                            and all(json.loads(item['receipt']).get(k)==v for k,v in json.loads(global_row['binding']).get('input',{}).items()),'LOCAL_GLOBAL_HISTORY')
        config=json.loads(self.path(self.scope['item4_scope']['configuration']['path']).read_bytes())
        with sqlite3.connect((self.path(self.scope['item4_scope']['configuration']['path']).parent/'jobs.sqlite').resolve().as_uri()+'?mode=ro',uri=True) as local:
            local.row_factory=sqlite3.Row
            for row in retained:
                if row['id'] in self.scope['frozen_rows']:continue
                binding=json.loads(row['binding']);item=local.execute('SELECT * FROM manual_calls WHERE id=?',(row['id'],)).fetchone()
                require(binding.get('source')==config['source'] and binding.get('run_id')==ITEM4_RUN
                    and item is not None and item['stage']=='run_spec_author' and item['attempt']==24
                    and item['status']=='COMPLETE' and json.loads(item['receipt'])==json.loads(row['receipt']),'ITEM4_NEW_ROW_BINDING')
        return retained

    def extend(self,batch,original):
        rows=self.rows(batch);retained,selected,counts=classify(self.scope,rows)
        self.sequence_view(batch,rows)
        require(original.get('limit')==79 and original.get('scoped_run_id')==ITEM4_RUN,'ORIGINAL_ITEM4_ALLOWANCE')
        return {**original,'limit':95,'preparation_interleaving':{'scope_sha256':sha(canonical(self.scope)),
            'review_sha256':self.approval,'original_limit':79,'actual_scientific_calls':len(rows),
            'classified_preparation_call_ids':selected,'preparation_counts':counts}}

    def allowance(self,batch,run,stage,ident,source,receipt):
        key,lane=self.owner(batch,run)
        require(source==self.scope['source_sha'] and stage in STAGES,'CALL_SOURCE_STAGE')
        permitted={identity(run,stage,n) for n in (1,2)};require(ident in permitted,'CALL_ID')
        rows=self.rows(batch);retained,selected,counts=classify(self.scope,rows)
        self.sequence_view(batch,rows)
        require(ident not in {r['id'] for r in rows} and counts[key]<8,'CALL_DUPLICATE_OR_CAP')
        state=self.path(lane['state'])
        import sqlite3
        local=sqlite3.connect((state/'jobs.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
        try:
            n=local.execute('SELECT count(*) FROM manual_calls WHERE stage=?',(stage,)).fetchone()[0]+1
            total=local.execute('SELECT count(*) FROM manual_calls').fetchone()[0]
            require(identity(run,stage,n)==ident and total==counts[key] and total<8,'LOCAL_GLOBAL_COUNTS')
        finally:local.close()
        return {'limit':95,'scoped_run_id':run,'authority_sha256':AUTHORITY,'review_sha256':self.approval,
            'scope_sha256':sha(canonical(self.scope)),'actual_scientific_calls':len(rows),'preparation_counts':counts}

    def terminal_ids(self,batch,run,stage,ident,source,receipt):
        # This reviewed overlay authorizes new independent preparation only. It
        # never retries or marks scientifically accepted any historical failure.
        self.owner(batch,run)
        require(source==self.scope['source_sha'] and stage in STAGES and ident in
                {identity(run,stage,n) for n in (1,2)},'TERMINAL_CALL_SCOPE')
        result=[]
        from orchestrator import administrative_terminal,private_records,completed_run
        already_closed=completed_run.closed_ids(batch,run,root=self.filesystem_root)
        for ident,pin in self.scope['terminal_rows'].items():
            row=batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(ident,)).fetchone()
            require(row is not None and row['status']=='UNCERTAIN' and sha(canonical(dict(row)))==pin,'TERMINAL_ORIGINAL_CHANGED')
            if ident in already_closed:continue
            if ident=='af4547778fe7e1f35698089607ab524d08346618131512c232670b7ccbf02ab8':
                # Existing independently approved exact pre-SDK classifier,
                # including current original service state and all original bytes.
                from tools.item4_smoke_response_runtime import sender_qualification
                proof=sender_qualification(dict(row))
            else:
                proof=administrative_terminal.verify(dict(row),self.path(str(administrative_terminal.ROOT/ident)))
            require(proof.get('id')==ident and proof.get('proof_sha256'),'TERMINAL_PROOF')
            result.append(ident)
        return result


def connect(scope,review_folder,*,filesystem_root=Path('/')):
    global _ACTIVE
    require(_ACTIVE is None,'ALREADY_CONNECTED')
    value=Overlay(scope,review_folder,filesystem_root=filesystem_root)
    from orchestrator import autonomy_limits
    old=autonomy_limits.scientific_batch_allowance
    def allowance(batch,run,stage,ident,source,receipt):
        if lane_for(value.scope,run):return value.allowance(batch,run,stage,ident,source,receipt)
        result=old(batch,run,stage,ident,source,receipt)
        if run==ITEM4_RUN:return value.extend(batch,result)
        return result
    autonomy_limits.scientific_batch_allowance=allowance
    _ACTIVE=value
    return value


def item4_sequence_view(batch,rows):
    return rows if _ACTIVE is None else _ACTIVE.sequence_view(batch,rows)


def terminal_ids(batch,run,stage,ident,source,receipt):
    if _ACTIVE is None or lane_for(_ACTIVE.scope,run) is None:return []
    return _ACTIVE.terminal_ids(batch,run,stage,ident,source,receipt)

import base64,copy,json,os,sqlite3,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools import preparation_premodel_recovery as r
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.manual_executor import ManualExecutor

class ExactProofTests(unittest.TestCase):
    def setUp(self):
        self.b=r.binding();o=self.b['original'];self.args=[o['global_call'],o['local_call'],base64.b64decode(self.b['config']['base64']),o['manual_state'],o['manual_account'],{n:z['sha256'] for n,z in self.b['workspace'].items()},{n:z['sha256'] for n,z in self.b['source_files'].items()}]
    def test_exact_original_positive_proof(self):
        p=r.verify_original(*self.args);self.assertEqual(p['id'],r.ID);self.assertFalse(p['model_client_launched'])
    def test_changed_rows_account_state_or_input_fail_closed(self):
        for index,key in [(0,'status'),(1,'status'),(3,'payload'),(4,'payload')]:
            with self.subTest(index=index):
                args=copy.deepcopy(self.args);args[index][key]='changed'
                with self.assertRaises(ValueError):r.verify_original(*args)
        for index in [5,6]:
            args=copy.deepcopy(self.args);args[index][next(iter(args[index]))]='0'*64
            with self.assertRaises(ValueError):r.verify_original(*args)
    def test_receipt_is_failed_and_keeps_reserved_count(self):
        v=r.make_receipt('a'*64);self.assertEqual(v['outcome'],'FAILED_BEFORE_MODEL');self.assertEqual(v['accounting_units'],1)
        self.assertFalse(v['model_client_launched']);self.assertEqual(v['reconciliation']['original_local_account_count'],0)
        self.assertNotIn('accounting',v);self.assertEqual(json.loads(self.b['original']['local_call']['receipt'])['stage'],v['stage'])
    def test_only_branch_changes_in_corrected_config(self):
        old=json.loads(self.args[2]);new=r.new_config();self.assertEqual(new['branch'],r.BRANCH);new['branch']=old['branch'];self.assertEqual(new,old)

class CopiedSqliteApplication(unittest.TestCase):
    def test_real_finish_sqlite_branches_preservation_and_later_account_progress(self):
        b=copy.deepcopy(r.binding());o=b['original'];source_repo=Path(__file__).resolve().parents[1]
        # Only synthetic filesystem ownership differs; all140 original names,
        # types, modes and content hashes remain exactly captured.
        for item in b['workspace_tree'].values():item.update(uid=os.getuid(),gid=os.getgid())
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);ledger=r.mapped(r.LEDGER,root);lane=r.mapped(r.LANE,root);lane.mkdir(parents=True)
            batch=BatchAccounts(ledger,filesystem_root=root);local=ManualExecutor(lane/'jobs.sqlite')
            def insert(db,table,row):
                keys=list(row);db.execute('INSERT INTO '+table+'('+','.join(keys)+') VALUES('+','.join('?' for _ in keys)+')',[row[k] for k in keys])
            insert(batch.db,'autonomy_calls',o['global_call']);insert(batch.db,'jobs',o['global_job'])
            for table,key in [('manual_calls','local_call'),('manual_account','manual_account'),('manual_state','manual_state')]:insert(local.db,table,o[key])
            local.db.close()
            for parent in [r.LANE.parent,r.COLAB]:
                repo=r.mapped(parent/'repository',root);repo.parent.mkdir(parents=True,exist_ok=True)
                subprocess.run(['git','clone','--quiet','--no-hardlinks','--no-checkout',str(source_repo),str(repo)],check=True)
                subprocess.run(['git','checkout','--quiet','-b',o['git_branch'],r.SOURCE],cwd=repo,check=True)
            for key in ['config','owner']:
                p=r.mapped(b[key]['path'],root);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(base64.b64decode(b[key]['base64']))
            # Retained exact captured input/code bytes, never patient fixtures.
            capture=json.loads((source_repo.parent/'PREMODEL_READONLY_CAPTURE_V2.stdout').read_text())
            for group in ['workspace_files','source_files']:
                for row in capture[group].values():
                    p=r.mapped(row['path'],root);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(base64.b64decode(row['base64']))
            full=json.loads((source_repo.parent/'PREMODEL_COMPLETE_TREE_V2.stdout').read_text())
            for name,row in full['workspace_files'].items():
                p=r.mapped(row['path'],root);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(base64.b64decode(row['base64']));p.chmod(b['workspace_tree'][name]['mode'])
            work=r.mapped(Path(next(iter(b['workspace'].values()))['path']).parent,root)
            (work/'evidence').chmod(b['workspace_tree']['evidence']['mode'])
            approved={'report_sha256':'a'*64,'verdict':'APPROVE','change_id':r.CHANGE}
            with patch.object(r,'binding',return_value=b),patch.object(r,'approval',return_value=approved),patch.object(r.os,'getuid',return_value=1003),patch.object(r.os,'getgid',return_value=1003):
                work=r.mapped(Path(next(iter(b['workspace'].values()))['path']).parent,root)
                unexpected=work/'unexpected-subdirectory';unexpected.mkdir()
                with self.assertRaisesRegex(ValueError,'WORKSPACE_MEMBERSHIP'):
                    r.administrative_exception(batch.db,filesystem_root=root,check_unit=lambda:None)
                self.assertFalse(r.mapped(r.RECORD,root).exists())
                unexpected.rmdir()
                extra=work/'evidence'/'unexpected.txt';extra.write_text('synthetic')
                with self.assertRaisesRegex(ValueError,'WORKSPACE_MEMBERSHIP'):
                    r.administrative_exception(batch.db,filesystem_root=root,check_unit=lambda:None)
                extra.unlink()
                alias=work/'evidence'/'unexpected-link';alias.symlink_to(work/'prompt.md')
                with self.assertRaisesRegex(ValueError,'SYMLINK'):
                    r.administrative_exception(batch.db,filesystem_root=root,check_unit=lambda:None)
                alias.unlink()
                changed=next((work/'evidence').iterdir());original=changed.read_bytes();changed.chmod(0o600);changed.write_bytes(original+b'changed');changed.chmod(0o400)
                with self.assertRaisesRegex(ValueError,'WORKSPACE_MEMBERSHIP'):
                    r.administrative_exception(batch.db,filesystem_root=root,check_unit=lambda:None)
                changed.chmod(0o600);changed.write_bytes(original);changed.chmod(0o400)
                unknown=dict(o['global_call']);unknown.update(id='f'*64,change_id='unknown-run')
                insert(batch.db,'autonomy_calls',unknown)
                with self.assertRaisesRegex(ValueError,'OTHER_RUNNING_CALL'):
                    r.apply(batch,root/'synthetic-approval',filesystem_root=root,check_unit=lambda:None)
                self.assertFalse(r.mapped(r.RECORD,root).exists())
                batch.db.execute('DELETE FROM autonomy_calls WHERE id=?',('f'*64,))
                result=r.apply(batch,root/'synthetic-approval',filesystem_root=root,check_unit=lambda:None)
                self.assertEqual(result['status'],'RECONCILED_FAILED_NOT_COMPLETE');self.assertEqual(batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0],1)
                after=r.one(batch.db,'SELECT * FROM autonomy_calls WHERE id=?',(r.ID,));self.assertEqual(after['status'],'FAILED')
                db=r.read_local(root);self.assertEqual(r.one(db,'SELECT * FROM manual_calls WHERE id=?',(r.ID,)),o['local_call']);self.assertEqual(r.one(db,'SELECT * FROM manual_account WHERE id=1'),o['manual_account']);db.close()
                proof=r.load_verified_proof(root/'synthetic-approval',filesystem_root=root);self.assertEqual(proof.verify_global({'source_sha':r.SOURCE},after)['id'],r.ID)
                # Later real model-stage state/account may progress; history proof
                # must not freeze mutable lane state or pretend original admission.
                db=sqlite3.connect(lane/'jobs.sqlite');db.execute("UPDATE manual_state SET payload=? WHERE id=1",(json.dumps({'phase':'run_spec_review'}),));account=json.loads(o['manual_account']['payload']);account['count']=1;db.execute('UPDATE manual_account SET payload=?,version=1 WHERE id=1',(json.dumps(account),));db.commit();db.close()
                self.assertEqual(proof.verify_global({'source_sha':r.SOURCE},after)['id'],r.ID)
                changed=copy.deepcopy(after);changed['status']='COMPLETE'
                with self.assertRaises(ValueError):proof.verify_global({'source_sha':r.SOURCE},changed)
                with self.assertRaisesRegex(ValueError,'EXISTING_RECONCILIATION'):r.apply(batch,root/'synthetic-approval',filesystem_root=root,check_unit=lambda:None)
            batch.db.close()

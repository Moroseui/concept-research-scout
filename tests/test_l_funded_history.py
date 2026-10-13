"""Synthetic refusal controls for the proposed L sibling-history continuation."""
import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from orchestrator import l_funded_history as h

class HistoryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.lane = self.root / "sibling"
        self.lane.mkdir()
        self.global_db = sqlite3.connect(":memory:")
        self.global_db.row_factory = sqlite3.Row
        self.addCleanup(self.global_db.close)
        self.local = sqlite3.connect(self.lane / "jobs.sqlite")
        self.local.row_factory = sqlite3.Row
        self.addCleanup(self.local.close)
        self.global_db.executescript("CREATE TABLE autonomy_runs(id TEXT,status TEXT,binding TEXT);"
            "CREATE TABLE autonomy_calls(id TEXT,change_id TEXT,status TEXT,charge INTEGER);")
        self.local.executescript("CREATE TABLE manual_calls(id TEXT,stage TEXT,attempt INTEGER,status TEXT);"
            "CREATE TABLE manual_state(id INTEGER,payload TEXT);"
            "CREATE TABLE manual_account(id INTEGER,payload TEXT,version INTEGER);")
        oldrows = [dict(id="old-"+str(i),stage="run_spec_review",attempt=i+1,status="COMPLETE") for i in range(24)]
        newrows = [dict(id=h.AUTHOR,stage="run_spec_author",attempt=13,status="UNCERTAIN"),
                   dict(id=h.REVIEW,stage="run_spec_review",attempt=12,status="COMPLETE")]
        for r in oldrows+newrows:
            self.local.execute("INSERT INTO manual_calls VALUES(:id,:stage,:attempt,:status)",r)
            self.global_db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?)",(r["id"],h.SIBLING,r["status"],5))
        owner = dict(id=h.SIBLING,status="ACTIVE",binding="original")
        self.global_db.execute("INSERT INTO autonomy_runs VALUES(:id,:status,:binding)",owner)
        state = dict(phase="BLOCKED",reason="BOUNDED_PROVENANCE_REVIEW_REVISE")
        self.local.execute("INSERT INTO manual_state VALUES(1,?)",(json.dumps(state),))
        self.local.execute("INSERT INTO manual_account VALUES(1,'count26',26)")
        self.local.commit()
        config = {"run_id":h.SIBLING}
        raw = json.dumps(config).encode()
        (self.lane/"lane.json").write_bytes(raw)
        (self.lane/"preparation-plan.json").write_bytes(b"unchanged plan")
        globals = [dict(r) for r in self.global_db.execute("SELECT * FROM autonomy_calls ORDER BY rowid")]
        prior = dict(config=config,owner=owner,lane=str(self.lane),local_calls=oldrows,
                     global_calls=globals[:24],plan_sha256=h.digest(b"unchanged plan"),
                     state_row=dict(id=1,payload=json.dumps(dict(phase="BLOCKED",
                        reason="OUTPUT_VALIDATION_REFUSED: ANALYSIS_REVISION_ROUND"))))
        self.scope = {"prior":prior}
        self.checkpoint = dict(run=h.SIBLING,config=config,owner=owner,lane=str(self.lane),
            local_rows=oldrows+newrows,global_rows=globals,config_sha256=h.digest(raw),
            state_row=dict(self.local.execute("SELECT * FROM manual_state").fetchone()),
            account_row=dict(self.local.execute("SELECT * FROM manual_account").fetchone()))
        self.accounts = SimpleNamespace(db=self.global_db)
        mock=patch("orchestrator.colab_arm_question.path",side_effect=lambda a,p:Path(p))
        mock.start();self.addCleanup(mock.stop)
        self.proof={"call":h.AUTHOR,"native_exit":"ok","original_status":"UNCERTAIN",
                    "new_calls":0,"scientific_acceptance":False}
        self.seen=0

    def qualify(self, accounts, db):
        self.assertIs(accounts,self.accounts)
        self.assertEqual(db.execute("PRAGMA query_only").fetchone()[0],1)
        with self.assertRaises(sqlite3.OperationalError):
            db.execute("UPDATE manual_account SET version=0")
        self.seen+=1
        return self.proof

    def check(self):
        return h.preserved(self.accounts,self.scope,self.checkpoint,self.qualify)

    def test_exact_history_and_readonly_qualified_additions_preserve_both_databases(self):
        before=("\n".join(self.global_db.iterdump()),"\n".join(self.local.iterdump()))
        self.assertEqual(self.check(),self.proof)
        self.assertEqual(self.seen,1)
        self.assertEqual(before,("\n".join(self.global_db.iterdump()),"\n".join(self.local.iterdump())))

    def test_original_charge_change_refused(self):
        self.global_db.execute("UPDATE autonomy_calls SET charge=0 WHERE id='old-0'")
        with self.assertRaisesRegex(ValueError,"ORIGINAL_GLOBAL_CHANGED"):self.check()

    def test_original_prefix_not_replaced_by_current_snapshot(self):
        self.checkpoint["local_rows"][0]={**self.checkpoint["local_rows"][0],"status":"FAILED"}
        with self.assertRaisesRegex(ValueError,"ORIGINAL_PREFIX"):self.check()

    def test_extra_unapproved_call_refused(self):
        self.global_db.execute("INSERT INTO autonomy_calls VALUES('extra',?,'COMPLETE',5)",(h.SIBLING,))
        with self.assertRaisesRegex(ValueError,"GLOBAL_HISTORY"):self.check()

    def test_unknown_uncertain_addition_refused(self):
        self.checkpoint["local_rows"][24]={**self.checkpoint["local_rows"][24],"id":"unknown"}
        with self.assertRaisesRegex(ValueError,"EXACT_ADDITIONS"):self.check()

    def test_local_mutation_refused(self):
        self.local.execute("UPDATE manual_calls SET status='COMPLETE' WHERE id=?",(h.AUTHOR,))
        self.local.commit()
        with self.assertRaisesRegex(ValueError,"LOCAL_HISTORY"):self.check()

    def test_state_cannot_advance_unnoticed(self):
        self.local.execute("UPDATE manual_state SET payload='{}'");self.local.commit()
        with self.assertRaisesRegex(ValueError,"STATE_CHANGED"):self.check()

    def test_account_cannot_be_reset(self):
        self.local.execute("UPDATE manual_account SET version=0");self.local.commit()
        with self.assertRaisesRegex(ValueError,"ACCOUNT_CHANGED"):self.check()

    def test_owner_cannot_change(self):
        self.global_db.execute("UPDATE autonomy_runs SET binding='new'")
        with self.assertRaisesRegex(ValueError,"OWNER_CHANGED"):self.check()

    def test_plan_cannot_change(self):
        (self.lane/"preparation-plan.json").write_text("changed")
        with self.assertRaisesRegex(ValueError,"PLAN_CHANGED"):self.check()

    def test_config_bytes_cannot_change(self):
        (self.lane/"lane.json").write_text(json.dumps({"run_id":h.SIBLING})+" ")
        with self.assertRaisesRegex(ValueError,"CONFIG_CHANGED"):self.check()

    def test_qualification_required_and_cannot_accept_science(self):
        for key,value in [("call","unknown"),("native_exit","failed"),("original_status","COMPLETE"),
                          ("new_calls",1),("scientific_acceptance",True)]:
            original=copy.deepcopy(self.proof)
            self.proof[key]=value
            with self.assertRaisesRegex(ValueError,"INSTALLED_QUALIFICATION"):self.check()
            self.proof=original

    def test_qualification_error_propagates(self):
        def failed(*args):raise ValueError("installed proof failed")
        with self.assertRaisesRegex(ValueError,"installed proof failed"):
            h.preserved(self.accounts,self.scope,self.checkpoint,failed)

if __name__=="__main__":unittest.main()

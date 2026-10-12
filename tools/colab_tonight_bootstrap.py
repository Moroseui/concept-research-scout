"""One operator-authorized administrative call51 to review the cap repair."""
from pathlib import Path
import hashlib,json
CHANGE='colab-tonight-cap-20261012'
DAY='2026-10-12'
AUTHORITY='23a45f2fdf214ba69f808393973fb5b6bff38a72a50dd6601106647a919e4cbd'
def require(ok,why):
    if not ok:raise ValueError('TONIGHT_REVIEW_BOOTSTRAP_'+why)
def allow_once(db,limits,manifest,packet,source,operator,day):
    require(db.in_transaction,'TRANSACTION_REQUIRED')
    require(day==DAY and manifest['change_id']==CHANGE and manifest['round']==1
            and manifest.get('predecessor')is None and manifest['source_sha']==source,'EXACT_REQUEST')
    raw=json.dumps(manifest,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    require(hashlib.sha256(raw).hexdigest()==packet,'PACKET_BINDING')
    p=Path(operator)
    require(not p.is_symlink()and hashlib.sha256(p.read_bytes()).hexdigest()==AUTHORITY,'OPERATOR_AUTHORITY')
    require(limits.DAILY==50,'PRIOR_LIMIT')
    require(db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(DAY,)).fetchone()[0]==50,'CALL51_ONLY')
    require(not db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'RUNNING_CALL')
    require(not db.execute('SELECT 1 FROM autonomy_calls WHERE id=? OR change_id=?',(packet,CHANGE)).fetchone(),'ONE_USE')
    # The caller has already authenticated every preserved uncertain terminal
    # proof. This affects only the one native administrative reservation.
    prior=limits.daily_allowance
    require(prior(day)['limit']==50,'PRIOR_DATED_LIMIT')
    consumed=[]
    def one_admission(selected_day):
        require(selected_day==DAY and db.in_transaction and not consumed,'ONE_DATED_ADMISSION')
        require(db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(DAY,)).fetchone()[0]==50,'CALL51_ONLY')
        consumed.append(True)
        return {'limit':100,'authority_sha256':AUTHORITY}
    limits.daily_allowance=one_admission
    return 50

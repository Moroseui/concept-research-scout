"""Read-only measurement of recorded dispatch attempts across all repository branches."""
import argparse
from collections import Counter
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
import subprocess


def measure(pages,as_of,days=28):
    end=datetime.fromisoformat(as_of.replace('Z','+00:00'))
    start=(end-timedelta(days=days-1)).replace(hour=0,minute=0,second=0,microsecond=0)
    runs={}
    total=None
    for page in pages:
        if total is None:total=page['total_count']
        if total!=page['total_count']:raise ValueError('dispatch list changed; remeasure a consistent snapshot')
        for run in page['workflow_runs']:runs[run['id']]=run
    if len(runs)!=total:raise ValueError('incomplete dispatch pagination')
    daily=Counter();selected=[]
    for r in runs.values():
        stamp=datetime.fromisoformat(r['created_at'].replace('Z','+00:00'))
        if start<=stamp<=end:
            daily[stamp.date().isoformat()]+=r['run_attempt']
            selected.append({k:r[k] for k in ['id','created_at','run_attempt','head_branch','path','event','conclusion']})
    # Attempt timestamps are unavailable in this snapshot; if reruns occurred,
    # separate run-attempt API evidence is needed before an exact daily claim.
    reruns=any(r['run_attempt']!=1 for r in selected)
    peak=max(daily.values(),default=0)
    return {'measured_at':as_of,'window_start':start.strftime('%Y-%m-%dT%H:%M:%SZ'),'calendar_dates':days,'last_date_partial':True,
            'all_recorded_dispatch_runs':total,'window_runs':len(selected),'daily_attempts':dict(sorted(daily.items())),
            'observed_peak':peak,'recommended_n':4*peak if peak and not reruns else None,'recommended_hard_ceiling':8*peak if peak and not reruns else None,
            'recommendation_ratified':False,'cross_branch':True,'attempt_timestamps_unresolved':reruns,'runs':sorted(selected,key=lambda r:r['created_at']),
            'limitations':['Deleted/unavailable historical runs cannot be counted.','This is recorded job activity, not model calls or dollar spend.','Future repeats/new run IDs and rerun attempts count even when artifacts replay.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pages',nargs='+',required=True);p.add_argument('--as-of',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    r=measure([json.loads(Path(f).read_text()) for f in a.pages],a.as_of)
    Path(a.output).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['window_runs','observed_peak','recommended_n','recommendation_ratified']}))

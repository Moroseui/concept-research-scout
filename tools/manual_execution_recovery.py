"""Explicit one-attempt infrastructure re-emission; no model or job launch."""
import argparse
import json
from pathlib import Path
from orchestrator.manual_executor import ManualExecutor,lock

def main():
    p=argparse.ArgumentParser()
    for name in ('state','failure','authorization','decision','package','destination'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--job',required=True);a=p.parse_args()
    with lock(a.state/'driver.lock'):
        if (a.state/'HALT').exists():raise ValueError('OPERATOR_HALT')
        result=ManualExecutor(a.state/'jobs.sqlite').reemit_infrastructure_failure(
            a.job,a.failure,a.authorization,a.decision,a.package,a.destination)
        print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()

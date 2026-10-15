"""Preserve exact existing science/operational bindings; add storage reliability explicitly."""
from pathlib import Path
import hashlib
import json
import sys

PINNED = {
 "A1_pnormct": {
  "colab_operational_resume.py":"2802300857a76eeec165e75b05b84931ae303e1be58834d8bd8346827e118cb0",
  "colab_epoch_watchdog.py":"4191f442775f1d8d8baa1f6d3059742daf73730a4d85e1deff383964795644cc",
  "identity":"8ddef576e07622c10a2101c88bf56ec0dcd3be661e7c14a86abec4b1a263c989"},
 "A1_pnorm_v2": {
  "colab_operational_resume.py":"230b7512eaa3c8cda629dde4fa8eb307ce180038f21a974cf6e6f5e9d94ae571",
  "colab_epoch_watchdog.py":"4191f442775f1d8d8baa1f6d3059742daf73730a4d85e1deff383964795644cc",
  "colab_private_output.py":"80fcad04110062a5b44e77c5ffe30faafda2158e95871be4a9737418dfdff930",
  "identity":"be8fd7fccc89cce3ad186e1d6c302f94f8c2ad4918ce8ee164e15a5558593fbf"}
}
def checked(arm):
    if arm not in PINNED:raise RuntimeError("UNKNOWN_RESUME_ARM")
    root=Path(__file__).parent
    for name,pin in PINNED[arm].items():
        if name=="identity":continue
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=pin:
            raise RuntimeError("ORIGINAL_OPERATIONAL_SOURCE_CHANGED")
    import colab_operational_resume as original
    if original.policy_identity()!=PINNED[arm]["identity"]:
        raise RuntimeError("ORIGINAL_OPERATIONAL_BINDING_CHANGED")
    return original

def child(path,arm):
    original=checked(arm)
    from colab_private_output import install as folder
    from colab_storage_reliability import install as reliability
    prior=original.install_adapter
    def install(m):
        result=prior(m)
        folder(m)
        storage=reliability(m)
        print("STORAGE_REPAIR "+json.dumps(storage),flush=True)
        return result
    original.install_adapter=install
    try:return original.child(path,arm)
    finally:original.install_adapter=prior

def run_notebook(m,arm,folds):
    original=checked(arm)
    from colab_private_output import install as folder
    import colab_epoch_watchdog as watchdog
    folder(m)
    previous=watchdog.supervise
    def dispatch(argv,token,**kwargs):
        expected=[sys.executable,"-u",str(Path(original.__file__)),"--child",m.__file__,arm]
        if argv!=expected:raise RuntimeError("UNEXPECTED_TRAINING_COMMAND")
        return previous([*argv[:2],str(Path(__file__)),*argv[3:]],token,**kwargs)
    watchdog.supervise=dispatch
    try:return original.run_notebook(m,arm,folds)
    finally:watchdog.supervise=previous

if __name__=="__main__":
    if len(sys.argv)!=4 or sys.argv[1]!="--child":raise RuntimeError("EXACT_CHILD_REQUIRED")
    child(sys.argv[2],sys.argv[3])

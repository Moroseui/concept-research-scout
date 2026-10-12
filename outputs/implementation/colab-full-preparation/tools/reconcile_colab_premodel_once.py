"""Explicit reconciliation after independent approval; never launches a call."""
from pathlib import Path
import os
import sys
import json
from orchestrator import colab_premodel_terminal as proof
from tools.colab_simple_runtime import reviewed
from orchestrator.autonomy_accounting import BatchAccounts

def main():
    if os.getuid() != 1003 or os.getgid() != 1003 or not sys.flags.no_user_site:
        raise ValueError("SERVICE_OWNER_REQUIRED")
    folder = Path(sys.argv[1])
    result, manifest = reviewed(folder)
    root = Path(__file__).resolve().parents[1]
    for name, pin in manifest["source_files"].items():
        if proof.sha((root / name).read_bytes()) != pin:
            raise ValueError("EXACT_REVIEWED_RECONCILIATION_SOURCE_REQUIRED")
    if result["verdict"] != "APPROVE":
        raise ValueError("INDEPENDENT_APPROVAL_REQUIRED")
    accounts = BatchAccounts("/var/lib/research-system-autonomy/reviews")
    try:
        return proof.reconcile(accounts)
    finally:
        accounts.db.close()

if __name__ == "__main__":
    os.umask(0o077)
    print(json.dumps(main(), sort_keys=True))

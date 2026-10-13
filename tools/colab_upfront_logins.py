"""Move every browser interaction into the first executable Colab cell.

Scientific modules and input/lease checks are unchanged. The small transformation
recognizes exact delivery setup fragments and refuses unknown variants.
"""
import copy

READY = "All logins done, you can leave now"
AUTH = "drive.mount('/content/drive')\nauth.authenticate_user()\n"
SNAPSHOTS = {
    "A1_pnormct": (
        "snapshot = _message.blocking_request('get_ipynb', timeout_sec=60)['ipynb']\n"
        "Path('/content/delivery-executed.ipynb').write_text(json.dumps(snapshot))\n"
    ),
    "A1_pnorm_v2": (
        "notebook = _message.blocking_request('get_ipynb', timeout_sec=60)\n"
        "pipeline.need(isinstance(notebook, dict) and isinstance(notebook.get('ipynb'), dict), 'Cannot capture executed notebook')\n"
        "Path('/content/delivery-executed.ipynb').write_text(json.dumps(notebook['ipynb'], ensure_ascii=False))\n"
    ),
    "A1_L": (
        "nb = _message.blocking_request('get_ipynb')['ipynb']\n"
        "for cell in nb['cells']:\n"
        "    if cell.get('cell_type') == 'code':\n"
        "        cell['outputs'] = []\n"
        "        cell['execution_count'] = None\n"
        "Path('/content/delivery-executed.ipynb').write_text(json.dumps(nb, ensure_ascii=False))\n"
    ),
}

def first_cell(profile):
    if profile not in SNAPSHOTS:
        raise ValueError("Unknown login profile")
    # No pipeline import, dependency installation, patient I/O or credential-file
    # access before the ready line. The provider owns both existing login flows.
    code = """# FIRST CELL: all logins and browser-dependent setup (about two minutes)
from google.colab import drive, auth, _message
from pathlib import Path
import json, signal, time
print("Complete the Drive and API login prompts now. Stay until the all-logins-done line.", flush=True)
_login_started = time.monotonic()
def _login_timeout(signum, frame):
    raise TimeoutError("Initial login did not finish within two minutes. No installation or training started.")
if signal.getitimer(signal.ITIMER_REAL) != (0.0, 0.0):
    raise RuntimeError("Unexpected existing login timer; no work started")
_login_old_handler = signal.signal(signal.SIGALRM, _login_timeout)
signal.setitimer(signal.ITIMER_REAL, 120)
try:
    drive.mount('/content/drive', timeout_ms=60000)
    auth.authenticate_user()
    _snapshot_reply = _message.blocking_request('get_ipynb', timeout_sec=30)
    if not isinstance(_snapshot_reply, dict) or not isinstance(_snapshot_reply.get('ipynb'), dict):
        raise RuntimeError('Cannot capture executed notebook')
    _snapshot = _snapshot_reply['ipynb']
"""
    if profile == "A1_L":
        code += """    for _cell in _snapshot['cells']:
        if _cell.get('cell_type') == 'code':
            _cell['outputs'] = []
            _cell['execution_count'] = None
"""
    code += """    Path('/content/delivery-executed.ipynb').write_text(json.dumps(_snapshot, ensure_ascii=False))
finally:
    signal.setitimer(signal.ITIMER_REAL, 0)
    signal.signal(signal.SIGALRM, _login_old_handler)
print("All logins done, you can leave now", flush=True)
"""
    return {"cell_type": "code", "metadata": {"tags": ["all-interactions-first"]},
            "source": [code], "execution_count": None, "outputs": []}

def frontload(notebook, setup_index, profile):
    result = copy.deepcopy(notebook)
    setup = "".join(result["cells"][setup_index]["source"])
    snapshot = SNAPSHOTS[profile]
    if setup.count(AUTH) != 1 or setup.count(snapshot) != 1:
        raise ValueError("Exact known authentication and snapshot blocks required")
    setup = setup.replace(AUTH, "").replace(snapshot, "")
    if any(token in setup for token in ("drive.mount(", "auth.authenticate_user(", "_message.blocking_request(")):
        raise ValueError("Unexpected later browser interaction")
    result["cells"][setup_index]["source"] = [setup]
    first_code = next(i for i, cell in enumerate(result["cells"]) if cell["cell_type"] == "code")
    result["cells"].insert(first_code, first_cell(profile))
    result.setdefault("metadata", {})["interaction_policy"] = {
        "schema": "all-interactions-first/v1", "deadline_seconds": 120,
        "ready_message": READY, "separate_existing_drive_api_logins": True,
        "no_later_browser_requests": True,
    }
    return result

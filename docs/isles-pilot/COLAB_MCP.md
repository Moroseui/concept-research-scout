# Colab integration check — execution still unverified

Installed client: **codex-cli 0.153.4**; local `codex mcp list` reports no
configured server. Official server inspected at
[googlecolab/colab-mcp](https://github.com/googlecolab/colab-mcp), commit
**b9ab3899e0f1fa493390b1fd6d54aa2e464ecdf1**, package 1.0.1. Its Python
requirement is >=3.13 and FastMCP is pinned to 2.14.5.

The official README requires a local client supporting
`notifications/tools/list_changed`; it does not list Codex among its examples.
The inspected middleware sends that notification after browser connectivity
changes and then exposes the browser's notebook tools. OpenAI's
[official MCP documentation](https://developers.openai.com/codex/mcp) documents
stdio server configuration, but does not establish that this installed version
refreshes the Colab tool list correctly. Compatibility is **not yet proven**.

## What was actually tested

The source was installed in isolated `/tmp/isles-pilot-venv`. The versioned
`campaigns/isles24-pilot/colab/probe_mcp.py` initializes a real MCP stdio session
and lists its tools, without opening a browser or connecting data.
The first attempt timed out under restricted localhost permissions; repeating
with localhost permission succeeded. Server name ColabMCP, reported framework
version 2.14.5, one tool: `open_colab_browser_connection`.
This is a generic MCP handshake, not proof of Codex execution compatibility.
No authenticated browser/runtime is connected. No notebook execution or result
retrieval through Colab MCP has happened. No cloud resource was provisioned.

The synthetic notebook executes a standard-library script to write the exact
bytes `ISLES pilot synthetic execution: 6 * 7 = 42` plus a newline. A separate
retrieval operation reads the file back and returns its text and SHA-256. Local
execution checks the same code path; it is labeled local, never Colab execution.
No patient data, Drive mount, GPU or credentials are involved in this notebook.

## Required operator connection and acceptance test

On the same machine as the browser, configure the installed test server:

```bash
codex mcp add colab-pilot -- /tmp/isles-pilot-venv/bin/colab-mcp
```

That path is temporary: for ongoing use install the pinned official commit in
a durable Python >=3.13 environment and use its `colab-mcp` executable. The
command changes the user's Codex MCP configuration; it has been prepared, not
run. Restart Codex if required to load the configuration. Sign into Google in
the local browser, allow the Colab connection, and connect a CPU runtime.
Use `open_colab_browser_connection` only for the synthetic notebook first.
Do not share its connection URL/token or put them in Git.

Acceptance requires all of: notebook tools appear in Codex after connection;
Codex invokes execution of the synthetic write cell; Codex separately retrieves
the written result; returned text/hash equal the fixed expected bytes; the
execution and retrieval outputs are saved as a receipt. If tools fail to refresh,
record the failure for 0.153.4 and preserve the manual route. Do not assert that
restarting resolves the issue until tested. Do not connect patient data until
this end-to-end test succeeds and the experiment review gate is satisfied.

Manual fallback: open `synthetic_execution.ipynb` in Colab and Run All, then
retain both cell outputs. For P001, use its separate reviewed notebook and the
existing Drive/archive. Patient outputs remain private; aggregate return
validation is handled by the versioned P001 validator. The research workflow
does not depend on MCP availability.


## Registered connection test — 2026-09-05

The server is now registered as `colab-pilot` at the durable executable
`/home/partho/.local/share/isles-colab-mcp/bin/colab-mcp`. Client 0.153.4;
colab-mcp 1.0.1, FastMCP/protocol server 2.14.5, MCP SDK 1.29.1; official
source pin b9ab3899e0f1fa493390b1fd6d54aa2e464ecdf1.

**Complete remote test did not pass.** Google's actual
open_colab_browser_connection returned false after its 60-second wait. The
operator reported that no tab opened. Only the connection tool remained
available; no remote notebook cell was loaded or executed and no retrieval
occurred. The exact requested notebook was read from Git, not run locally as a
substitute. COLAB_MCP_TEST_20260905.json records its hash, source pin, expected
payload/hash and null remote results.

A token-free xdg-open probe in the local execution context returned exit 4 and
`WSL … UtilBindVsockAnyPort:307: socket failed 1`. The Python browser backend
is xdg-open, and HTTPS is associated with Firefox under WSL. This supports a
desktop-handoff failure, but is not the MCP tool's own captured browser stderr.
There is no evidence that Codex ignored a successful tool-list-change event.

A separate synthetic diagnostic of the installed session.py confirmed that
its timeout cancels the pending proxy initialization task; a second wait raises
CancelledError. The production server was not patched. After repairing browser
handoff, start a fresh registered MCP server session before retrying. No broad
permission changes, approval bypass, Drive mount, patient execution, GPU request
or paid provisioning occurred. Connection tokens were not copied into receipts.


## Windows browser through WSL — 2026-09-05

The operator confirmed the ordinary Colab homepage opened in Windows. The
server interpreter also dispatched the homepage using its filtered process
environment plus the following scoped settings in ~/.codex/config.toml:

```toml
[mcp_servers.colab-pilot]
command = "/home/partho/.local/share/isles-colab-mcp/bin/colab-mcp"
env_vars = ["WSL_INTEROP", "WSL_DISTRO_NAME"]

[mcp_servers.colab-pilot.env]
BROWSER = "/mnt/c/Windows/explorer.exe %s &"
```

Python interprets the trailing & as BackgroundBrowser, without a shell wrapper.
Synchronous Explorer returned 1 without stderr in both normal and MCP-derived
environments; background dispatch returned true. That return alone does not
establish a Colab connection. Scoped env_vars forwarding is documented in
[the official MCP configuration guide](https://developers.openai.com/codex/mcp).
No ephemeral interoperability socket path is hardcoded.

Windows PowerShell successfully retrieved a token-free HTTP response from a
WSL IPv4 loopback listener. This verifies that path only, not a browser
WebSocket handshake. The receipt retains the initial byte-array formatting
mismatch and its explicit decoding.

The official connection retry timed out awaiting tools/call after 120s. The
live registered process still lacked BROWSER and WSL_INTEROP: saved settings
had not reloaded. No notebook tools appeared. The current CLI/tool interface
provides no server reload command; a fresh Codex session is required before
testing the final configuration. Its success remains unverified.
COLAB_MCP_WSL_TEST_20260905.json records these distinct checks. No remote
acquisition, write or retrieval occurred; the complete test has not passed.
No approval rejection occurred during the targeted Windows/config operations.


## Corrected Windows URL handoff — 2026-09-05

The next fresh registered process did load the Explorer BROWSER setting and
both WSL variables. The official connection returned false; the operator
reported that File Explorer opened instead of the browser. This supersedes
any inference that Explorer background dispatch reliably opens connection URLs.
Notebook tools remained absent and no remote notebook execution occurred.

Replaced only the server-scoped BROWSER value with
`/home/partho/.local/share/isles-colab-mcp/bin/open-colab-windows %s`.
The local helper accepts only HTTPS colab.research.google.com URLs and invokes
Windows PowerShell Start-Process. It passes the URL through stdin, never through
interpolation into PowerShell source, and suppresses child output to avoid
logging connection URLs. Existing server command, package and WSL forwarding
remain unchanged. The helper SHA-256 and test evidence are in
COLAB_MCP_WINDOWS_HELPER_TEST_20260905.json.

Python's launcher in the registered process environment with only BROWSER
updated returned true for the ordinary homepage. The operator confirmed Colab
opened in the Windows browser. Mocked synthetic tests verified intact fragment
passing and rejection of four invalid URLs without launching a process.
The corrected helper has not yet been exercised by the official connection
because the existing process retains its earlier BROWSER setting. Restart Codex
before retrying. Remote acquisition, write and separate retrieval remain undone.


### Connected MCP, notebook tools unavailable — 2026-09-05

With the corrected Windows helper, the official registered connection returned
true; a second connection-status call also returned true. Codex 0.153.4 logged
receipt of the server tool-list-change notification. Repeated discovery in this
active turn still exposed only open_colab_browser_connection. This establishes
a working browser/MCP handshake but not a working notebook execution route.
The precise internal refresh failure remains undetermined. No remote notebook
was loaded, executed or retrieved. The exact notebook bytes at 1a81c037 were
rehash-verified locally without running its cells. The complete test has not
passed. COLAB_MCP_CONNECTED_TEST_20260905.json records results and a token-free
log excerpt. Next diagnostic: keep the connected tab open and check tool
availability on a new conversation turn, without another server restart.


## Complete remote execution and retrieval — 2026-09-05

Under a different MCP client (Claude Code, claude-fable-5, server name
`colab-worker`), a fresh official browser connection returned true and the full
notebook tool set appeared in the same turn: get_cells, add/update/move/delete
cell and run_code_cell. The connected session exposed a fresh blank notebook;
the exact cell sources of `synthetic_execution.ipynb` at 1a81c037 (notebook
SHA-256 3c050e1f4552bc42e469b3c448930efbf7853a79bdc55d0f3969f52d3e9e7741) were
written into it and read back byte-identical before any execution.

The acquisition cell executed remotely and passed its own pin/cleanliness
checks for source d6a1184b4378e849213fd887a6f7b103fb1a64d5. The synthetic write
cell and, in a separate call, the retrieval cell both returned CompletedProcess
returncode 0. Because the pinned cells' subprocess stdout was not persisted in
the notebook outputs over MCP, one clearly labeled supplementary transport cell
was appended after the pinned cells; it re-ran only the read-only `retrieve`
operation of the same versioned smoke.py and printed token-free runtime
evidence. Returned text and SHA-256 equal the fixed expected payload
(776c3a10f968497c0ced99011f78f8375079c6f7545dab2445921e298473a800). Runtime
evidence shows genuine Colab (COLAB_RELEASE_TAG present, /content exists),
Python 3.13.15, and no nvidia-smi: a CPU runtime. No Drive mount, patient
data, GPU, paid provisioning, remote cleanup or branch change occurred, and no
connection token was recorded. COLAB_MCP_REMOTE_EXECUTION_20260905.json is the
receipt. The acceptance test defined above has now passed end to end; the
codex-cli 0.153.4 tool-refresh failure remains recorded separately and
unresolved for that client.

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

# Future bounded job profiles and actual prompt sources

Observed client versions: Codex CLI 0.153.4; Claude Code 2.1.222. Existing private
Colab server installation/config/browser environment is unchanged. No global
Claude registration, token export, Drive mount or server restart was performed
for configuration changes.

| Source | Actual evidence | Treatment |
|---|---|---|
| Codex host sandbox | repository .git is read-only; private ~/.local paths and network/GUI require escalation | current session policy cannot be overridden by repository profiles; request scoped authorization where needed |
| Network sandbox | gh auth appeared invalid with DNS blocked, succeeded outside sandbox | not a real credential failure |
| Claude tool permissions | dontAsk can deny tools outside explicit allowlist | future author/reviewer profile supplies only required tools; no broad bypass |
| Browser consent | open_colab_browser_connection returned false in first monitor | human interaction/authentication remains a real blocker |
| Output-read contract | second monitor rejected get_cells without includeOutputs=false | future pre-tool hook denies the read before MCP, rather than accepting a bad receipt |
| Drive authorization | must happen visibly in browser | never hide consent in captured console |

`configs/pilot/agents-unattended.toml` is copied only into new disposable system
stage roots. Codex uses workspace-write, sandbox tool network disabled,
approval_policy=never (unavailable permissions fail rather than prompt). Claude
uses dontAsk, a bounded tool list and an empty strict MCP configuration. These
are not OS egress allowlists: provider authentication still requires network; these settings alone are not an OS firewall. Only public
source/specification and permitted aggregate context may be staged. No patient
files, private evidence backups or credentials may be copied into a stage root.
Managed policies can still deny execution; never replace them with a bypass.
The root AGENTS.toml and all P001 review-bound files remain unchanged.

`configs/pilot/colab-worker-future.json` is an additive --settings profile for
future worker sessions only, alongside the existing private --mcp-config and
--strict-mcp-config. Its PreToolUse hook refuses missing/true includeOutputs.
The hook only adds a denial; it never grants or rewrites permission requests.
The adapter still binds exact cells, verifies source readback, and captures logs
privately. The current snapshot deliberately does not load this profile.

Validation: installed CLIs accept the listed launch options; synthetic guard
checks reject missing/true/string-valued output flags and permit boolean false.
Real campaign discussion exercises the new author/reviewer profile. Synthetic
SQLite demo exercises event progression and the private-return inbox. These
checks do not establish unattended browser consent or a deployed network policy.

Future worker host permissions: write only its private job directory and allowed
stage workspace; read installed CLIs, authentication stores (never expose them),
reviewed snapshot, and worker-only MCP configuration; reach provider login/API,
GitHub (publication process only), Colab websocket/localhost and Windows browser
interop. Browser/Drive interaction and public-history cleanup remain explicit
operator gates. Job failures create fixed-status inbox entries. Unknown dispatch
outcomes require reconciliation; never retry a mutation based on missing output.

Official references: [Codex sandbox/security](https://developers.openai.com/codex/security),
[Codex configuration](https://developers.openai.com/codex/config-reference),
[Claude hooks](https://code.claude.com/docs/en/hooks-guide).

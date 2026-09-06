# Publication boundary: covered routes and remaining credential bypass

This is an application-enforced boundary, not universal GitHub enforcement.
Inspection used authenticated read-only GitHub APIs on 2026-09-06. The current
local credential reports admin/maintain/push permission. Main is unprotected.
The active results ruleset prohibits deletion and non-fast-forward updates, with
no bypass actors, but does not inspect content or prevent fast-forward exposure.
Default Actions permissions are read-only and Actions cannot approve PRs.
No permissions, visibility, rulesets or credentials were changed.

| Route | Before-publication enforcement | Scope / limitation |
|---|---|---|
| `workflow_boundary.publish` pilot code/docs | Whole outgoing history, explicit before/source/destination, permitted paths/types, secret/content scans, empty notebook outputs, rejected contaminated ancestry; then exact remote compare-and-swap | Existing pilot-only authorization remains; post-push CI is additional detection. |
| `git_publication.publish` reusable reviewed-operation route | Exact caller-supplied operation grant and commit:path→SHA256 inventory; scans every newly reachable commit and changed blob relative to every parent, including deleted intermediate files; validates before push | Supports other branch names/merge histories as an API, but no new production branch grant is supplied. A JSON grant does not authenticate an operator; callers must establish authorization separately. Results/clinical payloads are not authorized by a byte inventory. |
| `scout._push_checkpoint` / CI `_commit_all` | Now calls the controlled pilot publisher with explicit source/before/destination request; absent binding refuses and preserves local checkpoint | Removed unconditional `git push` and automatic pull/rebase retry. Legacy CI must supply a reviewed checkpoint request; no implicit main write. |
| All seven human controls: Actions artifact and Summary | Exact three-file export, hash/type/size/symlink/content checks before artifact-name release or Summary write; shared public-text validator; upload only validated directory | Only permitted aggregate/proposal records. No raw console/checkpoint upload. Old validated replay is revalidated. |
| Infrastructure failure Summary | Fixed message through the shared public-text validator | No raw exception or submitted question is interpolated into Summary. Action/dependency logs are separate public runner logs, not claimed private. |
| Proposed limiter state-ref writes | Closed metadata-only schema; exact one-file tree; explicit fixed state ref; validation before commit creation and leased append; conflicts reload with capped retries | Inactive. Needs operator-approved initialization and writer permission. No scientific data, questions or model outputs enter state. |
| Proposed limiter notices | Closed status metadata, validated Summary and fixed warning annotation; durable ledger notification record | No guaranteed phone push/email delivery. Inactive until policy/permission approval. |
| Numbered/P001 notebooks | Reviewed export/return validators; current generated notebooks do not commit/push results | Local private outputs and original console have their own return route. Historical frozen launchers may contain unsafe old push code: not authorized automation routes and must not be used for publication. No regeneration/edit of frozen P001 cells here. |
| 047 cleanup rehearsal | No push is executed; only an exact proposed remote command is produced after private rehearsal | Rewrite remains reserved; this batch does not enable it. |
| PR description/update | Operator-reviewed permitted documentation and validated metadata supplied as exact body file | Administrative CLI can bypass repository code; review the body before API publication. No patient/private material is attached. |

## What can bypass this

The existing local credential can run direct `git push` or create/update GitHub
Git blobs/trees/commits/refs and Contents API files. It can change workflows and
repository settings. A manual/direct push need not call our Python validator.
The existing local AGENTS.toml also permits Claude Bash(git:*) and network-enabled
Codex operation; a local model process with access to the operator's stored GitHub
authentication can bypass the wrapper too. The author-operated review invocation
has no tools, and hosted scientific transport has tools disabled, stripped GitHub
tokens and read-only workflow permissions; those narrower routes do not remove
the outer/local credential capability. AGENTS.toml and credential storage are not
silently rewritten in this closeout.
Legacy source fetched outside the reviewed automation path can do the same when
given a write credential. On a public repository, post-push CI is too late to
prevent exposure. Results deletion/non-fast-forward protection is not a content
policy. PR checks/rules alone do not keep disallowed bytes from arriving on an
unprotected feature branch.

No claim of universal secret/clinical-data recognition is made for text scanners.
Closed artifact schemas, explicit inventories, source review and credentials
restricted to the publisher must work together. Existing frozen source contains
cohort identifier constants; preserving those reviewed source bytes is not new
permission to publish patient records. New archive/image/table payload types are
rejected by the controlled code publisher; case-linked JSON/JSONL/text records
are refused, but arbitrary obfuscated clinical prose cannot be proven safe by regex.

## Permission decision required for stronger enforcement

Before claiming all-public-branch protection, choose an exclusive publication
identity/service boundary: only that writer may mutate refs/content, with callers
submitting validated candidate bytes rather than holding a bypassing write/admin
credential. Configure branch/ruleset coverage and protect the writer's code and
policy from its callers. This likely needs credential separation or removal of
existing bypass capabilities; **no new credential or scope change is authorized
here**. Merely adding a local pre-push hook is insufficient because `--no-verify`
and API writes bypass it. The concrete current promise is pre-publication checks
on the controlled routes listed above, with honest fail-closed refusal elsewhere.

For limiter activation specifically, `contents:write` on the existing Actions
token would be repository-wide, not state-ref scoped. Do not grant it to model
steps. A separate admission job with no model credentials is prepared and still read-only.
An operator-protected reset path and ref restrictions remain permission/design
choices, not silently applied credential changes. The current workflow retains
read-only permissions, so activating the proposed config alone refuses state writes.

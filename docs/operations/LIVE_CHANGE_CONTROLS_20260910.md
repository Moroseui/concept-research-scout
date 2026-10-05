# Propose and inspect a saved change

After the reviewed wrapper is installed, a human administrator using the existing
authenticated root SSH route can propose a change with one command:

```sh
research-system-live-control propose 'idea:047b' 'Explain the missing input and the next recovery step in the saved status.'
research-system-live-control changes
research-system-live-control change FULL_REQUEST_ID
```

`propose` records the target and plain-language request against the installed
source. It returns the saved request identity. It does not authorize, apply or
review a change and does not start scientific work. `changes` shows the existing
bounded summary, including pending review and criticism. `change` shows one full
verified request and event chain; use the 64-character identity returned at
submission. Further authorizations, implementation evidence and independent
review remain recorded through the existing change-request operations.

The wrapper requires root OS authentication, then runs these fixed operations as
the existing controller user against its fixed private store. Callers cannot
select another path, source, environment or command. Invalid argument counts and
request identities refuse before accessing state; submitted content uses the
system's existing content and size guards.

This is the human admin proposal route. Attribution is `kind: human`,
`identity: ssh-uid:0`, `identity_source: cli_declared`: an authenticated root
transport with a declared human proposer, not proof of who is at the keyboard.
Agents use the same `orchestrator.change_requests.submit` operation or existing
CLI with their actual `--actor-json`; they must not use this route to attribute
their own proposal to a human. Both routes share validation and saved task state.

The existing `status`, `pause`, `resume`, `poll-controls` and `submit-research`
commands retain their original meanings and exact single-argument form. These
new proposal controls grant no scientific execution or unattended activation
authority. Installation and phone SSH access must be verified separately.

# Notification App: approved design and registration settings

Operator approval (current deployment-closeout instruction): dedicated GitHub App,
Issues read/write and Metadata read, installed only on
`Moroseui/concept-research-scout`. Initial use is checked notifications and
synthetic acknowledgment testing. Operational decisions through replies are NOT
authorized. This supersedes the earlier proposal's unapproved wording only for
this narrow design; no reset, launch, publishing or unattended authority follows.

Actual App ID, slug, installation ID and bot ID have not been supplied. No key is
installed and no notification has been sent. The adapter must record and verify
those actual identities, repository ID and operator numeric ID before sending.

Registration settings (personal account Moroseui):

| Setting | Value |
|---|---|
| App name | Moroseui Research Notify (availability must be checked) |
| Description | Checked research-system notifications and synthetic acknowledgments only. |
| Homepage URL | https://github.com/Moroseui/concept-research-scout |
| Callback URL | Blank |
| Request user authorization (OAuth) during installation | Off |
| Enable Device Flow | Off |
| Setup URL / Redirect on update | Blank / Off |
| Webhook Active | Off; bounded polling requires no inbound endpoint |
| Repository Issues | Read and write |
| Repository Metadata | Read-only (mandatory) |
| All other repository, organization and account permissions | No access |
| Webhook event subscriptions | None |
| Where can this GitHub App be installed? | Only on this account |
| Installation repository access | Only select repositories: concept-research-scout |

Do not generate a client secret or authorize an OAuth user token. After creating
and installing the App, record its actual identity before generating/transferring
the private key. The key will reside in a private directory accessible only to
the dedicated notification runtime UID and setup administrator; never paste it
into chat, write it in Git, or place it in the driver/reviewer/worker home.

The adapter verifies the authenticated App, exact permissions, selected-repository
installation, full metadata-only repository listing, bot/operator identities,
then mints an Issues token restricted to this repository. Unexpected access or
identities refuse. It exposes no token output and refuses redirects. Pending or
lost issue creation stays UNCERTAIN and never automatically reposts. An operator
must reconcile an uncertain notification against the existing issue before any
new attempt; absence of a local receipt does not establish non-delivery.

Synthetic acknowledgments only record receipt of a notification; they cannot
ratify decisions, reset a limiter or dispatch work. Device delivery and an actual
authenticated acknowledgment remain unproven until the operator phone test.

References: [GitHub registration](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app),
[App permissions](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app),
[App authentication](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app).

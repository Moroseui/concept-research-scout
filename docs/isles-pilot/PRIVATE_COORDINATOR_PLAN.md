# Proposed private coordinator and scientific execution worker

**PROPOSAL ONLY — nothing provisioned; separate operator approval required.**
Proposed project ID: `isles24-pilot-20260905` (availability not yet checked).
Region `us-central1`, zone `us-central1-a`. Billing account must be supplied
privately when approving deployment; no credentials belong in this checkout.

The worker is API-driven compute: submit an immutable scientific container through
Google Cloud Batch's Jobs API. It does not mean buying a new language-model API
subscription. Scientific author/reviewer stages initially remain on the existing
local authenticated CLIs. Any later hosted model API needs its own approved budget.

| Proposed resource | Exact configuration | Authority/data boundary |
|---|---|---|
| `pilot-private` VPC / `pilot-central` subnet | custom VPC, 10.24.0.0/24, Private Google Access | no external VM IP, no NAT, no public application endpoint |
| `pilot-coordinator` VM | e2-small, Debian 12, 20 GiB pd-standard boot, no external IP | private SQLite job/event/inbox state; only fixed job types |
| `pilot-coordinator` service account | custom Batch submit/get/delete permissions; actAs only pilot-worker SA | no project Editor/Owner, no GitHub token, no Drive OAuth |
| `pilot-worker` service account | read input/source buckets; create objects only in private-output bucket | cannot alter approved inputs or publish to GitHub |
| Batch template `p001-cpu-v1` | 1 task, e2-standard-4 (4 vCPU/16 GiB), max parallelism 1, CPU only, 200 GiB ephemeral pd-standard | immutable image digest + source/spec/cohort/review identities; 4-hour total task cap, original 60-minute analysis cap |
| `isles24-pilot-20260905-inputs` bucket | regional Standard, uniform access, public-access prevention | pinned archive and source packages; writer is operator only |
| `isles24-pilot-20260905-private` bucket | same controls, versioning | original console, checkpoints, failures, receipts; no automated deletion |
| `isles24-pilot-20260905-aggregate` bucket | same controls | only validated permitted aggregate outputs |
| Artifact Registry `pilot-images` | regional Docker repository | immutable container digest selected by reviewed job template |
| IAP administrative access | OS Login; SSH only from 35.235.240.0/20 to coordinator tag | operator identity only; no public SSH/IP |

Coordinator and worker use attached service accounts and metadata-server short-lived
tokens; no JSON service-account keys. The coordinator cannot change firewall/IAM,
create arbitrary machines, or submit arbitrary containers: enforce fixed templates
in its service and a separate deployment administrator identity. Batch submit IAM
alone does not constrain every job field; the service must validate the complete
request. No patient values enter model prompts, GitHub CI, or Cloud Logging.
Full scientific console goes directly to the private bucket; operational logging
contains only job IDs, fixed statuses, durations and aggregate manifests.

No NAT is needed because runtime jobs use only Google APIs through Private Google
Access. Upload the pinned archive and reviewed container through an operator-approved
transfer before execution. Container dependencies must be baked into the image;
no runtime pip/apt/GitHub/Zenodo downloads. Source review and deployment approval are
separate from each job's scientific approval. The existing Colab run is not migrated.

## Cost envelope (USD, public on-demand list estimates checked 2026-09-05)

- e2-small: $0.016752855/hour, about **$12.23/730-hour month**.
- 20 GiB standard persistent disk: approximately **$0.80/month**.
- 100 GiB regional Standard storage: approximately **$2/month**, plus operations.
- e2-standard-4 worker: approximately **$0.134023/hour**; one four-hour job about
  **$0.54 compute**, plus roughly **$0.044** for 200 GiB scratch disk over four hours.
- Proposed pilot ceiling: **$25/month coordinator/storage** and **$2 per worker job**,
  initially **one synthetic job then one approved P001 job**, no GPU or autoscaling.
  These are authorization limits implemented in the coordinator, not guarantees
  that a Cloud Billing alert will stop expenditure. Billing alerts at $10/$20/$25
  are notifications, not hard caps. Egress, retained output volume, registry storage,
  taxes and regional/price changes can add cost; no free-tier credit is assumed.

Sources: [Compute pricing](https://cloud.google.com/products/compute/pricing/general-purpose),
[Disk pricing](https://cloud.google.com/compute/disks-image-pricing),
[Storage pricing](https://cloud.google.com/storage/pricing),
[Batch overview](https://cloud.google.com/batch/docs/overview),
[Private Google Access](https://cloud.google.com/vpc/docs/private-google-access).

## Approval and rollout

1. Approve this resource/budget plan and supply the billing account/project choice.
2. Operator deploys using a dedicated administrator identity; fish-compatible
   command sheet is `PRIVATE_COORDINATOR_SETUP.fish`. It is deliberately plan-only.
3. Build/pin a small synthetic worker container; submit through the Batch API;
   retrieve original console/artifact and independently verify hash. Test duplicate
   callbacks, coordinator restart, expired leases and an ambiguous dispatch.
4. Fresh review of the actual container/template/IAM policy and end-to-end receipt
   before patient execution. The current tested local coordinator is not yet a
   deployed API service or a production IAM enforcement boundary.
5. Upload reviewed inputs privately; dispatch only an approved scientific snapshot.
   Return validation, import and interpretation still use the research pipeline.

Not yet implemented/provisioned: authenticated coordinator API, custom IAM policy
files, scientific container build, Batch template deployment, private archive
transfer, managed startup service. These are explicit deployment prerequisites;
this document does not claim the remote coordinator is running.

# Manual engine review: original round1 preserved

Source reviewed:065fbef7a60d6d1de0ac75e887b8d54ff071f36d. Original report:
engine-review/reviews/001-claude-engine-review.md (its internal title is003).
Reviewer attribution: Claude Opus5.5, claude-opus-5-5, Claude Code desktop;
report states no native session ID was available. No session identity invented.
Verdict: **CHANGES REQUIRED**. B1 is its blocker; A1-A7 remain advisories at their
original scope. Operator explicitly requests B1,A4,A2,A7,A3,A1/A5 repairs for
round2; that instruction does not rewrite Claude's classifications or approve
this successor. Maximum two rounds. No model call before round2 approval.

Original report SHA256: adb1ea26fba9acf710ff4ff7938401a733f00193a002465ad875d9017e2811c8

Round2 repairs: fixed first Drive-mount cell; ordered reviewed code-cell identity
instead of notebook serialization bytes; narrowly recorded pre-computation
re-emission; pre-run original baseline pins and fixed path normalization;
BLOCKED reason and one-paragraph decision request; preserved malformed returns;
reserved prepared-input hash checked again at the actual native stdin boundary;
Drive-only package references and per-call enforced filesystem isolation.

The original seven files were read and hashed at the operator-provided private
folder, not copied into source or model inputs. REFERENCE_BINDINGS.json contains
only the original hashes, JSON top-level key sets and fixed Drive path.

A1 follow-up authorized by the operator: reserved IDs in the local split are
membership, not images/labels; keeping them on disk is permitted if no stage
model can read them. No dataset files moved or deleted. Files uploaded unchanged
to My Drive/isles-pilot/sprint10-inputs-PRIVATE/ per operator confirmation; this
is not an independent Drive readback. The package keeps only path/hash/count.

The wrapper is now implemented: each author/reviewer gets a fresh mount/PID
namespace, its stage workspace, selected native binaries/runtime and only its
own tool credentials in a private per-call home. No host root, home, /mnt/c,
Drive mount, DriveFS cache or other stage is bound. A real namespace/denial probe
runs before reservation; an in-namespace guard runs again before native exec.
Failure has no unconfined fallback. The prior cache-exists refusal is removed.
Detailed allowlist, deterministic evidence and limitations: STEP_D_ISOLATION.md.
Manual round2 review remains required before any model call.

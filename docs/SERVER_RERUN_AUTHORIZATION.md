# Separate Sprint10 server acceptance lane

Actual operator decision (from the RC2 preparation request; preserved verbatim):

> Budget: I grant a new lane for the server rerun of the Sprint 10 known case: at most 6 model calls, plus one more Colab CPU run by me.

Other express boundaries from the same request:

> Before deploying, prepare one revision covering the review's advisories and deployment-plan gaps, then stop for one Claude review round. No deployment, no model calls.

This records future execution authority; it does not release the current preparation/review hold. The new lane must be initialized with `--server-rerun` in its own repository and state directories after independent approval and the deployment plan's gates. Its policy binds this file, n=3, and a six-call lifetime cap. Existing laptop accounting and its eight-call grant are unchanged. Per-role limits stay two, for scientific author/reviewer invocations. The RC3 clarification below permits a deterministic, provenance-recorded format repair without any model call. No automatic retries of uncertain/failed calls. One new manual Colab CPU run; no training, final-evaluation or reserve-patient access. Original accepted outputs remain under their original identities; new server outputs have a separate run-specific path.


## RC3 operator clarification (actual reply)

> Acceptable, with two conditions:
> 1. Split only at a sentence boundary, never mid-sentence. If the first sentence alone exceeds 150 words, do not repair; block with a clear message.
> 2. Label the moved text plainly (for example "Summary continued (moved automatically for length):") and record the repair in the stage's provenance. The reviewer checks that the shortened summary still states the answer and the main caveat; if it doesn't, that is a normal reviewer revision request.
>
> The six-call cap stays unchanged. Proceed with the rest of the round as specified.
>
> I'm open to raising the cap in future lanes if a real run shows it's needed; propose it with the evidence rather than working around it.

No higher cap is implemented. Two spec calls plus author/reviewer and one
reviewer-requested author/reviewer revision pair fit exactly six. A deterministic
format pass consumes no model call or author slot. Ambiguous or overlong first
sentences block rather than being cut. Every original authored file and native
receipt remains bound unchanged; a separately hashed derived file is reviewed.

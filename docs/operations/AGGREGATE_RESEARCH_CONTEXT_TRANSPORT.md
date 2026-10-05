# Transporting reviewed aggregate context

The existing validated context reader can prepare a bounded transport when an
external notebook's original reviewer text contains private case details:

```python
from orchestrator.research_context import evidence_context

context = evidence_context(private_checkout, 'isles24-prediction',
                           withhold_external_review_text=True)
```

The default reader is unchanged and retains the complete private review. The
explicit option validates the same original interpretation, review, decision and
charter-consideration bindings first. For each validated external interpretation,
it omits the entire original review text from the derived projection while keeping
the review's source, SHA-256 and actual recorded verdict. It marks that text as
withheld and explains that criticism and conditions may exist. It does not rewrite
the review, replace its findings, or interpret approval as absence of criticism.
Original files and every other interpretation/consideration field remain unchanged.

Both models must receive the withholding marker and limitation. If a next decision
requires the full review findings, that evidence remains a dependency; this option
does not authorize proceeding without it. The source and projection hashes identify
exactly what was supplied. Hashes use sorted compact UTF-8 JSON; the projected hash
covers the context before its `transport` metadata is added. Record the enclosing
task packet and actual role-context hashes through the existing workflow as usual.

This option is narrow: it withholds only raw external-interpretation review text.
It does not filter case identifiers from other fields or change nonexternal reviews.
The existing publication and text validators check the entire resulting projection
and refuse unsafe remaining content with `AGGREGATE_CONTEXT_TRANSPORT_REJECTED`.
The caller then preserves the private original and reports the affected dependency;
it must not silently edit scientific text to get past the check. These checks do
not grant public publication or establish anonymization. Deliberate blinding still
returns no evidence.

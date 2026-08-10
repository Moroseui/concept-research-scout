Revise the idea in response to `critique.md`. Narrow it to one clean question. Remove unnecessary architecture. Preserve a meaningful negative outcome. Update `idea_card.json` and write `revision.md` describing every material change. Do not write code.

## Claim retention (required)

End `revision.md` with one fenced json block classifying the revised
deliverable against the ORIGINAL deliverable sentence (ledger field
`deliverable_original`):

```json
{"claim_retention": "same|narrowed|different"}
```

`different` should be rare: under the claim-identity rule it normally
means supersede-and-re-register, not revise.

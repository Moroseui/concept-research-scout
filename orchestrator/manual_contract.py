"""Manual-lane output contracts; semantic merit remains an independent review."""
import re

TYPES={"experiment","analysis","stop","blocker_resolution"}
NEXT_INSTRUCTION=("Write investigator_next_decision.json with exactly status=PROPOSAL_ONLY, "
    "proposed_action_type (experiment, analysis, stop, blocker_resolution), action, rationale, "
    "charter_basis and blocker_ids (list). Propose one concrete charter-directed experiment or "
    "analysis, or an explicit stop with its reason. Cite the charter question in charter_basis "
    "for experiment/analysis. Further review or reconciliation of this run is allowed only as "
    "blocker_resolution with the IDs of applicable open blocker records; otherwise blocker_ids "
    "must be empty. The action is a proposal, not a launch. ")
READABILITY_INSTRUCTION=("Start interpretation.md with '# Summary', at most 150 plain-language "
    "words covering the question, answer, key numbers and main caveats, followed by '# Details'. "
    "Give evidence-linked details and uncertainty there. Do not restate review rules or "
    "authorization language in either output. ")


def validate_next(value, open_blockers):
    fields={"status","proposed_action_type","action","rationale","charter_basis","blocker_ids"}
    if not isinstance(value,dict) or set(value)!=fields or value['status']!='PROPOSAL_ONLY':
        raise ValueError('INVALID_NEXT_DECISION_FIELDS')
    kind=value['proposed_action_type']
    if not isinstance(kind,str) or kind not in TYPES:raise ValueError('INVALID_NEXT_ACTION_TYPE')
    if any(not isinstance(value[k],str) or not value[k].strip() for k in ['action','rationale']):
        raise ValueError('CONCRETE_NEXT_ACTION_AND_REASON_REQUIRED')
    if not isinstance(value['charter_basis'],str):raise ValueError('INVALID_CHARTER_BASIS')
    if kind in {'experiment','analysis'} and not value['charter_basis'].strip():
        raise ValueError('NEXT_ACTION_CHARTER_BASIS_REQUIRED')
    ids=value['blocker_ids']
    if not isinstance(ids,list) or any(not isinstance(x,str) for x in ids) or len(set(ids))!=len(ids):
        raise ValueError('INVALID_NEXT_BLOCKER_IDS')
    if kind=='blocker_resolution':
        if not ids or not set(ids)<=set(open_blockers):raise ValueError('OPEN_BLOCKER_BINDING_REQUIRED')
    elif ids:raise ValueError('UNEXPECTED_NEXT_BLOCKER_IDS')
    # Common procedural deflection is not a research action. Independent review
    # checks the meaning, specificity and charter connection beyond this guard.
    if kind in {'experiment','analysis'} and re.search(r'\b(review|reconcile|reconciliation)\b.*\b(this run|same run|current run|interpretation|sprint10|reproduction)\b',value['action'],re.I):
        raise ValueError('REVIEW_RECONCILIATION_REQUIRES_OPEN_BLOCKER')


def validate_summary(text):
    match=re.match(r'\A# Summary\s*\n(.*?)\n# Details(?:\s*\n|$)',text,re.S)
    if not match or not match[1].strip():raise ValueError('PLAIN_SUMMARY_THEN_DETAILS_REQUIRED')
    if len(match[1].split())>150:raise ValueError('SUMMARY_EXCEEDS_150_WORDS')


def details_body(text):
    """The immutable scientific body for the sole summary-format correction."""
    match=re.search(r'^# Details[ \t]*\n',text,re.M)
    if not match or not text[match.end():].strip():raise ValueError('FORMAT_REVISION_REQUIRES_EXISTING_DETAILS')
    return text[match.start():]


def repair_summary_length(text):
    """Lossless deterministic relocation, never a model/science revision.

    Ambiguous abbreviation/initial boundaries are not used. No sentence boundary
    at or below150 words is a named refusal, never a mid-sentence cut.
    """
    try:
        validate_summary(text)
        return text,None
    except ValueError as error:
        if str(error)!='SUMMARY_EXCEEDS_150_WORDS':raise
    match=re.match(r'\A# Summary\s*\n(.*?)\n# Details(?:[ \t]*\n)',text,re.S)
    if match is None:raise ValueError('PLAIN_SUMMARY_AND_DETAILS_REQUIRED')
    summary=match.group(1)
    boundaries=[]
    for end in re.finditer(r'[.!?]["\')]*?(?=\s+[A-Z0-9]|$)',summary):
        prefix=summary[:end.end()]
        last=re.search(r'([A-Za-z.]+)[.!?]["\')]*$',prefix)
        if summary[end.start()]=='.' and last:
            word=last.group(1).lower().rstrip('.')
            if len(word)<=2 or '.' in word or last.group(1).isupper() or word in {'dr','mr','mrs','ms','prof','fig','vs','etc','inc','ltd','approx','eq','no','nos','vol','ref','refs','resp','std','avg','est','dept','univ','assoc','eds','sec','secs','supp'}:continue
        if len(prefix.split())<=150:boundaries.append(end.end())
    if not boundaries:raise ValueError('SUMMARY_FIRST_SENTENCE_EXCEEDS_150_OR_BOUNDARY_AMBIGUOUS: no automatic repair; shorten at a sentence boundary')
    cut=max(boundaries);kept,moved=summary[:cut],summary[cut:]
    repaired=text[:match.start(1)]+kept+'\n# Details\n\nSummary continued (moved automatically for length):'+moved+'\n\n'+text[match.end():]
    validate_summary(repaired)
    return repaired,{'kind':'DETERMINISTIC_SUMMARY_RELOCATION','summary_characters':len(summary),'sentence_boundary_offset':cut,'summary_words_before':len(summary.split()),'summary_words_after':len(kept.split()),'moved_text':moved,'model_calls':0,'meaning_check':'independent reviewer must check retained answer and main caveat'}

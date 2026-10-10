"""The existing private intake text scan, usable before remote result transfer.

Pure stdlib only; the public scanner and allowed content rules are unchanged.
"""
import html
import re
from urllib.parse import unquote
from orchestrator.privacy_patterns import SECRET

KINDS = {'code', 'aggregate', 'plan', 'review', 'per_patient'}
STAGES = {'run_spec_author', 'run_spec_review', 'result_interpretation_author', 'result_interpretation_review'}
ID = re.compile(r'(?i)(?:sub[-_])?stroke[-_]?[0-9]+')
TOKEN = re.compile(r'(?:ya29\.[A-Za-z0-9_-]+|eyJ[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+|(?:ak|as)-[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]+)')
ASSIGNMENT = re.compile(r'''(?ix)["']?(?:token|access_token|refresh_token|id_token|token_secret|client_secret|api_key|private_key|authorization|password)["']?\s*[:=]\s*["']?([^\s,"'}\]]+)''')


OPAQUE = re.compile(r'[A-Za-z0-9+/]{256,}={0,2}')


def text_variants(text):
    values = [text]
    for _ in range(2):
        decoded = html.unescape(unquote(values[-1]))
        decoded = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m[1], 16)), decoded)
        if decoded == values[-1]:
            break
        values.append(decoded)
    return values


def reject_opaque(raw):
    """Same predicate for early feedback; the full host scan stays mandatory."""
    for value in text_variants(raw.decode('utf-8')):
        if OPAQUE.search(value):
            raise ValueError('PRIVATE_INTAKE_OPAQUE_PAYLOAD_REJECTED')


def scan(raw, cases, *, kind, reason=''):
    """Two mandatory fail-closed scans; returns counts, never rejected values.

    This is a known-secret/identifier detector, not a claim that arbitrary opaque
    data can be proven safe. Opaque formats are refused; evidence registration
    and review must also establish the development-only content provenance.
    """
    if kind not in KINDS or not isinstance(raw, bytes) or len(raw) > 1_500_000 or b'\0' in raw:
        raise ValueError('PRIVATE_INTAKE_TEXT_TYPE_OR_LIMIT')
    if kind == 'per_patient' and (not isinstance(reason, str) or not reason.strip()):
        raise ValueError('PRIVATE_INTAKE_ANALYSIS_REASON_REQUIRED')
    text = raw.decode('utf-8')
    # Notebook JSON is decoded before this function. Also inspect common textual
    # escaping so a literal escaped identifier/token cannot evade the check.
    found = set()
    for value in text_variants(text):
        if SECRET.search(value.encode()) or TOKEN.search(value) or ASSIGNMENT.search(value):
            raise ValueError('PRIVATE_INTAKE_SECRET_REJECTED')
        # Long encoded blobs cannot be inspected as plain scientific text.
        if OPAQUE.search(value):
            raise ValueError('PRIVATE_INTAKE_OPAQUE_PAYLOAD_REJECTED')
        for match in ID.finditer(value):
            digits = re.search(r'[0-9]+', match[0])[0]
            normalized = 'sub-stroke' + digits
            if normalized not in cases or match[0] != normalized:
                raise ValueError('PRIVATE_INTAKE_NONDEVELOPMENT_OR_NONCANONICAL_ID')
            found.add(normalized)
    if found and kind not in {'code', 'per_patient'}:
        raise ValueError('PRIVATE_INTAKE_PATIENT_LEVEL_CLASSIFICATION_REQUIRED')
    return {'secret_scan': 'PASS', 'locked_and_unknown_id_scan': 'PASS',
            'development_identifiers': len(found), 'bytes': len(raw), 'characters': len(text)}


"""Shared pre-publication validation for text summaries and closed Actions exports."""
from pathlib import Path
import re

DANGER=re.compile(r'(sub[-_]stroke[0-9]+|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN (?:(?:RSA |OPENSSH |EC |DSA |ENCRYPTED )?PRIVATE KEY|PGP PRIVATE KEY BLOCK)-----)',re.I)


def text(value,limit=100000):
    if not isinstance(value,str) or len(value.encode())>limit or DANGER.search(value) or any(ord(c)<32 and c not in '\n\t' for c in value):
        raise ValueError('PUBLIC_TEXT_REJECTED')
    return value


def summary(value,destination):
    text(value)
    p=Path(destination)
    if p.is_symlink():raise ValueError('SUMMARY_SYMLINK_REJECTED')
    with p.open('a') as f:f.write(value+'\n')


def infrastructure_failure():
    import os
    summary('## BLOCKED\nA preflight or runner step failed. Inspect the named gate, then repair its source, review, dependency or existing authentication binding. No reviewed result is claimed.',os.environ['GITHUB_STEP_SUMMARY'])

if __name__=='__main__':infrastructure_failure()

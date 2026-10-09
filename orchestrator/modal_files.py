"""Shared, stdlib-only return-file limits and paths; no provider operations."""
from pathlib import PurePosixPath
import re

MAX_FILE = 64 * 1024 * 1024
MAX_TOTAL = 256 * 1024 * 1024


def safe_name(name):
    if (not isinstance(name,str) or not name or len(name)>240 or
        str(PurePosixPath(name))!=name or name.startswith('/') or
        any(x in {'','.','..'} for x in name.split('/')) or
        not re.fullmatch(r'[a-zA-Z0-9_./-]+',name)):
        raise ValueError('MODAL_MEMBER_PATH')
    return name


def member_map(value, *, maximum=MAX_TOTAL):
    if not isinstance(value,dict) or not 1<=len(value)<=1024:raise ValueError('MODAL_MEMBER_COUNT')
    total=0
    for name,item in value.items():
        safe_name(name)
        if (not isinstance(item,dict) or set(item)!={'sha256','bytes'} or
            not isinstance(item['sha256'],str) or not re.fullmatch('[a-f0-9]{64}',item['sha256']) or
            type(item['bytes']) is not int or not 0<=item['bytes']<=MAX_FILE):
            raise ValueError('MODAL_MEMBER_IDENTITY')
        total+=item['bytes']
    if total>maximum:raise ValueError('MODAL_MEMBERS_TOO_LARGE')
    return value



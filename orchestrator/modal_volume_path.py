"""Bind one provider mount alias to its controller-recorded Volume identity.

This is not a general symlink permission. Child I/O keeps using private_records
unchanged, with its original no-symlink, owner-only and no-hardlink checks.
"""
import os
from pathlib import Path
import re
import stat


def _bound_root(alias, volume_id, allowed):
    alias=Path(alias)
    if str(alias) not in allowed:
        raise ValueError('DOWNLOAD_VOLUME_ALIAS')
    if not isinstance(volume_id,str) or not re.fullmatch(r'vo-[A-Za-z0-9]{1,80}',volume_id):
        raise ValueError('DOWNLOAD_VOLUME_ID')
    expected=Path('/__modal/volumes')/volume_id
    # The SDK mounts the selected volume behind this alias. A user-chosen or
    # redirected target is never accepted merely because resolve() succeeds.
    before=alias.lstat()
    if not stat.S_ISLNK(before.st_mode):
        raise ValueError('DOWNLOAD_VOLUME_TARGET')
    if alias.resolve(strict=True)!=expected:
        raise ValueError('DOWNLOAD_VOLUME_TARGET')
    # Preserve the original ancestor rule (directory, no symlinks). The provider
    # owns the mount-root mode; every new child still goes through the unchanged
    # private writer. Do not invent host-specific owner/mode prerequisites here.
    for path in [expected,*expected.parents]:
        info=path.lstat()
        if not stat.S_ISDIR(info.st_mode):
            raise ValueError('DOWNLOAD_VOLUME_PARENT')
    target=expected.stat()
    after=alias.lstat()
    if (before.st_dev,before.st_ino,before.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_mtime_ns):
        raise ValueError('DOWNLOAD_VOLUME_ALIAS_CHANGED')
    if alias.resolve(strict=True)!=expected or alias.stat()[:3]!=target[:3]:
        raise ValueError('DOWNLOAD_VOLUME_ALIAS_CHANGED')
    return expected


def bound_root(alias, volume_id):
    # Preserve the downloader's one-alias contract exactly.
    return _bound_root(alias, volume_id, {'/volume'})


def bound_fit_roots(volume_ids):
    """Bind only already-mounted fit roles; wheels are read-only dependency input."""
    aliases={'inputs':'/preprocessed','progress':'/progress','package':'/reviewed'}
    if isinstance(volume_ids,dict) and 'wheels' in volume_ids:aliases['wheels']='/wheels'
    if (not isinstance(volume_ids,dict) or set(volume_ids)!=set(aliases)
            or any(not isinstance(v,str) or not re.fullmatch(r'vo-[A-Za-z0-9]{1,80}',v)
                   for v in volume_ids.values()) or len(set(volume_ids.values()))!=len(aliases)):
        raise ValueError('FIT_VOLUME_ROLE_BINDING')
    roots={role:_bound_root(alias,volume_ids[role],set(aliases.values()))
           for role,alias in aliases.items()}
    # Verify every alias again after resolving the set. Child checks stay strict.
    if any(_bound_root(aliases[k],volume_ids[k],set(aliases.values()))!=v for k,v in roots.items()):
        raise ValueError('FIT_VOLUME_ROLE_CHANGED')
    return roots

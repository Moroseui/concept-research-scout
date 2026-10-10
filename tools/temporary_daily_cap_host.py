"""Retain reviewed host checks and bounded maintenance for the dated-cap unit."""
import importlib.util
import os
from pathlib import Path
import sys

OLD_ROOT = Path('/opt/research-system/manual-repair-helpers/item4-author24-delivery-20261010')
OLD_REVIEW = Path('/var/lib/research-system-manual-sprint10-deployment/item4-author24-delivery-20261010/review')
OLD_UNIT = 'research-item4-author24-delivery-20261010.service'
NEW_UNIT = 'research-temporary-daily-cap-20261010-author.service'
HOST_PIN = 'a180f1ca903ca0a82566016d58425a4411dcfbfc512568afe57138b2c3329ade'


def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result


def connect():
    import hashlib
    if os.getuid()!=0 or not sys.flags.no_user_site:
        raise ValueError('DATED_HOST_ROOT_ISOLATED_PYTHON_REQUIRED')
    path=OLD_ROOT/'tools/item4_response_host_operation.py'
    host=load('_unchanged_author24_host_operation',path)
    host.require(hashlib.sha256(host.trusted(path).read_bytes()).hexdigest()==HOST_PIN,'ORIGINAL_HOST_SOURCE')
    host.authority(OLD_REVIEW)  # Genuine original author24 authority and engine pins.
    cap=load('_installed_dated_daily_cap',Path(__file__).with_name('temporary_daily_cap.py'))
    cap.verified()
    host.require(Path(__file__).resolve()==cap.ROOT/'tools/temporary_daily_cap_host.py','DATED_HOST_SOURCE_PATH')
    state=dict(line.split('=',1) for line in host.command(
        ['systemctl','show',OLD_UNIT,'-p','ActiveState','-p','MainPID']).splitlines())
    host.require(state=={'MainPID':'0','ActiveState':'inactive'},'ORIGINAL_AUTHOR_MUST_REMAIN_HELD')
    # Only target and fresh operation-record directory change. The original
    # readiness verifier, host hook, limits, pulse logic and safe_stop stay exact.
    host.UNIT=NEW_UNIT
    host.OPERATION_ROOT=cap.RECORD/'operation'
    return host


def main(argv=None):
    argv=sys.argv[1:] if argv is None else argv
    if len(argv)!=1 or argv[0] not in {'start','pulse'}:
        raise ValueError('DATED_HOST_ACTION_SCOPE')
    host=connect()
    previous=sys.argv
    try:
        sys.argv=[str(__file__),argv[0],'--stage','author','--review',str(OLD_REVIEW)]
        return host.main()
    finally:sys.argv=previous


if __name__=='__main__':
    os.umask(0o077)
    main()

#!/usr/bin/env python3
"""Install one versioned administrative entry point on the held new M3 lane."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from orchestrator.manual_executor import digest
from orchestrator.manual_host_guard import trusted
from tools.modal_evidence_transition import approval, REQUIRED
from tools.modal_interpretation_recovery import ROOT
from tools.install_modal_transition import private_new_file, OLD_UNIT_SHA, RUNTIME_SHA

SDK = '/var/lib/research-system-autonomy/preparation/m3-modal-sdk-1.6.0/venv/lib/python3.12/site-packages'
OLD_DROPS = {'20-one-transition.conf': 'd06b2dbda4309a10f462724cb9e4a69f9ad58c63be481a62320cffeb994ae5a4',
    '30-image-provider.conf': '2617d4031f12e32592d61e17f18d6d68f46f70eccb7b76c40b6b85f22cf65e18',
    '40-root-search-path.conf': 'ce1fd5fdf56851022548dc558ba34e836cd42d71a259df7074a7b8ab34d65992'}


def command(source, review):
    provider = Path('/var/lib/research-system-manual-sprint10-deployment') / ROOT.name / 'provider-20e4df5d19720725d272ce9d6f2f8448348f44f0'
    args = ['/usr/bin/env', 'PYTHONPATH=' + str(source) + ':' + SDK,
        '/usr/bin/python3', '-s', '-B', str(source / 'tools/modal_evidence_transition.py'),
        '--state', str(ROOT / 'lane'), '--preparation', str(ROOT / 'modal-preparation'),
        '--approval-folder', str(review), '--provider-folder', str(provider)]
    if any(not re.fullmatch(r'[A-Za-z0-9_./:=\-]+', arg) for arg in args):
        raise ValueError('UNSAFE_UNIT_ARGUMENT')
    return args


def unit_bytes(args):
    # Structured directives and validated argv; no placeholder substitution.
    directives = [('ExecStart', ''), ('ExecStart', ' '.join(args))]
    return ('[Service]\n' + '\n'.join(k + '=' + v for k, v in directives) + '\n').encode()


def install(review):
    os.umask(0o077)
    if os.geteuid() != 0 or not sys.flags.no_user_site:
        raise ValueError('ROOT_NO_USER_SITE_REQUIRED')
    source = Path(__file__).resolve().parents[1]
    trusted(source)
    result = approval(review)
    for name in REQUIRED:
        trusted(source / name)
    unit = Path('/etc/systemd/system') / (ROOT.name + '.service')
    drops = unit.with_name(unit.name + '.d')
    runtime = Path('/etc/research-system-manual-sprint10/releases') / ROOT.name / 'runtime.json'
    if digest(trusted(unit).read_bytes()) != OLD_UNIT_SHA or digest(trusted(runtime).read_bytes()) != RUNTIME_SHA:
        raise ValueError('ORIGINAL_INSTALL_CHANGED')
    for name, h in OLD_DROPS.items():
        if digest(trusted(drops / name).read_bytes()) != h:
            raise ValueError('ORIGINAL_OVERRIDE_CHANGED')
    for suffix in ('.service', '.timer'):
        if subprocess.check_output(['/usr/bin/systemctl', 'show', ROOT.name + suffix,
                                    '-p', 'ActiveState', '--value'], text=True).strip() != 'inactive':
            raise ValueError('LANE_MUST_BE_HELD')
    actual = subprocess.check_output(['/usr/bin/systemctl', 'show', unit.name,
        '-p', 'DropInPaths', '--value'], text=True).split()
    if actual != [str(drops / name) for name in OLD_DROPS]:
        raise ValueError('UNEXPECTED_OVERRIDE')
    args = command(source, Path(review))
    body = unit_bytes(args)
    target = drops / '50-evidence-delivery.conf'
    dest = Path('/var/lib/research-system-manual-sprint10-deployment') / ROOT.name / ('evidence-delivery-' + result['source_sha'])
    if target.exists() or target.is_symlink() or dest.exists() or dest.is_symlink():
        raise ValueError('EXISTING_EVIDENCE_INSTALL_RECONCILE')
    trusted(dest.parent); trusted(drops)
    dest.mkdir(mode=0o700)
    intent = {'source': result['source_sha'], 'report_sha256': result['report_sha256'],
        'runtime_sha256': RUNTIME_SHA, 'argv': args, 'drop_sha256': digest(body),
        'rollback': 'Stop only the new lane timer; require inactive service/no model call; '
                    'verify this drop hash, remove only50-evidence-delivery.conf and daemon-reload. '
                    'Do not resume the old entry point with a recovered state. Preserve originals.'}
    private_new_file(dest / 'INTENT.json', json.dumps(intent, sort_keys=True).encode())
    private_new_file(target, body); private_new_file(dest / 'dropin.conf', body)
    os.chown(dest, 0, 1003); dest.chmod(0o550)
    subprocess.run(['/usr/bin/systemctl', 'daemon-reload'], check=True)
    loaded = subprocess.check_output(['/usr/bin/systemctl', 'show', unit.name,
        '-p', 'ExecStart', '--value'], text=True)
    if 'argv[]=' + ' '.join(args) not in loaded:
        raise ValueError('EVIDENCE_ENTRY_NOT_LOADED')
    for name, h in OLD_DROPS.items():
        if digest((drops / name).read_bytes()) != h:
            raise ValueError('ORIGINAL_OVERRIDE_CHANGED')
    return {'status': 'INSTALLED_HELD', **intent}


def main():
    p = argparse.ArgumentParser(); p.add_argument('--approval-folder', required=True)
    a = p.parse_args(); print(json.dumps(install(a.approval_folder)))


if __name__ == '__main__':
    main()

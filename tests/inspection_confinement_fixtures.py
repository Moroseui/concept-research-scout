"""Synthetic confinement originals only: never native isolation or approval."""
import copy
import datetime
import os
from pathlib import Path

from orchestrator import inspection_runtime as runtime

E, H = runtime.encoded, runtime.digest
FIXTURE_PROFILE = b'# private synthetic ABI4 profile fixture; never loaded\n'
FIXTURE_PROFILE_SHA = H(FIXTURE_PROFILE)


def row(raw, uid=0, gid=0, mode=0o600):
    return {'sha256': H(raw), 'bytes': len(raw), 'uid': uid, 'gid': gid, 'mode': mode}


def static_confinement(*, uid=0, gid=0, receipt_path=None):
    return {'schema': runtime.CONFINEMENT_SCHEMA,
        'profile': row(FIXTURE_PROFILE, uid, gid),
        'parser': row(b'fixture parser', uid, gid),
        'policy_files': {'abi/4.0': row(b'ABI4 fixture', uid, gid),
            'tunables/global': row(b'global fixture', uid, gid),
            'local/bwrap-userns-restrict': None, 'local/unpriv_bwrap': None},
        'parser_version': 'AppArmor parser version synthetic',
        'packages': copy.deepcopy(runtime.PACKAGE_VERSIONS),
        'kernel_release': os.uname().release,
        'preprocessed_sha256': H(b'fixed flattened fixture\n'),
        'sysctls': copy.deepcopy(runtime.SYSCTL_VALUES),
        'provision_receipt_path': receipt_path or str(runtime.SESSION_ROOT/'22222222-2222-4222-8222-222222222222'/'confinement-load.json')}


def command_original(argv, conf):
    if argv == [runtime.PARSER, '--version']:
        text = conf['parser_version']+'\nCopyright fixture\n'
    elif argv == runtime.PACKAGES_ARGV:
        text = ''.join(k+'\t'+v+'\n' for k,v in sorted(conf['packages'].items()))
    elif argv == runtime._parser_argv('preprocess'): text = 'fixed flattened fixture\n'
    elif argv in (runtime._parser_argv('compile'), runtime._parser_argv('load')): text = ''
    else: raise AssertionError('Unexpected command in offline fixture: '+repr(argv))
    return {'argv': argv, 'returncode': 0, 'stdout': text, 'stderr': ''}


def provision(execution):
    conf = execution['confinement']
    return {'schema': runtime.PROVISION_SCHEMA, 'status': 'PROFILE_LOADED',
        'confinement_sha256': H(E(conf)), 'bwrap_sha256': execution['files']['bwrap']['sha256'],
        'profile_sha256': runtime.PROFILE_SHA256,
        'load': command_original(runtime._parser_argv('load'), conf),
        'loaded_profiles': [n+' (enforce)' for n in runtime.PROFILE_NAMES]}


def readback(execution, source, session_id, attempt=1):
    conf = execution['confinement']; original = E(provision(execution))
    return {'schema': runtime.READBACK_SCHEMA, 'status': 'VERIFIED_PROTECTION_READBACK',
        'execution_sha256': H(E(execution)), 'confinement_sha256': H(E(conf)),
        'observed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'profile_sha256': runtime.PROFILE_SHA256, 'bwrap_sha256': execution['files']['bwrap']['sha256'],
        'bwrap_privileged_bits': 0, 'bwrap_file_capabilities': False, 'apparmor_enabled': 'Y',
        'loaded_profiles': [n+' (enforce)' for n in runtime.PROFILE_NAMES],
        'kernel_release': conf['kernel_release'],
        'sysctls': {k: str(v) for k,v in runtime.SYSCTL_VALUES.items()}, 'policy_files': conf['policy_files'],
        'commands': {k: command_original(argv, conf) for k,argv in {
            'version': [runtime.PARSER, '--version'], 'packages': runtime.PACKAGES_ARGV,
            'preprocess': runtime._parser_argv('preprocess'), 'compile': runtime._parser_argv('compile')}.items()},
        'provision_original': original.decode(), 'provision_sha256': H(original),
        'provider_calls': 0, 'policy_loads': 0, 'credential_content_reads': 0,
        'source': source, 'session_id': session_id, 'attempt': attempt}


def install_fixture(test):
    conf = static_confinement(uid=test.uid, gid=test.gid)
    root = test.base/'apparmor.d'; root.mkdir()
    profile = root/'bwrap-userns-restrict'; profile.write_bytes(FIXTURE_PROFILE); profile.chmod(0o600)
    parser = test.inputs/'parser'; parser.write_bytes(b'fixture parser'); parser.chmod(0o600)
    for name,raw in [('abi/4.0', b'ABI4 fixture'), ('tunables/global', b'global fixture')]:
        path = root/name; path.parent.mkdir(exist_ok=True); path.write_bytes(raw); path.chmod(0o600)
    (root/'local').mkdir()
    kernel = test.base/'kernel'; kernel.mkdir()
    enabled = kernel/'enabled'; enabled.write_text('Y\n')
    profiles = kernel/'profiles'; profiles.write_text('bwrap (enforce)\nunpriv_bwrap (enforce)\n')
    sysctls = {}
    for n,v in runtime.SYSCTL_VALUES.items():
        path = kernel/n; path.write_text(str(v)+'\n');sysctls[n]=path
    from unittest.mock import patch
    for name,value in {'APPARMOR_BASE':root, 'PROFILE_PATH':profile, 'PARSER':str(parser),
                       'PROFILE_SHA256':FIXTURE_PROFILE_SHA, 'PROFILE_BYTES':len(FIXTURE_PROFILE),
                       'ENABLED_PATH':enabled, 'PROFILES_PATH':profiles, 'SYSCTL_PATHS':sysctls}.items():
        handle=patch.object(runtime,name,value);handle.start();test.addCleanup(handle.stop)
    test.execution['confinement'] = conf
    receipt=Path(conf['provision_receipt_path']);receipt.parent.mkdir()
    receipt.write_bytes(E(provision(test.execution)));receipt.chmod(0o400)
    test.conf = conf;test.provision_path=receipt
    test.real_observe_command=runtime._observe_command
    handle=patch.object(runtime,'_observe_command',side_effect=lambda argv:command_original(argv,conf))
    test.probes=handle.start();test.addCleanup(handle.stop)

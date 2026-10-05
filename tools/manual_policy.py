#!/usr/bin/env python3
"""Explicit reviewed host-policy installation/revert, separate from source install.

No host-wide sysctl change, no broad AppArmor reload, no credentials or models.
The package profile is restored to its original bytes and disabled by link;
the identical reviewed scoped policy resides in an administrator-owned file.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
from tools import deploy_manual_lane as base
from tools import manual_host_control as host


def loaded(root):
    return base.bound(root,'/sys/kernel/security/apparmor/profiles').read_text().splitlines()


def reload(root,path):
    if Path(root)==Path('/'):
        subprocess.run(['apparmor_parser','-r','-T','-I','/etc/apparmor.d',str(path)],check=True,capture_output=True)
    else:
        # Explicitly synthetic kernel for scratch tests, never a live receipt.
        target=base.bound(root,'/sys/kernel/security/apparmor/profiles')
        mode='unconfined' if b'flags=(unconfined)' in path.read_bytes() else 'enforce'
        target.write_text('bwrap ('+mode+')\nunpriv_bwrap (enforce)\n')


def check(root,mode):
    profiles=loaded(root)
    if 'bwrap ('+mode+')' not in profiles or any(p.startswith('bwrap (') and p!='bwrap ('+mode+')' for p in profiles):raise ValueError('BWRAP_MODE_NOT_CONFIRMED')
    if 'unpriv_bwrap (enforce)' not in profiles:raise ValueError('UNPRIV_BWRAP_CHANGED')
    if base.bound(root,'/proc/sys/kernel/apparmor_restrict_unprivileged_userns').read_text().strip()!='1':raise ValueError('HOST_WIDE_RESTRICTION_CHANGED')


def install(root,source,checkpoint):
    root=Path(root).absolute();checkpoint=base.bound(root,checkpoint)
    source=Path(source)/'deploy/manual-lane/host-policy'
    original=(source/'vendor-original.profile').read_bytes();admin=(source/'admin.profile').read_bytes()
    vendor=base.bound(root,str(host.VENDOR));custom=base.bound(root,str(host.PROFILE));disabled=base.bound(root,str(host.DISABLE));nr=base.bound(root,str(host.NEEDRESTART))
    # This migration is only from the observed, approved RC4 scoped state.
    if vendor.read_bytes()!=admin:raise ValueError('APPARMOR_PREDECESSOR_CHANGED')
    check(root,'unconfined')
    for p in [checkpoint,custom,nr]:
        if p.exists():raise ValueError('POLICY_DESTINATION_EXISTS')
    if disabled.exists() or disabled.is_symlink():raise ValueError('DISABLE_LINK_ALREADY_EXISTS')
    checkpoint.mkdir(parents=True,mode=0o700)
    base.save_new(checkpoint/'before.profile',vendor.read_bytes(),0o400)
    base.save_new(checkpoint/'before.json',{'loaded':loaded(root),'vendor_sha256':base.sha(vendor),'global_restriction':'1','status':'STARTED_NO_BLIND_RETRY'})
    base.save_new(checkpoint/'original.profile',original,0o400)
    custom.parent.mkdir(parents=True,exist_ok=True);nr.parent.mkdir(parents=True,exist_ok=True);disabled.parent.mkdir(parents=True,exist_ok=True)
    base.save_new(custom,admin,0o644)
    host.atomic(vendor,original)
    disabled.symlink_to(host.VENDOR if root==Path('/') else vendor)
    base.save_new(nr,host.EXCLUSION,0o644)
    reload(root,custom);check(root,'unconfined')
    receipt={'status':'PASS','kind':'LIVE' if root==Path('/') else 'SYNTHETIC_SCRATCH','vendor_sha256':base.sha(vendor),'admin_sha256':base.sha(custom),'needrestart_sha256':base.sha(nr),'loaded':loaded(root),'global_restriction':'1',
       'accepted_risk':'Any process may create user namespaces using /usr/bin/bwrap. This is an explicit scoped AppArmor exception; filesystem isolation and Codex inner sandbox remain mandatory.'}
    base.save_new(checkpoint/'applied.json',receipt);return receipt


def revert(root,checkpoint):
    root=Path(root).absolute();checkpoint=base.bound(root,checkpoint);r=base.read(checkpoint/'applied.json')
    vendor=base.bound(root,str(host.VENDOR));custom=base.bound(root,str(host.PROFILE));nr=base.bound(root,str(host.NEEDRESTART))
    # bound() deliberately refuses symlinks; this one exact owned link is handled explicitly.
    disabled=base.bound(root,'/etc/apparmor.d/disable')/'bwrap-userns-restrict'
    if not disabled.is_symlink() or disabled.resolve()!=vendor:raise ValueError('DISABLE_LINK_DRIFT')
    for p,key in [(vendor,'vendor_sha256'),(custom,'admin_sha256'),(nr,'needrestart_sha256')]:
        if base.sha(p)!=r[key]:raise ValueError('POLICY_REVERT_DRIFT')
    original=checkpoint/'original.profile'
    if base.sha(original)!=r['vendor_sha256']:raise ValueError('ORIGINAL_POLICY_CHANGED')
    if (checkpoint/'revert-intent.json').exists():raise ValueError('REVERT_RECONCILE_NO_RETRY')
    base.save_new(checkpoint/'revert-intent.json',{'status':'STARTED'})
    host.atomic(vendor,original.read_bytes())  # fsync + replace + parent fsync
    custom.rename(checkpoint/'admin.profile.removed');disabled.unlink();nr.rename(checkpoint/'needrestart.removed')
    reload(root,vendor);check(root,'enforce')
    result={'status':'PASS','loaded':loaded(root),'bwrap':'enforce','global_restriction':'1','rewrite':'atomic replace and fsync'}
    base.save_new(checkpoint/'reverted.json',result);return result


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['install','revert']);p.add_argument('--root',required=True);p.add_argument('--live',action='store_true');p.add_argument('--source');p.add_argument('--checkpoint',required=True);a=p.parse_args()
    if Path(a.root).absolute()==Path('/'):
        if not a.live or os.geteuid()!=0:raise SystemExit('LIVE_ROOT_FLAG_REQUIRED')
    elif a.live:raise SystemExit('LIVE_ROOT_REQUIRED')
    print(json.dumps(install(a.root,a.source,a.checkpoint) if a.action=='install' else revert(a.root,a.checkpoint),sort_keys=True,indent=2))

if __name__=='__main__':main()

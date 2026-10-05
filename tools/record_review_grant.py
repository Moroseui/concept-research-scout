"""Record an already-authorized retry grant; never launches or grants a retry."""
import json
import os
from pathlib import Path
from orchestrator import autonomy_review as review, private_records


def record(destination, bodies, manifest):
    """Root records exact verified originals; all creation stays owner-only until sealed."""
    if os.geteuid() != 0:raise ValueError('ROOT_GRANT_RECORD_REQUIRED')
    destination = Path(destination)
    permit = json.loads(bodies['permit.json'])
    if (review.sha(bodies['operator-original.txt']) != permit['operator_original_sha256'] or
        review.sha(bodies['packet-policy-original.txt']) != review.PACKET_POLICY_SHA256 or
        review.sha(bodies['permit.json']) != manifest['provider_retry_permit_sha256']):
        raise ValueError('GRANT_AUTHORITY_BINDING')
    for name in bodies:review.relative(name)
    if destination.exists() or destination.is_symlink():
        private_records.check_tree(destination)
        if review.inventory(destination) != {name:review.sha(raw) for name,raw in bodies.items()}:
            raise ValueError('EXISTING_GRANT_CHANGED_PRESERVE')
        for path in [destination,*destination.rglob('*')]:
            st=path.stat()
            if (st.st_uid,st.st_gid,st.st_mode & 0o777) != (0,1003,0o550 if path.is_dir() else 0o440):
                raise ValueError('EXISTING_GRANT_OWNER_MODE')
        original=review.verify_packet(destination/'original-packet')
        review.verify_provider_retry_scope(manifest,original)
        if review.sha(review.canonical(original)) != permit['original_packet_sha256']:
            raise ValueError('GRANT_ORIGINAL_BINDING')
        return {'status':'EXACT_PRIVATE_GRANT_ALREADY_RECORDED_NO_WRITE_NO_CALL','files':review.inventory(destination)}
    private_records.mkdir(destination, parents=True)
    for name, raw in bodies.items():
        review.write_once(destination/name, raw)
        private_records.check(destination/name)
    original = review.verify_packet(destination/'original-packet')
    review.verify_provider_retry_scope(manifest, original)
    if review.sha(review.canonical(original)) != permit['original_packet_sha256']:
        raise ValueError('GRANT_ORIGINAL_BINDING')
    # Seal children before permitting the service group to traverse the root.
    for path in sorted(destination.rglob('*'), reverse=True):
        os.chown(path, 0, 1003);path.chmod(0o550 if path.is_dir() else 0o440)
        private_records.check(path)
    os.chown(destination, 0, 1003);destination.chmod(0o550)
    private_records.check_tree(destination)
    return {'status':'PRIVATE_GRANT_RECORDED_NO_CALL', 'files':review.inventory(destination)}

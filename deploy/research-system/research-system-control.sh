#!/bin/sh
# Human convenience wrapper over the same versioned coordinator interface.
case "$1" in
  status|pause|resume|submit-research) ;;
  *) echo 'Usage: research-system-control status|pause|resume|submit-research' >&2; exit 2 ;;
esac
exec env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/opt/research-system/handover /usr/bin/python3 -B -m orchestrator.handover_runtime --config /etc/research-system/handover-controller.json --human "$@"

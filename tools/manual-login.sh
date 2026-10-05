#!/usr/bin/env bash
# Operator-only fresh login on this host; no model invocation or IDE auth copy.
set -eu
umask 077
case "${1:-}" in codex|claude) ;; *) echo 'Usage: manual-login.sh codex|claude' >&2; exit 2 ;; esac
release=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export PYTHONPATH="$release"
exec python3 -B -m orchestrator.manual_auth login "$1"

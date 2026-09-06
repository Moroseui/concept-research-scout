#!/usr/bin/env bash
# Bounded administrator bootstrap; no standing sudo/model/publication authority.
set -euo pipefail
[[ $(id -u) == 0 ]] || { echo 'root setup session required' >&2; exit 1; }
case "${1:-}" in
  accounts-tools)
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y python3-venv git nodejs npm ripgrep acl gh time
    getent group research-runtime >/dev/null || groupadd --system research-runtime
    for role in research-admin research-driver research-reviewer; do
      id "$role" >/dev/null 2>&1 || useradd --create-home --shell /bin/bash "$role"
      chmod 700 "/home/$role"
    done
    for role in research-controller research-worker research-publisher; do
      id "$role" >/dev/null 2>&1 || useradd --system --create-home --home-dir "/var/lib/research-system/$role" --shell /usr/sbin/nologin "$role"
      chmod 700 "/var/lib/research-system/$role"
    done
    usermod -a -G research-runtime research-controller
    usermod -a -G research-runtime research-worker
    install -d -o root -g root -m 755 /opt/research-system/releases /etc/research-system
    install -d -o research-controller -g research-runtime -m 2750 /var/lib/research-system/requests
    install -d -o research-worker -g research-runtime -m 2750 /var/lib/research-system/outputs
    install -d -o research-driver -g research-driver -m 700 /srv/research-system/work
    install -d -o research-admin -g research-admin -m 700 /home/research-admin/.ssh
    if [[ ! -e /home/research-admin/.ssh/authorized_keys ]]; then
      install -o research-admin -g research-admin -m 600 /root/.ssh/authorized_keys /home/research-admin/.ssh/authorized_keys
    fi
    # Pinned official package versions; no credentials or automatic model fallback.
    npm install --global @openai/codex@0.153.4 @anthropic-ai/claude-code@2.1.222
    codex --version
    claude --version
    ;;
  firewall)
    # Run only after verifying non-root key login in a separate connection.
    [[ -f /etc/research-system/nonroot-access-verified ]] || { echo 'verify replacement access first' >&2; exit 1; }
    ufw allow OpenSSH
    ufw default deny incoming
    ufw default allow outgoing
    ufw --force enable
    ufw status
    ;;
  *) echo 'usage: bootstrap.sh accounts-tools|firewall' >&2; exit 2;;
esac

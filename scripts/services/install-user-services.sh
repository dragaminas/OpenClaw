#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"

print_header "Servicios de usuario OpenClaw"
for unit_name in openclaw-gateway.service openclaw-node.service; do
  if systemctl --user cat "$unit_name" >/dev/null 2>&1; then
    kv "$unit_name" "installed"
  else
    warn "$unit_name no esta disponible para systemd --user"
  fi
done

if [[ "$mode" == "apply" ]]; then
  systemctl --user daemon-reload
  systemctl --user enable openclaw-gateway.service
  systemctl --user enable openclaw-node.service
  systemctl --user restart openclaw-gateway.service
  systemctl --user restart openclaw-node.service
  log "Servicios habilitados para arranque en sesion de usuario"
fi

for unit_name in openclaw-gateway.service openclaw-node.service; do
  enabled_state="$(systemctl --user is-enabled "$unit_name" 2>/dev/null || true)"
  kv "${unit_name}_enabled" "$enabled_state"
  active_state="$(systemctl --user is-active "$unit_name" 2>/dev/null || true)"
  kv "${unit_name}_active" "$active_state"
done

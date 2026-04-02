#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"

print_header "Servicios de usuario OpenClaw"
kv "mode" "$mode"
kv "openclaw_node_service_enabled" "$OPENCLAW_ENABLE_NODE_SERVICE"

managed_units=(openclaw-gateway.service)
if [[ "${OPENCLAW_ENABLE_NODE_SERVICE:-false}" == "true" ]]; then
  managed_units+=(openclaw-node.service)
fi

for unit_name in openclaw-gateway.service openclaw-node.service; do
  if systemctl --user cat "$unit_name" >/dev/null 2>&1; then
    kv "$unit_name" "installed"
  else
    warn "$unit_name no esta disponible para systemd --user"
  fi
done

if [[ "$mode" == "apply" ]]; then
  require_cmd openclaw

  if ! systemctl --user cat openclaw-gateway.service >/dev/null 2>&1; then
    openclaw gateway install --force --port "$OPENCLAW_GATEWAY_PORT"
  fi

  if [[ "${OPENCLAW_ENABLE_NODE_SERVICE:-false}" == "true" ]]; then
    if ! systemctl --user cat openclaw-node.service >/dev/null 2>&1; then
      openclaw node install --force --host "$OPENCLAW_GATEWAY_HOST" --port "$OPENCLAW_GATEWAY_PORT"
    fi
  elif systemctl --user cat openclaw-node.service >/dev/null 2>&1; then
    systemctl --user disable --now openclaw-node.service >/dev/null 2>&1 || true
    systemctl --user reset-failed openclaw-node.service >/dev/null 2>&1 || true
    log "Servicio opcional openclaw-node deshabilitado por politica local"
  fi

  systemctl --user daemon-reload
  systemctl --user enable openclaw-gateway.service
  systemctl --user restart openclaw-gateway.service

  if [[ "${OPENCLAW_ENABLE_NODE_SERVICE:-false}" == "true" ]]; then
    systemctl --user enable openclaw-node.service
    systemctl --user restart openclaw-node.service
  fi

  log "Servicios de OpenClaw convergidos"
fi

for unit_name in openclaw-gateway.service openclaw-node.service; do
  enabled_state="$(systemctl --user is-enabled "$unit_name" 2>/dev/null || true)"
  kv "${unit_name}_enabled" "$enabled_state"
  active_state="$(systemctl --user is-active "$unit_name" 2>/dev/null || true)"
  kv "${unit_name}_active" "$active_state"
done

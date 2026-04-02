#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

cmd="${1:-status}"
openclaw_units=(openclaw-gateway.service)
[[ "${OPENCLAW_ENABLE_NODE_SERVICE:-false}" == "true" ]] && openclaw_units+=(openclaw-node.service)

show_status() {
  print_header "Servicios de usuario"
  for unit_name in "${openclaw_units[@]}" comfyui.service; do
    kv "${unit_name}_enabled" "$(systemctl --user is-enabled "$unit_name" 2>/dev/null || true)"
    kv "${unit_name}_active" "$(systemctl --user is-active "$unit_name" 2>/dev/null || true)"
  done
}

case "$cmd" in
  install)
    "$REPO_ROOT/scripts/services/install-user-services.sh" apply
    "$REPO_ROOT/scripts/apps/comfyui.sh" install-service >/dev/null
    ;;
  start)
    "$REPO_ROOT/scripts/services/install-user-services.sh" apply >/dev/null
    systemctl --user start "${openclaw_units[@]}"
    "$REPO_ROOT/scripts/apps/comfyui.sh" start-service >/dev/null
    ;;
  restart)
    "$REPO_ROOT/scripts/services/install-user-services.sh" apply >/dev/null
    systemctl --user restart "${openclaw_units[@]}"
    "$REPO_ROOT/scripts/apps/comfyui.sh" restart-service >/dev/null
    ;;
  stop)
    for unit_name in "${openclaw_units[@]}"; do
      systemctl --user stop "$unit_name" >/dev/null 2>&1 || true
    done
    if systemctl --user cat comfyui.service >/dev/null 2>&1; then
      "$REPO_ROOT/scripts/apps/comfyui.sh" stop-service >/dev/null || true
    fi
    ;;
  status)
    ;;
  health)
    "$REPO_ROOT/scripts/doctor/workstation-health.sh"
    ;;
  *)
    die "Uso: $0 [install|start|restart|stop|status|health]"
    ;;
esac

show_status

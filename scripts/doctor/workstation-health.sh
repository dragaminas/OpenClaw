#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

print_header "Workstation health"
kv "work_user" "$WORK_USER"
kv "usage_profile" "$OPENCLAW_USAGE_PROFILE"

if "$REPO_ROOT/scripts/hardening/check-user.sh" "$WORK_USER" >/tmp/openclaw-check-user.log 2>&1; then
  kv "runtime_user" "ok"
else
  kv "runtime_user" "warn"
  sed -n '1,10p' /tmp/openclaw-check-user.log
fi

if lsblk -nr -o NAME,TYPE,TRAN,MOUNTPOINTS | awk '$2=="part" && $3=="nvme" && $4 != "" {found=1} END {exit found ? 0 : 1}'; then
  kv "internal_nvme_mounts" "warn"
else
  kv "internal_nvme_mounts" "ok"
fi

kv "openclaw_gateway_enabled" "$(systemctl --user is-enabled openclaw-gateway.service 2>/dev/null || true)"
kv "openclaw_gateway_active" "$(systemctl --user is-active openclaw-gateway.service 2>/dev/null || true)"
kv "openclaw_node_expected" "${OPENCLAW_ENABLE_NODE_SERVICE:-false}"
kv "openclaw_node_enabled" "$(systemctl --user is-enabled openclaw-node.service 2>/dev/null || true)"
kv "openclaw_node_active" "$(systemctl --user is-active openclaw-node.service 2>/dev/null || true)"
kv "comfyui_enabled" "$(systemctl --user is-enabled comfyui.service 2>/dev/null || true)"
kv "comfyui_active" "$(systemctl --user is-active comfyui.service 2>/dev/null || true)"

if [[ -n "$BLENDER_BIN" && -x "$BLENDER_BIN" ]]; then
  kv "blender" "ok"
  kv "blender_version" "$("$BLENDER_BIN" --version | sed -n '1p')"
else
  kv "blender" "missing"
fi

if tcp_port_is_listening "$COMFYUI_HOST" "$COMFYUI_PORT"; then
  kv "comfyui_port" "listening"
else
  kv "comfyui_port" "inactive"
fi

if command -v openclaw >/dev/null 2>&1; then
  kv "openclaw_version" "$(openclaw --version | sed -n 's/^OpenClaw \([^ ]*\).*/\1/p')"
  if openclaw status --all --json >/tmp/openclaw-status-health.json 2>/dev/null; then
    python3 - <<'PY' /tmp/openclaw-status-health.json
import json
import pathlib
import sys

payload = json.loads(pathlib.Path(sys.argv[1]).read_text())
link_channel = payload.get("linkChannel") or {}
agents = payload.get("agents") or {}
gateway = payload.get("gateway") or {}

print(f"whatsapp_linked={link_channel.get('linked')}")
print(f"gateway_reachable={gateway.get('reachable')}")
print(f"bootstrap_pending_count={agents.get('bootstrapPendingCount')}")
PY
  else
    warn "No se pudo leer openclaw status --all --json"
  fi
else
  warn "OpenClaw no esta disponible en PATH"
fi

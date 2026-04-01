#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"

print_header "Bootstrap de workstation"
kv "mode" "$mode"
kv "work_user" "$WORK_USER"
kv "studio_dir" "$STUDIO_DIR"
kv "openclaw_state_dir" "$OPENCLAW_STATE_DIR"

"$SCRIPT_DIR/validate-preconditions.sh"

if [[ "${CHECK_DANGEROUS_GROUPS:-true}" == "true" ]]; then
  "$SCRIPT_DIR/../hardening/check-user.sh" "$WORK_USER" || true
fi

if [[ "${VERIFY_INTERNAL_NVME_UNMOUNTED:-true}" == "true" ]]; then
  "$SCRIPT_DIR/../hardening/check-mounts.sh"
fi

if [[ "${DISABLE_GNOME_AUTOMOUNT:-true}" == "true" ]]; then
  "$SCRIPT_DIR/../hardening/disable-gnome-automount.sh" "$mode"
fi

"$SCRIPT_DIR/../openclaw/install-openclaw.sh"

if [[ "${HARDEN_OPENCLAW:-true}" == "true" ]]; then
  "$SCRIPT_DIR/../openclaw/configure-openclaw.sh" "$mode"
fi

if [[ "${CREATE_STUDIO_DIRS:-true}" == "true" ]]; then
  "$SCRIPT_DIR/../openclaw/setup-workspace.sh" "$mode"
fi

if [[ "${OPENCLAW_STUDIO_ACTIONS_ENABLE:-true}" == "true" ]]; then
  "$SCRIPT_DIR/../openclaw/install-studio-actions-plugin.sh" "$mode"
fi

if [[ "${ENABLE_OPENCLAW_SERVICES:-true}" == "true" ]]; then
  "$SCRIPT_DIR/../services/install-user-services.sh" "$mode"
fi

print_header "Integracion creativa"
if [[ "${COMFYUI_INSTALL:-true}" == "true" ]]; then
  "$SCRIPT_DIR/../apps/install-comfyui.sh" "$mode"
  if [[ "${COMFYUI_MANAGER_INSTALL:-true}" == "true" ]]; then
    "$SCRIPT_DIR/../apps/install-comfyui-manager.sh" "$mode"
  fi
  "$SCRIPT_DIR/../services/install-comfyui-service.sh" "$mode"
fi
"$SCRIPT_DIR/../apps/design-tools.sh"
"$SCRIPT_DIR/../apps/blender.sh" status
"$SCRIPT_DIR/../apps/comfyui.sh" status || true

print_header "Diagnostico final"
"$SCRIPT_DIR/../doctor/openclaw-status.sh"

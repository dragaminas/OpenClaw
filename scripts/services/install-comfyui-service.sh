#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"
unit_dir="$(systemd_user_dir)"
unit_path="$unit_dir/comfyui.service"
template_path="$REPO_ROOT/configs/systemd-user/comfyui.service.template"
manager_flags=()

if [[ "${COMFYUI_MANAGER_ENABLE:-${COMFYUI_MANAGER_INSTALL:-true}}" == "true" ]]; then
  manager_flags+=(--enable-manager)
  if [[ "${COMFYUI_MANAGER_USE_LEGACY_UI:-false}" == "true" ]]; then
    manager_flags+=(--enable-manager-legacy-ui)
  fi
fi

manager_flags_string="${manager_flags[*]}"

[[ -d "$COMFYUI_DIR" ]] || die "No existe COMFYUI_DIR=$COMFYUI_DIR"
[[ -x "$COMFYUI_VENV_DIR/bin/python" ]] || die "No existe el python del venv: $COMFYUI_VENV_DIR/bin/python"
[[ -f "$template_path" ]] || die "No existe la plantilla: $template_path"

print_header "Servicio de usuario ComfyUI"
kv "mode" "$mode"
kv "unit_path" "$unit_path"
kv "manager_flags" "$manager_flags_string"

if [[ "$mode" == "apply" ]]; then
  mkdir -p "$unit_dir"
  sed \
    -e "s|__WORK_HOME__|$WORK_HOME|g" \
    -e "s|__COMFYUI_DIR__|$COMFYUI_DIR|g" \
    -e "s|__COMFYUI_VENV_DIR__|$COMFYUI_VENV_DIR|g" \
    -e "s|__COMFYUI_HOST__|$COMFYUI_HOST|g" \
    -e "s|__COMFYUI_PORT__|$COMFYUI_PORT|g" \
    -e "s|__COMFYUI_MANAGER_FLAGS__|$manager_flags_string|g" \
    "$template_path" > "$unit_path"
  systemctl --user daemon-reload
  if [[ "${COMFYUI_ENABLE_SERVICE:-false}" == "true" ]]; then
    systemctl --user enable --now comfyui.service
  fi
  log "Servicio de usuario ComfyUI generado"
fi

if [[ -f "$unit_path" ]]; then
  kv "service_file" "$unit_path"
  kv "service_enabled" "$(systemctl --user is-enabled comfyui.service 2>/dev/null || true)"
  kv "service_active" "$(systemctl --user is-active comfyui.service 2>/dev/null || true)"
else
  warn "Aun no existe $unit_path"
fi

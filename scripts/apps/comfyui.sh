#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

cmd="${1:-status}"
comfyui_url="http://${COMFYUI_HOST}:${COMFYUI_PORT}/"
open_target_url="${2:-$comfyui_url}"
manager_requirements_file="$COMFYUI_DIR/manager_requirements.txt"

open_browser() {
  local url="$1"
  local display_value wayland_value dbus_value

  display_value="$(user_session_env_value DISPLAY)"
  wayland_value="$(user_session_env_value WAYLAND_DISPLAY)"
  dbus_value="$(user_session_env_value DBUS_SESSION_BUS_ADDRESS)"

  if [[ -z "$display_value" && -z "$wayland_value" ]]; then
    warn "No hay sesion grafica disponible; abre la URL manualmente"
    return 1
  fi

  if ! command -v xdg-open >/dev/null 2>&1; then
    warn "No existe xdg-open; abre la URL manualmente"
    return 1
  fi

  env \
    DISPLAY="${display_value:-}" \
    WAYLAND_DISPLAY="${wayland_value:-}" \
    DBUS_SESSION_BUS_ADDRESS="${dbus_value:-}" \
    xdg-open "$url" >/tmp/openclaw-comfyui-open.log 2>&1 &
}

ensure_service_unit() {
  if systemctl --user cat comfyui.service >/dev/null 2>&1; then
    return 0
  fi

  "$REPO_ROOT/scripts/services/install-comfyui-service.sh" apply >/dev/null
  systemctl --user cat comfyui.service >/dev/null 2>&1 || die "No existe comfyui.service en systemd --user"
}

manager_python_status() {
  [[ -x "$COMFYUI_VENV_DIR/bin/python" ]] || return 1

  "$COMFYUI_VENV_DIR/bin/python" - <<'PY'
import importlib.metadata
import importlib.util

spec = importlib.util.find_spec("comfyui_manager")
if spec is None:
    raise SystemExit(1)

print(importlib.metadata.version("comfyui-manager"))
PY
}

case "$cmd" in
  status)
    print_header "ComfyUI"
    kv "comfyui_dir" "$COMFYUI_DIR"
    if [[ -d "$COMFYUI_DIR" ]]; then
      service_state=""
      if [[ -d "$COMFYUI_DIR/.git" ]]; then
        kv "git_branch" "$(git -C "$COMFYUI_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
        kv "git_head" "$(git -C "$COMFYUI_DIR" rev-parse --short HEAD 2>/dev/null || true)"
      fi
      if [[ -f "$COMFYUI_DIR/main.py" ]]; then
        kv "main_py" "$COMFYUI_DIR/main.py"
      else
        warn "No se encontro main.py dentro de ComfyUI"
      fi
      if [[ -x "$COMFYUI_VENV_DIR/bin/python" ]]; then
        kv "venv_python" "$COMFYUI_VENV_DIR/bin/python"
        "$COMFYUI_VENV_DIR/bin/python" --version
        if "$COMFYUI_VENV_DIR/bin/python" -m pip --version >/dev/null 2>&1; then
          kv "venv_pip" "available"
        else
          kv "venv_pip" "missing"
        fi
      else
        warn "No existe venv de ComfyUI en $COMFYUI_VENV_DIR"
      fi
      if systemctl --user cat comfyui.service >/dev/null 2>&1; then
        kv "service_file" "$(systemd_user_dir)/comfyui.service"
        kv "service_enabled" "$(systemctl --user is-enabled comfyui.service 2>/dev/null || true)"
        service_state="$(systemctl --user is-active comfyui.service 2>/dev/null || true)"
        kv "service_active" "$service_state"
      fi
      kv "ui_url" "$comfyui_url"
      kv "manager_install_method" "${COMFYUI_MANAGER_INSTALL_METHOD:-core}"
      kv "manager_enabled" "${COMFYUI_MANAGER_ENABLE:-${COMFYUI_MANAGER_INSTALL:-true}}"
      kv "manager_legacy_ui" "${COMFYUI_MANAGER_USE_LEGACY_UI:-false}"
      if [[ -f "$manager_requirements_file" ]]; then
        kv "manager_requirements_file" "$manager_requirements_file"
      fi
      if manager_version="$(manager_python_status 2>/dev/null)"; then
        kv "manager_python_package" "installed"
        kv "manager_python_version" "$manager_version"
      else
        kv "manager_python_package" "missing"
      fi
      if [[ -d "$COMFYUI_MANAGER_DIR/.git" ]]; then
        kv "legacy_manager_dir" "$COMFYUI_MANAGER_DIR"
        kv "legacy_manager_git_branch" "$(git -C "$COMFYUI_MANAGER_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
        kv "legacy_manager_git_head" "$(git -C "$COMFYUI_MANAGER_DIR" rev-parse --short HEAD 2>/dev/null || true)"
      fi
      if [[ -d "$COMFYUI_DIR/models" ]]; then
        kv "models_dir" "$COMFYUI_DIR/models"
      fi
      if [[ -d "$COMFYUI_DIR/output" ]]; then
        kv "output_dir" "$COMFYUI_DIR/output"
      fi
      if tcp_port_is_listening "$COMFYUI_HOST" "$COMFYUI_PORT"; then
        kv "port_${COMFYUI_PORT}" "listening"
      elif [[ "$service_state" == "active" ]]; then
        kv "port_${COMFYUI_PORT}" "starting"
      else
        kv "port_${COMFYUI_PORT}" "inactive"
      fi
    else
      warn "ComfyUI no esta instalado en $COMFYUI_DIR"
      exit 6
    fi
    ;;
  check-port)
    print_header "ComfyUI port"
    if tcp_port_is_listening "$COMFYUI_HOST" "$COMFYUI_PORT"; then
      kv "port_${COMFYUI_PORT}" "listening"
    else
      kv "port_${COMFYUI_PORT}" "inactive"
      exit 8
    fi
    ;;
  url)
    print_header "ComfyUI URL"
    kv "ui_url" "$comfyui_url"
    ;;
  install-service)
    print_header "ComfyUI install service"
    "$REPO_ROOT/scripts/services/install-comfyui-service.sh" apply
    ;;
  start-service)
    print_header "ComfyUI start"
    ensure_service_unit
    if [[ "${COMFYUI_ENABLE_SERVICE:-false}" == "true" ]]; then
      systemctl --user enable --now comfyui.service
    else
      systemctl --user start comfyui.service
    fi
    if wait_for_tcp_port "$COMFYUI_HOST" "$COMFYUI_PORT" 90; then
      kv "service_active" "$(systemctl --user is-active comfyui.service 2>/dev/null || true)"
      kv "port_${COMFYUI_PORT}" "listening"
      kv "ui_url" "$comfyui_url"
    else
      systemctl --user status comfyui.service --no-pager | sed -n '1,80p'
      die "ComfyUI no quedo escuchando en ${COMFYUI_HOST}:${COMFYUI_PORT}"
    fi
    ;;
  stop-service)
    print_header "ComfyUI stop"
    systemctl --user cat comfyui.service >/dev/null 2>&1 || die "No existe comfyui.service en systemd --user"
    systemctl --user stop comfyui.service >/dev/null 2>&1 || true
    for _ in $(seq 1 30); do
      current_state="$(systemctl --user is-active comfyui.service 2>/dev/null || true)"
      if [[ "$current_state" != "active" && "$current_state" != "activating" && "$current_state" != "deactivating" ]]; then
        break
      fi
      sleep 1
    done
    kv "service_active" "$(systemctl --user is-active comfyui.service 2>/dev/null || true)"
    ;;
  restart-service)
    print_header "ComfyUI restart"
    ensure_service_unit
    systemctl --user restart comfyui.service
    if wait_for_tcp_port "$COMFYUI_HOST" "$COMFYUI_PORT" 90; then
      kv "service_active" "$(systemctl --user is-active comfyui.service 2>/dev/null || true)"
      kv "port_${COMFYUI_PORT}" "listening"
      kv "ui_url" "$comfyui_url"
    else
      systemctl --user status comfyui.service --no-pager | sed -n '1,80p'
      die "ComfyUI no quedo escuchando en ${COMFYUI_HOST}:${COMFYUI_PORT}"
    fi
    ;;
  wait-ready)
    print_header "ComfyUI wait"
    if wait_for_tcp_port "$COMFYUI_HOST" "$COMFYUI_PORT" 90; then
      kv "port_${COMFYUI_PORT}" "listening"
      kv "ui_url" "$comfyui_url"
    else
      kv "port_${COMFYUI_PORT}" "inactive"
      exit 10
    fi
    ;;
  open-ui)
    print_header "ComfyUI open"
    "$0" start-service >/dev/null
    if open_browser "$open_target_url"; then
      printf 'ComfyUI abierto en el navegador: %s\n' "$open_target_url"
    else
      printf 'ComfyUI listo. Abre esta URL: %s\n' "$open_target_url"
    fi
    ;;
  service-status)
    print_header "ComfyUI service"
    if systemctl --user cat comfyui.service >/dev/null 2>&1; then
      kv "service_enabled" "$(systemctl --user is-enabled comfyui.service 2>/dev/null || true)"
      kv "service_active" "$(systemctl --user is-active comfyui.service 2>/dev/null || true)"
      systemctl --user status comfyui.service --no-pager | sed -n '1,40p'
    else
      warn "No existe comfyui.service en systemd --user"
      exit 7
    fi
    ;;
  manager-status)
    print_header "ComfyUI Manager"
    kv "manager_install_method" "${COMFYUI_MANAGER_INSTALL_METHOD:-core}"
    kv "manager_enabled" "${COMFYUI_MANAGER_ENABLE:-${COMFYUI_MANAGER_INSTALL:-true}}"
    kv "manager_legacy_ui" "${COMFYUI_MANAGER_USE_LEGACY_UI:-false}"
    if [[ -f "$manager_requirements_file" ]]; then
      kv "manager_requirements_file" "$manager_requirements_file"
    fi
    if manager_version="$(manager_python_status 2>/dev/null)"; then
      kv "manager_python_package" "installed"
      kv "manager_python_version" "$manager_version"
    else
      kv "manager_python_package" "missing"
    fi
    if [[ -d "$COMFYUI_MANAGER_DIR/.git" ]]; then
      kv "legacy_manager_dir" "$COMFYUI_MANAGER_DIR"
      kv "legacy_manager_git_branch" "$(git -C "$COMFYUI_MANAGER_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
      kv "legacy_manager_git_head" "$(git -C "$COMFYUI_MANAGER_DIR" rev-parse --short HEAD 2>/dev/null || true)"
      if [[ -f "$COMFYUI_MANAGER_DIR/requirements.txt" ]]; then
        kv "legacy_manager_requirements_file" "$COMFYUI_MANAGER_DIR/requirements.txt"
      fi
    else
      kv "legacy_manager_dir" "missing"
    fi
    ;;
  *)
    die "Uso: $0 [status|check-port|url|install-service|start-service|stop-service|restart-service|wait-ready|open-ui|service-status|manager-status]"
    ;;
esac

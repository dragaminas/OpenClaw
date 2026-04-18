#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

cmd="${1:-status}"

HUNYUAN3D_DIR="${HUNYUAN3D_DIR:-$HOME/Hunyuan3D-2}"
HUNYUAN3D_VENV_DIR="$HUNYUAN3D_DIR/.venv"
HUNYUAN3D_HOST="${HUNYUAN3D_HOST:-127.0.0.1}"
HUNYUAN3D_API_PORT="${HUNYUAN3D_API_PORT:-8081}"
HUNYUAN3D_GRADIO_PORT="${HUNYUAN3D_GRADIO_PORT:-7860}"
HUNYUAN3D_MODEL_PATH="${HUNYUAN3D_MODEL_PATH:-tencent/Hunyuan3D-2mini}"
HUNYUAN3D_SUBFOLDER="${HUNYUAN3D_SUBFOLDER:-hunyuan3d-dit-v2-mini-turbo}"

api_url="http://${HUNYUAN3D_HOST}:${HUNYUAN3D_API_PORT}"
gradio_url="http://${HUNYUAN3D_HOST}:${HUNYUAN3D_GRADIO_PORT}"
open_target_url="${2:-$gradio_url}"

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
    xdg-open "$url" >/tmp/openclaw-hunyuan3d-open.log 2>&1 &
}

ensure_service_unit() {
  systemctl --user cat hunyuan3d.service >/dev/null 2>&1 || \
    die "No existe hunyuan3d.service en systemd --user. Ejecuta: bash scripts/apps/install-hunyuan3d.sh"
}

case "$cmd" in
  status)
    print_header "Hunyuan3D"
    kv "hunyuan3d_dir" "$HUNYUAN3D_DIR"
    if [[ -d "$HUNYUAN3D_DIR" ]]; then
      if [[ -d "$HUNYUAN3D_DIR/.git" ]]; then
        kv "git_branch" "$(git -C "$HUNYUAN3D_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
        kv "git_head" "$(git -C "$HUNYUAN3D_DIR" rev-parse --short HEAD 2>/dev/null || true)"
      fi
      if [[ -f "$HUNYUAN3D_DIR/gradio_app.py" ]]; then
        kv "gradio_app" "$HUNYUAN3D_DIR/gradio_app.py"
      else
        warn "No se encontro gradio_app.py en $HUNYUAN3D_DIR"
      fi
      if [[ -f "$HUNYUAN3D_DIR/api_server.py" ]]; then
        kv "api_server" "$HUNYUAN3D_DIR/api_server.py"
      else
        warn "No se encontro api_server.py en $HUNYUAN3D_DIR"
      fi
      if [[ -x "$HUNYUAN3D_VENV_DIR/bin/python3" ]]; then
        kv "venv_python" "$HUNYUAN3D_VENV_DIR/bin/python3"
        "$HUNYUAN3D_VENV_DIR/bin/python3" --version
      else
        warn "No existe venv de Hunyuan3D en $HUNYUAN3D_VENV_DIR"
      fi
      service_state=""
      if systemctl --user cat hunyuan3d.service >/dev/null 2>&1; then
        kv "service_file" "$(systemd_user_dir)/hunyuan3d.service"
        kv "service_enabled" "$(systemctl --user is-enabled hunyuan3d.service 2>/dev/null || true)"
        service_state="$(systemctl --user is-active hunyuan3d.service 2>/dev/null || true)"
        kv "service_active" "$service_state"
      else
        kv "service_file" "not installed"
      fi
      kv "model_path" "$HUNYUAN3D_MODEL_PATH"
      kv "gradio_url" "$gradio_url"
      kv "api_url" "$api_url"
      if tcp_port_is_listening "$HUNYUAN3D_HOST" "$HUNYUAN3D_GRADIO_PORT"; then
        kv "port_${HUNYUAN3D_GRADIO_PORT}_gradio" "listening"
      else
        kv "port_${HUNYUAN3D_GRADIO_PORT}_gradio" "inactive"
      fi
      if tcp_port_is_listening "$HUNYUAN3D_HOST" "$HUNYUAN3D_API_PORT"; then
        kv "port_${HUNYUAN3D_API_PORT}_api" "listening"
      else
        kv "port_${HUNYUAN3D_API_PORT}_api" "inactive"
      fi
      if ls ~/.cache/huggingface/hub/ 2>/dev/null | grep -q "Hunyuan"; then
        kv "model_cache" "present"
      else
        kv "model_cache" "missing — ejecuta: bash scripts/apps/install-hunyuan3d.sh"
      fi
    else
      warn "Hunyuan3D no esta instalado en $HUNYUAN3D_DIR"
      warn "Ejecuta: bash scripts/apps/install-hunyuan3d.sh"
      exit 6
    fi
    ;;

  check-port)
    print_header "Hunyuan3D ports"
    if tcp_port_is_listening "$HUNYUAN3D_HOST" "$HUNYUAN3D_API_PORT"; then
      kv "port_${HUNYUAN3D_API_PORT}_api" "listening"
    else
      kv "port_${HUNYUAN3D_API_PORT}_api" "inactive"
      exit 8
    fi
    ;;

  url)
    print_header "Hunyuan3D URLs"
    kv "gradio_url" "$gradio_url"
    kv "api_url" "$api_url"
    ;;

  install)
    print_header "Hunyuan3D install"
    bash "$SCRIPT_DIR/install-hunyuan3d.sh"
    ;;

  start-service)
    print_header "Hunyuan3D start"
    ensure_service_unit
    systemctl --user start hunyuan3d.service
    if wait_for_tcp_port "$HUNYUAN3D_HOST" "$HUNYUAN3D_GRADIO_PORT" 120; then
      kv "service_active" "$(systemctl --user is-active hunyuan3d.service 2>/dev/null || true)"
      kv "port_${HUNYUAN3D_GRADIO_PORT}_gradio" "listening"
      kv "gradio_url" "$gradio_url"
    else
      systemctl --user status hunyuan3d.service --no-pager | sed -n '1,80p'
      die "Hunyuan3D no quedo escuchando en ${HUNYUAN3D_HOST}:${HUNYUAN3D_GRADIO_PORT}"
    fi
    ;;

  stop-service)
    print_header "Hunyuan3D stop"
    systemctl --user cat hunyuan3d.service >/dev/null 2>&1 || die "No existe hunyuan3d.service en systemd --user"
    systemctl --user stop hunyuan3d.service >/dev/null 2>&1 || true
    for _ in $(seq 1 30); do
      current_state="$(systemctl --user is-active hunyuan3d.service 2>/dev/null || true)"
      if [[ "$current_state" != "active" && "$current_state" != "activating" && "$current_state" != "deactivating" ]]; then
        break
      fi
      sleep 1
    done
    kv "service_active" "$(systemctl --user is-active hunyuan3d.service 2>/dev/null || true)"
    ;;

  restart-service)
    print_header "Hunyuan3D restart"
    ensure_service_unit
    systemctl --user restart hunyuan3d.service
    if wait_for_tcp_port "$HUNYUAN3D_HOST" "$HUNYUAN3D_GRADIO_PORT" 120; then
      kv "service_active" "$(systemctl --user is-active hunyuan3d.service 2>/dev/null || true)"
      kv "port_${HUNYUAN3D_GRADIO_PORT}_gradio" "listening"
      kv "gradio_url" "$gradio_url"
    else
      systemctl --user status hunyuan3d.service --no-pager | sed -n '1,80p'
      die "Hunyuan3D no quedo escuchando en ${HUNYUAN3D_HOST}:${HUNYUAN3D_GRADIO_PORT}"
    fi
    ;;

  wait-ready)
    print_header "Hunyuan3D wait"
    if wait_for_tcp_port "$HUNYUAN3D_HOST" "$HUNYUAN3D_GRADIO_PORT" 120; then
      kv "port_${HUNYUAN3D_GRADIO_PORT}_gradio" "listening"
      kv "gradio_url" "$gradio_url"
    else
      kv "port_${HUNYUAN3D_GRADIO_PORT}_gradio" "inactive"
      exit 10
    fi
    ;;

  open-ui)
    print_header "Hunyuan3D open"
    if ! tcp_port_is_listening "$HUNYUAN3D_HOST" "$HUNYUAN3D_GRADIO_PORT"; then
      warn "La web UI no esta activa en $gradio_url"
      warn "Arrancala con: scripts/apps/hunyuan3d.sh start-service"
      warn "  o manualmente: cd ~/Hunyuan3D-2 && source .venv/bin/activate && python3 gradio_app.py --model_path $HUNYUAN3D_MODEL_PATH --subfolder $HUNYUAN3D_SUBFOLDER --low_vram_mode --enable_flashvdm"
    fi
    if open_browser "$open_target_url"; then
      printf 'Hunyuan3D web UI abierta en el navegador: %s\n' "$open_target_url"
    else
      printf 'Abre esta URL manualmente: %s\n' "$open_target_url"
    fi
    ;;

  service-status)
    print_header "Hunyuan3D service"
    if systemctl --user cat hunyuan3d.service >/dev/null 2>&1; then
      kv "service_enabled" "$(systemctl --user is-enabled hunyuan3d.service 2>/dev/null || true)"
      kv "service_active" "$(systemctl --user is-active hunyuan3d.service 2>/dev/null || true)"
      systemctl --user status hunyuan3d.service --no-pager | sed -n '1,40p'
    else
      warn "No existe hunyuan3d.service en systemd --user"
      warn "Ejecuta: bash scripts/apps/install-hunyuan3d.sh"
      exit 7
    fi
    ;;

  smoke-test)
    print_header "Hunyuan3D smoke"
    bash "$SCRIPT_DIR/hunyuan3d-smoke-validation.sh"
    ;;

  *)
    die "Uso: $0 [status|check-port|url|install|start-service|stop-service|restart-service|wait-ready|open-ui|service-status|smoke-test]"
    ;;
esac

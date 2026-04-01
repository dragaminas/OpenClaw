#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

cmd="${1:-status}"

case "$cmd" in
  status)
    print_header "ComfyUI"
    kv "comfyui_dir" "$COMFYUI_DIR"
    if [[ -d "$COMFYUI_DIR" ]]; then
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
        kv "service_active" "$(systemctl --user is-active comfyui.service 2>/dev/null || true)"
      fi
      if [[ -d "$COMFYUI_MANAGER_DIR/.git" ]]; then
        kv "manager_dir" "$COMFYUI_MANAGER_DIR"
        kv "manager_git_branch" "$(git -C "$COMFYUI_MANAGER_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
        kv "manager_git_head" "$(git -C "$COMFYUI_MANAGER_DIR" rev-parse --short HEAD 2>/dev/null || true)"
        if [[ -f "$COMFYUI_MANAGER_DIR/requirements.txt" && -x "$COMFYUI_VENV_DIR/bin/python" ]]; then
          if "$COMFYUI_VENV_DIR/bin/python" -m pip show gitpython >/dev/null 2>&1; then
            kv "manager_requirements" "installed_or_partially_installed"
          else
            kv "manager_requirements" "unknown"
          fi
        fi
      else
        kv "manager_dir" "missing"
      fi
      if command -v ss >/dev/null 2>&1; then
        if ss -ltn | awk '{print $4}' | rg -x "127.0.0.1:$COMFYUI_PORT|0.0.0.0:$COMFYUI_PORT|\\*:$COMFYUI_PORT|\\[::\\]:$COMFYUI_PORT" >/dev/null 2>&1; then
          kv "port_${COMFYUI_PORT}" "listening"
        else
          kv "port_${COMFYUI_PORT}" "inactive"
        fi
      fi
    else
      warn "ComfyUI no esta instalado en $COMFYUI_DIR"
      exit 6
    fi
    ;;
  check-port)
    print_header "ComfyUI port"
    if command -v ss >/dev/null 2>&1 && ss -ltn | awk '{print $4}' | rg -x "127.0.0.1:$COMFYUI_PORT|0.0.0.0:$COMFYUI_PORT|\\*:$COMFYUI_PORT|\\[::\\]:$COMFYUI_PORT" >/dev/null 2>&1; then
      kv "port_${COMFYUI_PORT}" "listening"
    else
      kv "port_${COMFYUI_PORT}" "inactive"
      exit 8
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
    if [[ -d "$COMFYUI_MANAGER_DIR/.git" ]]; then
      kv "manager_dir" "$COMFYUI_MANAGER_DIR"
      kv "manager_git_branch" "$(git -C "$COMFYUI_MANAGER_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
      kv "manager_git_head" "$(git -C "$COMFYUI_MANAGER_DIR" rev-parse --short HEAD 2>/dev/null || true)"
      if [[ -f "$COMFYUI_MANAGER_DIR/requirements.txt" ]]; then
        kv "manager_requirements_file" "$COMFYUI_MANAGER_DIR/requirements.txt"
      fi
    else
      warn "ComfyUI-Manager no esta instalado"
      exit 9
    fi
    ;;
  *)
    die "Uso: $0 [status|check-port|service-status|manager-status]"
    ;;
esac

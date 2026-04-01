#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"

require_cmd git

[[ -d "$COMFYUI_DIR" ]] || die "ComfyUI debe existir antes de instalar ComfyUI-Manager: $COMFYUI_DIR"

print_header "Instalacion de ComfyUI-Manager"
kv "mode" "$mode"
kv "manager_dir" "$COMFYUI_MANAGER_DIR"
kv "repo_url" "$COMFYUI_MANAGER_REPO_URL"
kv "repo_ref" "$COMFYUI_MANAGER_REPO_REF"

mkdir -p "$(dirname "$COMFYUI_MANAGER_DIR")"

if [[ ! -d "$COMFYUI_MANAGER_DIR/.git" ]]; then
  if [[ "$mode" == "apply" ]]; then
    rm -rf "$COMFYUI_MANAGER_DIR"
    git clone --depth 1 --branch "$COMFYUI_MANAGER_REPO_REF" "$COMFYUI_MANAGER_REPO_URL" "$COMFYUI_MANAGER_DIR"
    log "Repositorio ComfyUI-Manager clonado"
  else
    warn "ComfyUI-Manager aun no esta clonado"
  fi
else
  kv "manager_git_head" "$(git -C "$COMFYUI_MANAGER_DIR" rev-parse --short HEAD)"
  if [[ "$mode" == "apply" ]]; then
    git -C "$COMFYUI_MANAGER_DIR" fetch --depth 1 origin "$COMFYUI_MANAGER_REPO_REF"
    git -C "$COMFYUI_MANAGER_DIR" checkout "$COMFYUI_MANAGER_REPO_REF"
    git -C "$COMFYUI_MANAGER_DIR" pull --ff-only origin "$COMFYUI_MANAGER_REPO_REF" || true
    log "Repositorio ComfyUI-Manager actualizado"
  fi
fi

if [[ "${COMFYUI_MANAGER_INSTALL_REQUIREMENTS:-true}" == "true" && -f "$COMFYUI_MANAGER_DIR/requirements.txt" ]]; then
  if [[ ! -x "$COMFYUI_VENV_DIR/bin/python" ]]; then
    warn "No hay venv de ComfyUI para instalar requirements del manager"
  elif ! "$COMFYUI_VENV_DIR/bin/python" -m pip --version >/dev/null 2>&1; then
    warn "El venv de ComfyUI no tiene pip; no se instalan requirements del manager"
  elif [[ "$mode" == "apply" ]]; then
    "$COMFYUI_VENV_DIR/bin/python" -m pip install -r "$COMFYUI_MANAGER_DIR/requirements.txt"
    log "Requirements de ComfyUI-Manager instalados"
  else
    if "$COMFYUI_VENV_DIR/bin/python" -m pip show GitPython >/dev/null 2>&1; then
      kv "manager_requirements" "installed_or_partially_installed"
    else
      warn "Faltaria instalar requirements de ComfyUI-Manager"
    fi
  fi
fi

if [[ -d "$COMFYUI_MANAGER_DIR/.git" ]]; then
  kv "manager_git_branch" "$(git -C "$COMFYUI_MANAGER_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  kv "manager_git_head" "$(git -C "$COMFYUI_MANAGER_DIR" rev-parse --short HEAD 2>/dev/null || true)"
fi

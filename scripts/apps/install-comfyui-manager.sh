#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"
manager_install_method="${COMFYUI_MANAGER_INSTALL_METHOD:-core}"
manager_requirements_file="$COMFYUI_DIR/manager_requirements.txt"
legacy_manager_backup_dir=""
legacy_manager_backup_root="$COMFYUI_DIR/.legacy-manager-backups"

require_cmd git
require_cmd python3

[[ -d "$COMFYUI_DIR" ]] || die "ComfyUI debe existir antes de instalar ComfyUI-Manager: $COMFYUI_DIR"
[[ "$manager_install_method" == "core" || "$manager_install_method" == "legacy" ]] || die "COMFYUI_MANAGER_INSTALL_METHOD invalido: $manager_install_method"

print_header "Instalacion de ComfyUI-Manager"
kv "mode" "$mode"
kv "install_method" "$manager_install_method"
kv "manager_enable" "${COMFYUI_MANAGER_ENABLE:-true}"
kv "manager_use_legacy_ui" "${COMFYUI_MANAGER_USE_LEGACY_UI:-false}"
kv "manager_dir" "$COMFYUI_MANAGER_DIR"
kv "repo_url" "$COMFYUI_MANAGER_REPO_URL"
kv "repo_ref" "$COMFYUI_MANAGER_REPO_REF"
kv "manager_requirements_file" "$manager_requirements_file"
kv "legacy_manager_backup_root" "$legacy_manager_backup_root"

if [[ "$manager_install_method" == "core" ]]; then
  [[ -f "$manager_requirements_file" ]] || die "No existe manager_requirements.txt en $manager_requirements_file"

  shopt -s nullglob
  for legacy_path in "$COMFYUI_DIR"/custom_nodes/comfyui-manager*; do
    [[ -e "$legacy_path" ]] || continue
    kv "legacy_manager_dir" "$legacy_path"
    if [[ -d "$legacy_path/.git" ]]; then
      kv "legacy_manager_git_head" "$(git -C "$legacy_path" rev-parse --short HEAD 2>/dev/null || true)"
    fi
    if [[ "$mode" == "apply" ]]; then
      mkdir -p "$legacy_manager_backup_root"
      legacy_manager_backup_dir="$legacy_manager_backup_root/$(basename "$legacy_path").$(date +%Y%m%d%H%M%S)"
      mv "$legacy_path" "$legacy_manager_backup_dir"
      log "Instalacion legacy de ComfyUI-Manager movida a $legacy_manager_backup_dir"
    else
      warn "Existe una instalacion legacy de ComfyUI-Manager en custom_nodes; en apply se migrara fuera de custom_nodes"
    fi
  done
  shopt -u nullglob

  if [[ "${COMFYUI_MANAGER_INSTALL_REQUIREMENTS:-true}" == "true" ]]; then
    if [[ ! -x "$COMFYUI_VENV_DIR/bin/python" ]]; then
      warn "No hay venv de ComfyUI para instalar el manager integrado"
    elif ! "$COMFYUI_VENV_DIR/bin/python" -m pip --version >/dev/null 2>&1; then
      warn "El venv de ComfyUI no tiene pip; no se instalan dependencies del manager integrado"
    elif [[ "$mode" == "apply" ]]; then
      "$COMFYUI_VENV_DIR/bin/python" -m pip install -r "$manager_requirements_file"
      log "Dependencias del manager integrado instaladas"
    else
      warn "Faltaria instalar manager_requirements.txt"
    fi
  fi

  if [[ -x "$COMFYUI_VENV_DIR/bin/python" ]]; then
    if "$COMFYUI_VENV_DIR/bin/python" - <<'PY' >/tmp/openclaw-comfyui-manager-version.txt 2>/dev/null
import importlib.metadata
import importlib.util

spec = importlib.util.find_spec("comfyui_manager")
if spec is None:
    raise SystemExit(1)

print(importlib.metadata.version("comfyui-manager"))
PY
    then
      kv "manager_python_package" "installed"
      kv "manager_python_version" "$(cat /tmp/openclaw-comfyui-manager-version.txt)"
    else
      kv "manager_python_package" "missing"
    fi
  fi
else
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
fi

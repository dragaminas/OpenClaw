#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"

require_cmd git
require_cmd python3

requested_repo_ref="$COMFYUI_REPO_REF"
resolved_repo_ref="$COMFYUI_REPO_REF"

if [[ "$requested_repo_ref" == "latest-stable" ]]; then
  resolved_repo_ref="$(latest_github_release_tag_from_repo "$COMFYUI_REPO_URL")"
  if [[ -z "$resolved_repo_ref" ]]; then
    resolved_repo_ref="$(latest_semver_tag_from_remote "$COMFYUI_REPO_URL")"
  fi
  [[ -n "$resolved_repo_ref" ]] || die "No se pudo resolver el ultimo tag estable de ComfyUI"
fi

resolved_repo_ref_type="$(remote_git_ref_type "$COMFYUI_REPO_URL" "$resolved_repo_ref")"
[[ "$resolved_repo_ref_type" != "missing" ]] || die "No existe el ref de ComfyUI: $resolved_repo_ref"

print_header "Instalacion de ComfyUI"
kv "mode" "$mode"
kv "repo_url" "$COMFYUI_REPO_URL"
kv "repo_ref" "$requested_repo_ref"
kv "resolved_repo_ref" "$resolved_repo_ref"
kv "resolved_repo_ref_type" "$resolved_repo_ref_type"
kv "comfyui_dir" "$COMFYUI_DIR"
kv "venv_dir" "$COMFYUI_VENV_DIR"

if [[ ! -d "$COMFYUI_DIR/.git" ]]; then
  if [[ "$mode" == "apply" ]]; then
    rm -rf "$COMFYUI_DIR"
    git clone --depth 1 --branch "$resolved_repo_ref" "$COMFYUI_REPO_URL" "$COMFYUI_DIR"
    log "Repositorio ComfyUI clonado"
  else
    warn "ComfyUI aun no esta clonado"
  fi
else
  kv "git_head" "$(git -C "$COMFYUI_DIR" rev-parse --short HEAD)"
  if [[ "$mode" == "apply" ]]; then
    if [[ "$resolved_repo_ref_type" == "tag" ]]; then
      git -C "$COMFYUI_DIR" fetch --depth 1 origin "refs/tags/$resolved_repo_ref:refs/tags/$resolved_repo_ref"
      git -C "$COMFYUI_DIR" checkout --detach "$resolved_repo_ref"
    else
      git -C "$COMFYUI_DIR" fetch --depth 1 origin "$resolved_repo_ref"
      git -C "$COMFYUI_DIR" checkout -B "$resolved_repo_ref" "origin/$resolved_repo_ref"
    fi
    log "Repositorio ComfyUI actualizado"
  fi
fi

if [[ "${COMFYUI_CREATE_VENV:-true}" == "true" ]]; then
  recreate_for_missing_pip="false"
  if [[ -x "$COMFYUI_VENV_DIR/bin/python" ]] && ! "$COMFYUI_VENV_DIR/bin/python" -m pip --version >/dev/null 2>&1; then
    if [[ "${COMFYUI_RECREATE_VENV_IF_PIP_MISSING:-true}" == "true" ]]; then
      recreate_for_missing_pip="true"
    fi
  fi

  if [[ "$recreate_for_missing_pip" == "true" && "$mode" == "apply" ]]; then
    warn "El venv actual no tiene pip; se recrea ahora que el host ya soporta venv completo"
    rm -rf "$COMFYUI_VENV_DIR"
  fi

  if [[ ! -x "$COMFYUI_VENV_DIR/bin/python" && "$mode" == "apply" ]]; then
    if python3 -m venv "$COMFYUI_VENV_DIR"; then
      log "Venv de ComfyUI creado"
    else
      warn "No se pudo crear el venv con pip; se intenta crear sin pip"
      rm -rf "$COMFYUI_VENV_DIR"
      python3 -m venv --without-pip "$COMFYUI_VENV_DIR"
      warn "Venv creado sin pip. Para instalar requirements hara falta python3-venv o una estrategia alternativa"
    fi
  fi

  if [[ -x "$COMFYUI_VENV_DIR/bin/python" ]]; then
    "$COMFYUI_VENV_DIR/bin/python" --version
  else
    warn "No existe venv de ComfyUI"
  fi
fi

if [[ "${COMFYUI_INSTALL_REQUIREMENTS:-false}" == "true" ]]; then
  [[ -x "$COMFYUI_VENV_DIR/bin/python" ]] || die "No existe el python del venv para instalar requirements"
  if [[ "$mode" == "apply" ]]; then
    "$COMFYUI_VENV_DIR/bin/python" -m pip --version >/dev/null 2>&1 || die "El venv no dispone de pip. Instala python3-venv o recrea el entorno"
    "$COMFYUI_VENV_DIR/bin/python" -m pip install --upgrade pip
    "$COMFYUI_VENV_DIR/bin/python" -m pip install -r "$COMFYUI_DIR/requirements.txt"
    log "Dependencias de ComfyUI instaladas"
  else
    warn "Faltaria instalar requirements de ComfyUI"
  fi
fi

if [[ -f "$COMFYUI_DIR/main.py" ]]; then
  kv "main_py" "$COMFYUI_DIR/main.py"
else
  warn "No existe main.py en $COMFYUI_DIR"
fi

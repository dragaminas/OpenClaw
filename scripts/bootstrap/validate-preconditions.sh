#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

assert_not_root

print_header "Precondiciones del host"
kv "repo_root" "$REPO_ROOT"
kv "work_user" "$WORK_USER"
kv "primary_chat_channel" "$PRIMARY_CHAT_CHANNEL"

require_cmd lsblk
require_cmd findmnt
require_cmd gsettings

root_source="$(findmnt -n -o SOURCE / || true)"
root_target="$(findmnt -n -o TARGET / || true)"
root_fstype="$(findmnt -n -o FSTYPE / || true)"

print_header "Sistema base"
kv "root_source" "$root_source"
kv "root_target" "$root_target"
kv "root_fstype" "$root_fstype"

print_header "Sesion grafica y herramientas"
if command -v gsettings >/dev/null 2>&1; then
  kv "gsettings" "$(command -v gsettings)"
fi
if command -v openclaw >/dev/null 2>&1; then
  kv "openclaw" "$(command -v openclaw)"
else
  warn "OpenClaw no esta instalado"
fi
if command -v blender >/dev/null 2>&1; then
  kv "blender" "$(command -v blender)"
else
  warn "Blender no esta instalado"
fi
if [[ -d "$COMFYUI_DIR" ]]; then
  kv "comfyui_dir" "$COMFYUI_DIR"
else
  warn "No existe COMFYUI_DIR=$COMFYUI_DIR"
fi

print_header "Resultado"
log "Validacion completada. Usa scripts/hardening/check-mounts.sh para revisar discos y montajes."

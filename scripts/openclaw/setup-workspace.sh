#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"

print_header "Studio workspace"
for dir in "$STUDIO_DIR"; do
  if [[ "$mode" == "apply" ]]; then
    mkdir -p "$dir"
    ensure_mode "$dir" "$STUDIO_DIR_MODE"
  fi
  if [[ -d "$dir" ]]; then
    stat -c '%a %U %G %n' "$dir"
  else
    warn "Falta el directorio: $dir"
  fi
done

for dir in \
  "$STUDIO_DIR/BlenderProjects" \
  "$STUDIO_DIR/ComfyUI" \
  "$STUDIO_DIR/Exports" \
  "$STUDIO_DIR/Assets" \
  "$STUDIO_DIR/Downloads"; do
  if [[ "$mode" == "apply" ]]; then
    mkdir -p "$dir"
    ensure_mode "$dir" "$STUDIO_PROJECT_DIR_MODE"
  fi
  if [[ -d "$dir" ]]; then
    stat -c '%a %U %G %n' "$dir"
  else
    warn "Falta el directorio: $dir"
  fi
done

log "Revision de workspace completada"

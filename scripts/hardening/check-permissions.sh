#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

state_dir="${1:-$OPENCLAW_STATE_DIR}"
credentials_dir="$state_dir/credentials"

print_header "Permisos sensibles"

if [[ -d "$state_dir" ]]; then
  stat -c '%a %U %G %n' "$state_dir"
else
  warn "No existe state dir: $state_dir"
fi

if [[ -d "$credentials_dir" ]]; then
  stat -c '%a %U %G %n' "$credentials_dir"
  mode="$(stat -c '%a' "$credentials_dir")"
  if [[ "$mode" != "$OPENCLAW_CREDENTIALS_MODE" ]]; then
    warn "Credenciales con permisos inseguros: $mode"
    exit 5
  fi
else
  warn "No existe credentials dir: $credentials_dir"
fi

log "Permisos principales en orden"

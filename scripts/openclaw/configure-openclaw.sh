#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"
config_path="$OPENCLAW_STATE_DIR/openclaw.json"
credentials_dir="$OPENCLAW_STATE_DIR/credentials"

require_cmd openclaw
[[ -f "$config_path" ]] || die "No existe el archivo de configuracion: $config_path"

print_header "Estado actual"
openclaw config validate
kv "allowInsecureAuth" "$(openclaw config get gateway.controlUi.allowInsecureAuth)"
kv "gateway_bind" "$(openclaw config get gateway.bind)"

if [[ "$mode" == "apply" ]]; then
  if [[ -d "$credentials_dir" ]]; then
    chmod "$OPENCLAW_CREDENTIALS_MODE" "$credentials_dir"
    log "Permisos aplicados a $credentials_dir"
  fi
  openclaw config set gateway.controlUi.allowInsecureAuth false >/dev/null
  openclaw config set gateway.bind loopback >/dev/null
  log "Configuracion endurecida aplicada"
fi

print_header "Estado final"
kv "allowInsecureAuth" "$(openclaw config get gateway.controlUi.allowInsecureAuth)"
kv "gateway_bind" "$(openclaw config get gateway.bind)"
if [[ -d "$credentials_dir" ]]; then
  stat -c '%a %U %G %n' "$credentials_dir"
fi

log "Configuracion de OpenClaw revisada"

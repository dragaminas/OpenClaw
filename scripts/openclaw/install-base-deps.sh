#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"
required_commands=(curl git python3 systemctl xdg-open realpath rsync tar)
packages=(curl git jq python3 python3-venv rsync xdg-utils)
missing=()

print_header "Dependencias base"
kv "mode" "$mode"

for cmd in "${required_commands[@]}"; do
  if command -v "$cmd" >/dev/null 2>&1; then
    kv "$cmd" "$(command -v "$cmd")"
  else
    warn "Falta el comando requerido: $cmd"
    missing+=("$cmd")
  fi
done

if command -v apt-get >/dev/null 2>&1; then
  kv "package_manager" "apt"
else
  warn "No se detecto apt-get; instala manualmente los paquetes base si faltan"
fi

if command -v node >/dev/null 2>&1; then
  kv "node_version" "$(node --version)"
else
  warn "Node se instalara o actualizara desde scripts/openclaw/install-openclaw.sh"
fi

if [[ "${#missing[@]}" -gt 0 && "$mode" == "apply" ]]; then
  command -v apt-get >/dev/null 2>&1 || die "No se puede instalar dependencias base automaticamente sin apt-get"
  require_cmd sudo
  sudo apt-get update
  sudo apt-get install -y "${packages[@]}"
  log "Dependencias base instaladas"
fi

if [[ "${#missing[@]}" -eq 0 ]]; then
  log "Dependencias base disponibles"
fi

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

assert_not_root

print_header "OpenClaw"
if command -v openclaw >/dev/null 2>&1; then
  kv "openclaw_bin" "$(command -v openclaw)"
  openclaw --version
else
  die "OpenClaw no esta instalado. Instala primero Node y el paquete openclaw."
fi

if command -v node >/dev/null 2>&1; then
  kv "node_bin" "$(command -v node)"
  node --version
else
  warn "Node no esta disponible en PATH"
fi

log "Verificacion de instalacion completada"

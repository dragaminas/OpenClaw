#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"
install_method="${OPENCLAW_INSTALL_METHOD:-npm-global}"
package_spec="${OPENCLAW_PACKAGE_SPEC:-openclaw@latest}"
latest_version=""

print_header "OpenClaw"
kv "mode" "$mode"
kv "install_method" "$install_method"
kv "package_spec" "$package_spec"
kv "installer_url" "$OPENCLAW_INSTALLER_URL"

if command -v node >/dev/null 2>&1; then
  kv "node_bin" "$(command -v node)"
  kv "node_version" "$(node --version)"
else
  warn "Node no esta disponible en PATH"
fi

if command -v npm >/dev/null 2>&1; then
  kv "npm_bin" "$(command -v npm)"
  kv "npm_version" "$(npm --version)"
  latest_version="$(npm view openclaw version 2>/dev/null || true)"
  [[ -n "$latest_version" ]] && kv "latest_openclaw_version" "$latest_version"
else
  warn "npm no esta disponible en PATH"
fi

if command -v openclaw >/dev/null 2>&1; then
  kv "openclaw_bin" "$(command -v openclaw)"
  openclaw --version
else
  warn "OpenClaw no esta instalado todavia"
fi

if [[ "$mode" == "apply" ]]; then
  case "$install_method" in
    npm-global)
      if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
        curl -fsSL "$OPENCLAW_INSTALLER_URL" | bash -s -- --no-onboard
      else
        npm install -g "$package_spec"
      fi
      ;;
    official-installer)
      curl -fsSL "$OPENCLAW_INSTALLER_URL" | bash -s -- --no-onboard
      ;;
    *)
      die "OPENCLAW_INSTALL_METHOD invalido: $install_method"
      ;;
  esac
fi

command -v openclaw >/dev/null 2>&1 || die "OpenClaw sigue sin estar disponible tras la instalacion"

kv "openclaw_bin_final" "$(command -v openclaw)"
openclaw --version
if ! openclaw doctor --non-interactive >/tmp/openclaw-doctor.log 2>&1; then
  warn "openclaw doctor reporto avisos; revisa /tmp/openclaw-doctor.log"
fi

log "Instalacion o actualizacion de OpenClaw revisada"

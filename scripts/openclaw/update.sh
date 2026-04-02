#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"
current_version=""
latest_version=""

if command -v openclaw >/dev/null 2>&1; then
  current_version="$(openclaw --version | sed -n 's/^OpenClaw \([^ ]*\).*/\1/p')"
fi

if command -v npm >/dev/null 2>&1; then
  latest_version="$(npm view openclaw version 2>/dev/null || true)"
fi

print_header "Actualizacion de OpenClaw"
kv "mode" "$mode"
kv "current_version" "${current_version:-missing}"
kv "latest_version" "${latest_version:-unknown}"
kv "package_spec" "$OPENCLAW_PACKAGE_SPEC"

if [[ "$mode" == "apply" ]]; then
  "$SCRIPT_DIR/backup.sh" apply >/dev/null
  "$SCRIPT_DIR/install-openclaw.sh" apply
  "$REPO_ROOT/scripts/services/install-user-services.sh" apply
  if [[ "${INSTALL_DESKTOP_SHORTCUTS:-true}" == "true" && "${OPENCLAW_DESKTOP_SHORTCUTS_ENABLE:-true}" == "true" ]]; then
    "$REPO_ROOT/scripts/desktop/install-shortcuts.sh" apply
  fi
  openclaw doctor --repair --non-interactive >/tmp/openclaw-update-doctor.log 2>&1 || true
  "$REPO_ROOT/scripts/doctor/workstation-health.sh"
fi

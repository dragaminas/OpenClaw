#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

message="${1:-$OPENCLAW_STUDIO_ACTIONS_COMMAND_PREFIX blender status}"

print_header "Prueba de Studio Actions"
kv "message" "$message"

node "$OPENCLAW_STUDIO_ACTIONS_PLUGIN_DIR/test-driver.mjs" "$message"

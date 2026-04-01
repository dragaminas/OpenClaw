#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

print_header "Herramientas creativas"
for tool_name in blender gimp inkscape krita; do
  if command -v "$tool_name" >/dev/null 2>&1; then
    kv "$tool_name" "$(command -v "$tool_name")"
  else
    warn "$tool_name no esta instalado"
  fi
done

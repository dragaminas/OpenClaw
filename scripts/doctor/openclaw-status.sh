#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

require_cmd openclaw

print_header "OpenClaw status"
openclaw status --all --json

print_header "OpenClaw security audit"
openclaw security audit --json

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

print_header "ComfyUI smoke validation"

python_bin="${COMFYUI_VENV_DIR:-$COMFYUI_DIR/.venv}/bin/python"
if [[ ! -x "$python_bin" ]]; then
  python_bin="$(command -v python3)"
fi

PYTHONPATH="$REPO_ROOT/src" "$python_bin" -m openclaw_studio.comfyui_smoke_validation "$@"

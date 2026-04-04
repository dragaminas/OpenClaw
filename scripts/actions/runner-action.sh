#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

command_name="${1:-help}"
runner_id="${2:-}"

print_help() {
  cat <<EOF
Comandos disponibles:
- help
- describe <runner_id>
- list-targets <runner_id> <operation_kind>
- start <runner_id> <operation_kind> [target_id]
- status <runner_id> <run_id>
- cancel <runner_id> <run_id>
- result <runner_id> <run_id>
EOF
}

resolve_python_bin() {
  if [[ -n "${OPENCLAW_STUDIO_PYTHON_BIN:-}" && -x "${OPENCLAW_STUDIO_PYTHON_BIN:-}" ]]; then
    printf '%s\n' "$OPENCLAW_STUDIO_PYTHON_BIN"
    return 0
  fi

  if [[ "$runner_id" == "comfyui" ]]; then
    local comfy_python="${COMFYUI_VENV_DIR:-$COMFYUI_DIR/.venv}/bin/python"
    if [[ -x "$comfy_python" ]]; then
      printf '%s\n' "$comfy_python"
      return 0
    fi
  fi

  command -v python3
}

case "$command_name" in
  help)
    print_help
    ;;
  describe|list-targets|start|status|cancel|result)
    python_bin="$(resolve_python_bin)"
    export PYTHONPATH="$REPO_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
    exec "$python_bin" -m openclaw_studio.runner_cli --json "$@"
    ;;
  *)
    die "Uso: $0 [help|describe|list-targets|start|status|cancel|result] ..."
    ;;
esac

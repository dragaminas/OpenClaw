#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

command_name="${1:-help}"

print_help() {
  cat <<EOF
Comandos disponibles:
- help
- status
- start
- restart
- open
- stop
- url
- workflows
- open-workflow <alias|use_case_id>
- workflow-path <alias|use_case_id>
EOF
}

case "$command_name" in
  help)
    print_help
    ;;
  status)
    "$REPO_ROOT/scripts/apps/comfyui.sh" status
    ;;
  start)
    "$REPO_ROOT/scripts/apps/comfyui.sh" start-service
    ;;
  restart)
    "$REPO_ROOT/scripts/apps/comfyui.sh" restart-service
    ;;
  open)
    "$REPO_ROOT/scripts/apps/comfyui.sh" open-ui
    ;;
  stop)
    "$REPO_ROOT/scripts/apps/comfyui.sh" stop-service
    ;;
  url)
    "$REPO_ROOT/scripts/apps/comfyui.sh" url
    ;;
  workflows)
    "$REPO_ROOT/scripts/apps/comfyui-workflow-library.sh" list
    ;;
  open-workflow)
    workflow_ref="${2:-}"
    [[ -n "$workflow_ref" ]] || die "Debes indicar un alias o use_case_id."
    "$REPO_ROOT/scripts/apps/comfyui-workflow-library.sh" open "$workflow_ref"
    ;;
  workflow-path)
    workflow_ref="${2:-}"
    [[ -n "$workflow_ref" ]] || die "Debes indicar un alias o use_case_id."
    "$REPO_ROOT/scripts/apps/comfyui-workflow-library.sh" describe "$workflow_ref"
    ;;
  *)
    die "Uso: $0 [help|status|start|restart|open|stop|url|workflows|open-workflow <alias|use_case_id>|workflow-path <alias|use_case_id>]"
    ;;
esac

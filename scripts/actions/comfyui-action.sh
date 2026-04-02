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
  *)
    die "Uso: $0 [help|status|start|restart|open|stop|url]"
    ;;
esac

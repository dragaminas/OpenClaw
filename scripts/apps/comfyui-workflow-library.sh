#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

command_name="${1:-help}"
workflow_ref="${2:-}"
module_dir="$COMFYUI_DIR/custom_nodes/openclaw-workflows"
comfyui_url="http://${COMFYUI_HOST}:${COMFYUI_PORT}/"

python_workflow_library() {
  env PYTHONPATH="$REPO_ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
    python3 -m openclaw_studio.comfyui_workflow_library "$@"
}

print_help() {
  cat <<EOF
Comandos disponibles:
- help
- sync
- list
- describe <alias|use_case_id>
- explain <alias|use_case_id>
- open <alias|use_case_id>
EOF
}

require_cmd python3

workflow_template_route_ready() {
  local workflow_alias="$1"

  python3 - "$COMFYUI_HOST" "$COMFYUI_PORT" "$workflow_alias" <<'PY' >/dev/null 2>&1
import sys
import urllib.request

host = sys.argv[1]
port = sys.argv[2]
workflow_alias = sys.argv[3]
url = (
    f"http://{host}:{port}/api/workflow_templates/"
    f"openclaw-workflows/{workflow_alias}.json"
)

try:
    with urllib.request.urlopen(url, timeout=3) as response:
        raise SystemExit(0 if response.status == 200 else 1)
except Exception:
    raise SystemExit(1)
PY
}

build_template_open_url() {
  local workflow_alias="$1"

  printf '%s?template=%s&source=%s\n' \
    "$comfyui_url" \
    "$workflow_alias" \
    "openclaw-workflows"
}

case "$command_name" in
  help)
    print_help
    ;;
  sync)
    python_workflow_library sync
    ;;
  list)
    python_workflow_library list
    if tcp_port_is_listening "$COMFYUI_HOST" "$COMFYUI_PORT" && ! workflow_template_route_ready "prepara-video"; then
      printf 'nota=ComfyUI sigue corriendo sin registrar openclaw-workflows; usa "studio comfyui abre workflow prepara-video" o reinicia ComfyUI.\n'
    fi
    ;;
  describe)
    [[ -n "$workflow_ref" ]] || die "Debes indicar un alias o use_case_id."
    python_workflow_library describe "$workflow_ref"
    ;;
  explain)
    [[ -n "$workflow_ref" ]] || die "Debes indicar un alias o use_case_id."
    python_workflow_library explain "$workflow_ref"
    ;;
  open)
    [[ -n "$workflow_ref" ]] || die "Debes indicar un alias o use_case_id."
    python_workflow_library sync >/dev/null

    workflow_description="$(python_workflow_library describe "$workflow_ref")"
    workflow_alias="$(printf '%s\n' "$workflow_description" | sed -n 's/^alias=//p' | head -n 1)"
    [[ -n "$workflow_alias" ]] || die "No pude resolver el alias del workflow solicitado."

    if tcp_port_is_listening "$COMFYUI_HOST" "$COMFYUI_PORT"; then
      if workflow_template_route_ready "$workflow_alias"; then
        "$REPO_ROOT/scripts/apps/comfyui.sh" wait-ready >/dev/null
      else
        "$REPO_ROOT/scripts/apps/comfyui.sh" restart-service >/dev/null
      fi
    else
      "$REPO_ROOT/scripts/apps/comfyui.sh" start-service >/dev/null
    fi

    workflow_template_route_ready "$workflow_alias" || die "ComfyUI no expuso el template openclaw-workflows/$workflow_alias tras preparar la biblioteca."
    template_open_url="$(build_template_open_url "$workflow_alias")"
    open_output="$("$REPO_ROOT/scripts/apps/comfyui.sh" open-ui "$template_open_url" 2>&1)"

    printf 'Workflow abierto en ComfyUI usando el template OpenClaw exacto.\n'
    printf '%s\n' "$workflow_description"
    printf 'ui_url=%s\n' "$comfyui_url"
    printf 'template_url=%s\n' "$template_open_url"
    printf '%s\n' "$open_output"
    ;;
  *)
    die "Uso: $0 [help|sync|list|describe <alias|use_case_id>|explain <alias|use_case_id>|open <alias|use_case_id>]"
    ;;
esac

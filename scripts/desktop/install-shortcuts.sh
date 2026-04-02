#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"
template_dir="$REPO_ROOT/configs/desktop"
desktop_dir="$WORK_HOME/.local/share/applications"

print_header "Accesos directos de escritorio"
kv "mode" "$mode"
kv "template_dir" "$template_dir"
kv "desktop_dir" "$desktop_dir"

shopt -s nullglob
templates=("$template_dir"/*.desktop.template)
shopt -u nullglob
[[ "${#templates[@]}" -gt 0 ]] || die "No se encontraron plantillas .desktop en $template_dir"

for template_path in "${templates[@]}"; do
  desktop_name="$(basename "${template_path%.template}")"
  target_path="$desktop_dir/$desktop_name"
  kv "shortcut" "$target_path"

  if [[ "$mode" == "apply" ]]; then
    mkdir -p "$desktop_dir"
    sed \
      -e "s|__REPO_ROOT__|$REPO_ROOT|g" \
      -e "s|__WORK_HOME__|$WORK_HOME|g" \
      "$template_path" >"$target_path"
    chmod 755 "$target_path"
  fi
done

if [[ "$mode" == "apply" && -x "$(command -v update-desktop-database || true)" ]]; then
  update-desktop-database "$desktop_dir" >/dev/null 2>&1 || true
fi

log "Accesos directos revisados"

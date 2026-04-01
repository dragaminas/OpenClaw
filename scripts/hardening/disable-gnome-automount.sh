#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"
require_cmd gsettings

current_automount="$(gsettings get org.gnome.desktop.media-handling automount)"
current_open="$(gsettings get org.gnome.desktop.media-handling automount-open)"

print_header "Estado GNOME"
kv "automount" "$current_automount"
kv "automount_open" "$current_open"

if [[ "$mode" == "apply" ]]; then
  gsettings set org.gnome.desktop.media-handling automount false
  gsettings set org.gnome.desktop.media-handling automount-open false
  log "Automontaje y apertura automatica deshabilitados en GNOME"
fi

new_automount="$(gsettings get org.gnome.desktop.media-handling automount)"
new_open="$(gsettings get org.gnome.desktop.media-handling automount-open)"

if [[ "$new_automount" != "false" || "$new_open" != "false" ]]; then
  warn "GNOME sigue con automontaje activo o incompleto"
  exit 4
fi

log "GNOME no automonta ni autoabre unidades"

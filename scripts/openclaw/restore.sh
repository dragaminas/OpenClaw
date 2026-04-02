#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"
archive_path="${2:-}"
staging_dir=""

[[ -n "$archive_path" ]] || die "Debes indicar la ruta del archivo .tar.gz a restaurar"
[[ -f "$archive_path" ]] || die "No existe el archivo de backup: $archive_path"

print_header "Restore de OpenClaw"
kv "mode" "$mode"
kv "archive_path" "$archive_path"

staging_dir="$(mktemp -d)"
trap 'rm -rf "$staging_dir"' EXIT
tar -xzf "$archive_path" -C "$staging_dir"

print_header "Contenido"
find "$staging_dir" -type f | sed "s#^$staging_dir/##" | sort

if [[ -f "$staging_dir/manifest.txt" ]]; then
  print_header "Manifest"
  sed -n '1,80p' "$staging_dir/manifest.txt"
fi

if [[ "$mode" == "apply" ]]; then
  rsync -a --exclude manifest.txt "$staging_dir"/ /
  log "Backup restaurado sobre el entorno actual"
fi

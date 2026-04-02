#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"
fstab_path="${FSTAB_PATH:-/etc/fstab}"
managed_tag="${OPENCLAW_FSTAB_MANAGED_TAG:-x-openclaw-managed}"
managed_count="$(awk -v tag="$managed_tag" 'NF && $0 !~ /^[[:space:]]*#/ && index($0, tag) > 0 {count++} END {print count+0}' "$fstab_path")"
needs_hardening="$(awk -v tag="$managed_tag" '
  NF && $0 !~ /^[[:space:]]*#/ && index($0, tag) > 0 {
    split($4, opts, ",")
    has_noauto = 0
    has_nofail = 0
    for (i in opts) {
      if (opts[i] == "noauto") has_noauto = 1
      if (opts[i] == "nofail") has_nofail = 1
    }
    if (!has_noauto || !has_nofail) print $0
  }
' "$fstab_path")"

print_header "Politica fstab"
kv "mode" "$mode"
kv "fstab_path" "$fstab_path"
kv "managed_tag" "$managed_tag"
kv "managed_entries" "$managed_count"

print_header "Entradas activas"
awk 'NF && $0 !~ /^[[:space:]]*#/' "$fstab_path"

if [[ -n "$needs_hardening" ]]; then
  print_header "Entradas gestionadas que necesitan noauto,nofail"
  printf '%s\n' "$needs_hardening"
else
  log "No hay entradas gestionadas que necesiten endurecimiento"
fi

if [[ "$mode" == "apply" ]]; then
  [[ -w "$fstab_path" ]] || die "Necesitas permisos de escritura sobre $fstab_path para aplicar cambios"
  backup_path="${fstab_path}.openclaw.$(date +%Y%m%d%H%M%S).bak"
  cp "$fstab_path" "$backup_path"
  python3 - "$fstab_path" "$managed_tag" <<'PY'
import pathlib
import sys

fstab_path = pathlib.Path(sys.argv[1])
tag = sys.argv[2]
lines = fstab_path.read_text().splitlines()
updated = []

for raw in lines:
    stripped = raw.strip()
    if not stripped or stripped.startswith("#") or tag not in raw:
        updated.append(raw)
        continue

    parts = raw.split()
    if len(parts) < 4:
        updated.append(raw)
        continue

    opts = []
    for item in parts[3].split(","):
        if item not in opts:
            opts.append(item)
    for item in ("noauto", "nofail"):
        if item not in opts:
            opts.append(item)
    parts[3] = ",".join(opts)
    updated.append("\t".join(parts))

fstab_path.write_text("\n".join(updated) + "\n")
PY
  kv "backup_path" "$backup_path"
  log "fstab actualizado solo sobre entradas marcadas con $managed_tag"
fi

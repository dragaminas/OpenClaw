#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

print_header "Discos detectados"
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS,MODEL,TRAN

print_header "Montajes activos"
findmnt -rn -o TARGET,SOURCE,FSTYPE,OPTIONS

print_header "NVMe internos"
internal_lines="$(lsblk -nr -o NAME,TYPE,TRAN,MOUNTPOINTS | awk '$2=="disk" && $3=="nvme" {print}')"
if [[ -z "$internal_lines" ]]; then
  log "No se detectaron discos nvme internos"
else
  printf '%s\n' "$internal_lines"
fi

mounted_nvme="$(lsblk -nr -o NAME,TYPE,TRAN,MOUNTPOINTS | awk '$2=="part" && $3=="nvme" && $4 != "" {print}')"
if [[ -n "$mounted_nvme" ]]; then
  warn "Hay particiones NVMe montadas:"
  printf '%s\n' "$mounted_nvme"
  exit 3
fi

log "No hay particiones NVMe montadas"

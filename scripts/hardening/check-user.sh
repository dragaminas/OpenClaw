#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

target_user="${1:-$WORK_USER}"

print_header "Usuario de trabajo"
if ! id "$target_user" >/dev/null 2>&1; then
  die "El usuario $target_user no existe"
fi

kv "user" "$target_user"
kv "uid" "$(id -u "$target_user")"
kv "home" "$(getent passwd "$target_user" | cut -d: -f6)"

groups_list="$(id -nG "$target_user")"
kv "groups" "$groups_list"

dangerous=()
for group_name in sudo wheel disk adm; do
  if id -nG "$target_user" | tr ' ' '\n' | rg -x "$group_name" >/dev/null 2>&1; then
    dangerous+=("$group_name")
  fi
done

if [[ "${#dangerous[@]}" -gt 0 ]]; then
  warn "El usuario pertenece a grupos sensibles: ${dangerous[*]}"
  exit 2
fi

log "Usuario apto para runtime no privilegiado"

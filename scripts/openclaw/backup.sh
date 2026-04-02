#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"
archive_path="${2:-$OPENCLAW_BACKUP_DIR/openclaw-backup-$(date +%Y%m%dT%H%M%S).tar.gz}"
staging_dir=""
include_paths=(
  "$REPO_ROOT/.env"
  "$OPENCLAW_STATE_DIR/openclaw.json"
  "$WORK_HOME/.config/systemd/user/openclaw-gateway.service"
  "$WORK_HOME/.config/systemd/user/openclaw-node.service"
  "$WORK_HOME/.config/systemd/user/comfyui.service"
  "$COMFYUI_DIR/user/default"
  "$COMFYUI_DIR/user/__manager"
  "$REPO_ROOT/plugins/studio-actions/openclaw.plugin.json"
)
excluded_notes=(
  "$OPENCLAW_STATE_DIR/credentials (secretos; excluido por defecto)"
  "$OPENCLAW_STATE_DIR/agents/main/agent/auth-profiles.json (secretos; excluido por defecto)"
  "$COMFYUI_DIR/models (artefactos pesados; excluido por defecto)"
  "$COMFYUI_DIR/output (artefactos pesados; excluido por defecto)"
)

if [[ "${OPENCLAW_BACKUP_INCLUDE_CREDENTIALS:-false}" == "true" ]]; then
  include_paths+=("$OPENCLAW_STATE_DIR/credentials" "$OPENCLAW_STATE_DIR/agents/main/agent/auth-profiles.json")
fi

if [[ "${OPENCLAW_BACKUP_INCLUDE_COMFY_OUTPUTS:-false}" == "true" ]]; then
  include_paths+=("$COMFYUI_DIR/output")
fi

print_header "Backup de OpenClaw"
kv "mode" "$mode"
kv "archive_path" "$archive_path"

print_header "Incluye"
for path in "${include_paths[@]}"; do
  [[ -e "$path" ]] || continue
  printf '%s\n' "$path"
done

print_header "Excluye"
printf '%s\n' "${excluded_notes[@]}"

if [[ "$mode" == "apply" ]]; then
  mkdir -p "$(dirname "$archive_path")"
  staging_dir="$(mktemp -d)"
  manifest_path="$staging_dir/manifest.txt"

  {
    printf 'Backup creado: %s\n' "$(date -Is)"
    printf 'Perfil: %s\n' "$OPENCLAW_USAGE_PROFILE"
    printf 'Incluye credenciales: %s\n' "$OPENCLAW_BACKUP_INCLUDE_CREDENTIALS"
    printf 'Incluye outputs ComfyUI: %s\n' "$OPENCLAW_BACKUP_INCLUDE_COMFY_OUTPUTS"
    printf '\nIncluye:\n'
    for path in "${include_paths[@]}"; do
      [[ -e "$path" ]] || continue
      printf '%s\n' "$path"
      rsync -aR "$path" "$staging_dir/"
    done
    printf '\nExcluye:\n'
    printf '%s\n' "${excluded_notes[@]}"
  } >"$manifest_path"

  tar -C "$staging_dir" -czf "$archive_path" .
  rm -rf "$staging_dir"
  kv "backup_created" "$archive_path"
  log "Backup generado"
fi

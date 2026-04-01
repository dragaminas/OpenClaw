#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [[ -f "$REPO_ROOT/.env" ]]; then
  # shellcheck disable=SC1091
  source "$REPO_ROOT/.env"
elif [[ -f "$REPO_ROOT/.env.example" ]]; then
  # shellcheck disable=SC1091
  source "$REPO_ROOT/.env.example"
fi

WORK_USER="${WORK_USER:-$USER}"
WORK_HOME="${WORK_HOME:-$HOME}"
STUDIO_DIR="${STUDIO_DIR:-$HOME/Studio}"
STUDIO_DIR_MODE="${STUDIO_DIR_MODE:-755}"
STUDIO_PROJECT_DIR_MODE="${STUDIO_PROJECT_DIR_MODE:-755}"
OPENCLAW_STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
OPENCLAW_CREDENTIALS_MODE="${OPENCLAW_CREDENTIALS_MODE:-700}"
OPENCLAW_GATEWAY_HOST="${OPENCLAW_GATEWAY_HOST:-127.0.0.1}"
OPENCLAW_GATEWAY_PORT="${OPENCLAW_GATEWAY_PORT:-18789}"
PRIMARY_CHAT_CHANNEL="${PRIMARY_CHAT_CHANNEL:-whatsapp}"
OPENCLAW_STUDIO_ACTIONS_ENABLE="${OPENCLAW_STUDIO_ACTIONS_ENABLE:-true}"
OPENCLAW_STUDIO_ACTIONS_PLUGIN_DIR="${OPENCLAW_STUDIO_ACTIONS_PLUGIN_DIR:-$REPO_ROOT/plugins/studio-actions}"
OPENCLAW_STUDIO_ACTIONS_COMMAND_PREFIX="${OPENCLAW_STUDIO_ACTIONS_COMMAND_PREFIX:-studio}"
OPENCLAW_STUDIO_ACTIONS_CHANNELS="${OPENCLAW_STUDIO_ACTIONS_CHANNELS:-whatsapp}"
OPENCLAW_STUDIO_ACTIONS_ALLOW_GROUP_MESSAGES="${OPENCLAW_STUDIO_ACTIONS_ALLOW_GROUP_MESSAGES:-false}"
BLENDER_BIN="${BLENDER_BIN:-$(command -v blender || true)}"
COMFYUI_DIR="${COMFYUI_DIR:-$HOME/ComfyUI}"
COMFYUI_REPO_URL="${COMFYUI_REPO_URL:-https://github.com/comfyanonymous/ComfyUI.git}"
COMFYUI_REPO_REF="${COMFYUI_REPO_REF:-master}"
COMFYUI_VENV_DIR="${COMFYUI_VENV_DIR:-$COMFYUI_DIR/.venv}"
COMFYUI_HOST="${COMFYUI_HOST:-127.0.0.1}"
COMFYUI_PORT="${COMFYUI_PORT:-8188}"
COMFYUI_MANAGER_DIR="${COMFYUI_MANAGER_DIR:-$COMFYUI_DIR/custom_nodes/comfyui-manager}"
COMFYUI_MANAGER_REPO_URL="${COMFYUI_MANAGER_REPO_URL:-https://github.com/ltdrdata/ComfyUI-Manager.git}"
COMFYUI_MANAGER_REPO_REF="${COMFYUI_MANAGER_REPO_REF:-main}"

log() {
  printf '[INFO] %s\n' "$*"
}

warn() {
  printf '[WARN] %s\n' "$*" >&2
}

error() {
  printf '[ERROR] %s\n' "$*" >&2
}

die() {
  error "$*"
  exit 1
}

require_cmd() {
  local cmd="$1"
  command -v "$cmd" >/dev/null 2>&1 || die "Falta el comando requerido: $cmd"
}

assert_not_root() {
  [[ "${EUID:-$(id -u)}" -ne 0 ]] || die "Este script debe ejecutarse como usuario normal, no como root"
}

json_escape() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

print_header() {
  printf '\n== %s ==\n' "$*"
}

run_mode() {
  local mode="${1:-audit}"
  if [[ "$mode" != "audit" && "$mode" != "apply" ]]; then
    die "Modo invalido: $mode. Usa audit o apply"
  fi
  printf '%s' "$mode"
}

kv() {
  printf '%s=%s\n' "$1" "$2"
}

ensure_mode() {
  local path="$1"
  local mode="$2"
  if [[ -e "$path" ]]; then
    chmod "$mode" "$path"
  fi
}

systemd_user_dir() {
  printf '%s/.config/systemd/user' "$WORK_HOME"
}

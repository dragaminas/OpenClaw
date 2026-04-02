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
OPENCLAW_INSTALL_METHOD="${OPENCLAW_INSTALL_METHOD:-npm-global}"
OPENCLAW_PACKAGE_SPEC="${OPENCLAW_PACKAGE_SPEC:-openclaw@latest}"
OPENCLAW_INSTALLER_URL="${OPENCLAW_INSTALLER_URL:-https://openclaw.ai/install.sh}"
OPENCLAW_ENABLE_NODE_SERVICE="${OPENCLAW_ENABLE_NODE_SERVICE:-false}"
OPENCLAW_DESKTOP_SHORTCUTS_ENABLE="${OPENCLAW_DESKTOP_SHORTCUTS_ENABLE:-true}"
OPENCLAW_USAGE_PROFILE="${OPENCLAW_USAGE_PROFILE:-child-safe}"
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
COMFYUI_REPO_REF="${COMFYUI_REPO_REF:-latest-stable}"
COMFYUI_VENV_DIR="${COMFYUI_VENV_DIR:-$COMFYUI_DIR/.venv}"
COMFYUI_HOST="${COMFYUI_HOST:-127.0.0.1}"
COMFYUI_PORT="${COMFYUI_PORT:-8188}"
COMFYUI_MANAGER_INSTALL_METHOD="${COMFYUI_MANAGER_INSTALL_METHOD:-core}"
COMFYUI_MANAGER_ENABLE="${COMFYUI_MANAGER_ENABLE:-${COMFYUI_MANAGER_INSTALL:-true}}"
COMFYUI_MANAGER_USE_LEGACY_UI="${COMFYUI_MANAGER_USE_LEGACY_UI:-false}"
COMFYUI_MANAGER_DIR="${COMFYUI_MANAGER_DIR:-$COMFYUI_DIR/custom_nodes/comfyui-manager}"
COMFYUI_MANAGER_REPO_URL="${COMFYUI_MANAGER_REPO_URL:-https://github.com/ltdrdata/ComfyUI-Manager.git}"
COMFYUI_MANAGER_REPO_REF="${COMFYUI_MANAGER_REPO_REF:-main}"
OPENCLAW_ALLOWED_BLENDER_PROJECTS_DIR="${OPENCLAW_ALLOWED_BLENDER_PROJECTS_DIR:-$STUDIO_DIR/BlenderProjects}"
OPENCLAW_ALLOWED_COMFYUI_OUTPUT_DIR="${OPENCLAW_ALLOWED_COMFYUI_OUTPUT_DIR:-$COMFYUI_DIR/output}"
OPENCLAW_BACKUP_DIR="${OPENCLAW_BACKUP_DIR:-$WORK_HOME/Backups/OpenClaw}"
OPENCLAW_BACKUP_INCLUDE_CREDENTIALS="${OPENCLAW_BACKUP_INCLUDE_CREDENTIALS:-false}"
OPENCLAW_BACKUP_INCLUDE_COMFY_OUTPUTS="${OPENCLAW_BACKUP_INCLUDE_COMFY_OUTPUTS:-false}"

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

user_session_env_value() {
  local key="$1"
  if [[ -n "${!key:-}" ]]; then
    printf '%s\n' "${!key}"
    return 0
  fi

  if command -v systemctl >/dev/null 2>&1; then
    systemctl --user show-environment 2>/dev/null | sed -n "s/^${key}=//p" | head -n 1
  fi
}

tcp_port_is_listening() {
  local host="$1"
  local port="$2"

  python3 - "$host" "$port" <<'PY' >/dev/null 2>&1
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(1.0)
    try:
        sock.connect((host, port))
    except OSError:
        raise SystemExit(1)

raise SystemExit(0)
PY
}

wait_for_tcp_port() {
  local host="$1"
  local port="$2"
  local timeout_seconds="${3:-60}"
  local elapsed=0

  while (( elapsed < timeout_seconds )); do
    if tcp_port_is_listening "$host" "$port"; then
      return 0
    fi
    sleep 1
    elapsed=$((elapsed + 1))
  done

  return 1
}

latest_semver_tag_from_remote() {
  local repo_url="$1"

  git ls-remote --tags "$repo_url" \
    | awk '{print $2}' \
    | sed 's#refs/tags/##' \
    | sed 's/\^{}//' \
    | sort -Vu \
    | tail -n 1
}

latest_github_release_tag_from_repo() {
  local repo_url="$1"
  local repo_path api_url

  repo_path="$(printf '%s' "$repo_url" | sed -E 's#^https://github.com/##; s#^git@github.com:##; s#\.git$##')"
  api_url="https://api.github.com/repos/${repo_path}/releases/latest"

  curl -Ls "$api_url" \
    | python3 -c 'import json, sys; payload = json.load(sys.stdin); print(payload.get("tag_name", ""))'
}

remote_git_ref_type() {
  local repo_url="$1"
  local ref="$2"

  if git ls-remote --exit-code --tags "$repo_url" "refs/tags/$ref" >/dev/null 2>&1; then
    printf 'tag\n'
    return 0
  fi

  if git ls-remote --exit-code --heads "$repo_url" "refs/heads/$ref" >/dev/null 2>&1; then
    printf 'branch\n'
    return 0
  fi

  printf 'missing\n'
}

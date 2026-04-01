#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"
plugin_id="studio-actions"
plugin_dir="$OPENCLAW_STUDIO_ACTIONS_PLUGIN_DIR"

require_cmd openclaw
require_cmd node

print_header "Plugin local de Studio"
kv "mode" "$mode"
kv "plugin_id" "$plugin_id"
kv "plugin_dir" "$plugin_dir"
kv "command_prefix" "$OPENCLAW_STUDIO_ACTIONS_COMMAND_PREFIX"
kv "channels" "$OPENCLAW_STUDIO_ACTIONS_CHANNELS"
kv "allow_group_messages" "$OPENCLAW_STUDIO_ACTIONS_ALLOW_GROUP_MESSAGES"

[[ -d "$plugin_dir" ]] || die "No existe el directorio del plugin: $plugin_dir"
[[ -f "$plugin_dir/package.json" ]] || die "Falta package.json en $plugin_dir"
[[ -f "$plugin_dir/openclaw.plugin.json" ]] || die "Falta openclaw.plugin.json en $plugin_dir"
[[ -f "$plugin_dir/index.js" ]] || die "Falta index.js en $plugin_dir"

current_paths_json="$(openclaw config get plugins.load.paths --json 2>/dev/null || printf '[]')"
kv "configured_plugin_paths" "$current_paths_json"

channels_json="$(node -e 'const raw = process.argv[1] || ""; const values = raw.split(",").map((item) => item.trim()).filter(Boolean); process.stdout.write(JSON.stringify(values.length > 0 ? values : ["whatsapp"]));' "$OPENCLAW_STUDIO_ACTIONS_CHANNELS")"
merged_paths_json="$(node -e 'const current = JSON.parse(process.argv[1]); const pluginPath = process.argv[2]; const merged = [...new Set([...current, pluginPath])]; process.stdout.write(JSON.stringify(merged));' "$current_paths_json" "$plugin_dir")"

if [[ "$mode" == "apply" ]]; then
  openclaw config set plugins.load.paths "$merged_paths_json" --strict-json >/dev/null
  openclaw config set 'plugins.entries.studio-actions.config.commandPrefix' "\"$OPENCLAW_STUDIO_ACTIONS_COMMAND_PREFIX\"" --strict-json >/dev/null
  openclaw config set 'plugins.entries.studio-actions.config.channels' "$channels_json" --strict-json >/dev/null
  openclaw config set 'plugins.entries.studio-actions.config.allowGroupMessages' "$OPENCLAW_STUDIO_ACTIONS_ALLOW_GROUP_MESSAGES" --strict-json >/dev/null
  log "Plugin local registrado en la configuracion de OpenClaw"
fi

print_header "Estado del plugin"
openclaw config validate >/dev/null
kv "plugin_paths" "$(openclaw config get plugins.load.paths --json 2>/dev/null || printf '[]')"
kv "command_prefix" "$(openclaw config get 'plugins.entries.studio-actions.config.commandPrefix' 2>/dev/null || true)"
kv "channels" "$(openclaw config get 'plugins.entries.studio-actions.config.channels' --json 2>/dev/null || true)"
kv "allow_group_messages" "$(openclaw config get 'plugins.entries.studio-actions.config.allowGroupMessages' 2>/dev/null || true)"

if openclaw plugins inspect "$plugin_id" --json >/dev/null 2>&1; then
  log "Plugin $plugin_id validado por OpenClaw"
else
  warn "Plugin $plugin_id aun no aparece cargado en OpenClaw"
fi

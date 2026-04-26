#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

mode="$(run_mode "${1:-${DEFAULT_MODE:-audit}}")"
unit_dir="$(systemd_user_dir)"
unit_path="$unit_dir/thermal-monitor.service"
template_path="$REPO_ROOT/configs/systemd-user/thermal-monitor.service.template"
monitor_log_dir="${THERMAL_MONITOR_LOG_DIR:-$WORK_HOME/logs/thermal-monitor}"

[[ -f "$template_path" ]] || die "No existe la plantilla: $template_path"
[[ -f "$REPO_ROOT/scripts/doctor/thermal-monitor.sh" ]] || die "No existe el script thermal-monitor.sh"

print_header "Servicio de usuario thermal monitor"
kv "mode" "$mode"
kv "unit_path" "$unit_path"
kv "log_dir" "$monitor_log_dir"

if [[ "$mode" == "apply" ]]; then
  mkdir -p "$unit_dir"
  mkdir -p "$monitor_log_dir"
  sed \
    -e "s|__WORK_HOME__|$WORK_HOME|g" \
    -e "s|__REPO_ROOT__|$REPO_ROOT|g" \
    -e "s|__THERMAL_MONITOR_INTERVAL_SEC__|${THERMAL_MONITOR_INTERVAL_SEC:-5}|g" \
    -e "s|__THERMAL_MONITOR_LOG_DIR__|$monitor_log_dir|g" \
    -e "s|__THERMAL_MONITOR_CPU_WARN_C__|${THERMAL_MONITOR_CPU_WARN_C:-85}|g" \
    -e "s|__THERMAL_MONITOR_CPU_CRIT_C__|${THERMAL_MONITOR_CPU_CRIT_C:-92}|g" \
    -e "s|__THERMAL_MONITOR_GPU_WARN_C__|${THERMAL_MONITOR_GPU_WARN_C:-80}|g" \
    -e "s|__THERMAL_MONITOR_GPU_CRIT_C__|${THERMAL_MONITOR_GPU_CRIT_C:-88}|g" \
    "$template_path" > "$unit_path"
  systemctl --user daemon-reload
  log "Servicio de usuario thermal monitor generado"
fi

if [[ -f "$unit_path" ]]; then
  kv "service_file" "$unit_path"
  kv "service_enabled" "$(systemctl --user is-enabled thermal-monitor.service 2>/dev/null || true)"
  kv "service_active" "$(systemctl --user is-active thermal-monitor.service 2>/dev/null || true)"
else
  warn "Aun no existe $unit_path"
fi

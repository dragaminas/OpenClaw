#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

cmd="${1:-status}"

THERMAL_MONITOR_SERVICE="thermal-monitor.service"
THERMAL_MONITOR_INTERVAL_SEC="${THERMAL_MONITOR_INTERVAL_SEC:-5}"
THERMAL_MONITOR_LOG_DIR="${THERMAL_MONITOR_LOG_DIR:-$HOME/logs/thermal-monitor}"
THERMAL_MONITOR_LOG_FILE="${THERMAL_MONITOR_LOG_FILE:-$THERMAL_MONITOR_LOG_DIR/thermal-monitor.log}"
THERMAL_MONITOR_ALERT_FILE="${THERMAL_MONITOR_ALERT_FILE:-$THERMAL_MONITOR_LOG_DIR/thermal-alerts.log}"
THERMAL_MONITOR_CPU_WARN_C="${THERMAL_MONITOR_CPU_WARN_C:-85}"
THERMAL_MONITOR_CPU_CRIT_C="${THERMAL_MONITOR_CPU_CRIT_C:-92}"
THERMAL_MONITOR_GPU_WARN_C="${THERMAL_MONITOR_GPU_WARN_C:-80}"
THERMAL_MONITOR_GPU_CRIT_C="${THERMAL_MONITOR_GPU_CRIT_C:-88}"

trim() {
  local value="${1:-}"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

ensure_log_dir() {
  mkdir -p "$THERMAL_MONITOR_LOG_DIR"
}

format_millic() {
  local raw="${1:-}"
  [[ -n "$raw" && "$raw" != "N/A" ]] || {
    printf 'na'
    return 0
  }

  python3 - "$raw" <<'PY'
import sys

value = float(sys.argv[1])
print(f"{value / 1000:.1f}")
PY
}

to_number_or_na() {
  local raw="${1:-}"
  raw="$(trim "$raw")"
  if [[ -z "$raw" || "$raw" == "N/A" || "$raw" == "[Not Supported]" ]]; then
    printf 'na'
  else
    printf '%s' "$raw"
  fi
}

sanitize_token() {
  local raw="${1:-}"
  raw="$(trim "$raw")"
  raw="${raw// /_}"
  raw="${raw//,/}"
  [[ -n "$raw" ]] || raw="na"
  printf '%s' "$raw"
}

read_k10temp_raw() {
  local wanted_label="$1"
  local hwmon label_file label value

  for hwmon in /sys/class/hwmon/hwmon*; do
    [[ -f "$hwmon/name" ]] || continue
    [[ "$(cat "$hwmon/name" 2>/dev/null)" == "k10temp" ]] || continue

    for input_path in "$hwmon"/temp*_input; do
      [[ -f "$input_path" ]] || continue
      label_file="${input_path%_input}_label"
      if [[ -f "$label_file" ]]; then
        label="$(cat "$label_file" 2>/dev/null)"
      else
        label="$(basename "${input_path%_input}")"
      fi

      if [[ "$label" == "$wanted_label" ]]; then
        value="$(cat "$input_path" 2>/dev/null || true)"
        printf '%s' "$value"
        return 0
      fi
    done
  done

  return 1
}

read_cpu_tctl_c() {
  local raw
  raw="$(read_k10temp_raw Tctl 2>/dev/null || true)"
  format_millic "$raw"
}

read_cpu_tccd1_c() {
  local raw
  raw="$(read_k10temp_raw Tccd1 2>/dev/null || true)"
  format_millic "$raw"
}

gpu_sample_csv() {
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    return 1
  fi

  nvidia-smi \
    --query-gpu=temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw,pstate,clocks_throttle_reasons.hw_thermal_slowdown,clocks_throttle_reasons.sw_thermal_slowdown \
    --format=csv,noheader,nounits 2>/dev/null | head -n 1
}

compare_ge() {
  local left="$1"
  local right="$2"

  python3 - "$left" "$right" <<'PY'
import sys

left = float(sys.argv[1])
right = float(sys.argv[2])
raise SystemExit(0 if left >= right else 1)
PY
}

sample_line() {
  local timestamp cpu_tctl_c cpu_tccd1_c gpu_line gpu_temp gpu_util gpu_mem_used gpu_mem_total gpu_power gpu_pstate
  local gpu_hw_thermal gpu_sw_thermal level notes

  timestamp="$(date --iso-8601=seconds)"
  cpu_tctl_c="$(read_cpu_tctl_c)"
  cpu_tccd1_c="$(read_cpu_tccd1_c)"

  gpu_temp="na"
  gpu_util="na"
  gpu_mem_used="na"
  gpu_mem_total="na"
  gpu_power="na"
  gpu_pstate="na"
  gpu_hw_thermal="na"
  gpu_sw_thermal="na"

  if gpu_line="$(gpu_sample_csv)"; then
    IFS=',' read -r gpu_temp gpu_util gpu_mem_used gpu_mem_total gpu_power gpu_pstate gpu_hw_thermal gpu_sw_thermal <<<"$gpu_line"
    gpu_temp="$(to_number_or_na "$gpu_temp")"
    gpu_util="$(to_number_or_na "$gpu_util")"
    gpu_mem_used="$(to_number_or_na "$gpu_mem_used")"
    gpu_mem_total="$(to_number_or_na "$gpu_mem_total")"
    gpu_power="$(to_number_or_na "$gpu_power")"
    gpu_pstate="$(sanitize_token "$gpu_pstate")"
    gpu_hw_thermal="$(sanitize_token "$gpu_hw_thermal")"
    gpu_sw_thermal="$(sanitize_token "$gpu_sw_thermal")"
  fi

  level="OK"
  notes=""

  if [[ "$cpu_tctl_c" != "na" ]]; then
    if compare_ge "$cpu_tctl_c" "$THERMAL_MONITOR_CPU_CRIT_C"; then
      level="CRIT"
      notes="${notes}cpu_tctl_high;"
    elif compare_ge "$cpu_tctl_c" "$THERMAL_MONITOR_CPU_WARN_C" && [[ "$level" == "OK" ]]; then
      level="WARN"
      notes="${notes}cpu_tctl_warn;"
    fi
  fi

  if [[ "$gpu_temp" != "na" ]]; then
    if compare_ge "$gpu_temp" "$THERMAL_MONITOR_GPU_CRIT_C"; then
      level="CRIT"
      notes="${notes}gpu_temp_high;"
    elif compare_ge "$gpu_temp" "$THERMAL_MONITOR_GPU_WARN_C" && [[ "$level" == "OK" ]]; then
      level="WARN"
      notes="${notes}gpu_temp_warn;"
    fi
  fi

  if [[ "$gpu_hw_thermal" == "Active" || "$gpu_sw_thermal" == "Active" ]]; then
    level="CRIT"
    notes="${notes}gpu_thermal_slowdown;"
  fi

  [[ -n "$notes" ]] || notes="none"

  printf '%s level=%s cpu_tctl_c=%s cpu_tccd1_c=%s gpu_temp_c=%s gpu_util_pct=%s gpu_mem_used_mib=%s gpu_mem_total_mib=%s gpu_power_w=%s gpu_pstate=%s gpu_hw_thermal=%s gpu_sw_thermal=%s notes=%s\n' \
    "$timestamp" "$level" "$cpu_tctl_c" "$cpu_tccd1_c" "$gpu_temp" "$gpu_util" "$gpu_mem_used" "$gpu_mem_total" "$gpu_power" "$gpu_pstate" "$gpu_hw_thermal" "$gpu_sw_thermal" "$notes"
}

ensure_service_unit() {
  if systemctl --user cat "$THERMAL_MONITOR_SERVICE" >/dev/null 2>&1; then
    return 0
  fi

  "$REPO_ROOT/scripts/services/install-thermal-monitor-service.sh" apply >/dev/null
  systemctl --user cat "$THERMAL_MONITOR_SERVICE" >/dev/null 2>&1 || \
    die "No existe $THERMAL_MONITOR_SERVICE en systemd --user"
}

show_service_status() {
  if systemctl --user cat "$THERMAL_MONITOR_SERVICE" >/dev/null 2>&1; then
    kv "service_file" "$(systemd_user_dir)/$THERMAL_MONITOR_SERVICE"
    kv "service_enabled" "$(systemctl --user is-enabled "$THERMAL_MONITOR_SERVICE" 2>/dev/null || true)"
    kv "service_active" "$(systemctl --user is-active "$THERMAL_MONITOR_SERVICE" 2>/dev/null || true)"
  else
    kv "service_file" "not installed"
  fi
}

case "$cmd" in
  status)
    print_header "Thermal monitor"
    kv "interval_sec" "$THERMAL_MONITOR_INTERVAL_SEC"
    kv "cpu_warn_c" "$THERMAL_MONITOR_CPU_WARN_C"
    kv "cpu_crit_c" "$THERMAL_MONITOR_CPU_CRIT_C"
    kv "gpu_warn_c" "$THERMAL_MONITOR_GPU_WARN_C"
    kv "gpu_crit_c" "$THERMAL_MONITOR_GPU_CRIT_C"
    kv "log_file" "$THERMAL_MONITOR_LOG_FILE"
    kv "alert_file" "$THERMAL_MONITOR_ALERT_FILE"
    show_service_status
    print_header "Current sample"
    sample_line
    if [[ -f "$THERMAL_MONITOR_ALERT_FILE" ]]; then
      print_header "Recent alerts"
      tail -n 10 "$THERMAL_MONITOR_ALERT_FILE"
    fi
    ;;

  sample)
    sample_line
    ;;

  run)
    ensure_log_dir
    printf '%s monitor_started interval_sec=%s cpu_warn_c=%s cpu_crit_c=%s gpu_warn_c=%s gpu_crit_c=%s\n' \
      "$(date --iso-8601=seconds)" \
      "$THERMAL_MONITOR_INTERVAL_SEC" \
      "$THERMAL_MONITOR_CPU_WARN_C" \
      "$THERMAL_MONITOR_CPU_CRIT_C" \
      "$THERMAL_MONITOR_GPU_WARN_C" \
      "$THERMAL_MONITOR_GPU_CRIT_C" | tee -a "$THERMAL_MONITOR_LOG_FILE" >/dev/null

    while true; do
      line="$(sample_line)"
      printf '%s\n' "$line" | tee -a "$THERMAL_MONITOR_LOG_FILE"
      if [[ "$line" == *"level=WARN"* || "$line" == *"level=CRIT"* ]]; then
        printf '%s\n' "$line" >> "$THERMAL_MONITOR_ALERT_FILE"
      fi
      sleep "$THERMAL_MONITOR_INTERVAL_SEC"
    done
    ;;

  install-service)
    print_header "Thermal monitor install service"
    "$REPO_ROOT/scripts/services/install-thermal-monitor-service.sh" apply
    ;;

  start-service)
    print_header "Thermal monitor start"
    ensure_service_unit
    systemctl --user start "$THERMAL_MONITOR_SERVICE"
    kv "service_active" "$(systemctl --user is-active "$THERMAL_MONITOR_SERVICE" 2>/dev/null || true)"
    kv "log_file" "$THERMAL_MONITOR_LOG_FILE"
    ;;

  stop-service)
    print_header "Thermal monitor stop"
    systemctl --user stop "$THERMAL_MONITOR_SERVICE" >/dev/null 2>&1 || true
    kv "service_active" "$(systemctl --user is-active "$THERMAL_MONITOR_SERVICE" 2>/dev/null || true)"
    ;;

  restart-service)
    print_header "Thermal monitor restart"
    ensure_service_unit
    systemctl --user restart "$THERMAL_MONITOR_SERVICE"
    kv "service_active" "$(systemctl --user is-active "$THERMAL_MONITOR_SERVICE" 2>/dev/null || true)"
    ;;

  service-status)
    print_header "Thermal monitor service"
    if systemctl --user cat "$THERMAL_MONITOR_SERVICE" >/dev/null 2>&1; then
      kv "service_enabled" "$(systemctl --user is-enabled "$THERMAL_MONITOR_SERVICE" 2>/dev/null || true)"
      kv "service_active" "$(systemctl --user is-active "$THERMAL_MONITOR_SERVICE" 2>/dev/null || true)"
      systemctl --user status "$THERMAL_MONITOR_SERVICE" --no-pager | sed -n '1,40p'
    else
      warn "No existe $THERMAL_MONITOR_SERVICE en systemd --user"
      exit 7
    fi
    ;;

  tail-log)
    lines="${2:-40}"
    [[ -f "$THERMAL_MONITOR_LOG_FILE" ]] || die "No existe el log: $THERMAL_MONITOR_LOG_FILE"
    tail -n "$lines" "$THERMAL_MONITOR_LOG_FILE"
    ;;

  *)
    die "Uso: $0 [status|sample|run|install-service|start-service|stop-service|restart-service|service-status|tail-log]"
    ;;
esac

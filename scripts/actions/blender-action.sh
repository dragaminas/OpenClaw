#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

command_name="${1:-help}"
project_root="$OPENCLAW_ALLOWED_BLENDER_PROJECTS_DIR"
safe_name_regex='^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$'

validate_safe_name() {
  local value="$1"
  [[ "$value" =~ $safe_name_regex ]] || die "Usa un nombre simple: letras, numeros, punto, guion o guion bajo."
}

resolve_project_file() {
  local input_ref="$1"
  local root_resolved candidate_resolved
  root_resolved="$(realpath -m "$project_root")"

  if [[ "$input_ref" =~ $safe_name_regex ]]; then
    candidate_resolved="$root_resolved/$input_ref/$input_ref.blend"
  else
    [[ "$input_ref" != /* ]] || die "No se permiten rutas absolutas."
    [[ "$input_ref" == *.blend ]] || die "Indica un nombre de proyecto o una ruta relativa a un archivo .blend."
    candidate_resolved="$(realpath -m "$root_resolved/$input_ref")"
    [[ "$candidate_resolved" == "$root_resolved/"* ]] || die "La ruta debe quedar dentro de $project_root."
  fi

  [[ -f "$candidate_resolved" ]] || die "No existe el proyecto solicitado: $candidate_resolved"
  printf '%s\n' "$candidate_resolved"
}

print_help() {
  cat <<EOF
Comandos disponibles:
- help
- launch
- status
- new <nombre>
- open <nombre|ruta-relativa.blend>
- smoke-test <nombre>
EOF
}

require_cmd realpath

case "$command_name" in
  help)
    print_help
    ;;
  launch)
    [[ -x "$BLENDER_BIN" ]] || die "Blender no esta disponible en $BLENDER_BIN"
    if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
      printf 'No hay sesion grafica para abrir Blender.\n'
      exit 0
    fi
    nohup "$BLENDER_BIN" >/tmp/openclaw-blender-launch.log 2>&1 &
    printf 'Blender abierto.\n'
    ;;
  status)
    [[ -x "$BLENDER_BIN" ]] || die "Blender no esta disponible en $BLENDER_BIN"
    version_line="$("$BLENDER_BIN" --version | sed -n '1p')"
    printf 'Blender listo: %s\n' "$version_line"
    printf 'Binario: %s\n' "$BLENDER_BIN"
    ;;
  new)
    project_name="${2:-}"
    [[ -n "$project_name" ]] || die "Debes indicar un nombre para el proyecto."
    validate_safe_name "$project_name"
    "$REPO_ROOT/scripts/apps/blender.sh" new-project "$project_name" >/dev/null
    printf 'Proyecto creado: %s/%s/%s.blend\n' "$project_root" "$project_name" "$project_name"
    ;;
  open)
    project_ref="${2:-}"
    [[ -n "$project_ref" ]] || die "Debes indicar el proyecto que quieres abrir."
    project_file="$(resolve_project_file "$project_ref")"
    if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
      printf 'Proyecto localizado, pero no hay sesion grafica para abrir Blender: %s\n' "$project_file"
      exit 0
    fi
    "$REPO_ROOT/scripts/apps/blender.sh" open-project "$project_file" >/dev/null
    printf 'Blender abierto con el proyecto: %s\n' "$project_file"
    ;;
  smoke-test)
    test_name="${2:-}"
    [[ -n "$test_name" ]] || die "Debes indicar un nombre para la prueba."
    validate_safe_name "$test_name"
    "$REPO_ROOT/scripts/apps/blender.sh" smoke-test "$test_name" >/dev/null
    printf 'Smoke test completado: %s/%s/%s.blend\n' "$project_root" "$test_name" "$test_name"
    printf 'Render generado: %s/%s/%s.png\n' "$project_root" "$test_name" "$test_name"
    ;;
  *)
    die "Uso: $0 [help|launch|status|new <nombre>|open <nombre|ruta-relativa.blend>|smoke-test <nombre>]"
    ;;
esac

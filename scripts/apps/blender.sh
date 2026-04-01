#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

cmd="${1:-status}"

case "$cmd" in
  status)
    print_header "Blender"
    if [[ -n "$BLENDER_BIN" && -x "$BLENDER_BIN" ]]; then
      kv "blender_bin" "$BLENDER_BIN"
      "$BLENDER_BIN" --version | sed -n '1,2p'
    else
      die "Blender no esta instalado o BLENDER_BIN no es ejecutable"
    fi
    ;;
  new-project)
    target_name="${2:-untitled}"
    target_dir="$STUDIO_DIR/BlenderProjects/$target_name"
    mkdir -p "$target_dir"
    target_file="$target_dir/$target_name.blend"
    if [[ -n "$BLENDER_BIN" && -x "$BLENDER_BIN" ]]; then
      "$BLENDER_BIN" --background --factory-startup \
        --python-expr "import bpy; bpy.ops.wm.save_as_mainfile(filepath=r'$target_file')" >/tmp/openclaw-blender-create.log 2>&1
    else
      touch "$target_file"
    fi
    kv "project_dir" "$target_dir"
    kv "project_file" "$target_file"
    ;;
  open-project)
    project_file="${2:-}"
    [[ -n "$project_file" ]] || die "Debes indicar un archivo .blend"
    [[ -f "$project_file" ]] || die "No existe el archivo: $project_file"
    if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
      warn "No hay sesion grafica detectada; no se lanza Blender"
      kv "project_file" "$project_file"
      exit 0
    fi
    nohup "$BLENDER_BIN" "$project_file" >/tmp/openclaw-blender-launch.log 2>&1 &
    kv "project_file" "$project_file"
    kv "launcher" "started"
    ;;
  smoke-test)
    test_name="${2:-smoke-test}"
    target_dir="$STUDIO_DIR/BlenderProjects/$test_name"
    blend_file="$target_dir/$test_name.blend"
    render_file="$target_dir/$test_name.png"
    helper_py="$SCRIPT_DIR/blender_smoke_test.py"
    mkdir -p "$target_dir"
    [[ -x "$BLENDER_BIN" ]] || die "Blender no esta disponible"
    [[ -f "$helper_py" ]] || die "No existe el helper: $helper_py"
    "$BLENDER_BIN" --background --factory-startup \
      --python "$helper_py" -- "$blend_file" "$render_file" >/tmp/openclaw-blender-smoke.log 2>&1
    [[ -f "$blend_file" ]] || die "No se genero el .blend esperado"
    [[ -f "$render_file" ]] || die "No se genero el render esperado"
    kv "project_dir" "$target_dir"
    kv "project_file" "$blend_file"
    kv "render_file" "$render_file"
    ;;
  *)
    die "Uso: $0 [status|new-project <nombre>|open-project <archivo.blend>|smoke-test <nombre>]"
    ;;
esac

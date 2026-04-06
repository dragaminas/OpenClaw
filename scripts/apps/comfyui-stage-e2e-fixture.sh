#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

source_video="$REPO_ROOT/blenderTest.mp4"
shot_id="blender-test"
fixture_version="v001"

print_help() {
  cat <<EOF
Uso: $0 [--source <video.mp4>] [--shot <shot_id>] [--version <v###>]

Prepara un video base canonico para las pruebas E2E de 8.15.
Por defecto usa:
- source: $REPO_ROOT/blenderTest.mp4
- shot: blender-test
- version: v001
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      source_video="${2:?Falta valor para --source}"
      shift 2
      ;;
    --shot)
      shot_id="${2:?Falta valor para --shot}"
      shift 2
      ;;
    --version)
      fixture_version="${2:?Falta valor para --version}"
      shift 2
      ;;
    help|-h|--help)
      print_help
      exit 0
      ;;
    *)
      die "Argumento no reconocido: $1"
      ;;
  esac
done

[[ -f "$source_video" ]] || die "No existe el video fuente: $source_video"

validation_root="$STUDIO_DIR/Validation/comfyui/e2e/$shot_id"
fixtures_dir="$validation_root/fixtures"
manifests_dir="$validation_root/manifests"
target_video="$fixtures_dir/${shot_id}__base__${fixture_version}.mp4"
manifest_path="$manifests_dir/${shot_id}__fixture__${fixture_version}.json"
source_sha256="$(sha256sum "$source_video" | awk '{print $1}')"
target_size_bytes="$(stat -c '%s' "$source_video")"

mkdir -p "$fixtures_dir" "$manifests_dir"
cp -f "$source_video" "$target_video"

cat >"$manifest_path" <<EOF
{
  "fixture_kind": "video_base",
  "phase": "8.15",
  "shot_id": "$(json_escape "$shot_id")",
  "source_path": "$(json_escape "$source_video")",
  "staged_path": "$(json_escape "$target_video")",
  "manifest_version": "$(json_escape "$fixture_version")",
  "sha256": "$(json_escape "$source_sha256")",
  "size_bytes": $target_size_bytes
}
EOF

print_header "ComfyUI E2E fixture"
kv "phase" "8.15"
kv "shot_id" "$shot_id"
kv "source_path" "$source_video"
kv "staged_path" "$target_video"
kv "manifest_path" "$manifest_path"
kv "sha256" "$source_sha256"

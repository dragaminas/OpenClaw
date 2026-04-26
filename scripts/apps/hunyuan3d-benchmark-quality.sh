#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

HUNYUAN3D_DIR="${HUNYUAN3D_DIR:-$HOME/Hunyuan3D-2}"
HUNYUAN3D_VENV_PYTHON="${HUNYUAN3D_VENV_PYTHON:-$HUNYUAN3D_DIR/.venv/bin/python3}"
PROFILE="${HUNYUAN3D_BENCHMARK_PROFILE:-quality}"
INPUT_IMAGE="${1:-${HUNYUAN3D_BENCHMARK_INPUT:-$COMFYUI_DIR/input/openclaw_object_ref.png}}"
SF3D_GLB="${SF3D_GLB:-$COMFYUI_DIR/output/openclaw/uc-3d-02/validation_sf3d_cpu_fallback_00001_.glb}"
BENCHMARK_ID="${HUNYUAN3D_BENCHMARK_ID:-openclaw_object_ref}"
BENCHMARK_ROOT="${HUNYUAN3D_BENCHMARK_ROOT:-$STUDIO_DIR/Assets3D/benchmarks/hunyuan3d}"

RUN_DIR="$BENCHMARK_ROOT/$BENCHMARK_ID/$PROFILE"
OUTPUT_DIR="$RUN_DIR/hunyuan3d/output"
PREVIEW_DIR="$RUN_DIR/hunyuan3d/previews"
REQUEST_DIR="$RUN_DIR/hunyuan3d/requests"
LOG_DIR="$RUN_DIR/hunyuan3d/logs"
REFERENCE_DIR="$RUN_DIR/references"

OUTPUT_GLB="$OUTPUT_DIR/${BENCHMARK_ID}__mesh__${PROFILE}__v001.glb"
OUTPUT_STATS="$REQUEST_DIR/${BENCHMARK_ID}__stats__${PROFILE}__v001.json"
OUTPUT_PREVIEW="$PREVIEW_DIR/${BENCHMARK_ID}__preview__${PROFILE}__v001.png"
SF3D_PREVIEW="$REFERENCE_DIR/${BENCHMARK_ID}__sf3d__preview__v001.png"
SF3D_STATS="$REFERENCE_DIR/${BENCHMARK_ID}__sf3d__stats__v001.json"
COMPARISON_PNG="$REFERENCE_DIR/${BENCHMARK_ID}__comparison__${PROFILE}__v001.png"
SUMMARY_TXT="$LOG_DIR/${BENCHMARK_ID}__summary__${PROFILE}__v001.txt"

resolve_profile() {
  case "$PROFILE" in
    baseline)
      MODEL_PATH="tencent/Hunyuan3D-2mini"
      SUBFOLDER="hunyuan3d-dit-v2-mini-turbo"
      NUM_STEPS=5
      ENABLE_FLASHVDM=1
      ;;
    balanced)
      MODEL_PATH="tencent/Hunyuan3D-2mini"
      SUBFOLDER="hunyuan3d-dit-v2-mini"
      NUM_STEPS=30
      ENABLE_FLASHVDM=0
      ;;
    quality)
      MODEL_PATH="tencent/Hunyuan3D-2.1"
      SUBFOLDER="hunyuan3d-dit-v2-1"
      NUM_STEPS=30
      ENABLE_FLASHVDM=0
      ;;
    *)
      die "Perfil invalido: $PROFILE. Usa baseline, balanced o quality"
      ;;
  esac
}

resolve_profile

[[ -x "$HUNYUAN3D_VENV_PYTHON" ]] || die "No existe python del venv: $HUNYUAN3D_VENV_PYTHON"
[[ -f "$INPUT_IMAGE" ]] || die "No existe imagen de entrada: $INPUT_IMAGE"
[[ -f "$SCRIPT_DIR/hunyuan3d-run-shapegen.py" ]] || die "Falta $SCRIPT_DIR/hunyuan3d-run-shapegen.py"
[[ -f "$SCRIPT_DIR/blender_render_glb_preview.py" ]] || die "Falta $SCRIPT_DIR/blender_render_glb_preview.py"
require_cmd blender

mkdir -p "$OUTPUT_DIR" "$PREVIEW_DIR" "$REQUEST_DIR" "$LOG_DIR" "$REFERENCE_DIR"

print_header "Hunyuan3D benchmark-quality"
kv "profile" "$PROFILE"
kv "input_image" "$INPUT_IMAGE"
kv "sf3d_glb" "$SF3D_GLB"
kv "model_path" "$MODEL_PATH"
kv "subfolder" "$SUBFOLDER"
kv "num_inference_steps" "$NUM_STEPS"
kv "output_glb" "$OUTPUT_GLB"

run_cmd=(
  "$HUNYUAN3D_VENV_PYTHON" "$SCRIPT_DIR/hunyuan3d-run-shapegen.py"
  --repo-dir "$HUNYUAN3D_DIR"
  --input-image "$INPUT_IMAGE"
  --output-glb "$OUTPUT_GLB"
  --stats-json "$OUTPUT_STATS"
  --model-path "$MODEL_PATH"
  --subfolder "$SUBFOLDER"
  --seed 42
  --num-inference-steps "$NUM_STEPS"
  --guidance-scale 5.0
  --octree-resolution 256
)

if [[ "$ENABLE_FLASHVDM" == "1" ]]; then
  run_cmd+=(--enable-flashvdm)
fi

"${run_cmd[@]}" | tee "$LOG_DIR/${BENCHMARK_ID}__run__${PROFILE}__v001.log"

blender -b --python "$SCRIPT_DIR/blender_render_glb_preview.py" -- \
  "$OUTPUT_GLB" "$OUTPUT_PREVIEW" >/dev/null

if [[ -f "$SF3D_GLB" ]]; then
  blender -b --python "$SCRIPT_DIR/blender_render_glb_preview.py" -- \
    "$SF3D_GLB" "$SF3D_PREVIEW" >/dev/null

  "$HUNYUAN3D_VENV_PYTHON" - "$SF3D_GLB" "$SF3D_STATS" <<'PY'
import json
import sys
from pathlib import Path

import trimesh

glb_path = Path(sys.argv[1]).expanduser().resolve()
stats_path = Path(sys.argv[2]).expanduser().resolve()
mesh = trimesh.load(glb_path, force="mesh")
stats = {
    "glb_path": str(glb_path),
    "glb_bytes": glb_path.stat().st_size,
    "vertices": int(len(mesh.vertices)),
    "faces": int(len(mesh.faces)),
    "is_watertight": bool(mesh.is_watertight),
    "bounding_box_extents": [float(value) for value in mesh.bounding_box.extents],
}
stats_path.write_text(json.dumps(stats, indent=2, sort_keys=True))
print(json.dumps(stats, indent=2, sort_keys=True))
PY

  "$HUNYUAN3D_VENV_PYTHON" - \
    "$OUTPUT_PREVIEW" "$SF3D_PREVIEW" "$COMPARISON_PNG" "$PROFILE" <<'PY'
import sys
from pathlib import Path

from PIL import Image, ImageDraw

hunyuan_preview = Path(sys.argv[1]).expanduser().resolve()
sf3d_preview = Path(sys.argv[2]).expanduser().resolve()
comparison_png = Path(sys.argv[3]).expanduser().resolve()
profile = sys.argv[4]

left = Image.open(hunyuan_preview).convert("RGB")
right = Image.open(sf3d_preview).convert("RGB")
width = left.width + right.width
height = max(left.height, right.height) + 80
canvas = Image.new("RGB", (width, height), (244, 246, 250))
draw = ImageDraw.Draw(canvas)
canvas.paste(left, (0, 80))
canvas.paste(right, (left.width, 80))
draw.text((24, 24), f"Hunyuan3D {profile}", fill=(20, 28, 44))
draw.text((left.width + 24, 24), "SF3D referencia", fill=(20, 28, 44))
comparison_png.parent.mkdir(parents=True, exist_ok=True)
canvas.save(comparison_png)
PY
fi

"$HUNYUAN3D_VENV_PYTHON" - \
  "$OUTPUT_STATS" "$SF3D_STATS" "$OUTPUT_PREVIEW" "$SF3D_PREVIEW" "$COMPARISON_PNG" "$SUMMARY_TXT" "$PROFILE" <<'PY'
import json
import sys
from pathlib import Path

output_stats = Path(sys.argv[1]).expanduser().resolve()
sf3d_stats = Path(sys.argv[2]).expanduser().resolve()
output_preview = Path(sys.argv[3]).expanduser().resolve()
sf3d_preview = Path(sys.argv[4]).expanduser().resolve()
comparison_png = Path(sys.argv[5]).expanduser().resolve()
summary_txt = Path(sys.argv[6]).expanduser().resolve()
profile = sys.argv[7]

hunyuan = json.loads(output_stats.read_text())
lines = [
    f"profile={profile}",
    f"hunyuan_glb={hunyuan['output_glb']}",
    f"hunyuan_preview={output_preview}",
    f"hunyuan_glb_bytes={hunyuan['glb_bytes']}",
    f"hunyuan_vertices={hunyuan['vertices']}",
    f"hunyuan_faces={hunyuan['faces']}",
    f"hunyuan_is_watertight={hunyuan['is_watertight']}",
    f"hunyuan_duration_seconds={hunyuan['duration_seconds']}",
]

if sf3d_stats.exists():
    sf3d = json.loads(sf3d_stats.read_text())
    lines.extend(
        [
            f"sf3d_glb={sf3d['glb_path']}",
            f"sf3d_preview={sf3d_preview}",
            f"sf3d_glb_bytes={sf3d['glb_bytes']}",
            f"sf3d_vertices={sf3d['vertices']}",
            f"sf3d_faces={sf3d['faces']}",
            f"sf3d_is_watertight={sf3d['is_watertight']}",
        ]
    )
if comparison_png.exists():
    lines.append(f"comparison_png={comparison_png}")

summary_txt.write_text("\n".join(lines) + "\n")
print(summary_txt.read_text(), end="")
PY

echo ""
printf 'Benchmark listo.\n'
printf 'Resumen: %s\n' "$SUMMARY_TXT"
printf 'Preview Hunyuan: %s\n' "$OUTPUT_PREVIEW"
if [[ -f "$COMPARISON_PNG" ]]; then
  printf 'Comparativa visual: %s\n' "$COMPARISON_PNG"
fi

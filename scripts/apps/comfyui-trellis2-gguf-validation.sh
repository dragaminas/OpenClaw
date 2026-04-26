#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

COMFYUI_TRELLIS2_LAB_DIR="${COMFYUI_TRELLIS2_LAB_DIR:-$HOME/ComfyUI-trellis2-lab}"
TRELLIS2_GGUF_VALIDATION_ID="${TRELLIS2_GGUF_VALIDATION_ID:-openclaw_object_ref}"
TRELLIS2_GGUF_VALIDATION_ROOT="${TRELLIS2_GGUF_VALIDATION_ROOT:-$STUDIO_DIR/Assets3D/benchmarks/trellis2-gguf}"
TRELLIS2_GGUF_CREATIVE_IMAGE="${TRELLIS2_GGUF_CREATIVE_IMAGE:-}"
TRELLIS2_GGUF_FIXTURE_IMAGE="${TRELLIS2_GGUF_FIXTURE_IMAGE:-$COMFYUI_DIR/input/openclaw_object_ref.png}"
TRELLIS2_GGUF_WORKFLOW_SPEC="${TRELLIS2_GGUF_WORKFLOW_SPEC:-$REPO_ROOT/docs/comfyui/trellis2-gguf-interface.md}"
RUN_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

RUN_DIR="$TRELLIS2_GGUF_VALIDATION_ROOT/$TRELLIS2_GGUF_VALIDATION_ID/$RUN_STAMP"
LOG_DIR="$RUN_DIR/logs"
REPORT_DIR="$RUN_DIR/reports"
mkdir -p "$LOG_DIR" "$REPORT_DIR"

SUMMARY_TXT="$REPORT_DIR/trellis2_gguf_validation_summary.txt"
SUMMARY_JSON="$REPORT_DIR/trellis2_gguf_validation_summary.json"
NODES_TXT="$REPORT_DIR/installed_nodes.txt"
MODELS_TXT="$REPORT_DIR/minimum_models_check.txt"
MODEL_LAYOUT_TXT="$REPORT_DIR/workflow_model_layout_check.txt"
WORKFLOW_BACKENDS_TXT="$REPORT_DIR/workflow_backend_check.txt"
O_VOXEL_TXT="$REPORT_DIR/o_voxel_cuda_check.txt"

status="pass_preflight"
declare -a reasons=()

declare -a required_model_names=(
  "dinov3-vitl16-pretrain-lvd1689m.safetensors"
  "ss_dec_conv3d_16l8_fp16.safetensors"
  "shape_dec_next_dc_f16c32_fp16.safetensors"
  "tex_dec_next_dc_f16c32_fp16.safetensors"
  "slat_flow_img2shape_dit_1_3B_512_bf16_Q4_K_M.gguf"
  "slat_flow_imgshape2tex_dit_1_3B_512_bf16_Q4_K_M.gguf"
  "ss_flow_img_dit_1_3B_64_bf16_Q4_K_M.gguf"
)

set_status_if_pass() {
  local new_status="$1"
  local reason="$2"
  if [[ "$status" == "pass_preflight" ]]; then
    status="$new_status"
  fi
  reasons+=("$reason")
}

print_header "Trellis2 GGUF validation"
kv "run_dir" "$RUN_DIR"
kv "comfyui_lab_dir" "$COMFYUI_TRELLIS2_LAB_DIR"
kv "fixture_image" "$TRELLIS2_GGUF_FIXTURE_IMAGE"
kv "creative_image" "${TRELLIS2_GGUF_CREATIVE_IMAGE:-not_provided}"
kv "workflow_spec" "$TRELLIS2_GGUF_WORKFLOW_SPEC"

if [[ ! -d "$COMFYUI_TRELLIS2_LAB_DIR" ]]; then
  set_status_if_pass \
    "blocked_missing_experimental_runtime" \
    "No existe el runtime aislado COMFYUI_TRELLIS2_LAB_DIR=$COMFYUI_TRELLIS2_LAB_DIR"
fi

if [[ ! -f "$TRELLIS2_GGUF_WORKFLOW_SPEC" ]]; then
  set_status_if_pass \
    "blocked_missing_workflow_spec" \
    "No existe la especificacion de workflow esperada en $TRELLIS2_GGUF_WORKFLOW_SPEC"
fi

if [[ ! -f "$TRELLIS2_GGUF_FIXTURE_IMAGE" ]]; then
  set_status_if_pass \
    "blocked_missing_fixture" \
    "No existe la imagen fixture esperada en $TRELLIS2_GGUF_FIXTURE_IMAGE"
fi

python_version="$(python3 --version 2>&1 | awk '{print $2}')"
comfyui_python_version="not_found"
torch_version="not_found"
torch_cuda_available="unknown"
gpu_info="nvidia-smi-not-available"
if command -v nvidia-smi >/dev/null 2>&1; then
  gpu_info="$(nvidia-smi --query-gpu=name,driver_version,memory.total,power.limit --format=csv,noheader | head -n 1)"
fi

trellis2_python="$COMFYUI_TRELLIS2_LAB_DIR/.venv/bin/python"
if [[ -x "$trellis2_python" ]]; then
  comfyui_python_version="$("$trellis2_python" -c 'import platform; print(platform.python_version())')"
  torch_version="$("$trellis2_python" -c 'import torch; print(torch.__version__)' 2>/dev/null || echo not_found)"
  torch_cuda_available="$("$trellis2_python" -c 'import torch; print(torch.cuda.is_available())' 2>/dev/null || echo unknown)"
elif [[ -x "$COMFYUI_DIR/.venv/bin/python" ]]; then
  comfyui_python_version="$($COMFYUI_DIR/.venv/bin/python -c 'import platform; print(platform.python_version())')"
  torch_version="$($COMFYUI_DIR/.venv/bin/python -c 'import torch; print(torch.__version__)' 2>/dev/null || echo not_found)"
  torch_cuda_available="$($COMFYUI_DIR/.venv/bin/python -c 'import torch; print(torch.cuda.is_available())' 2>/dev/null || echo unknown)"
fi

{
  printf 'openclaw-hunyuan3d-lite=%s\n' "$(test -d "$COMFYUI_DIR/custom_nodes/openclaw-hunyuan3d-lite" && echo present || echo missing)"
  printf 'openclaw-workflows=%s\n' "$(test -d "$COMFYUI_DIR/custom_nodes/openclaw-workflows" && echo present || echo missing)"
  printf 'comfyui-trellis2=%s\n' "$(test -d "$COMFYUI_TRELLIS2_LAB_DIR/custom_nodes/ComfyUI-Trellis2" && echo present || echo missing)"
  printf 'comfyui-gguf=%s\n' "$(test -d "$COMFYUI_TRELLIS2_LAB_DIR/custom_nodes/ComfyUI-GGUF" && echo present || echo missing)"
} >"$NODES_TXT"

if [[ ! -d "$COMFYUI_TRELLIS2_LAB_DIR/custom_nodes/ComfyUI-Trellis2" ]]; then
  set_status_if_pass \
    "blocked_missing_trellis_nodes" \
    "Falta ComfyUI-Trellis2 en $COMFYUI_TRELLIS2_LAB_DIR/custom_nodes/"
fi

if [[ ! -d "$COMFYUI_TRELLIS2_LAB_DIR/custom_nodes/ComfyUI-GGUF" ]]; then
  set_status_if_pass \
    "blocked_missing_gguf_nodes" \
    "Falta ComfyUI-GGUF en $COMFYUI_TRELLIS2_LAB_DIR/custom_nodes/"
fi

model_hits=0
for model_name in "${required_model_names[@]}"; do
  model_path=""
  if [[ -d "$COMFYUI_TRELLIS2_LAB_DIR/models" ]]; then
    model_path="$(find "$COMFYUI_TRELLIS2_LAB_DIR/models" -type f -name "$model_name" | head -n 1 || true)"
  fi
  if [[ -n "$model_path" ]]; then
    printf '%s=present:%s\n' "$model_name" "$model_path" >>"$MODELS_TXT"
    model_hits=$((model_hits + 1))
  else
    printf '%s=missing\n' "$model_name" >>"$MODELS_TXT"
  fi
done

if (( model_hits < ${#required_model_names[@]} )); then
  set_status_if_pass \
    "blocked_missing_minimum_models" \
    "Set minimo incompleto para Trellis2 GGUF ($model_hits/${#required_model_names[@]} modelos)"
fi

trellis2_model_root="$COMFYUI_TRELLIS2_LAB_DIR/models/microsoft/TRELLIS.2-4B"
trellis2_image_root="$COMFYUI_TRELLIS2_LAB_DIR/models/microsoft/TRELLIS-image-large"
trellis2_dinov3_model="$COMFYUI_TRELLIS2_LAB_DIR/models/facebook/dinov3-vitl16-pretrain-lvd1689m/model.safetensors"
trellis2_dinov3_config="$COMFYUI_TRELLIS2_LAB_DIR/models/facebook/dinov3-vitl16-pretrain-lvd1689m/config.json"
{
  printf 'facebook_dinov3_model=%s:%s\n' \
    "$(test -f "$trellis2_dinov3_model" && echo present || echo missing)" \
    "$trellis2_dinov3_model"
  printf 'facebook_dinov3_config=%s:%s\n' \
    "$(test -f "$trellis2_dinov3_config" && echo present || echo missing)" \
    "$trellis2_dinov3_config"
  printf 'trellis2_pipeline=%s:%s\n' \
    "$(test -f "$trellis2_model_root/pipeline.json" && echo present || echo missing)" \
    "$trellis2_model_root/pipeline.json"
  printf 'trellis2_image_large_decoder=%s:%s\n' \
    "$(test -f "$trellis2_image_root/ckpts/ss_dec_conv3d_16l8_fp16.safetensors" && echo present || echo missing)" \
    "$trellis2_image_root/ckpts/ss_dec_conv3d_16l8_fp16.safetensors"
} >"$MODEL_LAYOUT_TXT"

if [[ ! -f "$trellis2_dinov3_model" ]]; then
  set_status_if_pass \
    "blocked_missing_dinov3_layout" \
    "Falta el DINOv3 en el layout que Trellis2LoadModel usa: $trellis2_dinov3_model"
fi

if [[ ! -f "$trellis2_dinov3_config" ]]; then
  set_status_if_pass \
    "blocked_missing_dinov3_config" \
    "Falta $trellis2_dinov3_config; sin este config Transformers usa dimensiones por defecto y falla con mismatch"
elif [[ -x "$trellis2_python" ]]; then
  if ! "$trellis2_python" - "$trellis2_dinov3_config" <<'PY'
import json
import sys
from pathlib import Path

config = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
expected = {
    "model_type": "dinov3_vit",
    "hidden_size": 1024,
    "num_hidden_layers": 24,
    "num_attention_heads": 16,
    "num_register_tokens": 4,
    "patch_size": 16,
}
for key, value in expected.items():
    if config.get(key) != value:
        raise SystemExit(f"{key}={config.get(key)!r}, expected {value!r}")
PY
  then
    set_status_if_pass \
      "blocked_invalid_dinov3_config" \
      "El config DINOv3 local no coincide con facebook/dinov3-vitl16-pretrain-lvd1689m"
  fi
fi

if [[ ! -f "$trellis2_model_root/pipeline.json" ]]; then
  set_status_if_pass \
    "blocked_missing_trellis2_model_layout" \
    "El workflow Trellis2LoadModel espera $trellis2_model_root/pipeline.json; los modelos minimos GGUF estan presentes, pero aun no estan enlazados a ese layout ejecutable"
fi

if [[ ! -f "$trellis2_image_root/ckpts/ss_dec_conv3d_16l8_fp16.safetensors" ]]; then
  set_status_if_pass \
    "blocked_missing_trellis_image_large_layout" \
    "Falta $trellis2_image_root/ckpts/ss_dec_conv3d_16l8_fp16.safetensors, requerido por Trellis2LoadModel antes de inferencia"
fi

workflow_backend_status="not_checked"
workflow_backend_root="$COMFYUI_TRELLIS2_LAB_DIR/custom_nodes/ComfyUI-Trellis2/example_workflows"
if [[ -d "$workflow_backend_root" && -x "$trellis2_python" ]]; then
  if "$trellis2_python" - "$workflow_backend_root" "$WORKFLOW_BACKENDS_TXT" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
report = Path(sys.argv[2])
bad = []
lines = []
for path in sorted(root.glob("*.json")):
    data = json.loads(path.read_text(encoding="utf-8"))
    for node in data.get("nodes", []):
        if node.get("type") != "Trellis2LoadModel":
            continue
        values = node.get("widgets_values")
        backend = values[1] if isinstance(values, list) and len(values) > 1 else "missing"
        conv_backend = values[5] if isinstance(values, list) and len(values) > 5 else "missing"
        lines.append(f"{path.name}=backend:{backend};conv_backend:{conv_backend}")
        if backend in {"flash_attn", "flash_attn_3", "xformers"}:
            bad.append(f"{path.name}:{backend}")
        if conv_backend == "flex_gemm":
            bad.append(f"{path.name}:{conv_backend}")

report.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
if bad:
    raise SystemExit(",".join(bad))
PY
  then
    workflow_backend_status="pass"
  else
    workflow_backend_status="blocked"
    set_status_if_pass \
      "blocked_missing_attention_backend" \
      "Algun workflow Trellis2LoadModel sigue usando flash_attn/xformers o flex_gemm; ejecuta scripts/apps/comfyui-trellis2-gguf-prepare-layout.sh"
  fi
fi

o_voxel_status="not_checked"
if [[ -x "$trellis2_python" ]]; then
  if "$trellis2_python" - "$O_VOXEL_TXT" <<'PY'
import importlib
import subprocess
import sys
from pathlib import Path

import torch

report = Path(sys.argv[1])
lines = []
module = importlib.import_module("o_voxel._C")
so_path = Path(module.__file__)
capability = torch.cuda.get_device_capability(0) if torch.cuda.is_available() else None
expected_arch = f"sm_{capability[0]}{capability[1]}" if capability else "cpu"

lines.append(f"module={so_path}")
lines.append(f"torch_cuda={torch.version.cuda}")
lines.append(f"device={torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'}")
lines.append(f"expected_arch={expected_arch}")

if expected_arch != "cpu":
    result = subprocess.run(
        ["cuobjdump", "--list-elf", str(so_path)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    lines.append("cuobjdump=" + result.stdout.replace("\n", "\\n"))
    if expected_arch not in result.stdout:
        report.write_text("\n".join(lines) + "\n", encoding="utf-8")
        raise SystemExit(f"{expected_arch} not found in o_voxel CUDA binary")

report.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
  then
    o_voxel_status="pass"
  else
    o_voxel_status="blocked"
    set_status_if_pass \
      "blocked_o_voxel_cuda_arch" \
      "o_voxel no expone kernel CUDA compatible con la GPU actual; ejecuta scripts/apps/comfyui-trellis2-gguf-prepare-layout.sh"
  fi
fi

if [[ -n "$TRELLIS2_GGUF_CREATIVE_IMAGE" && ! -f "$TRELLIS2_GGUF_CREATIVE_IMAGE" ]]; then
  set_status_if_pass \
    "blocked_missing_creative_image" \
    "No existe TRELLIS2_GGUF_CREATIVE_IMAGE=$TRELLIS2_GGUF_CREATIVE_IMAGE"
fi

if ! tcp_port_is_listening "$COMFYUI_HOST" "$COMFYUI_PORT"; then
  reasons+=("ComfyUI principal no esta escuchando en $COMFYUI_HOST:$COMFYUI_PORT (no bloquea el preflight)")
fi

if [[ "$status" == "pass_preflight" ]]; then
  reasons+=("Preflight listo: ya puedes ejecutar corrida comparativa SF3D/Hunyuan/Trellis sobre el mismo fixture")
fi

{
  printf 'timestamp_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'status=%s\n' "$status"
  printf 'run_dir=%s\n' "$RUN_DIR"
  printf 'comfyui_lab_dir=%s\n' "$COMFYUI_TRELLIS2_LAB_DIR"
  printf 'fixture_image=%s\n' "$TRELLIS2_GGUF_FIXTURE_IMAGE"
  printf 'creative_image=%s\n' "${TRELLIS2_GGUF_CREATIVE_IMAGE:-not_provided}"
  printf 'workflow_spec=%s\n' "$TRELLIS2_GGUF_WORKFLOW_SPEC"
  printf 'python=%s\n' "$python_version"
  printf 'comfyui_python=%s\n' "$comfyui_python_version"
  printf 'torch=%s\n' "$torch_version"
  printf 'torch_cuda_available=%s\n' "$torch_cuda_available"
  printf 'gpu=%s\n' "$gpu_info"
  printf 'reasons_count=%s\n' "${#reasons[@]}"
  for i in "${!reasons[@]}"; do
    printf 'reason_%02d=%s\n' "$((i + 1))" "${reasons[$i]}"
  done
  printf 'nodes_report=%s\n' "$NODES_TXT"
  printf 'models_report=%s\n' "$MODELS_TXT"
  printf 'model_layout_report=%s\n' "$MODEL_LAYOUT_TXT"
  printf 'workflow_backend_status=%s\n' "$workflow_backend_status"
  printf 'workflow_backend_report=%s\n' "$WORKFLOW_BACKENDS_TXT"
  printf 'o_voxel_status=%s\n' "$o_voxel_status"
  printf 'o_voxel_report=%s\n' "$O_VOXEL_TXT"
} >"$SUMMARY_TXT"

python3 - "$SUMMARY_JSON" "$status" "$RUN_DIR" "$COMFYUI_TRELLIS2_LAB_DIR" "$TRELLIS2_GGUF_FIXTURE_IMAGE" "$TRELLIS2_GGUF_CREATIVE_IMAGE" "$TRELLIS2_GGUF_WORKFLOW_SPEC" "$python_version" "$comfyui_python_version" "$torch_version" "$torch_cuda_available" "$gpu_info" "${reasons[@]}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

summary_json = Path(sys.argv[1]).expanduser().resolve()
status = sys.argv[2]
run_dir = sys.argv[3]
lab_dir = sys.argv[4]
fixture_image = sys.argv[5]
creative_image = sys.argv[6] or "not_provided"
workflow_spec = sys.argv[7]
python_version = sys.argv[8]
comfyui_python_version = sys.argv[9]
torch_version = sys.argv[10]
torch_cuda_available = sys.argv[11]
gpu_info = sys.argv[12]
reasons = [value for value in sys.argv[13:] if value]

payload = {
    "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "status": status,
    "run_dir": run_dir,
    "comfyui_trellis2_lab_dir": lab_dir,
    "fixture_image": fixture_image,
    "creative_image": creative_image,
    "workflow_spec": workflow_spec,
    "runtime": {
        "python": python_version,
        "comfyui_python": comfyui_python_version,
        "torch": torch_version,
        "torch_cuda_available": torch_cuda_available,
        "gpu": gpu_info,
    },
    "reasons": reasons,
}

summary_json.parent.mkdir(parents=True, exist_ok=True)
summary_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
print(json.dumps(payload, indent=2, sort_keys=True))
PY

echo ""
printf 'Resumen: %s\n' "$SUMMARY_TXT"
printf 'JSON:    %s\n' "$SUMMARY_JSON"
printf 'Nodos:   %s\n' "$NODES_TXT"
printf 'Modelos: %s\n' "$MODELS_TXT"
printf 'Layout:  %s\n' "$MODEL_LAYOUT_TXT"
printf 'Backend: %s\n' "$WORKFLOW_BACKENDS_TXT"
printf 'o_voxel:%s\n' "$O_VOXEL_TXT"

if [[ "$status" != "pass_preflight" ]]; then
  exit 2
fi

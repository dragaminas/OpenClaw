#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"

COMFYUI_TRELLIS2_LAB_DIR="${COMFYUI_TRELLIS2_LAB_DIR:-$HOME/ComfyUI-trellis2-lab}"
SOURCE_ROOT="${TRELLIS2_GGUF_SOURCE_ROOT:-$COMFYUI_TRELLIS2_LAB_DIR/models/Aero-Ex/Trellis2-GGUF}"
MODEL_ROOT="$COMFYUI_TRELLIS2_LAB_DIR/models/microsoft/TRELLIS.2-4B"
IMAGE_ROOT="$COMFYUI_TRELLIS2_LAB_DIR/models/microsoft/TRELLIS-image-large"
FACEBOOK_ROOT="$COMFYUI_TRELLIS2_LAB_DIR/models/facebook/dinov3-vitl16-pretrain-lvd1689m"
WORKFLOWS_ROOT="$COMFYUI_TRELLIS2_LAB_DIR/custom_nodes/ComfyUI-Trellis2/example_workflows"
REPO_WORKFLOWS_ROOT="$REPO_ROOT/ComfyUIWorkflows"
O_VOXEL_SM86_WHEEL="$COMFYUI_TRELLIS2_LAB_DIR/custom_nodes/ComfyUI-Trellis2/wheels/Linux/Torch270/o_voxel-0.0.1-cp312-cp312-linux_x86_64.whl"
FLEX_GEMM_SM86_WHEEL="$COMFYUI_TRELLIS2_LAB_DIR/custom_nodes/ComfyUI-Trellis2/wheels/Linux/Torch270/flex_gemm-0.0.1-cp312-cp312-linux_x86_64.whl"

link_file() {
  local source_path="$1"
  local target_path="$2"

  [[ -f "$source_path" ]] || die "Falta fuente: $source_path"
  mkdir -p "$(dirname "$target_path")"

  if [[ -L "$target_path" ]]; then
    local current_target
    current_target="$(readlink "$target_path")"
    if [[ "$current_target" == "$source_path" ]]; then
      return 0
    fi
    rm "$target_path"
  elif [[ -e "$target_path" ]]; then
    if cmp -s "$source_path" "$target_path"; then
      return 0
    fi
    die "Ya existe $target_path y no es symlink; no lo sobreescribo"
  fi

  ln -s "$source_path" "$target_path"
}

print_header "Trellis2 GGUF layout"
kv "lab_dir" "$COMFYUI_TRELLIS2_LAB_DIR"
kv "source_root" "$SOURCE_ROOT"
kv "model_root" "$MODEL_ROOT"

[[ -d "$COMFYUI_TRELLIS2_LAB_DIR" ]] || die "No existe $COMFYUI_TRELLIS2_LAB_DIR"
[[ -d "$SOURCE_ROOT" ]] || die "No existe $SOURCE_ROOT"

link_file "$SOURCE_ROOT/pipeline.json" "$MODEL_ROOT/pipeline.json"
link_file "$SOURCE_ROOT/texturing_pipeline.json" "$MODEL_ROOT/texturing_pipeline.json"

link_file "$SOURCE_ROOT/refiner/ss_flow_img_dit_1_3B_64_bf16.json" "$MODEL_ROOT/ckpts/ss_flow_img_dit_1_3B_64_bf16.json"
link_file "$SOURCE_ROOT/refiner/ss_flow_img_dit_1_3B_64_bf16.safetensors" "$MODEL_ROOT/ckpts/ss_flow_img_dit_1_3B_64_bf16.safetensors"
link_file "$SOURCE_ROOT/refiner/ss_flow_img_dit_1_3B_64_bf16_Q4_K_M.gguf" "$MODEL_ROOT/ckpts/ss_flow_img_dit_1_3B_64_bf16.gguf"

link_file "$SOURCE_ROOT/shape/slat_flow_img2shape_dit_1_3B_512_bf16.json" "$MODEL_ROOT/ckpts/slat_flow_img2shape_dit_1_3B_512_bf16.json"
link_file "$SOURCE_ROOT/shape/slat_flow_img2shape_dit_1_3B_512_bf16.safetensors" "$MODEL_ROOT/ckpts/slat_flow_img2shape_dit_1_3B_512_bf16.safetensors"
link_file "$SOURCE_ROOT/shape/slat_flow_img2shape_dit_1_3B_512_bf16_Q4_K_M.gguf" "$MODEL_ROOT/ckpts/slat_flow_img2shape_dit_1_3B_512_bf16.gguf"
link_file "$SOURCE_ROOT/shape/slat_flow_img2shape_dit_1_3B_1024_bf16.json" "$MODEL_ROOT/ckpts/slat_flow_img2shape_dit_1_3B_1024_bf16.json"
link_file "$SOURCE_ROOT/shape/slat_flow_img2shape_dit_1_3B_1024_bf16.safetensors" "$MODEL_ROOT/ckpts/slat_flow_img2shape_dit_1_3B_1024_bf16.safetensors"
link_file "$SOURCE_ROOT/shape/slat_flow_img2shape_dit_1_3B_1024_bf16_Q4_K_M.gguf" "$MODEL_ROOT/ckpts/slat_flow_img2shape_dit_1_3B_1024_bf16.gguf"

link_file "$SOURCE_ROOT/texture/slat_flow_imgshape2tex_dit_1_3B_512_bf16.json" "$MODEL_ROOT/ckpts/slat_flow_imgshape2tex_dit_1_3B_512_bf16.json"
link_file "$SOURCE_ROOT/texture/slat_flow_imgshape2tex_dit_1_3B_512_bf16.safetensors" "$MODEL_ROOT/ckpts/slat_flow_imgshape2tex_dit_1_3B_512_bf16.safetensors"
link_file "$SOURCE_ROOT/texture/slat_flow_imgshape2tex_dit_1_3B_512_bf16_Q4_K_M.gguf" "$MODEL_ROOT/ckpts/slat_flow_imgshape2tex_dit_1_3B_512_bf16.gguf"
link_file "$SOURCE_ROOT/texture/slat_flow_imgshape2tex_dit_1_3B_1024_bf16.json" "$MODEL_ROOT/ckpts/slat_flow_imgshape2tex_dit_1_3B_1024_bf16.json"
link_file "$SOURCE_ROOT/texture/slat_flow_imgshape2tex_dit_1_3B_1024_bf16.safetensors" "$MODEL_ROOT/ckpts/slat_flow_imgshape2tex_dit_1_3B_1024_bf16.safetensors"
link_file "$SOURCE_ROOT/texture/slat_flow_imgshape2tex_dit_1_3B_1024_bf16_Q4_K_M.gguf" "$MODEL_ROOT/ckpts/slat_flow_imgshape2tex_dit_1_3B_1024_bf16.gguf"

link_file "$SOURCE_ROOT/decoders/Stage2/shape_dec_next_dc_f16c32_fp16.json" "$MODEL_ROOT/ckpts/shape_dec_next_dc_f16c32_fp16.json"
link_file "$SOURCE_ROOT/decoders/Stage2/shape_dec_next_dc_f16c32_fp16.safetensors" "$MODEL_ROOT/ckpts/shape_dec_next_dc_f16c32_fp16.safetensors"
link_file "$SOURCE_ROOT/decoders/Stage2/tex_dec_next_dc_f16c32_fp16.json" "$MODEL_ROOT/ckpts/tex_dec_next_dc_f16c32_fp16.json"
link_file "$SOURCE_ROOT/decoders/Stage2/tex_dec_next_dc_f16c32_fp16.safetensors" "$MODEL_ROOT/ckpts/tex_dec_next_dc_f16c32_fp16.safetensors"

link_file "$SOURCE_ROOT/encoders/shape_enc_next_dc_f16c32_fp16.json" "$MODEL_ROOT/ckpts/shape_enc_next_dc_f16c32_fp16.json"
link_file "$SOURCE_ROOT/encoders/shape_enc_next_dc_f16c32_fp16.safetensors" "$MODEL_ROOT/ckpts/shape_enc_next_dc_f16c32_fp16.safetensors"

link_file "$SOURCE_ROOT/decoders/Stage1/ss_dec_conv3d_16l8_fp16.json" "$IMAGE_ROOT/ckpts/ss_dec_conv3d_16l8_fp16.json"
link_file "$SOURCE_ROOT/decoders/Stage1/ss_dec_conv3d_16l8_fp16.safetensors" "$IMAGE_ROOT/ckpts/ss_dec_conv3d_16l8_fp16.safetensors"

mkdir -p "$FACEBOOK_ROOT"
link_file "$SOURCE_ROOT/Vision/dinov3-vitl16-pretrain-lvd1689m.safetensors" "$FACEBOOK_ROOT/model.safetensors"
if [[ -f "$SOURCE_ROOT/Vision/preprocessor_config.json" ]]; then
  link_file "$SOURCE_ROOT/Vision/preprocessor_config.json" "$FACEBOOK_ROOT/preprocessor_config.json"
fi

cat >"$FACEBOOK_ROOT/config.json" <<'JSON'
{
  "model_type": "dinov3_vit",
  "hidden_size": 1024,
  "num_hidden_layers": 24,
  "num_attention_heads": 16,
  "intermediate_size": 4096,
  "patch_size": 16,
  "num_channels": 3,
  "num_register_tokens": 4,
  "image_size": 224,
  "hidden_act": "gelu",
  "attention_dropout": 0.0,
  "initializer_range": 0.02,
  "layer_norm_eps": 0.00001,
  "layerscale_value": 1.0,
  "apply_layernorm": true,
  "use_gated_mlp": false,
  "mlp_bias": true,
  "proj_bias": true,
  "query_bias": true,
  "key_bias": false,
  "value_bias": true,
  "rope_theta": 100.0,
  "pos_embed_rescale": 2.0,
  "reshape_hidden_states": true,
  "out_features": [
    "stage24"
  ],
  "out_indices": [
    24
  ]
}
JSON

if [[ -f "$O_VOXEL_SM86_WHEEL" ]]; then
  "$COMFYUI_TRELLIS2_LAB_DIR/.venv/bin/python" -m pip install --force-reinstall --no-deps "$O_VOXEL_SM86_WHEEL"
else
  die "Falta wheel o_voxel compatible sm_86: $O_VOXEL_SM86_WHEEL"
fi

if [[ -f "$FLEX_GEMM_SM86_WHEEL" ]]; then
  "$COMFYUI_TRELLIS2_LAB_DIR/.venv/bin/python" -m pip install --force-reinstall --no-deps "$FLEX_GEMM_SM86_WHEEL"
else
  die "Falta wheel flex_gemm compatible sm_86: $FLEX_GEMM_SM86_WHEEL"
fi

if ! "$COMFYUI_TRELLIS2_LAB_DIR/.venv/bin/python" <<'PY'
import nvdiffrast.torch as dr
dr.RasterizeCudaContext()
print("nvdiffrast_cuda=ok")
PY
then
  TORCH_CUDA_ARCH_LIST=8.6 FORCE_CUDA=1 \
    "$COMFYUI_TRELLIS2_LAB_DIR/.venv/bin/python" -m pip install \
      --force-reinstall --no-deps --no-build-isolation \
      git+https://github.com/NVlabs/nvdiffrast.git
fi

if [[ -d "$WORKFLOWS_ROOT" ]]; then
  for workflow_name in Trellis2_High_Quality_GGUF.json Trellis2_High_Quality_GGUF_Q8.json Trellis2_High_Quality_FP16.json Trellis2Multiviews_GGUF.json; do
    if [[ -f "$REPO_WORKFLOWS_ROOT/$workflow_name" ]]; then
      cp "$REPO_WORKFLOWS_ROOT/$workflow_name" "$WORKFLOWS_ROOT/$workflow_name"
    fi
  done

  "$COMFYUI_TRELLIS2_LAB_DIR/.venv/bin/python" - "$WORKFLOWS_ROOT" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
changed = []
for path in sorted(root.glob("*.json")):
    data = json.loads(path.read_text(encoding="utf-8"))
    touched = False
    for node in data.get("nodes", []):
        if node.get("type") not in {"Trellis2LoadModel", "Trellis2LoadModel_GGUF"}:
            continue
        values = node.get("widgets_values")
        backend_index = 1 if node.get("type") == "Trellis2LoadModel" else 2
        if isinstance(values, list) and len(values) > backend_index and values[backend_index] in {"flash_attn", "flash_attn_3", "xformers"}:
            values[backend_index] = "sdpa"
            touched = True
        if node.get("type") == "Trellis2LoadModel" and isinstance(values, list) and len(values) > 1 and values[1] in {"flash_attn", "flash_attn_3", "xformers"}:
            values[1] = "sdpa"
            touched = True
        if node.get("type") == "Trellis2LoadModel" and isinstance(values, list) and len(values) > 5 and values[5] == "flex_gemm":
            values[5] = "spconv"
            touched = True
        if node.get("type") == "Trellis2LoadImageWithTransparency" and isinstance(values, list) and values:
            current_image = root.parent.parent.parent / "input" / values[0]
            fallback_image = root.parent.parent.parent / "input" / "ChatGPT Image Apr 25, 2026, 04_19_30 PM.png"
            if not current_image.exists() and fallback_image.exists():
                values[0] = fallback_image.name
                touched = True
        if node.get("type") == "Preview3D":
            values = node.get("widgets_values")
            if isinstance(values, list) and values and isinstance(values[0], str) and values[0].startswith("F:/"):
                values[0] = ""
                touched = True
        if node.get("type") == "Trellis2PreProcessImage":
            values = node.get("widgets_values")
            if isinstance(values, list) and len(values) > 1 and values[1] is True:
                values[1] = False
                touched = True
    if touched:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        changed.append(path.name)

if changed:
    print("patched_workflows=" + ",".join(changed))
else:
    print("patched_workflows=none")
PY
fi

kv "status" "layout_ready"

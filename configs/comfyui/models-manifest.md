# Manifest de Modelos ComfyUI

Este documento implementa el entregable de `8.8`.
Describe donde viven los modelos en la maquina local y distingue entre:

- stack operativo preferido hoy
- biblioteca heredada conservada para variantes futuras
- assets no descargados a proposito porque hoy no son la opcion correcta

## Estado actual resumido

| Asset | Tipo | Ruta esperada | Estado local | Uso |
| --- | --- | --- | --- | --- |
| `z_image_turbo_bf16.safetensors` | diffusion model | `models/diffusion_models/` | presente | `UC-IMG-02`, `UC-IMG-03` |
| `qwen_3_4b.safetensors` | text encoder | `models/text_encoders/` | presente | `UC-IMG-01`, `UC-IMG-02`, `UC-IMG-03` |
| `ae.safetensors` | VAE | `models/vae/` | presente | stack `Z-Image` |
| `Z-Image-Turbo-Fun-Controlnet-Union-2.1-2601-8steps.safetensors` | model patch | `models/model_patches/` | presente | `UC-IMG-02`, `UC-IMG-03` |
| `da3_base.safetensors` | depth model | `models/depthanything3/` | presente | ruta exacta `DepthAnything_V3` para `UC-VID-01` |
| `depth_anything_v2_vitl_fp32.safetensors` | depth model | `models/depthanything/` | presente | fallback de preprocess |
| `wan2.2_ti2v_5B_fp16.safetensors` | diffusion model | `models/diffusion_models/` | presente | ruta preferida para `UC-VID-03` |
| `umt5_xxl_fp16.safetensors` | text encoder | `models/text_encoders/` | presente | stack `Wan 2.2` preferido |
| `wan2.2_vae.safetensors` | VAE | `models/vae/` | presente | stack `Wan 2.2` preferido |
| `wan-14B_vace_skyreels_v3_R2V_e4m3fn_v1.safetensors` | diffusion model | `models/diffusion_models/wan/` | presente | biblioteca heredada para `UC-VID-02` |
| `wan_2.1_vae.safetensors` | VAE | `models/vae/` | presente | biblioteca heredada `Wan 2.1` |
| `Wan2.1_T2V_14B_FusionX_LoRA.safetensors` | LoRA | `models/loras/` | presente | biblioteca heredada `UC-VID-02` |
| `wan/Lenovo.safetensors` | LoRA | `models/loras/wan/` | presente | biblioteca heredada `UC-VID-02` |
| `Lenovo.safetensors` | symlink de conveniencia | `models/loras/` | presente | compatibilidad con rutas heredadas |
| `RealESRGAN_x4plus.pth` | upscale model | `models/upscale_models/` | presente | `UC-VID-04` |

## Layout recomendado

```text
/home/eric/ComfyUI/models/
├── diffusion_models/
│   └── wan/
├── text_encoders/
├── vae/
├── loras/
│   └── wan/
├── model_patches/
├── depthanything/
├── depthanything3/
└── upscale_models/
```

## Stack operativo preferido hoy

Confirmado en disco y alineado con la prioridad actual del producto:

- `models/diffusion_models/z_image_turbo_bf16.safetensors`
- `models/text_encoders/qwen_3_4b.safetensors`
- `models/vae/ae.safetensors`
- `models/model_patches/Z-Image-Turbo-Fun-Controlnet-Union-2.1-2601-8steps.safetensors`
- `models/depthanything3/da3_base.safetensors`
- `models/depthanything/depth_anything_v2_vitl_fp32.safetensors`
- `models/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors`
- `models/text_encoders/umt5_xxl_fp16.safetensors`
- `models/vae/wan2.2_vae.safetensors`

Esto deja:

- imagen lista para prueba con `Z-Image Turbo CN`
- preprocess listo para prueba con `DepthAnything_V3`
- video `first/last frame` listo para prueba con `Wan 2.2 5B fp16`

## Biblioteca heredada conservada

Tambien quedaron descargados assets del stack original, pero se conservan como
referencia y no como ruta preferida:

- `models/diffusion_models/wan/wan-14B_vace_skyreels_v3_R2V_e4m3fn_v1.safetensors`
- `models/vae/wan_2.1_vae.safetensors`
- `models/loras/Wan2.1_T2V_14B_FusionX_LoRA.safetensors`
- `models/loras/wan/Lenovo.safetensors`
- `models/upscale_models/RealESRGAN_x4plus.pth`

Sirven para:

- preservar `UC-VID-02` como biblioteca de referencia
- comparar contra variantes futuras
- mantener una ruta simple de upscale en `UC-VID-04`

## Assets no descargados a proposito

No se descargaron porque hoy no son la opcion correcta para el baseline
preferido:

- `umt5_xxl_fp8_e4m3fn_scaled.safetensors`
- `wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors`
- `wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors`
- `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors`
- `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors`

Lectura correcta:

- se evitan cuantizados cuando hay ruta `fp16` viable
- `fp8`, `GGUF` y equivalentes quedan como fallback
- la biblioteca heredada cuantizada no manda sobre la ruta nueva del producto

## Mejor opcion actual para `UC-VID-03`

Con el estado actual de `ComfyUI`, la opcion preferida para
`RTX 3060 12 GB` es:

- `wan2.2_ti2v_5B_fp16.safetensors`
- `wan2.2_vae.safetensors`
- `umt5_xxl_fp16.safetensors`

combinados con:

- `Wan22FirstLastFrameToVideoLatent`

y, solo si la VRAM aprieta:

- `Wan22FirstLastFrameToVideoLatentTiledVAE`

## Regla de ubicacion

- las derivaciones locales del repo deben apuntar a nombres y carpetas
  normalizados
- si el workflow original usa rutas heredadas, la version de producto debe
  corregirlas en `ComfyUIWorkflows/local/`
- si un asset aun no existe, el manifest debe marcarlo como `faltante`
- si un asset cuantizado no es la opcion preferida, puede quedar ausente sin
  que eso invalide el baseline actual

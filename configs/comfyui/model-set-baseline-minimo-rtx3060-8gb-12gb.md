# Model Set Baseline Minimo RTX 3060 8 GB-12 GB

Este documento implementa la tarea `8.9` del `DevPlan`.
Define el set que el producto considera baseline para `minimum`, priorizando
assets no cuantizados cuando son viables en el hardware actual.

## Set objetivo preferido

| Asset | Tipo | Rol | Estado hoy |
| --- | --- | --- | --- |
| `qwen_3_4b.safetensors` | text encoder | base imagen `Z-Image` | presente |
| `z_image_turbo_bf16.safetensors` | diffusion model | base imagen `Z-Image` | presente |
| `ae.safetensors` | VAE | stack `Z-Image` | presente |
| `Z-Image-Turbo-Fun-Controlnet-Union-2.1-2601-8steps.safetensors` | model patch | `UC-IMG-02`, `UC-IMG-03` | presente |
| `da3_base.safetensors` | depth model | ruta exacta `DepthAnything_V3` para `UC-VID-01` | presente |
| `depth_anything_v2_vitl_fp32.safetensors` | depth model | fallback estable para preprocess | presente |
| `wan2.2_ti2v_5B_fp16.safetensors` | diffusion model | video `first/last frame` preferido para `UC-VID-03` | presente |
| `umt5_xxl_fp16.safetensors` | text encoder | stack `Wan 2.2` preferido | presente |
| `wan2.2_vae.safetensors` | VAE | stack `Wan 2.2` preferido | presente |

## Lectura operativa

Con este set, el baseline minimo queda:

- listo para prueba en imagen con `Z-Image Turbo CN`
- listo para prueba en preprocess con `DepthAnything_V3`
- listo para prueba en `first frame -> last frame` con `Wan 2.2 5B fp16`

La regla de producto es:

- preferir `fp16` o pesos completos cuando entren razonablemente
- degradar despues resolucion, duracion o `TiledVAE`
- dejar `fp8`, `GGUF` y cuantizados equivalentes como fallback, no como default

## Biblioteca heredada separada del baseline

Estos assets pueden convivir en la maquina, pero no definen el baseline
preferido:

- `wan-14B_vace_skyreels_v3_R2V_e4m3fn_v1.safetensors`
- `wan_2.1_vae.safetensors`
- `Wan2.1_T2V_14B_FusionX_LoRA.safetensors`
- `Lenovo.safetensors`
- `RealESRGAN_x4plus.pth`

Sirven para:

- conservar el AI Renderer original como biblioteca de referencia
- probar variantes heredadas cuando interese comparar
- habilitar upscale simple en `UC-VID-04`

## Ubicacion sugerida

- `models/text_encoders/`
- `models/diffusion_models/`
- `models/vae/`
- `models/model_patches/`
- `models/depthanything3/`
- `models/depthanything/`

Para biblioteca heredada adicional:

- `models/diffusion_models/wan/`
- `models/loras/`
- `models/loras/wan/`
- `models/upscale_models/`

## Regla de producto

El baseline minimo no se declara operativo por intencion, sino por assets
presentes y por una ruta preferida clara.

Hoy esa ruta preferida ya no es el stack cuantizado heredado `VACE/Wan 2.1`,
sino:

- `Z-Image` para imagen
- `DepthAnything_V3` con `V2` como fallback para preprocess
- `Wan 2.2 5B fp16` para video nuevo

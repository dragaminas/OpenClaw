# Auditoria de Workflows Base

Este documento implementa la tarea `8.5` del `DevPlan`.
Audita los JSON originales de `ComfyUIWorkflows/` como biblioteca de
referencia, no como variantes listas por defecto.

## Criterio de clasificacion

- `baseline-compatible`: el workflow esta razonablemente cerca de poder correr
  en `minimum`
- `referencia de alto VRAM`: sirve como fuente para variantes futuras de
  `maximum`
- `base adaptable`: contiene valor claro, pero necesita ajustes locales antes
  de ser variante primaria
- `experimento`: sirve para exploracion, no para producto
- `legado`: conservar solo por historial

## Resultado

| Archivo | Clase | Casos servidos | Estado crudo | Motivo principal |
| --- | --- | --- | --- | --- |
| `260303_MICKMUMPITZ_Z-IMAGE_TURBO_CN_1-1.json` | `baseline-compatible` | `UC-IMG-02`, `UC-IMG-03` | casi utilizable | usa stack ligero, el patch ya esta presente y solo queda validar la variante derivada |
| `260225_MICKMUMPITZ_AI-RENDERER-PREPROCESS_1-0.json` | `base adaptable` | `UC-VID-01` | no baseline directo | el stack `DepthAnything_V3` ya esta disponible, pero falta validar salidas y empaquetado de controles |
| `260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0.json` | `base adaptable` | `UC-VID-02` | no baseline directo | su biblioteca heredada ya puede estar presente, pero sigue siendo una ruta cuantizada y no la preferida para baseline |
| `260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0_Runpod.json` | `referencia de alto VRAM` | `UC-VID-02` | referencia | esta orientado a hardware con mas margen y sirve mejor como biblioteca futura |

## Detalle por workflow

### `260303_MICKMUMPITZ_Z-IMAGE_TURBO_CN_1-1.json`

- nodos: `23`
- dependencias importantes:
  - `QwenImageDiffsynthControlnet`
  - `ModelPatchLoader`
  - `VHS_LoadVideo`
  - `rgthree`
- assets esperados:
  - `qwen_3_4b.safetensors`
  - `z_image_turbo_bf16.safetensors`
  - `ae.safetensors`
  - `Z-Image-Turbo-Fun-Controlnet-Union-2.1-2601-8steps.safetensors`
- observaciones:
  - el runtime local ya tiene el modelo, el text encoder, el VAE y el
    `model patch`
  - el JSON original usa rutas de modelo con subdirectorios que no coinciden con
    el layout actual del entorno local

### `260225_MICKMUMPITZ_AI-RENDERER-PREPROCESS_1-0.json`

- nodos: `22`
- dependencias importantes:
  - `VHS_*`
  - `CannyEdgePreprocessor`
  - `OpenposePreprocessor`
  - `ResolutionPicker`
  - `PreprocessSwitch`
- assets esperados:
  - `da3_base.safetensors`
- observaciones:
  - el runtime local ya expone `DownloadAndLoadDepthAnythingV3Model`
    y `DepthAnything_V3`
  - el modelo `V3` ya puede estar descargado localmente y el fallback
    `DepthAnything_V2` tambien
  - si se quiere usar hoy como baseline, el siguiente paso ya no es completar
    assets sino validar el paquete de salidas
  - los `SAVE PREPROCESS` originales no estan optimizados como paquete de
    salidas persistentes para el bridge con Blender

### `260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0.json`

- nodos: `66`
- dependencias importantes:
  - `ComfyUI-WanVideoWrapper`
  - `wanvaceadvanced`
  - `Impact Pack`
  - `easy-use`
  - `Essentials`
  - `VideoHelperSuite`
  - `mickmumpitz-nodes`
- assets esperados:
  - `wan-14B_vace_skyreels_v3_R2V_e4m3fn_v1.safetensors`
  - `umt5_xxl_fp16.safetensors`
  - `wan_2.1_vae.safetensors`
  - LoRAs `Wan2.1_T2V_14B_FusionX_LoRA` y `Lenovo`
- observaciones:
  - conceptualmente es el mejor punto de partida para `UC-VID-02`
  - hoy sigue siendo una base adaptable, no una variante operativa cerrada
  - aunque la biblioteca heredada ya este descargada, la ruta sigue sin ser la
    preferida para baseline porque nace de un stack cuantizado y de supuestos
    mas pesados que la variante `Wan 2.2 5B fp16`
  - usa placeholders y nombres de entrada propios del autor

### `260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0_Runpod.json`

- nodos: `64`
- dependencias importantes:
  - mismas familias que la variante local
  - `WanVacePhantomSimpleV2`
- assets esperados:
  - misma familia Wan del workflow local
- observaciones:
  - es mejor tratarlo como referencia de producto para `maximum`
  - inspira variantes mas ambiciosas, pero no debe ser la ruta principal del
    baseline

## Lectura de producto

- no hay workflows claramente `legado` en la biblioteca actual
- tampoco hay `experimentos` puros; todos los JSON base aportan algo util
- el unico workflow mas cerca de ser baseline hoy es `Z-Image Turbo CN`
- el valor del resto esta en derivarlos y versionarlos, no en ejecutarlos
  "tal cual"
- para video nuevo, la ruta preferida de producto deberia salir antes de
  `Wan 2.2 5B fp16` que del stack heredado `VACE/Wan 2.1`

## Implicacion inmediata

La biblioteca base debe conservarse intacta y toda productizacion nueva debe
vivir en `ComfyUIWorkflows/local/`.

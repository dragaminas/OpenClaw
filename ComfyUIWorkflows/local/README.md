# Workflows Derivados Locales

Este directorio implementa la tarea `8.11` del `DevPlan`.
Contiene variantes versionadas para producto sin sobrescribir los JSON
originales descargados.

## Regla de trazabilidad

Cada JSON derivado incluye metadatos en `extra.openclaw` con:

- `derived_from`
- `use_case_id`
- `hardware_profile`
- `role`

## Inventario actual

| Archivo | Procedencia | Rol |
| --- | --- | --- |
| `minimum/uc-img-02-z-image-turbo-cn-rtx3060-v1.json` | `260303_MICKMUMPITZ_Z-IMAGE_TURBO_CN_1-1.json` | baseline candidato para `UC-IMG-02` |
| `minimum/uc-img-03-z-image-style-exploration-rtx3060-v1.json` | `260303_MICKMUMPITZ_Z-IMAGE_TURBO_CN_1-1.json` | exploracion de estilo para `UC-IMG-03` |
| `minimum/uc-vid-01-ai-renderer-preprocess-rtx3060-v1.json` | `260225_MICKMUMPITZ_AI-RENDERER-PREPROCESS_1-0.json` | preprocess baseline con adaptacion a `DepthAnything_V2` |
| `minimum/uc-vid-02-ai-renderer-video-rtx3060-v1.json` | `260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0.json` | render de video baseline candidato |
| `maximum/uc-vid-02-ai-renderer-video-high-vram-reference-v1.json` | `260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0_Runpod.json` | referencia de alto VRAM |
| `adaptable/uc-img-01-text-to-image-z-image-template-v1.json` | `Text to Image (Z-Image-Turbo).json` | semilla template para `UC-IMG-01` |
| `adaptable/uc-vid-03-image-to-video-wan22-template-v1.json` | `Image to Video (Wan 2.2).json` | semilla template para `UC-VID-03` |
| `adaptable/uc-vid-04-video-upscale-ganx4-template-v1.json` | `Video Upscale(GAN x4).json` | referencia simple para `UC-VID-04` |
| `adaptable/uc-3d-01-text-to-asset-sf3d-bridge-v1.json` | `stable-fast-3d/demo_files/workflows/sf3d_example.json` | puente `UC-3D-01` con imagen semilla staged antes de `SF3D` |
| `minimum/uc-3d-02-image-to-asset-sf3d-single-image-v1.json` | `stable-fast-3d/demo_files/workflows/sf3d_example.json` | baseline `single image -> asset 3D` para `UC-3D-02` |
| `adaptable/uc-3d-03-text-to-scene-sf3d-asset-pack-bridge-v1.json` | `stable-fast-3d/demo_files/workflows/sf3d_example.json` | puente `UC-3D-03` orientado a set de activos y envolventes |
| `adaptable/uc-3d-04-image-to-scene-sf3d-asset-pack-v1.json` | `stable-fast-3d/demo_files/workflows/sf3d_example.json` | descomposicion de escena a activos o shell usando `SF3D` por pieza |

## Que se ha normalizado aqui

- nombres de entrada y salida mas previsibles
- rutas de asset mas alineadas con el entorno local
- metadatos de procedencia
- versionado propio sin tocar la biblioteca original

## Que no debe hacerse

- editar directamente los JSON originales de `ComfyUIWorkflows/`
- declarar operativa una variante solo por existir este archivo
- borrar la referencia al workflow base del que nacio

# Mapa de Workflows y Derivaciones

Este documento implementa la tarea `8.6` del `DevPlan`.
Mapea que papel cumple cada workflow base, de que perfil parte y que
derivaciones futuras deberia inspirar.

## Mapa resumido

| Workflow base | Rol hoy | Perfil de partida | Casos que cubre | Derivaciones esperadas |
| --- | --- | --- | --- | --- |
| `260225_MICKMUMPITZ_AI-RENDERER-PREPROCESS_1-0.json` | fuente para preprocess de controles | `minimum` objetivo, pero no listo crudo | `UC-VID-01` | paquete de controles persistente, fallback `DepthAnything_V2`, segmentacion por shot |
| `260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0.json` | fuente heredada para render de video local | biblioteca util para `minimum`, pero no ruta primaria | `UC-VID-02` | variante baseline segmentada, exploracion de estilo, version medium |
| `260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0_Runpod.json` | referencia de alto VRAM | `maximum` | `UC-VID-02` | variante maxima, lotes largos, adaptacion con mas calidad y menos compromisos |
| `260303_MICKMUMPITZ_Z-IMAGE_TURBO_CN_1-1.json` | base de imagen ligera | `minimum` | `UC-IMG-02`, `UC-IMG-03` | version text-to-image, look-dev rapido, preset de estilo |

## Detalle por workflow

### Preprocess

Archivo:
`ComfyUIWorkflows/260225_MICKMUMPITZ_AI-RENDERER-PREPROCESS_1-0.json`

Sirve hoy para:

- extraer `lineart`
- extraer `pose`
- definir como empaquetar controles de un plano base

Perfil de partida:

- pensado como paso previo local
- compatible con `minimum` solo despues de adaptar el bloque de profundidad

Derivaciones que deberia inspirar:

- `uc-vid-01-ai-renderer-preprocess-rtx3060-v1.json`
- una variante sin profundidad
- una variante con `DepthAnything_V3` validada sobre el baseline actual

### AI Renderer local

Archivo:
`ComfyUIWorkflows/260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0.json`

Sirve hoy para:

- convertir animacion base mas referencias en render de video
- inspirar la captura de slots de `UC-VID-02`

Perfil de partida:

- apunta a local, pero no esta listo para baseline sin curacion
- aunque su biblioteca heredada se conserve localmente, no debe imponerse como
  camino preferido frente a `Wan 2.2 5B fp16`

Derivaciones que deberia inspirar:

- `uc-vid-02-ai-renderer-video-rtx3060-v1.json`
- una variante de exploracion de estilo para `UC-IMG-03`
- una futura variante `medium` con resolucion y longitud mayores

### AI Renderer high VRAM

Archivo:
`ComfyUIWorkflows/260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0_Runpod.json`

Sirve hoy para:

- conservar decisiones de estructura y sampling mas ambiciosas
- comparar contra la variante local cuando el baseline aun no cubre un caso

Perfil de partida:

- `maximum`

Derivaciones que deberia inspirar:

- `uc-vid-02-ai-renderer-video-high-vram-reference-v1.json`
- una futura variante nativa de `maximum`
- posibles presets de lote o calidad cuando el hardware mejore

### Z-Image Turbo CN

Archivo:
`ComfyUIWorkflows/260303_MICKMUMPITZ_Z-IMAGE_TURBO_CN_1-1.json`

Sirve hoy para:

- renderizar un frame o still desde una imagen base
- servir como laboratorio de prompt y control visual ligero

Perfil de partida:

- `minimum`

Derivaciones que deberia inspirar:

- `uc-img-02-z-image-turbo-cn-rtx3060-v1.json`
- `uc-img-03-z-image-style-exploration-rtx3060-v1.json`
- una variante `UC-IMG-01` basada en template `Text to Image (Z-Image-Turbo)`

## Templates locales de ComfyUI reutilizados

Ademas de los workflows base del repo, el stack local ya trae templates utiles
que conviene versionar como semillas de futuras derivaciones:

| Template local | Uso | Derivacion prevista |
| --- | --- | --- |
| `Text to Image (Z-Image-Turbo).json` | imagen desde prompt | `UC-IMG-01` |
| `Image to Video (Wan 2.2).json` | start image a video | referencia general para `UC-VID-03` |
| `Video Upscale(GAN x4).json` | mejora de video | referencia para `UC-VID-04` |

Ademas, tras la instalacion de nodos faltantes, el stack local ya dispone de:

- `Wan22FirstLastFrameToVideoLatent`
- `Wan22FirstLastFrameToVideoLatentTiledVAE`

Eso abre una ruta mas prometedora para `UC-VID-03` que la simple variante de
`start image -> video`, porque permite usar `first frame + last frame` con la
familia `Wan 2.2 5B`.

Regla de preferencia para video:

- primero intentar `Wan 2.2 5B fp16` y `umt5_xxl_fp16`
- si la prueba real muestra insuficiencia critica, degradar despues
- dejar el stack cuantizado heredado como biblioteca y referencia, no como
  default

## Regla operativa

- el workflow base original nunca se sobrescribe
- la variante de producto siempre vive en `ComfyUIWorkflows/local/`
- toda derivacion debe registrar su `derived_from`
- el catalogo Python debe apuntar primero a la derivacion local y dejar la
  fuente original como referencia secundaria

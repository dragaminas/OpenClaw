# Rutas Fallback

Este documento implementa la tarea `8.10` del `DevPlan`.
El fallback no se entiende aqui como "solo para VRAM limitada", sino como
cualquier ruta razonable cuando el flujo ideal aun no tiene implementacion
operativa en el baseline actual.

## Principio

Se usa fallback cuando ocurre alguna de estas situaciones:

- falta un modelo critico
- falta un custom node o el runtime no expone el nodo esperado
- existe workflow base, pero no derivacion local lista
- el plano es demasiado pesado para el preset baseline
- el objetivo real se puede resolver con una ruta mas simple y segura

## Decision general

| Caso | Ruta primaria | Fallback recomendado |
| --- | --- | --- |
| `UC-IMG-02` | `Z-Image Turbo CN` con patch | si falta el patch, usar template `Text to Image (Z-Image-Turbo)` o bloquear con mensaje claro |
| `UC-VID-01` | preprocess completo con `depth/pose/outline` | si falta el modelo `V3`, seguir con `outline + pose` o usar `DepthAnything_V2` |
| `UC-VID-02` | biblioteca heredada `AI Renderer 2.0` | si no compensa usar el stack cuantizado, degradar a preprocess reutilizable o priorizar `UC-VID-03` |
| `UC-VID-03` | start/end con `Wan22FirstLastFrameToVideoLatent` y `Wan 2.2 5B fp16` | si la VRAM no alcanza, degradar despues a `TiledVAE`, menor resolucion o menor duracion |
| `UC-VID-04` | futura mejora nativa | usar `Video Upscale(GAN x4)` como ruta simple de mejora |

## Fallbacks ya definidos

### Profundidad

Situacion actual:

- el runtime local ya expone `DownloadAndLoadDepthAnythingV3Model`
  y `DepthAnything_V3`
- tambien expone `DownloadAndLoadDepthAnythingV2Model`
  y `DepthAnything_V2`

Ruta fallback:

- para `UC-VID-01`, la ruta ideal puede volver a `V3`
- si el modelo `V3` aun no esta descargado o no conviene usarlo, la derivacion
  local sigue pudiendo pasar a `V2`
- si tampoco esta el modelo `V2`, el preprocess sigue sin profundidad

### First frame / last frame con Wan 2.2

Situacion actual:

- el runtime local ya expone `Wan22FirstLastFrameToVideoLatent`
- tambien expone `Wan22FirstLastFrameToVideoLatentTiledVAE`
- el stack `Wan 2.2 TI2V 5B fp16` ya puede quedar presente localmente
- el `text encoder` preferido pasa a ser `umt5_xxl_fp16.safetensors`

Ruta recomendada:

- usar `Wan 2.2 TI2V 5B fp16` como camino principal para `UC-VID-03` en hardware
  `minimum`
- si la VRAM aprieta, preferir primero `TiledVAE`
- despues bajar resolucion, duracion o cantidad de frames
- no degradar de primeras a `fp8`, `Wan 2.1` o `GGUF` si lo que se quiere es
  mantener la ruta mas actual y menos cuantizada posible

### Z-Image sin patch de ControlNet

Situacion actual:

- el modelo base `z_image_turbo_bf16.safetensors` esta presente
- el patch `Z-Image-Turbo-Fun-Controlnet-Union-2.1-2601-8steps.safetensors`
  ya puede quedar presente localmente

Ruta fallback:

- usar template `Text to Image (Z-Image-Turbo)` para validar prompt y look
- no venderlo como sustituto completo de `UC-IMG-02`

### Render de video sin assets Wan locales

Situacion actual:

- la biblioteca heredada `wan-14B...`, `wan_2.1_vae` y las LoRAs principales
  puede quedar disponible localmente
- aun asi, no es la ruta preferida de baseline por apoyarse en un stack
  cuantizado y mas pesado

Ruta fallback:

- no intentar vender `UC-VID-02` como mejor primera opcion solo porque ya
  exista la biblioteca local
- generar y guardar primero `UC-VID-01` como paquete de controles
- priorizar `UC-VID-03` si el objetivo cabe en `first/last frame`
- conservar el shot como "pendiente de render AI heredado" si se prefiere no
  usar el stack cuantizado

### Fallback con GGUF

Estado actual:

- el runtime local expone `GGUFLoaderKJ`
- `ComfyUI-GGUF` como plugin independiente no esta instalado
- no hay aun workflow derivado listo con cuantizados Wan

Interpretacion:

- `GGUF` es una ruta candidata cuando un flujo Wan no tenga implementacion
  operativa en baseline
- hoy se considera `ruta evaluada pero no habilitada`

Condiciones para habilitarla:

- instalar `ComfyUI-GGUF` o una ruta equivalente confirmada
- preparar modelos cuantizados realmente compatibles
- versionar una derivacion concreta en `ComfyUIWorkflows/local/`
- validar tiempos y calidad aceptables para `minimum`

## Mensajes de usuario esperados

- "Este flujo todavia no tiene variante baseline operativa; te dejo el paquete
  de controles listo para continuar."
- "Falta el patch de ControlNet; puedo hacer una prueba de look sin control o
  esperar a completar el set de modelos."
- "La ruta GGUF esta prevista, pero aun no esta habilitada en esta maquina."

## Regla de producto

Nunca presentar un fallback como si fuera equivalente al flujo primario.

El sistema debe decir con claridad si esta:

- degradando calidad
- reduciendo control
- dejando el caso preparado pero no resuelto
- remitiendo a una variante futura

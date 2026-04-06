# Validacion E2E de Fase 8

Este documento implementa el entregable de `8.15`.
Registra el estado real de validacion de extremo a extremo de la Fase 8 en
`ComfyUI`, sin fingir que los casos bloqueados ya estan aprobados.

En esta fase la validacion no depende todavia de que Blender este listo.
La integracion `Blender -> ComfyUI` ya queda diseñada en otros entregables,
pero el cierre funcional de `8.15` puede apoyarse en material de prueba
cualquiera.

## Material base actual elegido

Para este repo ya existe un clip local util para arrancar `8.15`:

- fuente local: `blenderTest.mp4`
- rol: video base para `UC-VID-01`
- cadena objetivo inicial: `UC-VID-01 -> UC-VID-02 -> UC-VID-04`
- `shot_id` canonico recomendado: `blender-test`

Para dejarlo en una ruta estable de validacion sin depender de la raiz del repo:

```bash
scripts/apps/comfyui-stage-e2e-fixture.sh
```

Eso publica:

- `~/Studio/Validation/comfyui/e2e/blender-test/fixtures/blender-test__base__v001.mp4`
- `~/Studio/Validation/comfyui/e2e/blender-test/manifests/blender-test__fixture__v001.json`

## Validaciones confirmadas

### Servicio y runtime

- `ComfyUI` local activo en `http://127.0.0.1:8188/`
- `object_info` responde
- los custom nodes principales para VHS, Wan, KJNodes, Impact y control
  preprocess estan cargados

### Biblioteca derivada

- existen workflows derivados en `ComfyUIWorkflows/local/`
- el catalogo Python apunta primero a variantes derivadas, no a originales
  crudos

### Evidencia funcional minima que ya cierra `8.15`

- `smoke-light-5` confirmo `UC-IMG-02` con `SMK-IMG-02-01` en `pass` y un
  still publicado en
  `/home/eric/ComfyUI/output/openclaw/smoke/smoke-light-5/img02/render_00001_.png`
- `smoke-light-5` confirmo `UC-VID-01` con `SMK-VID-01-01` en `pass` y
  artefactos `depth`, `outline` y `pose` publicados sobre el fixture staged
- `general-video-v1-20260406-094217` confirmo despues una corrida real sobre
  `blenderTest.mp4`, reutilizando `UC-VID-01` y `UC-VID-02` dentro de la `V1`
  general publicada como `render-video`

## Matriz de validacion

| Caso | Estado | Motivo |
| --- | --- | --- |
| `UC-IMG-02` frame de prueba cualquiera | `pass` | `SMK-IMG-02-01` produjo `render_00001_.png` en `smoke-light-5` |
| `UC-VID-01` preprocess de controles | `pass` | `SMK-VID-01-01` exporto `depth`, `outline` y `pose` sobre el fixture staged |
| `UC-VID-02` video renderizado baseline | `pass` | la `V1` general dejo un render real sobre `blenderTest.mp4`, con artefactos revisables, reutilizando la derivacion operativa |
| `UC-VID-03` imagen a video / first-last frame | `blocked_missing_asset` | la smoke `smoke-light-5` sigue señalando assets locales ausentes para esta ruta |
| `UC-VID-04` mejora de video | `pass` | `SMK-VID-04-01` produjo `upscale_00001_.mp4` en `smoke-light-5` |

## Lectura correcta de 8.15

La tarea ya queda cerrada en este sistema. El minimo exigido por `8.15` ya se
cubre con una imagen fija real entrando en `UC-IMG-02` y con un clip corto
real, hoy `blenderTest.mp4`, entrando en `UC-VID-01`. Ademas ya existe una
corrida real posterior de la `V1` general que reutiliza `UC-VID-01` y
`UC-VID-02` sobre ese mismo fixture.

Lo que sigue pendiente en la fase ya no pertenece al cierre minimo de `8.15`,
sino a `8.18`, `8.21.5` y `8.21.6`.

## Que valida primero el baseline

Orden recomendado con los modelos ya presentes:

1. `UC-IMG-02` con una imagen fija de prueba cualquiera
2. `UC-VID-01` sobre un clip corto cualquiera para comprobar el paquete de controles
3. `UC-VID-03` sobre un clip corto o sobre first/last frame derivados del material elegido
4. `UC-VID-02` solo como comparativa contra la biblioteca heredada

## Perfil recomendado del material de prueba

Para no bloquear la validacion por el propio clip:

- `3-5` segundos
- `24 fps`
- `480p` o `720p`
- movimiento legible pero no caotico
- fondo y sujeto relativamente claros

Puede ser:

- un video local ya existente
- un clip libre de prueba
- un export de Blender mas adelante, cuando esa capa ya este lista

En este sistema, el video base elegido pasa a ser `blenderTest.mp4` mientras no
se sustituya por otro clip mas representativo.

## Evidencia local usada

- estado del servicio via `scripts/apps/comfyui.sh status`
- consulta de `http://127.0.0.1:8188/object_info`
- verificacion de modelos presentes en `/home/eric/ComfyUI/models`
- `~/Studio/Validation/comfyui/smoke/smoke-light-5/evidence/summary.md`
- `~/Studio/Validation/comfyui/smoke/smoke-light-5/manifests/SMK-IMG-02-01.json`
- `~/Studio/Validation/comfyui/smoke/smoke-light-5/manifests/SMK-VID-01-01.json`
- `~/Studio/Validation/comfyui/e2e/blender-test/general-video-v1/general-video-v1-20260406-094217/evidence/summary.md`
- `docs/comfyui/general-video-render-workflow-results.md`

## Criterio de cierre real

`8.15` solo deberia considerarse completamente cerrada cuando existan:

- una imagen fija de prueba entrando en `UC-IMG-02`
- un clip corto de prueba, hoy `blenderTest.mp4`, entrando en `UC-VID-01` y/o `UC-VID-02`
- artefactos de salida guardados con una convencion estable

A fecha `2026-04-06`, ese criterio ya queda satisfecho por:

- `SMK-IMG-02-01`
- `SMK-VID-01-01`
- `general-video-v1-20260406-094217`

La validacion especifica `Blender -> ComfyUI` puede quedar como aceptacion de
una fase posterior.

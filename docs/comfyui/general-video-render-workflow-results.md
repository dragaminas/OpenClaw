# Resultados V1 del Workflow General de Video

Este documento registra el cierre comprobado de `8.21.2` y `8.21.3`.
Tambien deja constancia de la primera comprobacion real de la rama opcional de
interpolacion FPS publicada despues de ese cierre inicial.

## Estado

- estado: `pass`
- run_id: `general-video-v1-20260406-094217`
- target_id: `general-video-v1`
- prompt_id: `2bd91043-a7c8-4cd0-bbae-1adb10eeed18`
- workflow: `ComfyUIWorkflows/local/minimum/uc-vid-02-general-video-render-rtx3060-v1.json`
- preset asociado: `configs/comfyui/presets/uc-vid-02-general-video-render-v1.yaml`
- validation_root: `~/Studio/Validation/comfyui/e2e/blender-test/general-video-v1/general-video-v1-20260406-094217`
- evidencia: `~/Studio/Validation/comfyui/e2e/blender-test/general-video-v1/general-video-v1-20260406-094217/evidence/summary.md`
- fixture base: `~/Studio/Validation/comfyui/e2e/blender-test/fixtures/blender-test__base__v001.mp4`
- fixture sha256: `ffa5b94c1db39b9341a8324e11e790107c6b1722c8f0094553c9b2dc2df08733`
- controles activos en la corrida validada: `bordes`, `pose`, `profundidad`
- perfil de validacion: `frame_load_cap=2`, `control_width=512`, `render_frame_rate=12`, `full_quality=false`
- tiempo total observado: `30.0` segundos

## Que quedo comprobado

- la derivacion `V1` reutiliza `UC-VID-01` para preprocess de controles y `UC-VID-02` para el render principal
- el workflow preserva aspect ratio por defecto al cargar el video base con `custom_width=512` y `custom_height=0`
- el primer frame queda visible y exportado como artefacto independiente
- los tres controles `bordes`, `pose` y `profundidad` pueden quedar activos a la vez en una corrida real local
- la corrida publica artefactos revisables para preview, preprocess y render final
- la biblioteca `openclaw-workflows` ya publica `render-video` usando esta V1 derivada
- la ruta `validation` sigue separada y mantiene overrides rapidos para humo y
  comprobacion tecnica, pero no debe contaminar el template funcional abierto
  desde la UI

## Artefactos publicados

- `~/ComfyUI/output/openclaw/general-video-v1/general-video-v1-20260406-094217/first_frame_00001_.png`
- `~/ComfyUI/output/openclaw/general-video-v1/general-video-v1-20260406-094217/preprocess_depth_00001.mp4`
- `~/ComfyUI/output/openclaw/general-video-v1/general-video-v1-20260406-094217/preprocess_outline_00001.mp4`
- `~/ComfyUI/output/openclaw/general-video-v1/general-video-v1-20260406-094217/preprocess_pose_00001.mp4`
- `~/ComfyUI/output/openclaw/general-video-v1/general-video-v1-20260406-094217/render_00001.mp4`

## Alcance real de este cierre

Lo que queda validado en `8.21.3` es la base operativa de la `V1`, no la version final de producto.

La corrida registrada aqui uso un perfil rapido de validacion (`frame_load_cap=2`,
`render_frame_rate=12`, `full_quality=false`). Ese perfil sirve para comprobar
que la cadena corre en esta maquina, pero no es el default que debe abrirse
desde la UI para pruebas funcionales.

Ya funciona de verdad:

- video base
- prompt
- preview del primer frame
- seleccion valida de controles
- preprocess publicado
- render principal publicado

Sigue pendiente para etapas posteriores:

- referencias de personaje por color
- segmentacion automatica de clips largos
- una variante generativa mas ambiciosa de interpolacion FPS para stopmotion;
  hoy ya existe una rama funcional local de mezcla temporal lineal con
  `usar_interpolacion_fps` y `fps_objetivo`
- mejora final o upscale hasta `Full HD`
- una corrida `full_quality` mas larga que vaya mas alla de la validacion rapida de base

## Comprobacion posterior de interpolacion FPS

Despues del cierre inicial de `8.21.3`, se verifico una corrida corta adicional
con la rama opcional de FPS activada:

- run_id: `general-video-v1-20260406-114555`
- status: `pass`
- prompt_id: `361c2927-6811-4041-9e98-0b75dbda8a08`
- validation_root: `~/Studio/Validation/comfyui/e2e/blender-test/general-video-v1/general-video-v1-20260406-114555`
- perfil: `frame_load_cap=3`, `render_frame_rate=48`, `enable_fps_interpolation=true`, `target_fps=48.0`, `full_quality=false`

Lo que quedo comprobado en esa corrida:

- `ComfyUI` cargo el helper node `OpenClawFPSInterpolation` desde el modulo
  `openclaw-workflows`
- `render-video` publico el template actualizado con la rama de FPS entre el
  render principal y `RENDER FINAL`
- la V1 siguio generando frame inicial, controles y video final reales con la
  rama opcional activada

## Comandos ejecutados

```bash
scripts/apps/comfyui-stage-e2e-fixture.sh
PYTHONPATH=src python3 -m openclaw_studio.comfyui_general_video_v1
python3 -m compileall src tests
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m openclaw_studio.comfyui_workflow_library sync
scripts/apps/comfyui-general-video-v1-validation.sh --controls bordes,pose,profundidad
scripts/apps/comfyui-general-video-v1-validation.sh --frame-load-cap 3 --render-frame-rate 48 --enable-fps-interpolation --target-fps 48
```

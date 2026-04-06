# Resultados V1 del Workflow General de Video

Este documento registra el cierre comprobado de `8.21.2`, `8.21.3`, `8.21.4`,
`8.21.5` y `8.21.6`.
Tambien deja constancia de la comprobacion real de la rama opcional de
interpolacion FPS publicada despues del cierre base inicial.

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

- una variante generativa mas ambiciosa de interpolacion FPS para stopmotion;
  hoy ya existe una rama funcional local de mezcla temporal lineal con
  `usar_interpolacion_fps` y `fps_objetivo`
- una recomposicion binaria automatica de segmentos en un unico master cuando
  el entorno ofrezca una via local estable de concatenacion
- una corrida `full_quality` mas larga que vaya mas alla de la validacion rapida de base

## Comprobacion real posterior de `8.21.4`

Despues del cierre base y de la rama opcional de FPS, se verifico una corrida
real adicional con la capa opcional de identidad activada:

- run_id: `general-video-v1-8214-identity-20260406-2`
- status: `pass`
- prompt_id: `fdd7db88-c573-4a86-bfd3-5b9a75a47daf`
- validation_root: `~/Studio/Validation/comfyui/e2e/blender-test/general-video-v1/general-video-v1-8214-identity-20260406-2`
- perfil: `frame_load_cap=2`, `render_frame_rate=12`, `enable_color_identity=true`, `full_quality=false`
- anclajes probados:
  - `rojo -> soldado protagonista | sujeto a la izquierda`
  - `azul -> dron enemigo | sujeto a la derecha`

Lo que quedo comprobado en esa corrida:

- `render-video` ya compila y ejecuta la rama `IDENTIDAD COLOR Y ENTIDADES`
  dentro de la misma `V1` funcional, sin abrir workflow paralelo
- el prompt final ya pasa por `OpenClawIdentityPromptBuilder` antes de
  `CLIPTextEncode`
- el workflow ya recompone `refimage` con `BATCH REFS IDENTIDAD`, usando el
  `start image` mas hasta `3` referencias opcionales
- la ejecucion con identidad activa sigue dejando preview, preprocess y render
  final reales
- el template publicado sigue abriendose como `render-video` desde
  `openclaw-workflows`

Limitacion verificada con evidencia:

- el entorno usado para esta subtarea no traia `ffmpeg`, `cv2`, `numpy`,
  `imageio` ni `av`, asi que no se sintetizo una segunda copia local del clip
  ya recoloreada por script
- la capa queda validada sobre `blenderTest.mp4` con anclajes de color,
  referencias visuales y resumen visible en canvas; el contrato para usar un
  clip base ya coloreado queda operativo en la misma entrada `BASE VIDEO`

Incidencia resuelta durante la validacion:

- un primer intento (`general-video-v1-8214-identity-20260406-1`) detecto que
  `LoadImage` no aceptaba el prefijo `input/` en las referencias staged
- tras corregir la ruta publicada a `references/<archivo>`, la corrida completa
  paso y dejo `render_00001.mp4`

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

## Smoke especifica de `8.21.5` y `8.21.6`

Para no dejar la nueva rama solo en validacion larga, se añadio una smoke
especifica del workflow general:

- run_id: `smoke-general-video-v1-82156b`
- case_id: `SMK-GEN-VID-01`
- status: `pass`
- gate_pass: `true`
- validation_root: `~/Studio/Validation/comfyui/smoke/smoke-general-video-v1-82156b`
- tiempo: `32.0` segundos

Lo que quedo comprobado:

- la `V1` general compila y ejecuta la rama visible de segmentacion
- la `V1` general publica `render` y `final_full_hd` dentro del mismo caso
- la smoke ya puede cubrir el camino real de `render-video`, no solo `UC-VID-02`
  y `UC-VID-04` por separado

## Comprobacion real de `8.21.5` y `8.21.6`

Se verifico una corrida real adicional sobre `blenderTest.mp4` con segmentacion
iterable y mejora final Full HD activas:

- run_id: `general-video-v1-82156-segments-fullhd-20260406-2`
- status: `pass`
- validation_root: `~/Studio/Validation/comfyui/e2e/blender-test/general-video-v1/general-video-v1-82156-segments-fullhd-20260406-2`
- perfil: `controls=bordes`, `control_width=256`, `segment_length_frames=49`, `segment_overlap_frames=1`, `usar_mejora_final_full_hd=true`, `full_quality=false`
- video base observado: `107` frames, `3.567` s, `30.0 fps`
- segmentos resultantes: `3`

Lo que quedo comprobado:

- la V1 ya itera subsecciones reales del fixture y deja evidencia separada por
  `segment_001`, `segment_002` y `segment_003`
- cada segmento publica:
  - `render_00001.mp4`
  - `final_full_hd_00001.mp4`
- la recomposicion temporal queda documentada en
  `manifests/recomposition.json`, con `drop_leading_frames_for_concat` a partir
  del segundo segmento
- la salida final Full HD ya no vive como ruta paralela; queda dentro del mismo
  workflow publicado

Rangos comprobados:

- `segment_001`: frames `1-49`
- `segment_002`: frames `49-97`
- `segment_003`: frames `97-107`

## Comandos ejecutados

```bash
scripts/apps/comfyui-stage-e2e-fixture.sh
PYTHONPATH=src python3 -m openclaw_studio.comfyui_general_video_v1
python3 -m compileall src tests
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m openclaw_studio.comfyui_workflow_library sync
scripts/apps/comfyui-general-video-v1-validation.sh --controls bordes,pose,profundidad
scripts/apps/comfyui-general-video-v1-validation.sh --frame-load-cap 3 --render-frame-rate 48 --enable-fps-interpolation --target-fps 48
PYTHONPATH=src python3 -m openclaw_studio.comfyui_general_video_v1_validation --run-id general-video-v1-8214-identity-20260406-2 --controls bordes,pose,profundidad --enable-color-identity --identity-color-1 rojo --identity-entity-1 "soldado protagonista" --identity-prompt-anchor-1 "sujeto a la izquierda" --identity-ref-1 /home/eric/Documents/OpenClaw/.tmp_identity_assets/identity_red.png --identity-color-2 azul --identity-entity-2 "dron enemigo" --identity-prompt-anchor-2 "sujeto a la derecha" --identity-ref-2 /home/eric/Documents/OpenClaw/.tmp_identity_assets/identity_blue.png
PYTHONPATH=src python3 -m openclaw_studio.comfyui_smoke_validation --run-id smoke-general-video-v1-82156b --case-id SMK-GEN-VID-01
PYTHONPATH=src python3 -m openclaw_studio.comfyui_general_video_v1_validation --run-id general-video-v1-82156-segments-fullhd-20260406-2 --controls bordes --control-width 256 --enable-segmentation --segment-length-frames 49 --segment-overlap-frames 1 --timeout-seconds 1800
```

# Resultados de Validacion Atomica y Compuesta 3D

Este documento implementa la tarea `9.14` del `DevPlan` en su estado actual.

## Estado

- estado: `pass_objetos_pending_escenas`
- fecha: `2026-04-18`
- gate ejecutado: `PF-3D-01`

## Resultado del gate

`PF-3D-01` pasa en la baseline `SF3D` de objetos:

- la extension oficial `stable-fast-3d` ya esta instalada y expone nodos en
  `ComfyUI`
- las dependencias nativas de `SF3D` ya quedaron alineadas
- el modelo `stabilityai/stable-fast-3d` ya es accesible con token y cache
- existe imagen fixture staged
- las carpetas de salida son escribibles
- `Blender` esta disponible para la comprobacion de handoff

## Impacto sobre las pruebas

Casos aprobados:

- `AT-3D-OBJ-01`
  - `UC-3D-02` genera `validation_sf3d_cpu_fallback_00001_.glb`
- `AT-3D-OBJ-02`
  - ese `glb` importa en `Blender` con `7948` vertices y `13096` caras
- `CP-3D-01`
  - `UC-3D-01` completa la ruta `texto -> imagen -> SF3D -> Blender`
  - artefacto: `validation_sf3d_bridge_00001_.glb`

Casos aun pendientes:

- `AT-3D-SCN-01`
- `AT-3D-SCN-02`
- `CP-3D-02`
- `CP-3D-03`

## Lo que queda establecido

- la linea de objetos `SF3D` funciona de verdad en este sistema
- el puente `texto -> imagen -> SF3D` ya no es solo teorico
- el handoff a `Blender` tambien queda demostrado
- la parte pendiente se concentra ya en la linea de escenas y composicion

## Comandos usados

```bash
curl -sf http://127.0.0.1:8188/object_info | jq 'keys[]' | rg 'StableFast3D'
ls -lt /home/eric/ComfyUI/output/openclaw/uc-3d-01
ls -lt /home/eric/ComfyUI/output/openclaw/uc-3d-02
blender -b --python /tmp/openclaw_blender_import_check.py -- \
  /home/eric/ComfyUI/output/openclaw/uc-3d-02/validation_sf3d_cpu_fallback_00001_.glb
blender -b --python /tmp/openclaw_blender_import_check.py -- \
  /home/eric/ComfyUI/output/openclaw/uc-3d-01/validation_sf3d_bridge_00001_.glb
```

# Resultados V1 del Workflow General de Objetos 3D

Este documento registra el estado actual de `9.9.3` con corte `2026-04-18`.

## Estado

- estado: `pass tecnico / fail visual`
- alcance validado: `UC-3D-01` y `UC-3D-02`
- workflows preparados:
  - `ComfyUIWorkflows/local/adaptable/uc-3d-01-text-to-asset-sf3d-bridge-v1.json`
  - `ComfyUIWorkflows/local/minimum/uc-3d-02-image-to-asset-sf3d-single-image-v1.json`
- preset asociado principal:
  - `configs/comfyui/presets/uc-3d-02-image-to-asset-sf3d-single-image.yaml`
- pendiente fuera de este corte:
  - validacion de escenas `UC-3D-03` y `UC-3D-04`

## Lectura correcta de este resultado

Este documento demuestra una cosa concreta:

- la cadena `ComfyUI -> SF3D -> glb -> Blender` se ejecuto de verdad

No demuestra por si mismo otra:

- que la calidad visual obtenida sea suficiente para mantener `SF3D` como
  apuesta principal del producto 3D

La lectura honesta de `9.9.3` pasa a ser:

- `pass` operativo de runtime, exportacion e importacion
- evidencia visual insuficiente para declarar exito de producto

## Que se ejecuto de verdad

Se valido el baseline oficial de `SF3D` en la maquina local `RTX 3060 12 GB`:

- clon del repo oficial `stable-fast-3d` en
  `/home/eric/ComfyUI/custom_nodes/stable-fast-3d`
- autenticacion real de `Hugging Face` para el repo gated
  `stabilityai/stable-fast-3d`
- alineacion de `numpy` a `1.26.4`
- alineacion del runtime con `transformers==4.42.3` para evitar el error
  `find_pruneable_heads_and_indices`
- instalacion de `pynanoinstantmeshes`
- compilacion local de `uv_unwrapper` y `texture_baker`
- ajuste local del nodo `SF3D` para:
  - normalizar y redimensionar mascaras procedentes de `ComfyUI`
  - caer a bake en `CPU` si `texture_baker` no tiene kernel `CUDA`
- reinicio real de `ComfyUI`
- comprobacion de nodos expuestos:
  `StableFast3DLoader`, `StableFast3DSampler`, `StableFast3DSave`,
  `StableFast3DPreview`
- corridas reales de `UC-3D-01` y `UC-3D-02`
- importacion real de ambos `glb` en `Blender 5.1.1` en modo headless

## Resultado real

Casos aprobados:

- `UC-3D-02` `imagen -> 3D`
  - input: `/home/eric/ComfyUI/input/openclaw_object_ref.png`
  - output: `/home/eric/ComfyUI/output/openclaw/uc-3d-02/validation_sf3d_cpu_fallback_00001_.glb`
  - tiempo total observado en `ComfyUI`: `8.25 s`
  - importacion `Blender`: `1` mesh, `7948` vertices, `13096` caras
- `UC-3D-01` `texto -> imagen -> 3D`
  - prompt: `silla de madera simple, fotografiada aislada sobre fondo limpio, vista de producto`
  - output: `/home/eric/ComfyUI/output/openclaw/uc-3d-01/validation_sf3d_bridge_00001_.glb`
  - tiempo total observado en `ComfyUI`: `236.76 s`
  - importacion `Blender`: `1` mesh, `25088` vertices, `41188` caras

Artefactos producidos en esta validacion:

- `validation_sf3d_cpu_fallback_00001_.glb`
- `validation_sf3d_bridge_00001_.glb`

## Lo que si queda validado

- el modelo gated `stable-fast-3d` ya descarga y carga de verdad
- `UC-3D-02` deja un `glb` exportable y reutilizable
- `UC-3D-01` valida el puente `texto -> imagen -> SF3D`
- ambos artefactos entran en `Blender` sin romper el handoff
- el catalogo Python y la biblioteca publicada en `ComfyUI` ya tienen una
  baseline `SF3D` operativa como benchmark tecnico

## Lo que sigue pendiente

- validar la linea de escenas `UC-3D-03` y `UC-3D-04`
- decidir si el fallback `CPU` de `texture_baker` se conserva como parche local
  del `MVP` o se sustituye por una recompilacion `CUDA`
- aislar el runtime si se quiere recuperar compatibilidad con extensiones que
  hoy esperan un `huggingface_hub` mas nuevo
- reconocer explicitamente que la calidad visual observada sigue siendo pobre y
  que esta evidencia no basta para sostener `SF3D` como ruta principal de
  producto

## Evidencia principal

```bash
curl -sf http://127.0.0.1:8188/object_info | jq 'keys[]' | rg 'StableFast3D'
ls -lt /home/eric/ComfyUI/output/openclaw/uc-3d-01
ls -lt /home/eric/ComfyUI/output/openclaw/uc-3d-02
blender -b --python /tmp/openclaw_blender_import_check.py -- \
  /home/eric/ComfyUI/output/openclaw/uc-3d-02/validation_sf3d_cpu_fallback_00001_.glb
blender -b --python /tmp/openclaw_blender_import_check.py -- \
  /home/eric/ComfyUI/output/openclaw/uc-3d-01/validation_sf3d_bridge_00001_.glb
```

# Resultados V1 del Workflow General de Objetos 3D

Este documento registra el estado actual de `9.9.3` con corte `2026-04-12`.

## Estado

- estado: `blocked_missing_asset`
- workflows preparados:
  - `ComfyUIWorkflows/local/adaptable/uc-3d-01-text-to-asset-sf3d-bridge-v1.json`
  - `ComfyUIWorkflows/local/minimum/uc-3d-02-image-to-asset-sf3d-single-image-v1.json`
- preset asociado principal:
  - `configs/comfyui/presets/uc-3d-02-image-to-asset-sf3d-single-image.yaml`

## Que se ejecuto de verdad

Se dejo corriendo el baseline oficial de `SF3D` en la maquina local
`RTX 3060 12 GB`:

- clon del repo oficial `stable-fast-3d` en
  `/home/eric/ComfyUI/custom_nodes/stable-fast-3d`
- alineacion de `numpy` a `1.26.4`
- instalacion de `pynanoinstantmeshes`
- compilacion local de `uv_unwrapper` y `texture_baker`
- reinicio real de `ComfyUI`
- comprobacion de nodos expuestos:
  `StableFast3DLoader`, `StableFast3DSampler`, `StableFast3DSave`,
  `StableFast3DPreview`
- intento real de carga del modelo `stabilityai/stable-fast-3d`

## Resultado real

La extension ya funciona, pero la primera carga real del modelo bloquea aqui:

- `SF3D.from_pretrained(...)` devuelve `GatedRepoError`
- detalle principal: `401 Unauthorized`
- motivo: no hay autenticacion valida para el repo gated
  `stabilityai/stable-fast-3d`

Artefactos producidos hoy:

- ninguno de `SF3D`, porque el bloqueo ocurre antes de descargar
  `config.yaml` y `model.safetensors`

## Lo que si queda validado

- los casos `UC-3D-01` y `UC-3D-02` ya tienen workflow `SF3D` versionado
- el catalogo Python ya expone `texto-a-3d` e `imagen-a-3d` sobre `SF3D`
- la extension oficial de `SF3D` ya carga en el `ComfyUI` local
- la biblioteca `openclaw-workflows` ya publica los templates `SF3D`

## Lo que sigue pendiente

- autenticar el `venv` o cachear el modelo `stable-fast-3d`
- correr de verdad `UC-3D-02` y producir un `glb`
- importar ese `glb` en `Blender`
- cerrar despues el puente `UC-3D-01`

## Evidencia principal

```bash
/home/eric/ComfyUI/.venv/bin/python - <<'PY'
import sys
sys.path.insert(0, '/home/eric/ComfyUI/custom_nodes/stable-fast-3d')
from sf3d.system import SF3D
SF3D.from_pretrained(
    'stabilityai/stable-fast-3d',
    config_name='config.yaml',
    weight_name='model.safetensors',
)
PY
curl -sf http://127.0.0.1:8188/object_info | jq 'keys[]' | rg 'StableFast3D'
```

# Resultados de Validacion Atomica y Compuesta 3D

Este documento implementa la tarea `9.14` del `DevPlan` en su estado actual.

## Estado

- estado: `blocked_missing_asset`
- fecha: `2026-04-12`
- gate ejecutado: `PF-3D-01`

## Resultado del gate

`PF-3D-01` falla hoy por estos motivos:

- la extension oficial `stable-fast-3d` ya esta instalada y expone nodos en
  `ComfyUI`
- las dependencias nativas de `SF3D` ya quedaron alineadas
- pero el modelo `stabilityai/stable-fast-3d` sigue inaccesible por
  `GatedRepoError: 401 Unauthorized`
- por tanto no hay todavia artefactos `3D` reales de la baseline `SF3D`

## Impacto sobre las pruebas

Casos no ejecutados por bloqueo previo:

- `AT-3D-OBJ-01`
- `AT-3D-OBJ-02`
- `AT-3D-SCN-01`
- `AT-3D-SCN-02`
- `CP-3D-01`
- `CP-3D-02`
- `CP-3D-03`

## Lo que queda establecido

- la validacion ya tiene gate, casos y criterio estable
- el bloqueo esta documentado con evidencia real del entorno
- no hay ambiguedad entre "el runtime esta roto" y "falta acceso al modelo"

## Comandos usados

```bash
curl -sf http://127.0.0.1:8188/object_info | jq 'keys[]' | rg 'StableFast3D'
/home/eric/ComfyUI/.venv/bin/python - <<'PY'
from huggingface_hub import get_token
print(bool(get_token()))
PY
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
```

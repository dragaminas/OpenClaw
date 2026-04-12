# Mapa de Casos de Uso 3D

Este documento implementa la tarea `9.8` del `DevPlan`.
Conecta los `UC-3D-*` con alias, workflows, presets y lectura de producto.

## Mapa principal

| ID | Alias | Entrada | Entrega preferida | Workflow V1 | Preset |
| --- | --- | --- | --- | --- | --- |
| `UC-3D-01` | `texto-a-3d` | texto | `asset` aislado | `ComfyUIWorkflows/local/adaptable/uc-3d-01-text-to-asset-sf3d-bridge-v1.json` | `uc-3d-01-text-to-asset-sf3d-bridge` |
| `UC-3D-02` | `imagen-a-3d` | imagen | `asset` aislado | `ComfyUIWorkflows/local/minimum/uc-3d-02-image-to-asset-sf3d-single-image-v1.json` | `uc-3d-02-image-to-asset-sf3d-single-image` |
| `UC-3D-03` | `texto-a-escena-3d` | texto | `set`, `blockout` o `envolvente` | `ComfyUIWorkflows/local/adaptable/uc-3d-03-text-to-scene-sf3d-asset-pack-bridge-v1.json` | `uc-3d-03-text-to-scene-sf3d-asset-pack-bridge` |
| `UC-3D-04` | `imagen-a-escena-3d` | imagen | `set`, `blockout` o `envolvente` | `ComfyUIWorkflows/local/adaptable/uc-3d-04-image-to-scene-sf3d-asset-pack-v1.json` | `uc-3d-04-image-to-scene-sf3d-asset-pack` |

## Variantes destacadas

La linea `V1` usa un mismo bloque `SF3D` para varios casos:

- `UC-3D-01` lo usa despues de generar una imagen semilla
- `UC-3D-02` lo usa de forma directa sobre la imagen del objeto
- `UC-3D-03` y `UC-3D-04` lo reutilizan por pieza, crop o envolvente

## Reglas de routing

- si el input ya es una imagen de objeto o personaje, priorizar `UC-3D-02`
- si el usuario pide una escena pero en realidad quiere piezas separadas,
  redirigir a `UC-3D-04`
- si el caso es `texto`, la `V1` debe tratarlo como puente a imagen semilla
- si la referencia visual es demasiado ambiciosa para una escena completa,
  la salida correcta es `asset_set`, `envolvente` o `blockout`

## Relacion con Blender

Todos los casos `UC-3D-*` deben leer `Blender` como etapa normal de producto:

- inspeccion
- cleanup
- escala
- pivot
- catalogacion
- composicion

## Estado de madurez

Con corte `2026-04-12`:

- los casos `UC-3D-*` ya quedan modelados en el catalogo Python
- sus workflows y presets V1 quedan versionados en el repo
- la baseline actual del `MVP` ya apunta a `SF3D`
- la validacion real local de `SF3D` sigue pendiente de cerrar por acceso al
  modelo y alineacion de dependencias
- la validacion historica con `Hunyuan` ya no cuenta como cierre del `MVP`

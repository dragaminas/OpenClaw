# Manifiesto de Modelos para la Linea 3D

Este documento implementa la tarea `9.6` como inventario operativo y deja
trazado el set minimo de modelos que hay que ubicar para cerrar la `V1`.

## Estado local auditado

Con corte `2026-04-18`, la extension oficial de `SF3D` ya esta integrada en el
runtime local y el modelo gated ya queda accesible con token activo y cache
local.

Nota operativa:

- la extension oficial descarga desde el repo gated
  `stabilityai/stable-fast-3d`
- hoy existe token activo bajo el `HOME` del servicio
- el modelo ya quedo descargado en `~/.cache/huggingface`
- la carga real ya se valido con `UC-3D-01` y `UC-3D-02`

## Canon de ubicacion propuesto

Para la extension oficial, la ubicacion primaria de descarga es el cache de
`Hugging Face`:

- `~/.cache/huggingface/hub/`

La extension `ComfyUI` vive en:

- `custom_nodes/stable-fast-3d/`

## Modelos priorizados

| Grupo | Ruta canonica esperada | Uso | Estado local |
| --- | --- | --- | --- |
| `Stable Fast 3D` | `~/.cache/huggingface/hub/.../models--stabilityai--stable-fast-3d/...` | baseline `UC-3D-01` y `UC-3D-02` | presente |
| `texture_baker` | `custom_nodes/stable-fast-3d/texture_baker/` instalado en el `venv` | bake de textura y export | presente |
| `uv_unwrapper` | `custom_nodes/stable-fast-3d/uv_unwrapper/` instalado en el `venv` | UV unwrap | presente |

## Orden minimo de descarga

Para una `V1` alineada con la decision de producto:

1. acceso al repo gated `stabilityai/stable-fast-3d`
2. descarga de `config.yaml`
3. descarga de `model.safetensors`
4. instalacion de `texture_baker`
5. instalacion de `uv_unwrapper`

## Lectura por perfil

| Perfil | Set minimo |
| --- | --- |
| `minimum` | `Stable Fast 3D` |
| `medium` | `minimum` + mas textura o mas lotes |
| `maximum` | `medium` + linea externa futura fuera de `ComfyUI` |

## Regla

Este manifiesto ya no es solo plan de descarga; ahora deja documentado:

- donde vive el baseline `SF3D`
- que el acceso gated ya quedo resuelto
- que `UC-3D-01` y `UC-3D-02` ya consumieron ese modelo con exito
- y que cualquier linea futura `Hunyuan3D` debe seguir tratandose aparte

## Investigacion posterior: `Trellis2 GGUF`

Con corte posterior, se abre una investigacion por calidad visual para evaluar
`TRELLIS.2` con cuantizaciones `GGUF` dentro de `ComfyUI`.

Regla especifica:

- no descargar la suite completa `Aero-Ex/Trellis2-GGUF` a ciegas
- empezar por el set minimo `512` `Q4_K_M` o equivalente
- conservar `SF3D` como baseline historico de comparacion
- comparar contra `Hunyuan3D-2mini-Turbo` con el mismo input antes de cambiar
  la ruta principal de producto

Referencia operativa:

- `docs/comfyui/trellis2-gguf-quality-investigation.md`

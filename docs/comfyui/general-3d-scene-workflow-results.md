# Resultados V1 del Workflow General de Escenas 3D

Este documento registra el estado actual de `9.11.3` con corte `2026-04-12`.

## Estado

- estado: `blocked_missing_asset`
- workflows preparados:
  - `ComfyUIWorkflows/local/adaptable/uc-3d-03-text-to-scene-sf3d-asset-pack-bridge-v1.json`
  - `ComfyUIWorkflows/local/adaptable/uc-3d-04-image-to-scene-sf3d-asset-pack-v1.json`
- preset asociado principal:
  - `configs/comfyui/presets/uc-3d-04-image-to-scene-sf3d-asset-pack.yaml`

## Que se comprobo

Se verifico el estado real del entorno antes de vender una corrida de escena:

- presencia real del baseline `SF3D` en `ComfyUI`
- ausencia de acceso al modelo gated
- ausencia de artefactos previos de escenas `3D` generados por `SF3D`

## Lectura del bloqueo

Hoy no hay base honesta para afirmar:

- que la primera pieza o shell ya se genera con `SF3D`
- que un set de activos `UC-3D-04` ya se exporta en esta maquina
- que la salida ya se importa en `Blender`

## Lo que si queda hecho

- la estrategia de escena V1 ya esta modelada
- el workflow de referencia ya esta versionado dentro del repo
- el caso `UC-3D-04` ya existe en el catalogo y en presets

## Proximo paso real para desbloquearlo

1. autenticar o cachear `stabilityai/stable-fast-3d`
2. correr un primer `UC-3D-02` con un crop o una envolvente
3. repetir el flujo por pieza para `UC-3D-04`
4. importar activos y shell en `Blender`

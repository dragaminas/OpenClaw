# Workflow General de Objetos y Personajes 3D

Este documento implementa la tarea `9.9.1` del `DevPlan`.
Define la estrategia `V1` para `UC-3D-01` y `UC-3D-02` con `Stable Fast 3D`
como baseline del `MVP`.

## Objetivo

Cerrar una cadena `3D` util para activos aislados, priorizando:

- mesh importable en `Blender`
- rapidez de iteracion
- portabilidad del runtime
- sufiencia visual antes que perfeccion hero

## Casos cubiertos

### `UC-3D-01`

`texto -> objeto/personaje 3D`

Lectura `V1`:

- no se trata como `text-to-3D` nativo puro dentro del mismo grafo
- se trata como puente `texto -> imagen semilla -> SF3D`
- el workflow versionado deja preparada la etapa `SF3D` y asume que la imagen
  semilla puede venir de `UC-IMG-01` o de una imagen staged manualmente

### `UC-3D-02`

`imagen -> objeto/personaje 3D`

Lectura `V1`:

- es el primer cierre prioritario del `MVP`
- la ruta base es la extension oficial de `Stable Fast 3D` para `ComfyUI`
- el caso base es `single image -> glb`
- `Blender` absorbe cleanup, escala, pivot y empaquetado final

## Workflow `V1` por caso

| Caso | Workflow | Perfil | Objetivo |
| --- | --- | --- | --- |
| `UC-3D-01` | `uc-3d-01-text-to-asset-sf3d-bridge-v1.json` | `adaptable` | usar una imagen semilla staged antes del bloque `SF3D` |
| `UC-3D-02` | `uc-3d-02-image-to-asset-sf3d-single-image-v1.json` | `minimum` | baseline `single image -> asset 3D` portable y simple |

## Contrato funcional

Entradas minimas:

- `categoria_activo`
- una `imagen_referencia` o un `prompt` que desemboque en imagen semilla

Entradas opcionales:

- `escala_aproximada`
- `modo_texturizado`
- alpha o mascara si la imagen ya llega recortada

Salidas esperadas:

- `glb` principal
- preview `3D`
- metadata para handoff

## Limites explicitos de producto

- la `V1` no promete rigging listo
- la `V1` no promete topologia final de produccion
- la `V1` no promete que las zonas no visibles aguanten un uso hero
- la `V1` no sustituye el cleanup o el layout fino en `Blender`

Si devuelve:

- una malla cerrada o reparable
- orientacion corregible
- escala razonable
- importacion valida en `Blender`

entonces la cadena ya aporta valor.

## Relacion con `9.13`, `9.14` y `9.15`

- `9.13` define validacion atomica para `SF3D`, export e importacion
- `9.14` debe registrar si la ruta pasa, bloquea o requiere fallback
- `9.15` expone los mismos workflows desde catalogo, presets y WhatsApp

## Regla de cierre

`UC-3D-01` y `UC-3D-02` no deberian venderse como cerrados por existir el JSON.
Necesitan una corrida real con la extension oficial de `SF3D` y una
importacion comprobada en `Blender`.

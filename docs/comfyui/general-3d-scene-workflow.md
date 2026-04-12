# Workflow General de Escenas 3D

Este documento implementa la tarea `9.11.1` del `DevPlan`.
Define la estrategia V1 para `UC-3D-03` y `UC-3D-04`.

## Objetivo

Tratar la escena 3D como composicion progresiva y no como mesh monolitico
obligatorio.

## Casos cubiertos

### `UC-3D-03`

`texto -> set de activos o escena`

Lectura V1:

- puente `texto -> imagen de concepto -> SF3D` por pieza
- la salida valida es `asset_set`, `envolvente` o `blockout`

### `UC-3D-04`

`imagen -> set de activos o escena`

Lectura V1:

- descomponer la referencia visual
- devolver piezas separadas, shell o bloque base
- preferir reutilizacion en `Blender`

## Workflow V1 por caso

| Caso | Workflow | Perfil | Resultado esperado |
| --- | --- | --- | --- |
| `UC-3D-03` | `uc-3d-03-text-to-scene-sf3d-asset-pack-bridge-v1.json` | `adaptable` | imagen de concepto a primera pieza o shell util |
| `UC-3D-04` | `uc-3d-04-image-to-scene-sf3d-asset-pack-v1.json` | `adaptable` | scene crop a activo, envolvente o bloque base |

Nota operativa:

- ambos JSON son templates de una pieza
- la escena `V1` se resuelve ejecutando el bloque `SF3D` varias veces sobre
  crops, referencias parciales o envolventes
- la composicion final sigue viviendose en `Blender`

## Entregables validos de V1

Se consideran cierres validos:

- `asset_set`
- `envolvente`
- `blockout`
- composicion parcial util

No se considera requisito de cierre:

- escena monolitica final limpia

## Regla de ruteo

- si la referencia es en realidad un solo mueble o personaje, salir de esta
  linea y usar `UC-3D-02`
- si la referencia tiene varios elementos y la composicion importa, mantener
  `UC-3D-04`
- si la escena es demasiado ambiciosa, dividir por familias:
  - `envolvente`
  - `muebles/props`
  - `personajes`

## Relacion con Blender

La escena V1 se completa en `Blender`, no dentro del mismo grafo:

- importacion
- escala y orientacion
- ensamblado
- materiales
- layout fino

## Regla de cierre

`9.11` no deberia venderse como escena final hasta que haya evidencia real de
una corrida local y composicion revisada.

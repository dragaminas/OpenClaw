# Validacion Atomica y Compuesta para la Linea 3D

Este documento implementa la tarea `9.13` del `DevPlan`.
Define las pruebas necesarias para no confundir "workflow versionado" con
"cadena 3D operativa".

## Gate previo

Antes de cualquier corrida, debe pasar `PF-3D-01`.

### `PF-3D-01` preflight local

Debe comprobar:

- extension oficial `stable-fast-3d` instalada o ruta equivalente
- dependencias nativas alineadas (`numpy`, `gpytoolbox`, `pynanoinstantmeshes`)
- acceso al modelo `stabilityai/stable-fast-3d` por cache local o token valido
- una imagen fixture staged
- carpeta de salida escribible

Si este gate falla:

- la validacion termina como `blocked_missing_asset`
- no se vende como `fail_runtime`

## Casos atomicos

| ID | Caso | Pasa si |
| --- | --- | --- |
| `AT-3D-OBJ-01` | `UC-3D-02` shape-first desde imagen | deja mesh exportable y preview |
| `AT-3D-OBJ-02` | importacion en `Blender` del mesh de `AT-3D-OBJ-01` | se abre, rota y escala de forma controlable |
| `AT-3D-SCN-01` | `UC-3D-04` descomposicion por pieza | deja al menos un activo, shell o bloque base exportable |
| `AT-3D-SCN-02` | importacion en `Blender` del resultado de escena | las piezas o envolventes quedan distinguibles y composibles |

## Casos compuestos

| ID | Cadena | Objetivo |
| --- | --- | --- |
| `CP-3D-01` | `UC-3D-01` puente -> `UC-3D-02` -> `Blender` | validar la ruta texto -> activo reutilizable |
| `CP-3D-02` | `UC-3D-04` -> `Blender` -> composicion con activos | validar descomposicion y montaje |
| `CP-3D-03` | activo aislado + escena descompuesta | comprobar que ambas lineas hablan el mismo contrato |

## Evidencia minima

Cada corrida deberia conservar:

- `run_id`
- workflow usado
- preset usado
- imagen de entrada
- mesh o rutas devueltas
- preview o captura
- nota corta sobre escala, eje y pivot

## Estados canonicos

La linea 3D debe reutilizar los mismos estados del runner:

- `pass`
- `soft_pass_with_fallback`
- `fail_runtime`
- `fail_quality`
- `blocked_missing_asset`

## Regla de aprobacion

- `AT-3D-OBJ-01` y `AT-3D-OBJ-02` deben pasar para afirmar que la linea de
  objetos funciona de verdad
- `AT-3D-SCN-01` o `AT-3D-SCN-02` pueden aprobar como `soft_pass_with_fallback`
  si la salida real es `asset_set` o `blockout`

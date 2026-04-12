# Perfiles de Hardware para la Linea 3D

Este documento implementa la tarea `9.3` del `DevPlan`.
Fija los perfiles objetivo para la linea `3D` usando como referencia la maquina
local real y los stacks priorizados en `9.2`.

## Foto actual del entorno local

Estado auditado el `2026-04-12`:

- GPU local: `NVIDIA GeForce RTX 3060 12 GB`
- driver: `580.126.09`
- runtime de `ComfyUI`: `/home/eric/ComfyUI/.venv/bin/python`
- Python: `3.12.3`
- `torch`: `2.11.0+cu130`
- `numpy`: `2.4.4`

Lectura operativa:

- el `MVP` debe evitar dependencias ocultas de `pytorch3d`
- la maquina local pide una ruta simple `single image -> asset -> Blender`
- la extension oficial de `SF3D` encaja mejor con esta premisa que un stack
  3D mas ambicioso dentro de `ComfyUI`

## Perfiles canonicos

| Perfil | Hardware de referencia | Objetivo realista | Ruta preferida |
| --- | --- | --- | --- |
| `minimum` | `RTX 3060 12 GB` local | `asset` reparable desde una sola imagen, exportable a `glb` | extension oficial `Stable Fast 3D` |
| `medium` | `16 GB-20 GB VRAM` local o remota ligera | texturas algo mas altas, lotes pequenos y mas margen de cleanup | `SF3D` + `Blender` |
| `maximum` | `24 GB+ VRAM` local o remota | mas lote, mas textura y linea externa futura | `SF3D` en `ComfyUI` + futura linea oficial `Hunyuan3D` fuera de fase |

## Perfil `minimum`

Este es el baseline de producto para la `V1`.

Debe asumir:

- prioridad a `UC-3D-02`
- una sola imagen como caso base
- alpha o mascara cuando existan
- composicion posterior en `Blender`

Ruta recomendada:

- `UC-3D-02`: extension oficial `Stable Fast 3D`
- `UC-3D-01`: `texto -> imagen semilla -> SF3D`
- `UC-3D-03` y `UC-3D-04`: ejecutar `SF3D` por pieza, crop o envolvente
- usar `remesh=none` en la primera pasada para minimizar friccion

Bloqueos observados hoy en la maquina local:

- la extension oficial de `SF3D` requiere alinear dependencias con
  `numpy 1.26.x`
- `gpytoolbox` rompe con `numpy 2.x`
- `pynanoinstantmeshes` aun no esta presente en el runtime local
- el modelo `stabilityai/stable-fast-3d` es gated y hoy no hay token activo en
  el `venv`

No deberia exigirse en este perfil:

- escena monolitica limpia
- lotes largos
- calidad hero de zonas no visibles

## Perfil `medium`

Sirve para una maquina mejor que el baseline local o para una corrida remota
moderada.

Debe habilitar:

- lotes pequenos de activos
- texturas algo mas altas
- mas margen para shells o envolventes
- mas tiempo para cleanup en `Blender`

Ruta recomendada:

- `SF3D` oficial con configuracion mas alta
- repetir corridas por activo en lugar de forzar una escena unica
- usar `Blender` para agrupar, reparar y reutilizar

## Perfil `maximum`

Es el perfil de referencia para calidad alta o remota.

Debe reservarse para:

- lotes mayores de activos
- texturas mas altas
- validaciones largas o remotas
- futura linea oficial `Hunyuan3D` fuera del baseline `ComfyUI`

Regla:

- no convertir este perfil en requisito oculto de la `V1`
- si una demo necesita `24 GB+`, debe decirse explicitamente

## Mapa por caso de uso

| Caso | `minimum` | `medium` | `maximum` |
| --- | --- | --- | --- |
| `UC-3D-01` | puente `texto -> imagen -> SF3D` | idem con mejor imagen semilla | linea externa futura si el puente no basta |
| `UC-3D-02` | `SF3D` single-image | `SF3D` con mas textura y cleanup | `SF3D` mas lote o futura linea externa |
| `UC-3D-03` | puente a imagen de concepto y despues piezas `SF3D` | set de activos mas rico | escena mas ambiciosa fuera de la fase |
| `UC-3D-04` | descomposicion parcial o `blockout` con `SF3D` por pieza | set de activos mas rico | escena mas ambiciosa fuera de la fase |

## Regla de producto

La definicion correcta de `minimum` para esta linea no es "todo lo que pueda
hacer el ecosistema 3D", sino "lo minimo que puede correr de verdad sin romper
la promesa principal de activo reutilizable y composicion posterior en
`Blender`".

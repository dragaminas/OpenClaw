# Rutas Fallback para la Linea 3D

Este documento implementa la tarea `9.17` del `DevPlan`.
Define como degradar sin romper la promesa de producto.

## Principio

El fallback correcto no es "abandonar el 3D".
Es conservar valor de produccion con una entrega mas modesta.

## Tabla de decision

| Caso | Ruta primaria | Fallback correcto |
| --- | --- | --- |
| `UC-3D-01` | puente `texto -> imagen -> SF3D` | devolver imagen semilla y dejar lista la etapa `UC-3D-02` |
| `UC-3D-02` | `SF3D` single-image | pedir mejor crop o alpha, o registrar proxy suficiente |
| `UC-3D-03` | puente a imagen de concepto y luego `SF3D` por pieza | devolver `blockout` o lista de activos objetivo |
| `UC-3D-04` | `SF3D` por pieza o shell | dividir en activos por separado o generar solo `envolvente` |

## Fallbacks preferidos

Orden de degradacion:

1. quitar textura
2. simplificar el crop o aislar mejor la pieza
3. pasar de escena a `asset_set`
4. pasar de `asset_set` a `blockout`
5. dejar preparado el caso para perfil superior o linea externa futura

## Fallbacks que no deberian venderse como equivalentes

- una sola imagen si el usuario pidio un asset rotatorio fiable
- una escena fusionada si el objetivo era composicion por piezas
- un render bonito sin mesh util

## Mensajes de usuario

- "La ruta premium no cabe en esta maquina; puedo cerrar primero una pieza util."
- "Esta escena conviene dividirla en piezas antes de intentar un unico mesh."
- "Con una sola vista, este activo solo pasa como proxy."

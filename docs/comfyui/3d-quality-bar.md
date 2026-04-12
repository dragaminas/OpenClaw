# Barra de Calidad para la Linea 3D

Este documento implementa la tarea `9.10` del `DevPlan`.
Define el minimo aceptable para dar por util un activo o una escena proxy.

## Objetos y personajes

Para considerar util un `asset` en la `V1`, deberian cumplirse estos puntos:

- malla cerrada o reparable con limpieza ligera
- volumen legible al rotar la camara
- orientacion corregible sin ambiguedad grave
- escala aproximable con una unica correccion razonable
- pivot usable para composicion
- export `glb` o equivalente importable en `Blender`

No es requisito obligatorio de la `V1`:

- topologia final de produccion
- rig listo
- `PBR` final
- UV perfectas

## Escenas, envolventes y sets

Para `UC-3D-03` y `UC-3D-04`, la calidad minima no es una escena final limpia.
Es alguna de estas tres:

- `set` de activos reutilizable
- `envolvente` clara
- `blockout` navegable

## Tiempos objetivo de producto

Barra orientativa, no benchmark cerrado:

- `asset` shape-first en baseline local: razonable si cabe en una iteracion
  unica de validacion y no obliga a abandonar la maquina durante horas
- escena descompuesta: razonable si devuelve primero piezas utiles, aunque la
  limpieza posterior quede para `Blender`

## Criterio duro adicional

Si la cara no visible del activo queda tan rota que impide girarlo o reutilizarlo,
la salida no pasa como `asset` principal.

En ese caso:

- degradar a proxy
- pedir mas vistas
- usar variante multivista
- o registrar fallback

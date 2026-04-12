# Casos de Uso 3D de ComfyUI

Este documento implementa la tarea `9.1` del `DevPlan`.
Su objetivo es definir que queremos ofrecer en la linea `3D` desde una
perspectiva de producto, sin atarlo todavia a un stack o workflow concreto.

## Objetivo

Definir interfaces funcionales claras para generacion `3D` con `ComfyUI`,
priorizando `assets` reutilizables que despues puedan inspeccionarse,
corregirse y componerse en `Blender`.

La idea central no es obligarnos a generar escenas completas de una sola vez.
Para este proyecto puede aportar mas valor producir por separado objetos,
personajes y envolventes que luego montemos con control fino en `Blender`.

## Decision de producto

La linea `3D` debe modelarse con esta jerarquia de valor:

1. `asset` aislado reutilizable
2. `set` de activos coherente
3. `blockout` o layout navegable
4. escena compuesta en `Blender`
5. escena final monolitica generada de una sola vez

Eso implica:

- una escena compleja no tiene por que cerrarse como un unico mesh final
- si el sistema devuelve muebles, personajes y envolventes por separado, eso ya
  puede ser un resultado de alto valor
- `Blender` no es un parche posterior, sino parte explicita del producto para
  layout fino, materiales, ensamblado, limpieza y animacion
- el exito inicial se debe medir por reutilizacion y control, no solo por
  espectacularidad de una demo cerrada

## Tipos de entregable

| Tipo | Descripcion | Valor principal |
| --- | --- | --- |
| `asset` aislado | un objeto o personaje util por si mismo | reutilizacion |
| `set` de activos | varios assets coherentes listos para componer | velocidad de montaje |
| `envolvente` | shell espacial de habitacion, fachada, calle o terreno | contexto para montaje |
| `blockout` | escena navegable simplificada con volumenes y jerarquia | validar layout |
| `escena compuesta` | escena montada en `Blender` a partir de piezas | control fino |
| `escena monolitica` | escena generada como una sola salida cerrada | demo rapida o comparativa |

## Familias de activos

Las familias de activos prioritarias para este proyecto son:

- `mueble` o `prop`: silla, mesa, lampara, sofa, roca, arbol, farola, etc.
- `personaje`: personaje principal, figurante, criatura o maniqui proxy
- `envolvente`: habitacion, fachada, calle, terreno, jardin, plaza o shell de
  paisaje
- `decoracion`: cuadros, plantas, textiles, utensilios y objetos pequenos

## Escala de prioridad

- `P0`: desbloquea una cadena real `ComfyUI -> Blender -> composicion`
- `P1`: muy valioso, pero depende de que exista un camino `P0` estable
- `P2`: exploracion util o demo ambiciosa, pero no bloquea la primera version

## Catalogo de interfaces funcionales

| ID | Prioridad | Interfaz funcional | Resultado buscado | Entregable preferido |
| --- | --- | --- | --- | --- |
| `UC-3D-01` | `P1` | `texto -> objeto/personaje 3D` | crear un `asset` nuevo sin imagen base | `asset` aislado |
| `UC-3D-02` | `P0` | `imagen -> objeto/personaje 3D` | convertir una referencia visual en un `asset` util | `asset` aislado |
| `UC-3D-03` | `P2` | `texto -> set de activos o escena` | producir una base espacial o un lote de activos desde una descripcion | `set` de activos o `blockout` |
| `UC-3D-04` | `P0` | `imagen -> set de activos o escena` | extraer o reconstruir una escena a partir de referencias visuales | `set` de activos, `envolvente` o `blockout` |

## Priorizacion operativa real

### `P0` inmediato

- `UC-3D-02` para generar objetos, props y personajes desde una imagen
- `UC-3D-04` cuando la imagen permita separar la escena en `envolvente` y
  activos independientes
- importacion estable de esos resultados en `Blender`

### `P1` despues del primer cierre

- `UC-3D-01` como via de ideacion de personajes y props desde texto
- variantes mas limpias de texturizado, escalado y catalogacion
- lotes pequenos de activos coherentes para interiorismo o paisajismo

### `P2` para exploracion controlada

- `UC-3D-03` como escena o set nacido desde texto
- escenas monoliticas completas
- flujos donde la escena cerrada se use solo como comparativa frente a la
  estrategia de composicion por `assets`

## Escenarios operativos prioritarios

| Escenario | Prioridad | Cadena preferida | Motivo |
| --- | --- | --- | --- |
| foto de un mueble -> mueble 3D | `P0` | `UC-3D-02 -> Blender` | caso simple, util y facil de evaluar |
| concept art o render de personaje -> personaje 3D | `P0` | `UC-3D-02 -> Blender` | desbloquea casting y animacion |
| referencia de interior -> envolvente + muebles separados | `P0` | `UC-3D-04 -> Blender` | maximiza control de layout |
| referencia de exterior o paisaje -> shell + rocas/arboles/props | `P1` | `UC-3D-04 -> Blender` | evita perseguir una escena cerrada demasiado pronto |
| texto -> prop o personaje hero | `P1` | `UC-3D-01 -> Blender` | valioso para ideacion, pero no tan barato como imagen -> 3D |
| texto -> escena completa | `P2` | `UC-3D-03` | demo interesante, peor encaje como primera entrega |

## Interfaces funcionales en detalle

## `UC-3D-01` `texto -> objeto/personaje 3D`

- Problema:
  necesitamos crear un `asset` 3D nuevo desde una descripcion textual, aun si
  no existe imagen base.
- Entradas minimas:
  - `prompt`
  - `categoria_activo`
- Entradas opcionales:
  - `referencias_estilo`
  - `escala_aproximada`
  - `materialidad_objetivo`
  - `topologia_objetivo`
- Salidas preferidas:
  - `asset` 3D exportable
  - preview del mesh
  - metadatos de ejecucion suficientes para iterar
- Criterio de producto:
  - la `V1` no necesita producir un personaje final listo para rig
  - si devuelve un proxy o un `asset` reparable que podamos llevar a `Blender`,
    ya es util

## `UC-3D-02` `imagen -> objeto/personaje 3D`

- Problema:
  necesitamos convertir una imagen o render en un `asset` 3D utilizable.
- Entradas minimas:
  - `imagen_referencia`
  - `categoria_activo`
- Entradas opcionales:
  - `alpha_o_mascara`
  - `imagenes_adicionales`
  - `escala_aproximada`
  - `modo_texturizado`
- Salidas preferidas:
  - mesh exportable con textura o con color suficiente para revision
  - pivote coherente
  - orientacion util para importacion en `Blender`
- Criterio de producto:
  - este es el primer caso que deberia cerrarse de verdad en el baseline local

## `UC-3D-03` `texto -> set de activos o escena`

- Problema:
  necesitamos pasar de una descripcion textual a una base espacial que podamos
  seguir refinando.
- Entradas minimas:
  - `prompt`
  - `tipo_escena`
- Entradas opcionales:
  - `lista_de_activos`
  - `estilo_visual`
  - `escala_espacial`
- Salidas preferidas:
  - `set` de activos
  - `blockout`
  - `envolvente`
- Salidas aceptables en `V1`:
  - escena proxy
  - lote parcial de activos con jerarquia util
- Criterio de producto:
  - no exigir escena final monolitica para cerrar la primera version

## `UC-3D-04` `imagen -> set de activos o escena`

- Problema:
  necesitamos traducir una referencia visual de interiorismo o paisajismo a un
  conjunto de piezas controlables.
- Entradas minimas:
  - `imagen_referencia`
  - `tipo_escena`
- Entradas opcionales:
  - `mascara_por_region`
  - `familias_objetivo`
  - `escala_espacial`
  - `nivel_de_descomposicion`
- Salidas preferidas:
  - `envolvente` separada
  - varios muebles o props independientes
  - personajes o proxies independientes si existen en la imagen
- Criterio de producto:
  - si el sistema logra separar la escena en partes reutilizables y
    composibles, eso vale mas que un mesh final poco editable

## Parametros canonicos transversales

- `prompt`
- `imagen_referencia`
- `imagenes_adicionales`
- `categoria_activo`
- `tipo_escena`
- `alpha_o_mascara`
- `escala_aproximada`
- `pivot_objetivo`
- `orientacion_objetivo`
- `materialidad_objetivo`
- `topologia_objetivo`
- `modo_texturizado`
- `perfil_hardware`
- `salida_objetivo`

## Reglas de modelado

- no modelar la escena completa como unica unidad cuando una descomposicion por
  activos ofrece mas control
- no tratar `Blender` como postproceso accidental; es parte del caso de uso
- la capa conversacional debe pedir primero si la persona quiere un `asset`,
  un `set`, una `envolvente` o una escena proxy
- cuando la referencia visual mezcle muchos elementos, el sistema deberia poder
  proponer `descomponer antes de generar`
- si el stack local no alcanza para una escena completa, el fallback correcto
  es devolver piezas utiles, no fallar sin mas

## Hipotesis de producto resultante

La mejor primera apuesta para esta linea `3D` no es "generar escenas completas
mejores que `Blender`", sino "generar en `ComfyUI` piezas suficientemente
buenas para componer escenas mejores en `Blender`".

Eso es especialmente cierto para:

- interiorismo
- paisajismo
- escenas con personajes
- escenas donde la direccion artistica o el layout importan mucho

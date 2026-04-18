# Composicion de Escenas 3D sobre la Linea Nativa `Hunyuan3D`

Este documento implementa la tarea `10.11` del `DevPlan`.
Replantea `UC-3D-03` y `UC-3D-04` como composicion por activos, `blockout`
o envolventes generados con `Hunyuan3D` nativo, evitando vender escena
monolitica donde no la hay.

## Principio

La escena 3D V1 en la linea nativa sigue siendo composicion, no mesh unico.

Esto no es una limitacion temporal a superar.
Es la decision de producto correcta para este baseline:

- escenas complejas generadas de golpe producen mallas inconsistentes
- la composicion en `Blender` da mas control al operador y al equipo creativo
- el valor real esta en los activos reutilizables, no en la escena fusionada

## Casos cubiertos

### `UC-3D-03` — `texto -> set o blockout`

Ruta V1 sobre la linea nativa:

```text
prompt
  -> ComfyUI genera imagen de concepto de la escena
  -> el operador o el sistema decide que piezas se pueden aislar
  -> cada pieza se genera con Hunyuan3D-2mini-Turbo
  -> un glb por pieza
  -> Blender recibe los activos y compone
```

Entrega valida:

- `asset_set` de dos o mas activos aislados
- `envolvente` del espacio (suelo, paredes, techo como bloque base)
- `blockout` navegable

No es entrega valida:

- una sola imagen del concepto
- una escena fusionada en un unico mesh si no se puede rotar ni descomponer

### `UC-3D-04` — `imagen -> set o blockout`

Ruta V1 sobre la linea nativa:

```text
imagen de referencia (interior, exterior, paisaje)
  -> el operador recorta o aisla los elementos principales
  -> cada recorte entra a Hunyuan3D-2mini-Turbo
  -> un glb por pieza
  -> Blender ensambla el set
```

Entrega valida: igual que `UC-3D-03`.

## Flujo recomendado para el operador

1. Identificar entre dos y cinco piezas clave de la escena
2. Aislar o recortar cada pieza como imagen separada
3. Lanzar `UC-3D-02` con cada recorte (reutilizar el mismo motor)
4. Revisar cada `glb` en `Blender`
5. Componer, ajustar escala y positar en una escena `Blender`

**Familias de activos tipicos por tipo de escena:**

| Tipo de escena | Familias sugeridas |
| --- | --- |
| `interior` | envolvente, muebles, props decorativos, personaje |
| `exterior` | envolvente arquitectonica, vegetacion, props, personaje |
| `paisaje` | envolvente natural, arboles, rocas, figura humana o animal |

## Estrategia de la envolvente

La envolvente es el activo mas util para asentar una escena.
Debe generarse primero, antes que los muebles o personajes.

Para interiorisimo: recortar un angulo limpio de la sala sin objetos.
Para exteriores: usar la arquitectura o el horizonte como referencia.

Si la envolvente no sale viable con `Hunyuan3D` desde una sola vista,
opciones:

1. construirla directamente en `Blender` con primitivas
2. usar una imagen menos ambiciosa de un plano unico

## Estado de la validacion

- estado: `pending_runtime`
- bloqueado por: instalacion de `Hunyuan3D` pendiente (`10.10` debe pasar primero)

Cuando `10.10` este listo, esta tarea de composicion puede avanzar con:

1. ejecutar `UC-3D-02` dos o tres veces con recortes de una misma imagen de referencia
2. importar cada `glb` en `Blender`
3. componer una escena muy basica: envolvente + un mueble o prop
4. documentar el resultado como evidencia de `UC-3D-04` real

## Criterios de cierre para `UC-3D-03` y `UC-3D-04`

Se considera cierre valido de V1 si se da alguna de estas condiciones:

- dos o mas activos generados con `Hunyuan3D` y compuestos en `Blender`
- una envolvente funcional mas un objeto o personaje en la misma escena
- un `blockout` de tres piezas con escala y orientacion coherente

No se considera cierre valido:

- una imagen de concepto sin `glb`
- un unico activo sin composicion de contexto
- una escena fusionada que no se puede descomponer

## Placeholder para resultados

| Corrida | Input | Activos generados | Composicion Blender | Estado |
| --- | --- | --- | --- | --- |
| `UC-3D-03 V1` | prompt de escena | — | — | `pending_runtime` |
| `UC-3D-04 V1` | imagen de interior | — | — | `pending_runtime` |

## Relacion con otros documentos

- mapa de casos de uso: `docs/hunyuan3d/usecase-map.md`
- contrato de I/O: `docs/hunyuan3d/io-contract.md`
- validacion de objetos: `docs/hunyuan3d/validation-results.md`
- fallbacks: `docs/hunyuan3d/fallback-paths.md`

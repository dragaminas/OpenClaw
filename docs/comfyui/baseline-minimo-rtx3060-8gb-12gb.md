# Baseline Minimo RTX 3060 8 GB-12 GB

Este documento implementa la tarea `8.4` del `DevPlan`.
Fija el baseline operativo del producto para `ComfyUI` en hardware local
equivalente a `RTX 3060 8 GB-12 GB`, sin asumir que siempre tendremos la
variante mas comoda de `12 GB`.

## Referencia actual de trabajo

Equipo disponible hoy:

- `RTX 3060 12 GB`
- `62 GiB RAM`
- `Ryzen 5 5600X`

Esta maquina sirve para perfilar el baseline, pero no para inflarlo. Las
decisiones de producto deben seguir siendo validas tambien para `RTX 3060 8 GB`
si hace falta bajar resolucion, lote o longitud.

## Regla de baseline

La regla operativa es:

- el producto se diseña primero para que el flujo no se rompa en `minimum`
- la calidad se degrada de forma controlada antes de declarar que un flujo no
  es viable
- si un workflow base solo existe en forma pesada, se conserva como referencia,
  no como variante primaria

## Presets base

### Imagen fija

| Preset | Uso | Resolucion sugerida | Batch | Notas |
| --- | --- | --- | --- | --- |
| `preview` | look-dev rapido, validacion de prompt | `768 x 768` o `896 x 512` | `1` | primera opcion para `UC-IMG-02` |
| `standard` | frame final corto o aprobacion interna | `1024` en lado largo si el resto del flujo es ligero | `1` | preferible en `12 GB`, no asumirlo en `8 GB` |
| `high` | reservado para `medium` o `maximum` | no baseline | `1` | no debe bloquear la UX principal |

### Preprocess de video

| Parametro | Baseline recomendado |
| --- | --- |
| FPS de control | `24` |
| resolucion de control | `512` en lado largo o `512 x 512` |
| frame load cap por pasada | `24-49` frames |
| controles activos por defecto | `outline` y `pose`; `depth` solo si el modelo esta disponible |
| salidas persistentes | si, guardar `lineart/depth/openpose` como paquete reutilizable |

### Render de video

| Preset | Resolucion objetivo | Longitud por segmento | Referencias | LoRAs |
| --- | --- | --- | --- | --- |
| `preview_segmented` | `512 x 512` a `640 x 640` | `24-49` frames | `1-2` | `0-1` |
| `standard_segmented` | `640 x 640` | `49` frames | `2-3` | `1-2` |
| `full_shot` | no baseline | no baseline | no baseline | no baseline |

## Degradaciones normales del sistema

Estas degradaciones no cuentan como fallo. Son comportamiento esperado del
baseline:

- bajar resolucion antes de bajar demasiados pasos de muestreo
- fragmentar el plano antes de intentar un render largo de una sola vez
- reducir cantidad de referencias cargadas a la vez
- desactivar controles opcionales no esenciales
- dejar `depth` fuera si el modelo de profundidad no esta disponible
- pasar de `AI Renderer` completo a `preprocess + revision` si falta un modelo
  grande
- usar templates o rutas fallback si aun no hay derivacion nativa del flujo

## Diferencia practica entre 8 GB y 12 GB

### `RTX 3060 8 GB`

- asumir `preview` como preset por defecto
- preferir imagen fija o clips muy cortos
- no forzar `depth + pose + outline` a la vez si no hace falta
- tratar el render de video largo como segmentado desde el inicio

### `RTX 3060 12 GB`

- permite usar `standard` con mas frecuencia
- da mas margen a dos referencias y a segmentos algo mas largos
- sigue sin convertir `maximum` en baseline

## Limites a respetar

- no diseñar presets que dependan de `24 GB` para el flujo principal
- no asumir disponibilidad de todos los modelos Wan grandes en el baseline
- no mezclar un workflow "abre en ComfyUI" con un workflow "corre hoy en local"

## Preset operativo inicial por caso de uso

| Caso | Preset inicial | Motivo |
| --- | --- | --- |
| `UC-IMG-02` | `preview` | es la entrada mas directa para tener un resultado visible pronto |
| `UC-VID-01` | `control_package_512` | produce materiales reutilizables con coste contenido |
| `UC-VID-02` | `preview_segmented` | evita que el plano completo bloquee el baseline |
| `UC-IMG-01` | `text_to_image_reference` | nace desde template, no desde workflow pesado |
| `UC-VID-03` | `template_reference_only` | aun no hay derivacion nativa baseline |
| `UC-VID-04` | `upscale_reference_only` | ruta futura, no baseline actual |

## Consecuencia para tareas siguientes

- `8.5` y `8.6` deben juzgar los workflows segun este baseline
- `8.10` debe tratar el fallback como parte normal del sistema
- `8.14` debe exponer mensajes compatibles con estas degradaciones
- `8.15` debe validar primero `preview` y `preview_segmented`

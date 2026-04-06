# Workflow General de Renderizacion de Video

Este documento implementa la tarea `8.21` del `DevPlan`.
Define el objetivo de producto, el contrato funcional y el plan de derivacion
para un workflow general de renderizacion de video en `ComfyUI`, ajustado al
hardware local y verificable en este sistema.

## Objetivo

Construir un workflow general que convierta un video base en una secuencia
renderizada con look final, reutilizando primero los workflows ya derivados en
este repo y completando solo lo que falte con templates locales de `ComfyUI` o,
si no existiera una referencia local suficiente, con ejemplos externos.

La idea correcta no es crear un grafo completamente ajeno a lo que ya existe.
La idea correcta es componer y estabilizar una cadena de producto a partir de:

- `UC-VID-01` para preprocess de controles
- `UC-VID-02` para render principal
- `UC-VID-04` para mejora final

## Resultado esperado

El workflow debe producir:

- un video renderizado a partir del video base
- una ruta clara de inspeccion del primer frame
- una configuracion reproducible para este hardware
- una evidencia local real de que corre en esta maquina

## Contrato funcional

## Parametros obligatorios

- `video_base`
- `prompt_escena_estilo`
- `controles_activos`

`controles_activos` no significa que los tres controles deban estar siempre
encendidos.
Significa que el usuario debe elegir una combinacion valida de `1` a `3`
controles entre:

- `bordes`
- `pose`
- `profundidad`

Forma equivalente de modelarlo en UI o en el JSON del workflow:

- `usar_bordes`
- `usar_pose`
- `usar_profundidad`

Regla canonica:

- al menos uno de esos tres flags debe estar en `true`
- el workflow debe aceptar cualquier combinacion valida de `1`, `2` o `3`
  controles activos

## Parametros opcionales

- `video_coloreado_por_personaje`
- `mapa_color_a_personaje`
- `referencias_personaje_por_color`
- `referencias_estilo`
- `duracion_objetivo`
- `resolucion_objetivo`
- `segmentar_clip_largo`
- `fps_objetivo`
- `modo_fps`

## Comportamiento obligatorio

El workflow general debe:

- cargar un video base como entrada principal
- permitir activar o desactivar bordes, pose y profundidad como fuentes de control
- aceptar un prompt que describa escena y estilo visual
- mostrar el frame inicial en un nodo claramente visible para validacion humana
- inferir y conservar automaticamente el aspect ratio del video de entrada
- escoger una resolucion adecuada al hardware local cuando el usuario no fije una
- dividir clips largos en subsecciones iterables cuando la duracion o el coste lo exijan
- aplicar una mejora posterior del video hasta `Full HD` cuando el clip base y el runtime lo permitan
- dejar abierta una etapa opcional de aumento de FPS para clips tipo stopmotion,
  colocada despues del render principal y antes del upscale final
- publicar una secuencia renderizada final y una evidencia estable de la corrida

## Comportamiento opcional deseado

El workflow general deberia ademas:

- aceptar un video base donde los personajes vengan codificados por color
- permitir asociar referencias de personaje a cada color
- usar esa asociacion para reforzar identidad visual de personajes a lo largo del plano

Esta parte es valiosa, pero no debe bloquear una primera version util del
workflow general.

## Lectura correcta del alcance

La primera version no necesita resolver todo a la vez.
El orden correcto es:

1. conseguir una version general que corra bien con video base, prompt y controles on/off
2. añadir despues el etiquetado por color y las referencias por personaje
3. estabilizar luego el troceado de clips largos
4. introducir, si aporta valor, una etapa opcional de aumento de FPS despues del
   render principal
5. cerrar por ultimo la mejora final hasta `Full HD`

## Base tecnica a reutilizar

## `UC-VID-01`

Rol dentro del workflow general:

- leer el video base
- extraer `lineart`
- extraer `pose`
- extraer `depth`
- persistir el paquete de controles para reutilizacion aguas abajo

Es la base natural para el bloque de controles activables.

## `UC-VID-02`

Rol dentro del workflow general:

- tomar el video base
- combinar prompt y referencias
- consumir controles cuando esten activos
- producir el render principal del plano

Es la base natural para el nucleo del workflow general.

## `UC-VID-04`

Rol dentro del workflow general:

- tomar el render principal
- mejorarlo o escalarlo
- publicar una salida mas final

Es la base natural para el bloque de mejora final.

## Orden de preferencia para completar huecos

Si falta alguna pieza, el orden de preferencia debe ser:

1. reutilizar workflows derivados ya presentes en `ComfyUIWorkflows/local/`
2. reutilizar templates locales de `ComfyUI`
3. buscar referencias externas

No deberiamos empezar buscando fuera si el repo ya tiene un bloque utilizable.

## Arquitectura recomendada del workflow

## Bloque 1: Entrada e inspeccion

Debe incluir como minimo:

- carga del video base
- extraccion del primer frame
- preview visible del primer frame
- inferencia de `fps`, `frame_count`, `width` y `height`
- calculo del aspect ratio

Objetivo:

- confirmar rapido si el material de entrada es util
- evitar ejecutar todo el pipeline sobre un clip mal elegido

## Bloque 2: Preprocess de controles

Debe partir de `UC-VID-01` y permitir:

- `bordes` on/off
- `pose` on/off
- `profundidad` on/off

Lectura correcta:

- no hace falta usar siempre los tres
- el workflow debe poder correr con cualquier combinacion valida de `1` a `3`
  controles activos
- el caso invalido es `0` controles activos

Salida esperada:

- un paquete persistente de controles con nombres y rutas estables

Regla:

- si un control esta apagado, el workflow no debe fallar; debe degradar de
  forma controlada y seguir con los controles restantes

## Bloque 3: Render principal

Debe partir de `UC-VID-02` y recibir:

- video base o subseccion actual
- prompt
- referencias opcionales
- controles activos

El render principal debe ser la primera salida usable del sistema.
No hace falta que la primera version sea la maxima calidad posible.
Hace falta que sea reproducible y compatible con esta maquina.

## Bloque 4: Segmentacion de clips largos

No todo clip debe trocearse.
La segmentacion solo deberia activarse cuando:

- el clip excede una duracion razonable para este hardware
- el coste de VRAM o de tiempo hace poco realista una corrida unica

Primera regla operativa sugerida:

- si el clip supera `5-8` segundos en el baseline actual, permitir o forzar
  subdivision por bloques

La segmentacion debe:

- conservar orden temporal
- permitir recomposicion estable
- dejar evidencia de cada subseccion

## Bloque 5: Mejora final

Debe partir de `UC-VID-04` o de un template local equivalente de upscale.

Objetivo:

- llevar el render principal a una salida mas final, idealmente `1920x1080`
- no disparar la VRAM mas alla de lo sostenible en la primera version

Regla de producto:

- si el upscale a `Full HD` no es viable en una sola pasada, se acepta una
  primera version que publique el render base y deje el upscale como paso
  posterior bien definido

## Bloque 5.5: Interpolacion opcional de FPS

Este bloque ya existe de forma opcional en la derivacion funcional actual, pero
todavia no deberia considerarse la version final de producto para stopmotion.

Regla:

- si existe, debe ir despues del render principal y antes del upscale final

Motivo:

- evita multiplicar el coste del render principal
- conserva el timing creativo del clip base durante la parte mas cara del
  pipeline
- permite comparar facilmente `render base` frente a `render con FPS aumentado`

Parametros actuales:

- `usar_interpolacion_fps`
- `fps_objetivo`

Comportamiento actual:

- si `usar_interpolacion_fps=false`, la rama devuelve los frames originales
- si `fps_objetivo` coincide con el `fps` base, la rama no hace nada
- si `fps_objetivo` es menor o igual que el `fps` base, la rama no hace nada
- si `fps_objetivo` es mayor, calcula un numero objetivo de frames para
  conservar duracion y genera los intermedios por mezcla temporal lineal
- para ratios no multiplos exactos, no intenta repartir un numero entero fijo
  de frames por hueco; remuestrea la secuencia completa al conteo objetivo
  usando una interpolacion temporal continua

Lectura correcta:

- esta primera implementacion sirve para experimentar desde la UI y para clips
  donde un aumento de FPS suave ya aporta valor
- una variante futura tipo `Wan 2.2` por pares de frames sigue siendo deseable
  para stopmotion exigente, pero no bloquea esta fase funcional

## V1 y V2

## V1 obligatoria

La primera derivacion que deberia considerarse valida para esta tarea es:

- video base
- prompt
- preview del primer frame
- aspect ratio preservado
- controles `bordes`, `pose` y `profundidad` con on/off, aceptando cualquier
  combinacion valida de `1` a `3` activos
- render principal local
- evidencia real con `blenderTest.mp4`

## V2 deseable

La segunda iteracion deberia añadir:

- referencias por personaje segun color
- segmentacion automatica de clips largos
- una variante mas avanzada de interpolacion FPS para stopmotion, idealmente
  apoyada en una ruta generativa tipo `Wan 2.2`
- mejora final a `Full HD`

## Decisiones de producto

## Aspect ratio

Debe preservarse siempre por defecto.
No deberiamos recortar o forzar `16:9` si el video base no lo es.

## Resolucion

La resolucion no deberia ser un parametro libre sin control.
En este stack conviene:

- inferir la resolucion del clip de entrada
- degradar a una resolucion segura para `RTX 3060`
- mantener `batch=1`

La subida a `Full HD` deberia quedar para el bloque de mejora final.
Si se añade interpolacion de FPS, deberia vivir antes de ese upscale final.

## Identidad de personajes por color

Este mecanismo debe tratarse como una capa adicional, no como requisito para
que el workflow general exista.

La primera pregunta es:

- puede el workflow general renderizar bien un plano base usando prompt,
  controles y referencias normales

La segunda pregunta, posterior, es:

- puede usar colores del video como anclas para asociar personajes concretos

## Rutas y convenciones

La implementacion deberia seguir las convenciones ya existentes en:

- `docs/comfyui/blender-bridge.md`
- `docs/comfyui/e2e-validation.md`
- `docs/comfyui/workflow-smoke-validation.md`

La derivacion local deberia vivir en `ComfyUIWorkflows/local/`.
No deberiamos modificar el workflow base original.

## Propuesta de artefactos

La tarea deberia dejar, como minimo:

- un workflow derivado general en `ComfyUIWorkflows/local/`
- una variante visible en la biblioteca `openclaw-workflows`
- un preset operativo asociado en `configs/comfyui/presets/`
- una evidencia de corrida real con `blenderTest.mp4`

Nombres sugeridos:

- workflow derivado:
  `ComfyUIWorkflows/local/minimum/uc-vid-02-general-video-render-rtx3060-v1.json`
- documento de resultados:
  `docs/comfyui/general-video-render-workflow-results.md`

## Plan de desarrollo recomendado

## Paso 1

Congelar el caso base con `blenderTest.mp4` y definir el `shot_id`
`blender-test` como fixture canonico de `8.15`.

## Paso 2

Derivar una primera version del workflow general reutilizando:

- preprocess de `UC-VID-01`
- render principal de `UC-VID-02`

Sin referencias por color todavia.

## Paso 3

Exponer switches claros para:

- `usar_bordes`
- `usar_pose`
- `usar_profundidad`

## Paso 4

Añadir el bloque de preview del primer frame y fijar la inferencia de aspect
ratio y resolucion segura.

## Paso 5

Correr una prueba real local con `blenderTest.mp4`.

## Paso 6

Solo despues de que la version base corra:

- añadir referencias por personaje asociadas a color
- estudiar troceado automatico de clips largos
- decidir si se integra interpolacion opcional de FPS para stopmotion
- conectar mejora final a `Full HD`

## Verificacion minima obligatoria

La tarea no deberia cerrarse solo con el JSON.
Debe demostrar corrida real en este sistema.

Verificacion minima esperada:

- `ComfyUI` activo y con los nodos requeridos cargados
- workflow derivado visible en la biblioteca local
- carga correcta de `blenderTest.mp4`
- preview correcta del primer frame
- al menos una corrida real con salida de video publicada
- evidencia local revisable

## Fixture base de validacion

Para esta tarea, el clip base es:

- `blenderTest.mp4`

Ruta canonicamente staged para `8.15`:

- `~/Studio/Validation/comfyui/e2e/blender-test/fixtures/blender-test__base__v001.mp4`

Script ya previsto para prepararlo:

```bash
scripts/apps/comfyui-stage-e2e-fixture.sh
```

## Regla de publicacion en UI

La biblioteca `openclaw-workflows` debe publicar aqui el workflow funcional,
no el de validacion rapida.

- `render-video` debe abrir la variante operativa para uso real desde la UI
- la variante operativa debe nacer con `frame_load_cap=0`
- la variante operativa debe heredar el `fps` del video base
- la variante operativa puede seguir usando una resolucion conservadora para
  `RTX 3060`, pero no debe truncar el clip por defecto
- cualquier ruta rapida de comprobacion debe quedarse fuera de la UI funcional
  y llevar explicitamente el apellido `validation`

## Comandos de verificacion esperados

La implementacion final de esta tarea deberia dejar documentados y ejecutados,
como minimo, comandos del estilo:

```bash
scripts/apps/comfyui-stage-e2e-fixture.sh
scripts/apps/comfyui.sh status
scripts/actions/comfyui-action.sh open-workflow render-video
scripts/openclaw/test-studio-actions-plugin.sh "studio comfyui abre workflow render-video"
scripts/apps/comfyui-general-video-v1-validation.sh --controls bordes,pose,profundidad
```

Y, cuando el runner operativo exista para esta ruta:

```bash
scripts/actions/runner-action.sh start comfyui operate <target_id>
scripts/actions/runner-action.sh status comfyui <run_id>
scripts/actions/runner-action.sh result comfyui <run_id>
```

## Relacion con otras tareas

## Relacion con `8.15`

Esta tarea es una forma concreta de cerrar de verdad la parte de video corto de
`8.15`, usando `blenderTest.mp4` como fixture estable y dejando una cadena
local reproducible.

## Relacion con `8.18`

La validacion atomica y compuesta de `8.18` deberia apoyarse despues en este
workflow general ya estabilizado, no en un conjunto difuso de grafos sin
criterio de producto.

## Relacion con `8.20`

La capa de WhatsApp y la interfaz `runner` ya quedaron preparadas.
Cuando este workflow general exista de verdad, deberia poder:

- abrirse visualmente desde WhatsApp
- explicarse desde WhatsApp
- compararse contra otros workflows
- ejecutarse por la misma infraestructura de `runner`

## Criterio de cierre real

`8.21` solo deberia considerarse cerrada cuando existan:

- una especificacion canonica de este workflow general
- una derivacion local versionada en `ComfyUIWorkflows/local/`
- una corrida real sobre `blenderTest.mp4`
- una salida publicada y revisable
- evidencia suficiente para decidir que partes ya son producto y cuales siguen
  pendientes

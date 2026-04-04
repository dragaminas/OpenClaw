# Validacion Atomica y Compuesta de Workflows via WhatsApp

Este documento implementa la tarea `8.17` del `DevPlan`.
Define el diseno de la validacion para los workflows derivados de
`ComfyUIWorkflows/local/` sin mezclar todavia el diseno con la ejecucion real,
que queda reservada para `8.18`.

## Como leer este documento

Este archivo es una especificacion de pruebas, no un runner ya operativo.

En otras palabras:

- `8.17` define que pruebas hay que correr
- `8.17` no implementa todavia los comandos finales para ejecutarlas
- la ejecucion real, la evidencia y los resultados quedan para `8.18`

Si lo que buscas es un comando unico tipo `make test` para `AT-IMG-02-01`,
`AT-VID-01-01` o `CP-VIDEO-01`, hoy todavia no existe en el repo.

Si hace falta un gate mas barato para comprobar primero que los workflows
simplemente corren, esa funcion queda ahora reservada para `8.19` en
`docs/comfyui/workflow-smoke-validation.md`.

## Que puedes correr hoy y que no

Hoy si puedes correr:

- comprobaciones de servicio de `ComfyUI`
- el puente local seguro ya existente para acciones basicas de `ComfyUI`
- la CLI guiada de `openclaw_studio` para explorar sesiones e inputs

Hoy no puedes correr todavia:

- `AT-IMG-02-01`
- `AT-VID-01-01`
- `AT-VID-02-01`
- `AT-IMG-03-01`
- `AT-VID-03-01`
- `AT-VID-04-01`
- `CP-STILL-01`
- `CP-VIDEO-01`
- `CP-MOTION-01`

como comandos automatizados ya cerrados dentro del repo.

## Comandos reales disponibles hoy

Para verificar que la base operativa esta viva, hoy los comandos utiles son:

```bash
scripts/apps/comfyui.sh status
scripts/apps/comfyui.sh start-service
scripts/apps/comfyui.sh restart-service
scripts/apps/comfyui.sh open-ui
```

Para probar el puente local compatible con WhatsApp, hoy puedes usar:

```bash
scripts/openclaw/test-studio-actions-plugin.sh "studio como esta comfyui"
scripts/openclaw/test-studio-actions-plugin.sh "studio inicia comfyui"
scripts/openclaw/test-studio-actions-plugin.sh "studio reinicia comfyui"
scripts/openclaw/test-studio-actions-plugin.sh "studio abre comfyui"
```

Para explorar la sesion guiada actual, hoy puedes usar:

```bash
PYTHONPATH=src python -m openclaw_studio
```

Esa CLI sirve para recorrer la sesion e introducir inputs, pero no ejecuta
todavia la suite `AT-*` o `CP-*`.

## Que faltara en `8.18`

La tarea `8.18` deberia anadir, como minimo:

- un comando o accion segura que reciba `test_id`, `preset_id` y `shot`
- la ejecucion real del workflow correspondiente
- la publicacion de artefactos en `published/`
- manifiestos, logs y evidencia
- el registro de resultados en
  `docs/comfyui/atomic-composed-whatsapp-validation-results.md`

Hasta que eso exista, este documento debe leerse como contrato de validacion y
no como manual final de ejecucion.

## Dependencia operativa para WhatsApp

Si queremos que `8.18` sea disparable por la persona usuaria desde la UI actual
de WhatsApp, antes hace falta `8.20`.

`8.20` no deberia crear otra implementacion distinta de la validacion, sino
extender el mismo runner y la misma evidencia de `8.19` para exponerlos por
chat.

## Objetivo

Definir una bateria de pruebas E2E lo mas simple pero suficiente posible para:

- validar cada workflow derivado de forma aislada
- validar la composicion entre workflows cuando un output alimenta al siguiente
- priorizar el baseline `minimum`
- dejar una interfaz ideal disparable desde WhatsApp
- conservar una ruta transitoria mientras la sesion guiada todavia no esta
  integrada de forma nativa en ese canal

## Principios

- una prueba atomica valida un solo workflow con fixtures estables
- una prueba compuesta valida la cadena entre workflows usando artefactos
  publicados por pruebas anteriores
- las pruebas deben usar el menor numero de inputs que aun permita detectar si
  el flujo sirve de verdad
- la validacion minima no debe depender de Blender
- el baseline `minimum` manda; las referencias `maximum` no bloquean el cierre
- si hace falta fallback, debe quedar registrado como fallback y no como pase
  limpio
- una prueba no cuenta como aprobada si exige abrir el grafo y corregir nodos a
  mano durante la corrida

## Alcance

Workflows cubiertos por este diseno:

- `UC-IMG-02`
- `UC-IMG-03`
- `UC-VID-01`
- `UC-VID-02`
- `UC-VID-03`
- `UC-VID-04`

Workflows fuera del gate minimo:

- `UC-IMG-01`, porque hoy sigue siendo semilla template y no flujo de producto
  maduro
- `UC-VID-02` variante `maximum`, porque es referencia y no baseline

## Realidad actual del canal WhatsApp

Hoy ya existe una capa segura de acciones por WhatsApp para operar `ComfyUI`,
pero la sesion guiada de `openclaw_studio` todavia no esta integrada
directamente en ese canal.

Por eso este diseno define dos niveles:

- nivel ideal: la validacion se dispara desde WhatsApp con mensajes breves
- nivel transitorio: la misma intencion se puede ejecutar desde el puente local
  o desde la CLI mientras llega la integracion directa

La tarea `8.17` deja fijado el contrato de uso. La tarea `8.18` decidira en
cada corrida si ese contrato se ejecuta ya desde WhatsApp o todavia desde un
puente local compatible.

## Raiz de validacion

Para no mezclar pruebas con produccion, la validacion deberia vivir bajo una
raiz separada:

```text
$STUDIO_DIR/Validation/comfyui/<run_id>/<shot>/
├── fixtures/
├── published/
├── output/
├── logs/
├── evidence/
└── manifests/
```

## Regla de carpetas

- `fixtures/`: inputs congelados para pruebas atomicas
- `published/`: artefactos aprobados para alimentar la siguiente prueba
- `output/`: salida cruda de cada corrida
- `logs/`: logs, tiempos y errores
- `evidence/`: capturas, hashes, notas cortas y comparativas
- `manifests/`: resumen legible por maquina y por humano

## Contrato de handoff

La composicion entre workflows no debe depender de adivinar nombres de archivo.
Cada prueba que pase publica un artefacto canonico para la siguiente.

Artefactos canonicos:

- still aprobado:
  `published/stills/<shot>__frame__v001.png`
- paquete de controles:
  - `published/controls/<shot>__lineart__v001.mp4`
  - `published/controls/<shot>__depth__v001.mp4`
  - `published/controls/<shot>__pose__v001.mp4`
- video renderizado:
  `published/video/<shot>__render__v001.mp4`
- video mejorado:
  `published/video/<shot>__upscale__v001.mp4`
- frame inicial publicado:
  `published/frames/<shot>__start__v001.png`
- frame final publicado:
  `published/frames/<shot>__end__v001.png`

Cada publicacion deberia registrar un manifiesto minimo:

- `test_id`
- `use_case_id`
- `preset_id`
- `workflow_path`
- `input_paths`
- `published_paths`
- `fallback_applied`
- `operator_verdict`
- `notes`

## Perfil minimo de fixtures

Para que la prueba sea barata pero util:

- imagen fija:
  - `768 x 768` o `896 x 512`
  - un sujeto principal claro
  - sin exceso de ruido o compresion
- clip de video:
  - `3-5` segundos
  - `24 fps`
  - `480p` o `720p`
  - movimiento legible y no caotico
  - una sola accion o desplazamiento simple
- referencias:
  - `1-2` imagenes de personaje
  - `1-2` imagenes de estilo

## Suite atomica minima

Estas pruebas validan cada workflow por separado usando `fixtures/`.

| Test | Caso | Preset | Input minimo | Pasa si |
| --- | --- | --- | --- | --- |
| `AT-IMG-02-01` | `UC-IMG-02` | `uc-img-02-frame-baseline-preview` | `1` imagen base + `1` prompt | guarda al menos `1` still util, sin editar el grafo, y publica un frame aprobado |
| `AT-VID-01-01` | `UC-VID-01` | `uc-vid-01-preprocess-control-package` | `1` clip corto | exporta `outline` y `pose`; `depth` puede venir por `V3` o fallback `V2`; publica el paquete |
| `AT-VID-02-01` | `UC-VID-02` | `uc-vid-02-video-baseline-segmented` | `1` clip corto o paquete de controles fixture + `1-2` referencias + `1` prompt | genera `1` clip corto segmentado y lo guarda en la ruta esperada |
| `AT-IMG-03-01` | `UC-IMG-03` | `uc-img-03-style-exploration` | `1` still fixture + `1-2` refs de estilo opcionales | produce variantes distinguibles y al menos `1` queda publicable |
| `AT-VID-03-01` | `UC-VID-03` | `uc-vid-03-image-to-video-reference` | `1` frame inicial + `1` frame final + prompt opcional | genera `1` clip corto coherente con los extremos |
| `AT-VID-04-01` | `UC-VID-04` | `uc-vid-04-upscale-reference` | `1` clip renderizado fixture | genera `1` clip mejorado y lo guarda con nombre estable |

## Notas por prueba atomica

### `AT-IMG-02-01`

Debe ser la primera prueba de imagen porque valida:

- carga del workflow derivado real
- patch `Z-Image`
- guardado de still
- ruta baseline mas util para mostrar un resultado temprano

### `AT-VID-01-01`

El criterio minimo no exige que `depth` sea siempre `V3`.
La prueba sigue contando como util si:

- `outline` y `pose` salen bien
- `depth` sale por `V3` o por `V2`

Si no sale profundidad pero el resto si, el veredicto correcto es:

- `soft_pass_with_fallback`

### `AT-VID-02-01`

Debe limitarse a longitud corta y segmentacion pequeña para no convertir la
validacion en una prueba de resistencia. El objetivo no es medir maxima
calidad, sino comprobar que el flujo produce un render coherente sin exigir
intervencion manual.

### `AT-VID-03-01`

Es importante para validar la familia `Wan 2.2 5B fp16`, pero no debe bloquear
el primer cierre del baseline si `UC-VID-01` y `UC-VID-02` ya prueban mejor el
pipeline principal.

### `AT-VID-04-01`

Debe ejecutarse sobre un clip corto ya estable. No sirve como prueba si se usa
un input roto o incompleto.

## Suite compuesta minima

Estas pruebas validan la cadena operativa usando artefactos ya publicados.

| Test | Cadena | Reusa output de | Pasa si |
| --- | --- | --- | --- |
| `CP-STILL-01` | `UC-IMG-02 -> UC-IMG-03` | still publicado por `AT-IMG-02-01` | el frame renderizado alimenta la exploracion de estilo sin reubicar archivos a mano |
| `CP-VIDEO-01` | `UC-VID-01 -> UC-VID-02 -> UC-VID-04` | paquete de controles publicado por `AT-VID-01-01` y video publicado por `AT-VID-02-01` | la cadena completa produce un video renderizado y luego un video mejorado con handoff estable |
| `CP-MOTION-01` | `UC-VID-03 -> UC-VID-04` | video publicado por `AT-VID-03-01` | la ruta de first/last frame puede rematarse con mejora simple sin pasos manuales fuera del contrato |

## Cadena principal a priorizar en `8.18`

La composicion mas importante para producto es:

1. `AT-VID-01-01`
2. publicar controles
3. `AT-VID-02-01`
4. publicar render
5. `AT-VID-04-01`

Si solo puede correrse una composicion completa al inicio, debe ser
`CP-VIDEO-01`.

## Criterios de pase

## Pase atomico

Una prueba atomica cuenta como `pass` cuando:

- usa el preset previsto sin editar el JSON durante la corrida
- consume solo fixtures declarados
- llega al guardado esperado
- deja artefacto legible en la ruta definida
- registra manifiesto y log
- supera una inspeccion visual rapida

## Pase compuesto

Una prueba compuesta cuenta como `pass` cuando:

- el siguiente workflow consume el artefacto publicado por el anterior
- no hay que renombrar archivos manualmente fuera del contrato de handoff
- la cadena completa deja evidencia de inicio, handoff y salida final
- el resultado final sigue siendo reconocible respecto al input de origen

## Estados de veredicto

- `pass`
- `soft_pass_with_fallback`
- `fail_runtime`
- `fail_quality`
- `blocked_missing_asset`
- `blocked_missing_integration`

## Interfaz ideal desde WhatsApp

La interfaz deberia usar lenguaje natural corto y evitar IDs tecnicos cuando no
aporten valor.

Mensajes ideales:

- `studio valida frame baseline para sh-test-001`
- `studio valida preprocess para sh-test-001`
- `studio valida render baseline para sh-test-001`
- `studio valida mejora de video para sh-test-001`
- `studio valida cadena de video para sh-test-001`
- `studio estado de validacion para sh-test-001`

## Contrato conversacional minimo

Para cada mensaje de validacion, el sistema deberia:

1. resolver el preset correcto
2. confirmar el `shot` y los inputs detectados
3. avisar si ejecuta baseline o fallback
4. correr el workflow
5. responder con:
   - estado
   - preset usado
   - ruta de salida
   - siguiente prueba sugerida

Ejemplo de respuesta esperada:

```text
Validacion preprocess lanzada para sh-test-001.
Preset: uc-vid-01-preprocess-control-package.
Si pasa, publico lineart, depth y pose para la cadena de render.
```

## Puente transitorio hasta la integracion completa

Mientras la integracion directa con WhatsApp no exista, `8.18` puede usar la
misma semantica de validacion a traves de un puente local.

Opciones validas:

- `scripts/openclaw/test-studio-actions-plugin.sh`
- `PYTHONPATH=src python -m openclaw_studio`
- una pequena accion segura que reciba `test_id`, `preset_id` y `shot`

La regla es no inventar otro lenguaje de pruebas distinto. El contrato de
mensajes y el contrato de manifiestos deben ser los mismos.

## Orden recomendado de ejecucion en `8.18`

1. `AT-IMG-02-01`
2. `AT-VID-01-01`
3. `AT-VID-02-01`
4. `CP-VIDEO-01`
5. `AT-IMG-03-01`
6. `CP-STILL-01`
7. `AT-VID-03-01`
8. `CP-MOTION-01`

## Cierre correcto de tareas

- `8.17` queda cerrada cuando este diseno ya fija:
  - suite atomica
  - suite compuesta
  - criterios de pase
  - contrato de handoff
  - interfaz ideal desde WhatsApp
- `8.18` solo puede cerrarse cuando existan corridas reales con evidencia y
  resultados documentados en
  `docs/comfyui/atomic-composed-whatsapp-validation-results.md`

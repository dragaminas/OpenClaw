# Extension de ComfyUI a WhatsApp sobre Runner Canonico

Este documento es la fuente de verdad para la tarea `8.20` del `DevPlan`.

Define como exponer `ComfyUI` y sus validaciones desde WhatsApp reutilizando la
misma infraestructura ya creada en `8.19`, sin abrir una estructura paralela
solo para el canal de chat.

## Objetivo

Permitir que la UI actual, WhatsApp, pueda:

- lanzar corridas de `ComfyUI`
- lanzar smoke tests
- lanzar validaciones futuras de `8.18`
- consultar estado y resultado
- reutilizar la misma evidencia y los mismos identificadores

## Decision principal

La decision correcta es:

- el runner de `ComfyUI` implementa una interfaz `runner` comun
- WhatsApp invoca ese runner a traves de `studio-actions`
- la misma base sirve para tests y para uso real de `ComfyUI`

La decision incorrecta seria:

- crear un runner solo para terminal
- crear otro runner solo para WhatsApp
- crear otra capa distinta solo para validaciones
- crear otra estructura distinta solo para uso real

## Dependencias

`8.20` depende de:

- `8.19`, porque ya existe una primera ejecucion real con evidencia
- `docs/architecture/runner-interface.md`, porque define el contrato comun

`8.18` pasa a depender operativamente de `8.20` si queremos que el usuario
pueda lanzar la validacion desde la UI real.

## Regla de no duplicacion

Todo lo siguiente debe reutilizarse y no reimplementarse:

- el mismo runner local
- los mismos `run_id`
- los mismos `case_id`
- los mismos estados
- la misma estructura de manifiestos
- la misma estructura de evidencia
- la misma publicacion de artefactos

Si algo cambia entre terminal y WhatsApp, debe cambiar solo la capa de entrada
o presentacion, no el modelo de ejecucion.

## Flujo deseado

```text
WhatsApp
  -> plugin studio-actions
  -> catalogo de acciones seguras
  -> scripts/actions/runner-action.sh
  -> openclaw_studio.runner_cli
  -> runner registry
  -> runner comfyui
  -> manifiestos y artefactos
  -> respuesta corta al chat
```

## Responsabilidades por capa

## WhatsApp

Solo deberia encargarse de:

- recibir el mensaje
- exigir la wake word `studio`
- pedir estado o cancelacion
- mostrar resultados de forma corta

## `studio-actions`

Deberia encargarse de:

- parsear la intencion segura
- resolver `runner_id`, `operation_kind` y `target_id`
- invocar el runner
- traducir la respuesta tecnica a texto de chat

No deberia:

- conocer detalles de nodos de `ComfyUI`
- reconstruir manifiestos
- inventar estados propios
- guardar evidencia por su cuenta

Implementacion concreta actual:

- parser y routing: `plugins/studio-actions/index.js`
- wrapper seguro del contrato: `scripts/actions/runner-action.sh`
- CLI del contrato: `src/openclaw_studio/runner_cli.py`
- registro y runner de `ComfyUI`: `src/openclaw_studio/runners/`

## Runner de `ComfyUI`

Deberia encargarse de:

- preparar inputs
- lanzar la corrida
- seguir el estado
- cancelar si hace falta
- escribir manifiestos y evidencia
- devolver resultados estables

## Modos que debe cubrir `8.20`

La extension de WhatsApp deberia cubrir desde el principio:

- `validate_smoke`
- `validate_atomic`
- `validate_composed`
- `operate`

Aunque al principio solo se ejecute realmente `validate_smoke`, el contrato no
deberia quedar cerrado solo para smoke.

## Superficie minima de comandos

## Estado base de la app

- `studio como esta comfyui`
- `studio inicia comfyui`
- `studio reinicia comfyui`
- `studio abre comfyui`
- `studio para comfyui`

## Biblioteca visible de workflows

- `studio comfyui workflows`
- `studio que hace prepara-video`
- `studio comfyui que hace prepara-video`
- `studio compara prepara-video y render-video`
- `studio comfyui abre workflow prepara-video`
- `studio comfyui ruta workflow prepara-video`

Estos comandos no lanzan el runner. Publican y exponen la biblioteca visible de
workflows de `OpenClaw` como templates nativos de `ComfyUI` bajo
`custom_nodes/openclaw-workflows/example_workflows/`, reutilizando el mismo
catalogo Python de flujos y aliases amigables.

`studio comfyui abre workflow <alias>` debe abrir la UI web con el template ya
seleccionado por URL, usando `template=<alias>&source=openclaw-workflows`, para
que el usuario vea el workflow exacto de `OpenClaw` y no el ultimo grafo
persistido por la sesion anterior.

`studio comfyui workflows` no deberia limitarse a listar aliases. Debe devolver
una descripcion breve y explicita de cada workflow, incluyendo que hace, cual
es su entrada obligatoria y que salida produce.

`studio que hace <alias>` y `studio comfyui que hace <alias>` deben resolver el
workflow desde el mismo catalogo canonico y explicar el flujo en lenguaje
humano, sin duplicar logica dentro de WhatsApp.

`studio compara <alias_a> y <alias_b>` debe resolver ambos workflows canonicos
y dejar pasar la consulta al agente con contexto grounded de los dos, para que
OpenClaw compare proposito, entradas, salidas y encadenamiento posible entre
ellos sin caer en una respuesta fija del plugin.

Implementacion actual recomendada:

- `before_dispatch` reconoce la consulta asesorada y la deja pasar
- el plugin prepara contexto derivado del workflow real
- `before_prompt_build` inyecta ese contexto al agente general
- OpenClaw responde de forma libre pero grounded

Eso evita convertir preguntas de producto en respuestas fijas del plugin y
permite explicar como usar el workflow mirando su estructura real.

## Smoke validation

- `studio corre smoke de comfyui`
- `studio comfyui smoke`
- `studio comfyui smoke SMK-VID-02-01`

## Validacion futura de `8.18`

- `studio comfyui validate atomic AT-IMG-02-01`
- `studio comfyui validate composed CP-VIDEO-01`

## Seguimiento

- `studio comfyui estado <run_id>`
- `studio comfyui cancela <run_id>`
- `studio comfyui evidencia <run_id>`

## Modelo de respuesta

La respuesta al chat deberia ser breve pero estable.

Campos recomendados:

- `run_id`
- `target_id`
- `status`
- `message`
- referencia corta a evidencia

Ejemplo:

```text
run_id=smoke-light-5
status=pass
target=SMK-VID-04-01
evidencia=~/Studio/Validation/comfyui/smoke/smoke-light-5/evidence/summary.md
```

Si la operacion todavia no esta implementada, debe responder por el mismo
runner con algo equivalente a:

```text
status=unsupported
accepted=false
```

## Estados canonicos esperados

WhatsApp debe reutilizar exactamente los estados del runner:

- `queued`
- `running`
- `pass`
- `soft_pass_with_fallback`
- `fail_compile`
- `fail_runtime`
- `fail_quality`
- `blocked_missing_asset`
- `cancelled`

No deberia inventar equivalentes alternativos solo para lenguaje natural.

## Relacion entre test y uso real

La misma infraestructura debe servir para ambos casos.

La diferencia entre un test y un uso real no deberia ser el stack de
ejecucion, sino:

- `operation_kind`
- `target_id`
- `inputs`
- nivel de evidencia esperada

Eso permite que el camino operativo sea uno solo.

## Que significa “usar ComfyUI desde WhatsApp”

No significa abrir shell ni mandar prompts arbitrarios al sistema.

Significa exponer acciones seguras y trazables como:

- correr un caso ya definido
- correr un preset ya definido
- pedir estado
- consultar evidencia
- cancelar una corrida

Los flujos abiertos o expertos pueden venir despues, pero deben entrar por el
mismo contrato de runner.

## Criterios de aceptacion de 8.20

`8.20` solo deberia cerrarse cuando:

- WhatsApp pueda lanzar la smoke suite completa
- WhatsApp pueda lanzar al menos un caso concreto por `case_id`
- el resultado escrito por WhatsApp reutilice el mismo `run_id`
- la evidencia generada sea la misma que la corrida local
- `studio-actions` no contenga logica especifica de workflows
- el mismo contrato quede listo para ser usado por `8.18`

## Estado implementado

Hoy ya quedan expuestos por WhatsApp:

- `studio comfyui workflows`
- `studio compara prepara-video y render-video`
- `studio comfyui abre workflow <alias>`
- `studio comfyui ruta workflow <alias>`
- `studio comfyui smoke`
- `studio comfyui smoke <case_id>`
- `studio comfyui estado <run_id>`
- `studio comfyui cancela <run_id>`
- `studio comfyui evidencia <run_id>`

Y quedan preparados por el mismo contrato:

- `studio comfyui validate atomic <test_id>`
- `studio comfyui validate composed <test_id>`

con respuesta `unsupported` hasta que `8.18` aterrice la ejecucion real.

La apertura visual de workflows y la ejecucion por runner comparten la misma
fuente de verdad de catalogo, pero no se mezclan:

- la biblioteca visible sirve para inspeccionar y cargar grafos en la UI web
- el runner sigue siendo la via canonica para operaciones con estado,
  evidencia y cancelacion

## No objetivos de 8.20

`8.20` no deberia exigir todavia:

- que toda la validacion atomica y compuesta ya este aprobada
- una UX conversacional avanzada
- flujos abiertos con libertad total de prompt
- permisos de shell por chat

Su meta es abrir el canal correcto sobre la estructura correcta.

## Relacion con los documentos canonicos

- contrato general: `docs/architecture/runner-interface.md`
- smoke actual: `docs/comfyui/workflow-smoke-validation.md`
- validacion diseñada para `8.18`: `docs/comfyui/atomic-composed-whatsapp-validation.md`
- operacion diaria de la app: `docs/operations/comfyui.md`

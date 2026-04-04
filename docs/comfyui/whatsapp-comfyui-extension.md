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

# Interfaz Canonica de Runner

Este documento define el contrato canonico para cualquier `runner` ejecutable
desde `OpenClaw Studio`.

Su funcion es evitar estructuras paralelas por aplicacion o por canal de UI.
La misma interfaz debe servir para:

- `ComfyUI`
- validaciones smoke, atomicas y compuestas
- uso real de la aplicacion desde WhatsApp
- futuras aplicaciones como Blender u otras herramientas creativas

## Objetivo

Tener una unica forma de:

- descubrir que operaciones expone una aplicacion
- lanzar una corrida
- consultar estado
- cancelar una corrida
- leer resultados y evidencia

La capa de canal no deberia conocer detalles internos del workflow ni del
script concreto de una aplicacion.

## Regla principal

Un canal de entrada como WhatsApp no debe crear su propio runner.

Debe actuar solo como:

- capa de parsing
- capa de autorizacion segura
- capa de seguimiento conversacional

y delegar la ejecucion a un `runner` canonico compartido.

## Capas de arquitectura

La arquitectura deseada queda asi:

```text
WhatsApp / CLI / futuras UIs
        |
        v
plugin o capa de acciones seguras
        |
        v
registro de runners
        |
        v
runner de aplicacion
        |
        v
manifiestos, artefactos y evidencia
```

## Que problema resuelve

Sin esta interfaz aparecerian duplicaciones como:

- un runner local para `ComfyUI`
- otro runner distinto solo para WhatsApp
- otra forma distinta de guardar evidencia para validaciones
- otra nomenclatura distinta para estados o `run_id`

Eso rompe trazabilidad y hace mucho mas caro extender el sistema.

## Entidades canonicas

## `runner_id`

Identificador estable del runner concreto.

Ejemplos:

- `comfyui`
- `blender`

## `operation_kind`

Tipo de operacion a ejecutar.

Valores previstos:

- `operate`
- `validate_smoke`
- `validate_atomic`
- `validate_composed`

## `target_id`

Identificador funcional del objetivo a correr.

Segun la operacion puede ser:

- `use_case_id`
- `case_id`
- `preset_id`
- un alias de suite

## `run_id`

Identificador unico de una corrida real.

Debe ser el mismo en:

- el runner local
- el canal de WhatsApp
- los manifiestos
- la evidencia publicada

## Operaciones minimas del contrato

Todo `runner` deberia exponer al menos estas capacidades:

1. `describe`
2. `list_targets`
3. `start_run`
4. `get_run_status`
5. `cancel_run`
6. `get_run_result`

## `describe`

Devuelve metadatos estables del runner:

- `runner_id`
- `display_label`
- `supported_operation_kinds`
- `supported_target_kinds`
- `supports_cancel`
- `supports_progress`
- `default_evidence_root`

## `list_targets`

Permite descubrir que puede correr ese runner sin que la UI tenga que codificar
listas a mano.

Ejemplos:

- casos smoke `SMK-*`
- tests atomicos `AT-*`
- tests compuestos `CP-*`
- flujos de uso real `UC-*`

## `start_run`

Recibe una peticion canonica y devuelve un handle estable.

Campos minimos de la peticion:

- `runner_id`
- `operation_kind`
- `target_id`
- `requested_by`
- `channel`
- `run_id` opcional
- `inputs` opcionales
- `options` opcionales

Campos minimos de respuesta:

- `run_id`
- `accepted`
- `status`
- `message`

Si la operacion todavia no esta implementada, el runner puede responder:

- `accepted=false`
- `status=unsupported`
- `message` claro

sin crear un `run_id` ficticio ni una estructura paralela.

## `get_run_status`

Devuelve el estado vivo de una corrida.

Estados canonicos recomendados:

- `queued`
- `running`
- `pass`
- `soft_pass_with_fallback`
- `fail_compile`
- `fail_runtime`
- `fail_quality`
- `blocked_missing_asset`
- `cancelled`

## `cancel_run`

Permite interrumpir la corrida activa sin destruir evidencia ya generada.

Si el backend soporta interrupcion selectiva, la cancelacion debe ser por
`run_id` o `prompt_id`, no global.

## `get_run_result`

Devuelve el resumen estable de una corrida terminada.

Debe incluir:

- `run_id`
- `status`
- `message`
- `target_id`
- `operation_kind`
- `artifact_refs`
- `manifest_path`
- `summary_path`

## Contrato de evidencia

La evidencia no depende del canal.

Una corrida lanzada desde terminal y otra lanzada desde WhatsApp deben producir
la misma estructura logica:

- manifiesto por caso o corrida
- resumen agregado
- artefactos de salida
- `run_id` consistente

Cuando una corrida tenga ciclo de vida activo, el runner puede anadir un
manifiesto operativo comun, por ejemplo:

- `manifests/run.json`

siempre que esa extension sea compartida por terminal, WhatsApp y futuras UIs,
y no una variante especial del canal.

La diferencia entre canales solo deberia estar en como se solicita la corrida y
como se presenta el resultado al usuario.

## Regla de no duplicacion

No se deberian permitir:

- runners especiales solo para WhatsApp
- manifiestos especiales solo para chat
- `case_id` distintos entre CLI y chat
- carpetas de evidencia distintas para la misma operacion
- una segunda taxonomia de estados para la capa conversacional

## ComfyUI como primera implementacion

El runner de `ComfyUI` creado en `8.19` debe leerse como la primera
implementacion de esta interfaz, no como una solucion aislada.

La evolucion correcta es:

1. encapsular su ejecucion bajo el contrato `runner`
2. reutilizarlo desde `studio-actions`
3. ampliar el mismo runner para `8.18`
4. reutilizar el mismo patron para otras apps

Implementacion concreta actual en el repo:

- contrato y registro: `src/openclaw_studio/runners/`
- CLI segura: `src/openclaw_studio/runner_cli.py`
- primer runner real: `src/openclaw_studio/runners/comfyui.py`
- ejecucion smoke reutilizada: `src/openclaw_studio/comfyui_smoke_validation.py`

## Relacion con WhatsApp

WhatsApp no deberia ejecutar scripts de aplicacion directamente cuando la
operacion ya tiene ciclo de vida, estados y evidencia.

La capa de WhatsApp deberia:

- resolver la intencion
- mapearla a una llamada al `runner`
- devolver respuestas cortas
- permitir pedir estado o cancelar

pero no asumir la logica del workflow ni la estructura de evidencia.

## Relacion con otras aplicaciones

Este contrato no es exclusivo de `ComfyUI`.

Tambien deberia servir para:

- smoke tests de Blender
- tareas guiadas de Blender con evidencia
- futuras apps creativas integradas en `Studio`

La implementacion concreta cambia; el contrato de ejecucion no.

## No objetivos

Este documento no define:

- el parser conversacional final de WhatsApp
- los workflows concretos de `ComfyUI`
- la semantica detallada de cada `AT-*` o `CP-*`
- la UX final de resultados por chat

Eso pertenece a documentos especificos de aplicacion o de canal.

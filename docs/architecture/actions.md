# Acciones Seguras

La capa de chat no expone shell libre. Todo lo que entra por WhatsApp pasa
primero por un catalogo limitado de acciones seguras.

## Regla de activacion

- la wake word actual es `studio`
- el mensaje debe empezar con `studio`
- despues de `studio` se admite lenguaje natural sencillo o modo tecnico

Comportamiento actual por WhatsApp:

- con wake word: el plugin intenta resolver una accion segura
- sin wake word: el plugin consume el mensaje en silencio
- el mensaje sin wake word no se envia al agente general

## Acciones iniciales implementadas

Lenguaje natural:

- `studio abre blender`
- `studio como esta blender`
- `studio crea proyecto <nombre>`
- `studio abre proyecto <nombre>`
- `studio haz una prueba de blender`
- `studio abre comfyui`
- `studio inicia comfyui`
- `studio reinicia comfyui`
- `studio como esta comfyui`
- `studio para comfyui`
- `studio lista workflows comfyui`
- `studio abre workflow prepara-video`
- `studio ruta workflow prepara-video`

Modo tecnico:

- `studio`
- `studio blender status`
- `studio blender new <nombre>`
- `studio blender open <nombre>`
- `studio blender smoke-test <nombre>`
- `studio comfyui status`
- `studio comfyui start`
- `studio comfyui restart`
- `studio comfyui open`
- `studio comfyui stop`
- `studio comfyui url`
- `studio comfyui workflows`
- `studio compara prepara-video y render-video`
- `studio comfyui abre workflow <alias>`
- `studio comfyui ruta workflow <alias>`
- `studio comfyui smoke`
- `studio comfyui smoke <case_id>`
- `studio comfyui estado <run_id>`
- `studio comfyui cancela <run_id>`
- `studio comfyui evidencia <run_id>`
- `studio comfyui validate atomic <test_id>`
- `studio comfyui validate composed <test_id>`

## Principios

- exigir un prefijo explicito en WhatsApp
- validar entradas
- limitar rutas a `STUDIO_DIR`
- responder con mensajes simples
- evitar comandos arbitrarios

## Dos modos de `studio`

No todo lo que entra con wake word deberia terminar en una respuesta fija del
plugin.

Hay dos modos validos:

- modo operativo: el plugin ejecuta una accion segura y responde directamente
- modo asesorado: el plugin reconoce la intencion, prepara contexto seguro y
  deja pasar el mensaje al agente general

El segundo modo sirve para preguntas como:

- `studio que hace prepara-video`
- `studio explica que hace prepare-video`
- `studio compara prepara-video y render-video`

En esos casos, `studio-actions` no deberia inventar una respuesta dura. Deberia
inyectar al prompt del agente contexto derivado del workflow real y dejar que
OpenClaw explique el flujo con mas libertad.

## Regla para operaciones con ciclo de vida

Cuando una accion tiene:

- estados de ejecucion
- evidencia
- cancelacion
- artefactos publicados

no deberia resolverse como un wrapper ad hoc por canal.

Deberia pasar por la interfaz canonica de `runner` descrita en
`docs/architecture/runner-interface.md`.

## Primer puente WhatsApp

El primer puente implementado usa un plugin local de OpenClaw con hook
`before_dispatch`.

Flujo:

1. llega un mensaje por WhatsApp
2. el plugin busca la wake word dentro del contenido real del usuario
3. si reconoce una accion de Blender, ejecuta un wrapper seguro del repo
4. devuelve una respuesta corta al mismo chat

## Detalle importante de parsing

En mensajes reales de WhatsApp, OpenClaw puede entregar el contenido al plugin
envuelto con metadatos multilinea. Por eso el parser:

- normaliza el mensaje completo
- intenta detectar la wake word al inicio del contenido normalizado
- si no aparece ahi, escanea linea por linea hasta encontrar la linea real del usuario

Eso permite que frases como `studio abre blender` sigan funcionando aunque el
mensaje llegue encapsulado dentro de un transcript mayor.

## Alcance actual

Implementado hoy:

- estado de Blender
- apertura de Blender
- creacion de proyecto nuevo
- apertura de proyecto existente
- smoke test de Blender
- estado de ComfyUI
- arranque de ComfyUI
- reinicio de ComfyUI
- apertura de la UI web de ComfyUI
- publicacion de workflows OpenClaw como templates nativos de ComfyUI
- apertura de la UI web con un workflow visible en Templates
- parada controlada de ComfyUI
- launch de `validate_smoke` por runner canonico
- consulta de estado, cancelacion y evidencia por `run_id`
- respuestas `unsupported` para `validate_atomic` y `validate_composed` a traves
  del mismo runner

Pendiente:

- implementacion real de `validate_atomic`
- implementacion real de `validate_composed`
- perfiles de acciones por usuario o por modo de uso
- mas wrappers para archivos y herramientas creativas

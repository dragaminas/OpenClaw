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
- `studio como esta comfyui`
- `studio para comfyui`

Modo tecnico:

- `studio`
- `studio blender status`
- `studio blender new <nombre>`
- `studio blender open <nombre>`
- `studio blender smoke-test <nombre>`
- `studio comfyui status`
- `studio comfyui start`
- `studio comfyui open`
- `studio comfyui stop`
- `studio comfyui url`

## Principios

- exigir un prefijo explicito en WhatsApp
- validar entradas
- limitar rutas a `STUDIO_DIR`
- responder con mensajes simples
- evitar comandos arbitrarios

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
- apertura de la UI web de ComfyUI
- parada controlada de ComfyUI

Pendiente:

- primer workflow real de ComfyUI orientado a imagen o video
- perfiles de acciones por usuario o por modo de uso
- mas wrappers para archivos y herramientas creativas

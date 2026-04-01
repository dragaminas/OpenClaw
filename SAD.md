# SAD

## Nombre

OpenClaw Creative Workstation

## Proposito

Convertir una instalacion Linux dedicada en una workstation creativa controlada
por chat, usando WhatsApp como interfaz principal y `OpenClaw` como
orquestador local de acciones seguras.

## Objetivos de arquitectura

- permitir uso cotidiano sin consola para una menor o una persona no tecnica
- mantener `OpenClaw` fuera de `root`
- limitar el alcance operativo del agente al usuario de trabajo y a carpetas autorizadas
- integrar aplicaciones locales como Blender y ComfyUI
- hacer reproducible la instalacion mediante `.env` y scripts

## Restricciones principales

- el sistema comparte hardware con otros sistemas
- los discos internos que no deban tocarse no deben montarse
- GNOME no debe automontar unidades por su cuenta
- la primera capa de chat no debe exponer shell libre
- el runtime normal debe operar como usuario no privilegiado

## Vista de contexto

```text
WhatsApp
   |
   v
Canal enlazado de OpenClaw
   |
   v
Gateway local de OpenClaw
   |
   v
Plugin local "studio-actions"
   |
   v
Wrappers seguros del repo
   |
   +--> Blender
   +--> ComfyUI
   +--> otras apps creativas
```

## Componentes

### 1. Sistema anfitrion Linux

Responsabilidades:

- arrancar desde el disco extraible dedicado
- mantener discos sensibles fuera del flujo normal
- ofrecer sesion grafica GNOME para apps GUI
- ejecutar servicios `systemd --user`

### 2. Configuracion declarativa

Archivos:

- [`.env.example`](/home/eric/Documents/OpenClaw/.env.example)
- [`.env`](/home/eric/Documents/OpenClaw/.env)

Responsabilidades:

- definir usuario, rutas, politicas y puertos
- seleccionar integraciones activas
- permitir convergencia por scripts

### 3. Bootstrap del repo

Script orquestador:

- [`apply-workstation.sh`](/home/eric/Documents/OpenClaw/scripts/bootstrap/apply-workstation.sh)

Responsabilidades:

- validar precondiciones
- aplicar hardening base
- preparar OpenClaw
- registrar plugins locales
- preparar Blender y ComfyUI
- reiniciar o dejar listos servicios de usuario

### 4. Runtime de OpenClaw

Piezas relevantes:

- estado en [`/home/eric/.openclaw`](/home/eric/.openclaw)
- servicios de usuario `openclaw-gateway.service` y `openclaw-node.service`
- canal de WhatsApp enlazado a la cuenta permitida

Responsabilidades:

- recibir mensajes del canal
- aplicar hooks/plugins
- despachar al agente solo cuando la capa segura no haya consumido el mensaje
- devolver respuestas al mismo chat

### 5. Plugin local `studio-actions`

Ubicacion:

- [`index.js`](/home/eric/Documents/OpenClaw/plugins/studio-actions/index.js)

Responsabilidades:

- exigir una wake word al inicio del mensaje, por defecto `studio`
- interpretar lenguaje natural sencillo despues de la wake word
- operar solo sobre canales autorizados, por defecto `whatsapp`
- ejecutar wrappers seguros del repo
- devolver respuestas breves y legibles

Configuracion en OpenClaw:

- `plugins.load.paths` incluye el directorio del plugin
- `plugins.entries.studio-actions.config` contiene `commandPrefix`, `channels` y `allowGroupMessages`

Decision clave:

- se usa el hook `before_dispatch`

Consecuencia:

- si el mensaje coincide con una accion segura, el plugin responde y evita que el mensaje siga al flujo general del agente
- si el mensaje llega por WhatsApp sin wake word, el plugin lo consume en silencio

Detalle operativo relevante:

- en la practica, algunos mensajes de WhatsApp llegan a OpenClaw envueltos con metadatos multilinea
- el parser del plugin inspecciona el texto normalizado completo y tambien linea por linea para localizar la wake word real dentro del contenido del usuario

### 6. Wrappers seguros

Piezas iniciales:

- [`blender-action.sh`](/home/eric/Documents/OpenClaw/scripts/actions/blender-action.sh)
- [`blender.sh`](/home/eric/Documents/OpenClaw/scripts/apps/blender.sh)

Responsabilidades:

- validar nombres y rutas
- limitar el acceso a `STUDIO_DIR/BlenderProjects`
- traducir acciones del chat a operaciones locales concretas

### 7. Aplicaciones creativas locales

Backends iniciales:

- Blender
- ComfyUI
- `ComfyUI-Manager`

Responsabilidades:

- ejecutar trabajo creativo real
- guardar proyectos y salidas dentro de `STUDIO_DIR`

## Flujo principal

### Flujo de bootstrap

1. se ajusta `.env`
2. se ejecuta `scripts/bootstrap/apply-workstation.sh audit`
3. se ejecuta `scripts/bootstrap/apply-workstation.sh apply`
4. el bootstrap endurece el sistema y OpenClaw
5. el bootstrap registra el plugin local y prepara apps creativas
6. el sistema queda listo para aceptar comandos seguros

### Flujo de mensaje seguro

1. la usuaria escribe por WhatsApp: `studio crea proyecto castillo`
2. OpenClaw recibe el mensaje en el canal enlazado
3. `studio-actions` localiza la wake word y convierte la frase en una accion segura
4. el plugin ejecuta `scripts/actions/blender-action.sh new castillo`
5. el wrapper valida el nombre y llama al wrapper de Blender
6. OpenClaw responde en el mismo chat con el resultado

### Flujo de mensaje sin wake word

1. llega un mensaje por WhatsApp sin el prefijo configurado
2. `studio-actions` lo consume sin responder
3. el mensaje no se envia al agente general

Esto evita activaciones accidentales y reduce la probabilidad de que texto libre
del chat termine interpretado como una instruccion abierta del sistema.

## Fronteras de seguridad

- no se usa `root` para el runtime normal
- el usuario de trabajo solo ve lo que Linux le permita ver
- el automontaje de GNOME se desactiva por script
- los discos sensibles deben permanecer desmontados
- el plugin inicial exige prefijo explicito y no acepta shell arbitrario
- los wrappers limitan rutas a carpetas autorizadas

## Decisiones tecnicas relevantes

### Linux como sandbox principal

Se acepta usar el propio sistema operativo dedicado como sandbox principal,
siempre que:

- el runtime no corra como `root`
- los discos sensibles no se monten
- GNOME no automonte unidades

### Plugin hook-only en lugar de shell libre

No se expone una consola por WhatsApp. En su lugar:

- un plugin local exige una wake word
- despues admite frases sencillas o comandos tecnicos seguros
- los mensajes se traducen a wrappers del repo
- el sistema responde con texto corto

### Configuracion por `.env`

Se prioriza `.env` porque:

- simplifica el bootstrap
- facilita reinstalacion y ajuste rapido
- mantiene un camino claro hacia convergencia declarativa

## Estado actual

Implementado:

- hardening base de OpenClaw
- desactivacion de automontaje en GNOME
- wrappers de Blender y ComfyUI
- plugin local `studio-actions`
- deteccion de wake word dentro de mensajes de WhatsApp con metadatos
- consumo silencioso de mensajes sin wake word en WhatsApp
- cierre del onboarding inicial de OpenClaw con `bootstrapPending=false`
- prueba local del puente seguro con Blender

Pendiente para cierre final:

- validacion real extremo a extremo por WhatsApp despues del ultimo ajuste
- usuario runtime dedicado en lugar de `eric`
- integrar ComfyUI en la misma capa segura
- estabilizar la puesta en servicio de ComfyUI

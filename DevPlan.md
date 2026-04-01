# Dev Plan

Plan por fases para convertir este repositorio en una base reproducible de
instalacion, hardening y operacion de una workstation Linux dedicada a
`OpenClaw`, con acciones seguras para Blender, ComfyUI y otras aplicaciones
creativas, usando WhatsApp como interfaz principal.

## Vision del proyecto

Resultado esperado:

- una instalacion Linux dedicada en un disco extraible
- un usuario de trabajo no privilegiado
- `OpenClaw` ejecutandose sin `root`
- integracion con apps creativas locales
- uso cotidiano desde WhatsApp
- operacion sencilla para una menor o una persona no tecnica
- 0 acceso operativo desde `OpenClaw` a discos internos mientras no esten montados ni concedidos al usuario de trabajo
- automontaje de GNOME deshabilitado y verificado
- instalacion y configuracion reproducibles mediante scripts
- administracion mantenible para el adulto responsable

## Precondiciones

- Linux instalado en un disco extraible conectado a un ordenador que bootea por USB
- contiene un usuario de trabajo no privilegiado
- existe WhatsApp o Telegram como canal disponible
- hay acceso a APIs de IA en linea o locales
- los discos internos que no deban tocarse no forman parte del flujo normal
- `sudo` se usa solo para instalacion y ajustes del sistema
- existe una sesion grafica GNOME o compatible
- el equipo dispone de Blender, ComfyUI o capacidad prevista para instalarlos

## Criterios de exito

- el sistema puede instalarse siguiendo scripts y documentacion
- `OpenClaw` arranca como servicio de usuario
- WhatsApp queda enlazado y funcional
- Blender y ComfyUI pueden abrirse o ejecutarse mediante acciones controladas
- los discos no permitidos no se montan automaticamente
- GNOME no monta unidades por su cuenta
- las credenciales y permisos locales quedan endurecidos
- existe un modo de diagnostico y reparacion basico

## Estado de implementacion

Leyenda:

- `[done]` completado y probado en este sistema
- `[in progress]` parcialmente implementado o pendiente de cierre
- `[pending]` aun no implementado

Bloqueos actuales observados en este sistema:

- el usuario `eric` sigue en grupos sensibles como `sudo` y `adm`
- falta confirmacion real por WhatsApp despues del ultimo fix del parser con wake word
- `openclaw-node.service` puede quedar temporalmente en `activating` durante pairing o reconexion

## Registro as-built fuera del plan original

Items ya implementados que no estaban desglosados asi en el plan inicial:

- [done] Cerrar el onboarding inicial de OpenClaw eliminando `BOOTSTRAP.md` y verificando `bootstrapPending=false`
- [done] Adaptar el parser del plugin a mensajes de WhatsApp encapsulados con metadatos multilinea
- [done] Consumir en silencio los mensajes de WhatsApp sin wake word para que no lleguen al agente general
- [done] Añadir un driver local del plugin para pruebas sin depender del chat real
- [done] Integrar `ComfyUI-Manager` y sus requirements dentro del bootstrap declarativo

## Fase 0: Fundacion del repo

Objetivo:
Definir la estructura del proyecto y la convencion de configuracion.

Tareas:

- [done] Crear estructura de carpetas `scripts/`, `configs/` y `docs/`
- [done] Crear `.env.example` con variables previstas
- [done] Definir convencion de nombres para scripts
- [done] Definir politica de logs y codigos de salida
- [done] Definir archivo de configuracion principal del proyecto
- [done] Documentar supuestos del sistema objetivo
- [done] Crear script de validacion de precondiciones del host

Entregables:

- [done] arbol base del repo
- [done] plantilla `.env.example`
- [done] documento de convenciones operativas
- [done] `scripts/bootstrap/validate-preconditions.sh`

## Fase 1: Hardening del sistema anfitrion

Objetivo:
Reducir superficie de riesgo antes de instalar automatizaciones de uso diario.

Tareas:

- [done] Crear script para verificar usuario de trabajo dedicado
- [done] Crear script para comprobar grupos peligrosos como `sudo`, `disk`, `adm`
- [done] Crear script para documentar discos presentes y discos montados
- [done] Crear script para comprobar que los discos internos sensibles no estan montados
- [pending] Crear script para documentar y aplicar ajustes de `fstab` cuando proceda
- [done] Crear script para desactivar automontaje y autoapertura de GNOME
- [done] Crear script para verificar que GNOME no vuelve a montar unidades
- [done] Crear script para revisar permisos sensibles del home y de directorios de credenciales
- [done] Crear documentacion con el procedimiento para desactivar automontaje en GNOME y validar el cambio

Entregables:

- [done] `scripts/hardening/check-user.sh`
- [done] `scripts/hardening/check-mounts.sh`
- [done] `scripts/hardening/disable-gnome-automount.sh`
- [done] `scripts/hardening/check-permissions.sh`
- [done] documentacion de hardening en `docs/security/`

## Fase 2: Bootstrap de OpenClaw

Objetivo:
Instalar y dejar operativo `OpenClaw` de forma reproducible.

Tareas:

- [pending] Crear script de instalacion de dependencias base
- [in progress] Crear script de instalacion o actualizacion de Node y `OpenClaw`
- [done] Crear script para preparar directorios de estado
- [done] Crear script para aplicar permisos seguros a `~/.openclaw`
- [done] Crear script para generar o validar configuracion base
- [done] Crear script para desactivar flags inseguras conocidas
- [done] Crear script para instalar servicios `systemd --user`
- [done] Crear script de estado que ejecute validaciones tipo `doctor` y `security audit`
- [done] Crear script para preparar carpeta de trabajo segura para proyectos y exportaciones

Entregables:

- [in progress] `scripts/openclaw/install-openclaw.sh`
- [done] `scripts/openclaw/configure-openclaw.sh`
- [done] `scripts/services/install-user-services.sh`
- [done] `scripts/doctor/openclaw-status.sh`
- [done] `scripts/openclaw/setup-workspace.sh`
- [done] plantillas y notas en `configs/openclaw/`

## Fase 3: Integracion de aplicaciones creativas

Objetivo:
Conectar `OpenClaw` con aplicaciones del sistema pensadas para flujos creativos.

Tareas:

- [done] Crear script para detectar Blender instalado
- [done] Crear script para lanzar Blender con un proyecto nuevo o existente
- [done] Crear script para detectar ComfyUI
- [done] Crear script para arrancar ComfyUI como servicio local o proceso controlado
- [done] Crear script para comprobar puertos, modelos y rutas de salida de ComfyUI
- [done] Evaluar integracion con Krita, GIMP o Inkscape
- [done] Definir carpeta de trabajo estandar para proyectos y exportaciones
- [done] Crear wrappers pensados para ser invocados por acciones seguras desde chat
- [done] Crear un plugin local de OpenClaw para interceptar acciones seguras via `before_dispatch`
- [done] Incluir la instalacion de `ComfyUI-Manager` en el setup reproducible

Entregables:

- [done] `scripts/apps/blender.sh`
- [done] `scripts/apps/comfyui.sh`
- [done] `scripts/apps/design-tools.sh`
- [done] `scripts/actions/blender-action.sh`
- [done] `scripts/actions/comfyui-action.sh`
- [in progress] `configs/comfyui/`
- [done] documentacion operativa en `docs/operations/`
- [done] `scripts/apps/install-comfyui-manager.sh`
- [done] `scripts/services/install-comfyui-service.sh`

## Fase 4: Capa de acciones seguras

Objetivo:
Traducir lenguaje natural de WhatsApp a acciones locales controladas.

Tareas:

- [done] Definir catalogo de acciones permitidas
- [done] Separar acciones por categoria: archivos, Blender, ComfyUI y utilidades visuales
- [in progress] Crear wrappers que validen parametros y rutas
- [done] Restringir acciones a carpetas de trabajo autorizadas
- [done] Evitar ejecucion arbitraria de comandos del sistema
- [done] Diseñar mensajes de respuesta legibles para usuario no tecnico
- [done] Conectar el primer puente `WhatsApp -> before_dispatch -> Blender`
- [done] Conectar el primer puente `WhatsApp -> before_dispatch -> ComfyUI`
- [done] Exigir wake word al inicio y permitir lenguaje natural despues
- [done] Ignorar en WhatsApp cualquier mensaje sin wake word

Entregables:

- [done] especificacion de acciones en `docs/architecture/`
- [done] wrappers en `scripts/apps/` o `scripts/actions/`
- [in progress] configuracion de rutas permitidas y perfiles de uso
- [done] plugin hook-only de OpenClaw en `plugins/studio-actions/`

## Fase 5: Experiencia sin consola

Objetivo:
Hacer que el sistema sea facil de usar y mantener sin depender de terminal.

Tareas:

- [pending] Crear accesos directos de escritorio para tareas administrativas comunes
- [pending] Crear script para iniciar o reiniciar servicios del usuario
- [pending] Crear script de comprobacion visual de estado
- [in progress] Documentar flujos cotidianos para la menor usuaria
- [in progress] Documentar flujos de mantenimiento para el adulto administrador

Entregables:

- [pending] accesos `.desktop`
- [pending] `scripts/doctor/workstation-health.sh`
- [in progress] guias cortas en `docs/operations/`

## Fase 6: Respaldo, restauracion y actualizaciones

Objetivo:
Mantener el sistema recuperable y facil de actualizar.

Tareas:

- [pending] Crear backup de configuraciones y estado importante
- [pending] Excluir secretos no necesarios o artefactos pesados cuando corresponda
- [pending] Crear script de restauracion
- [pending] Crear script de actualizacion segura de `OpenClaw`
- [pending] Crear checklist de verificacion post-update

Entregables:

- [pending] `scripts/openclaw/backup.sh`
- [pending] `scripts/openclaw/restore.sh`
- [pending] `scripts/openclaw/update.sh`
- [pending] runbooks en `docs/operations/`

## Fase 7: Validacion integral

Objetivo:
Confirmar que el sistema cumple el caso de uso final.

Tareas:

- [pending] Probar arranque en frio del equipo
- [in progress] Probar que `OpenClaw` arranca sin consola
- [in progress] Probar enlace y uso por WhatsApp
- [done] Probar lanzamiento de Blender
- [done] Probar arranque y ejecucion de ComfyUI
- [in progress] Probar bloqueo de discos no montados
- [done] Probar que GNOME no automonta unidades
- [in progress] Probar flujos reales con comandos seguros desde chat

Entregables:

- [pending] checklist de aceptacion
- [pending] reporte de incidencias
- [in progress] backlog de mejoras

## Riesgos a controlar

- confundir "no usar root" con "no tener acceso a discos"
- dejar discos montados y visibles para el usuario de trabajo
- exponer shell libre por chat
- permisos inseguros en credenciales o sesiones
- cambios de GNOME que reactiven automontaje
- dependencias cambiantes de Blender, ComfyUI u OpenClaw

## Orden recomendado de implementacion

1. Fundacion del repo
2. Hardening de discos, usuario y GNOME
3. Instalacion reproducible de `OpenClaw`
4. Servicios de usuario y diagnostico
5. Integracion con Blender y ComfyUI
6. Capa de acciones seguras para WhatsApp
7. UX sin consola
8. Backup, update y validacion final

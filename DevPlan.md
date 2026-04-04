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

Criterio de cierre de tareas:

- una tarea solo puede marcarse como completada si existe el entregable
  asociado en el repo o una evidencia operativa documentada y revisable
- si una tarea produce mas de un artefacto, el entregable principal debe seguir
  siendo una ruta concreta que sirva como punto de entrada para la revision

Bloqueos actuales observados en este sistema:

- el usuario `eric` sigue en grupos sensibles como `sudo` y `adm`

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

- [done] 0.1 Crear estructura de carpetas `scripts/`, `configs/` y `docs/`
- [done] 0.2 Crear `.env.example` con variables previstas
- [done] 0.3 Definir convencion de nombres para scripts
- [done] 0.4 Definir politica de logs y codigos de salida
- [done] 0.5 Definir archivo de configuracion principal del proyecto
- [done] 0.6 Documentar supuestos del sistema objetivo
- [done] 0.7 Crear script de validacion de precondiciones del host

Entregables por tarea:

- [done] 0.1 arbol base del repo con `scripts/`, `configs/` y `docs/`
- [done] 0.2 `.env.example`
- [done] 0.3 convencion de nombres documentada en `README.md`
- [done] 0.4 funciones comunes de log, error y salida en `scripts/lib/common.sh`
- [done] 0.5 configuracion declarativa central en `.env.example`
- [done] 0.6 supuestos del sistema objetivo documentados en `README.md`
- [done] 0.7 `scripts/bootstrap/validate-preconditions.sh`

## Fase 1: Hardening del sistema anfitrion

Objetivo:
Reducir superficie de riesgo antes de instalar automatizaciones de uso diario.

Tareas:

- [done] 1.1 Crear script para verificar usuario de trabajo dedicado
- [pending] 1.2 Remover al usuario de trabajo de grupos sensibles (`sudo`, `adm`) y validar nueva sesion
- [done] 1.3 Crear script para comprobar grupos peligrosos como `sudo`, `disk`, `adm`
- [done] 1.4 Crear script para documentar discos presentes y discos montados
- [done] 1.5 Crear script para comprobar que los discos internos sensibles no estan montados
- [done] 1.6 Crear script para documentar y aplicar ajustes de `fstab` cuando proceda
- [done] 1.7 Crear script para desactivar automontaje y autoapertura de GNOME
- [done] 1.8 Crear script para verificar que GNOME no vuelve a montar unidades
- [done] 1.9 Crear script para revisar permisos sensibles del home y de directorios de credenciales
- [done] 1.10 Crear documentacion con el procedimiento para desactivar automontaje en GNOME y validar el cambio

Entregables por tarea:

- [done] 1.1 `scripts/hardening/check-user.sh`
- [pending] 1.2 `docs/security/runtime-user-hardening.md`
- [done] 1.3 validacion de grupos peligrosos en `scripts/hardening/check-user.sh`
- [done] 1.4 `scripts/hardening/check-mounts.sh`
- [done] 1.5 comprobacion de discos sensibles no montados en `scripts/hardening/check-mounts.sh`
- [done] 1.6 `scripts/hardening/manage-fstab.sh`
- [done] 1.7 `scripts/hardening/disable-gnome-automount.sh`
- [done] 1.8 verificacion de automontaje en `scripts/hardening/disable-gnome-automount.sh`
- [done] 1.9 `scripts/hardening/check-permissions.sh`
- [done] 1.10 `docs/security/disks-and-automount.md`

## Fase 2: Bootstrap de OpenClaw

Objetivo:
Instalar y dejar operativo `OpenClaw` de forma reproducible.

Tareas:

- [done] 2.1 Crear script de instalacion de dependencias base
- [done] 2.2 Crear script de instalacion o actualizacion de Node y `OpenClaw`
- [done] 2.3 Crear script para preparar directorios de estado
- [done] 2.4 Crear script para aplicar permisos seguros a `~/.openclaw`
- [done] 2.5 Crear script para generar o validar configuracion base
- [done] 2.6 Crear script para desactivar flags inseguras conocidas
- [done] 2.7 Crear script para instalar servicios `systemd --user`
- [done] 2.8 Crear script de estado que ejecute validaciones tipo `doctor` y `security audit`
- [done] 2.9 Crear script para preparar carpeta de trabajo segura para proyectos y exportaciones

Entregables por tarea:

- [done] 2.1 `scripts/openclaw/install-base-deps.sh`
- [done] 2.2 `scripts/openclaw/install-openclaw.sh`
- [done] 2.3 preparacion de directorios de estado en `scripts/openclaw/configure-openclaw.sh`
- [done] 2.4 aplicacion de permisos seguros en `scripts/openclaw/configure-openclaw.sh`
- [done] 2.5 configuracion base en `scripts/openclaw/configure-openclaw.sh` y `configs/openclaw/README.md`
- [done] 2.6 gestion de flags inseguras en `scripts/openclaw/configure-openclaw.sh`
- [done] 2.7 `scripts/services/install-user-services.sh`
- [done] 2.8 `scripts/doctor/openclaw-status.sh`
- [done] 2.9 `scripts/openclaw/setup-workspace.sh`

## Fase 3: Integracion de aplicaciones creativas

Objetivo:
Conectar `OpenClaw` con aplicaciones del sistema pensadas para flujos creativos.

Tareas:

- [done] 3.1 Crear script para detectar Blender instalado
- [done] 3.2 Crear script para lanzar Blender con un proyecto nuevo o existente
- [done] 3.3 Crear script para detectar ComfyUI
- [done] 3.4 Crear script para arrancar ComfyUI como servicio local o proceso controlado
- [done] 3.5 Crear script para comprobar puertos, modelos y rutas de salida de ComfyUI
- [done] 3.6 Evaluar integracion con Krita, GIMP o Inkscape
- [done] 3.7 Definir carpeta de trabajo estandar para proyectos y exportaciones
- [done] 3.8 Crear wrappers pensados para ser invocados por acciones seguras desde chat
- [done] 3.9 Crear un plugin local de OpenClaw para interceptar acciones seguras via `before_dispatch`
- [done] 3.10 Incluir la instalacion de `ComfyUI-Manager` en el setup reproducible

Entregables por tarea:

- [done] 3.1 deteccion de Blender en `scripts/apps/blender.sh`
- [done] 3.2 lanzamiento de Blender en `scripts/apps/blender.sh`
- [done] 3.3 deteccion de ComfyUI en `scripts/apps/comfyui.sh`
- [done] 3.4 arranque controlado de ComfyUI en `scripts/apps/comfyui.sh`
- [done] 3.5 chequeos de puertos, modelos y salidas en `scripts/apps/comfyui.sh`
- [done] 3.6 integracion de herramientas de diseno en `scripts/apps/design-tools.sh`
- [done] 3.7 estandar de rutas creativas en `scripts/openclaw/setup-workspace.sh`
- [done] 3.8 wrappers seguros en `scripts/actions/blender-action.sh` y `scripts/actions/comfyui-action.sh`
- [done] 3.9 plugin local en `plugins/studio-actions/`
- [done] 3.10 `scripts/apps/install-comfyui-manager.sh`

## Fase 4: Capa de acciones seguras

Objetivo:
Traducir lenguaje natural de WhatsApp a acciones locales controladas.

Tareas:

- [done] 4.1 Definir catalogo de acciones permitidas
- [done] 4.2 Separar acciones por categoria: archivos, Blender, ComfyUI y utilidades visuales
- [done] 4.3 Crear wrappers que validen parametros y rutas
- [done] 4.4 Restringir acciones a carpetas de trabajo autorizadas
- [done] 4.5 Evitar ejecucion arbitraria de comandos del sistema
- [done] 4.6 Diseñar mensajes de respuesta legibles para usuario no tecnico
- [done] 4.7 Conectar el primer puente `WhatsApp -> before_dispatch -> Blender`
- [done] 4.8 Conectar el primer puente `WhatsApp -> before_dispatch -> ComfyUI`
- [done] 4.9 Exigir wake word al inicio y permitir lenguaje natural despues
- [done] 4.10 Ignorar en WhatsApp cualquier mensaje sin wake word

Entregables por tarea:

- [done] 4.1 catalogo de acciones en `docs/architecture/actions.md`
- [done] 4.2 separacion por categorias en `docs/architecture/actions.md`
- [done] 4.3 validacion de parametros y rutas en `scripts/actions/blender-action.sh` y `scripts/actions/comfyui-action.sh`
- [done] 4.4 restricciones de rutas en `.env.example` y en `scripts/actions/`
- [done] 4.5 ausencia de shell libre en `plugins/studio-actions/index.js`
- [done] 4.6 mensajes de respuesta legibles en `plugins/studio-actions/index.js`
- [done] 4.7 puente `WhatsApp -> Blender` en `plugins/studio-actions/index.js`
- [done] 4.8 puente `WhatsApp -> ComfyUI` en `plugins/studio-actions/index.js`
- [done] 4.9 wake word obligatoria en `plugins/studio-actions/index.js`
- [done] 4.10 consumo silencioso sin wake word en `plugins/studio-actions/index.js`

## Fase 5: Experiencia sin consola

Objetivo:
Hacer que el sistema sea facil de usar y mantener sin depender de terminal.

Tareas:

- [done] 5.1 Crear accesos directos de escritorio para tareas administrativas comunes
- [done] 5.2 Crear script para iniciar o reiniciar servicios del usuario
- [done] 5.3 Crear script de comprobacion visual de estado
- [done] 5.4 Documentar flujos cotidianos para la menor usuaria
- [done] 5.5 Documentar flujos de mantenimiento para el adulto administrador

Entregables por tarea:

- [done] 5.1 plantillas `.desktop` en `configs/desktop/` y `scripts/desktop/install-shortcuts.sh`
- [done] 5.2 `scripts/services/user-services.sh`
- [done] 5.3 `scripts/doctor/workstation-health.sh`
- [done] 5.4 `docs/operations/daily-use.md`
- [done] 5.5 `docs/operations/admin-maintenance.md`

## Fase 6: Respaldo, restauracion y actualizaciones

Objetivo:
Mantener el sistema recuperable y facil de actualizar.

Tareas:

- [done] 6.1 Crear backup de configuraciones y estado importante
- [done] 6.2 Excluir secretos no necesarios o artefactos pesados cuando corresponda
- [done] 6.3 Crear script de restauracion
- [done] 6.4 Crear script de actualizacion segura de `OpenClaw`
- [done] 6.5 Crear checklist de verificacion post-update

Entregables por tarea:

- [done] 6.1 `scripts/openclaw/backup.sh`
- [done] 6.2 politica de exclusiones y alcance en `docs/operations/backup-and-updates.md`
- [done] 6.3 `scripts/openclaw/restore.sh`
- [done] 6.4 `scripts/openclaw/update.sh`
- [done] 6.5 checklist post-update en `docs/operations/backup-and-updates.md`

## Fase 7: Validacion integral

Objetivo:
Confirmar que el sistema cumple el caso de uso final.

Tareas:

- [done] 7.1 Probar arranque en frio del equipo
- [done] 7.2 Probar que `OpenClaw` arranca sin consola
- [done] 7.3 Probar enlace y uso por WhatsApp
- [done] 7.4 Probar lanzamiento de Blender
- [done] 7.5 Probar arranque y ejecucion de ComfyUI
- [done] 7.6 Probar bloqueo de discos no montados
- [done] 7.7 Probar que GNOME no automonta unidades
- [done] 7.8 Probar flujos reales con comandos seguros desde chat

Entregables por tarea:

- [done] 7.1 evidencia de arranque en frio en `docs/operations/acceptance.md`
- [done] 7.2 evidencia de arranque sin consola en `docs/operations/acceptance.md`
- [done] 7.3 evidencia de enlace y uso por WhatsApp en `docs/operations/acceptance.md`
- [done] 7.4 evidencia de lanzamiento de Blender en `docs/operations/acceptance.md`
- [done] 7.5 evidencia de arranque y ejecucion de ComfyUI en `docs/operations/acceptance.md`
- [done] 7.6 evidencia de bloqueo de discos no montados en `docs/operations/acceptance.md`
- [done] 7.7 evidencia de no automontaje de GNOME en `docs/operations/acceptance.md`
- [done] 7.8 evidencia de flujos reales desde chat en `docs/operations/acceptance.md`

## Fase 8: Productizacion de workflows ComfyUI para Blender

Objetivo:
Convertir los workflows reales ya presentes en `ComfyUIWorkflows/` en una
cadena reproducible y utilizable para este stack, ajustada al hardware local y
conectada con Blender y con una interfaz de uso mas simple.

Tareas:

- [done] 8.1 Inventariar y priorizar casos de uso reales para imagen y video
- [done] 8.2 Definir la interfaz objetivo por caso de uso: sesion guiada principal, modo experto opcional y contratos de flujos configurables y ejecutables, con soporte futuro para canvas nativo de `ComfyUI`, preset operativo, atajo de escritorio o accion segura via `OpenClaw`
- [done] 8.3 Definir perfiles de hardware objetivo `minimo`, `medio` y `maximo`, centrando el producto inicial en `RTX 3060 8 GB-12 GB` como baseline compatible y dejando los perfiles superiores para variantes futuras sin bloquear el primer stack operativo
- [done] 8.4 Perfilar limites del baseline minimo (`RTX 3060 8 GB-12 GB`; con `RTX 3060 12 GB`, `62 GiB RAM` y `Ryzen 5 5600X` como referencia actual), fijar presets base de resolucion, duracion, batch e iteraciones y documentar las degradaciones normales del sistema
- [done] 8.5 Auditar, clasificar y documentar los workflows base en `ComfyUIWorkflows/` como biblioteca de referencia, distinguiendo baseline-compatible, referencia de alto VRAM, base adaptable, experimento y legado
- [done] 8.6 Mapear el papel de `260225_MICKMUMPITZ_AI-RENDERER-PREPROCESS_1-0.json`, `260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0.json`, `260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0_Runpod.json` y `260303_MICKMUMPITZ_Z-IMAGE_TURBO_CN_1-1.json`, indicando para que casos de uso sirven hoy, de que perfil parten y que derivaciones futuras deberian inspirar
- [done] 8.7 Inventariar e instalar los custom nodes requeridos por el baseline minimo y por la biblioteca de workflows base, separando dependencias bloqueantes, recomendadas y reservadas para variantes futuras (`VideoHelperSuite`, `DepthAnythingV3`, `ControlNet Aux`, `KJNodes`, `rgthree`, `Impact Pack`, `Essentials`, `easy-use`, `WanVideoWrapper`, `wanvaceadvanced`, `RES4LYF` y `ComfyUI-GGUF` si aplica)
- [done] 8.8 Descargar y ubicar los modelos, text encoders, VAE, model patches y LoRAs requeridos por el baseline minimo y por la biblioteca de workflows base, distinguiendo que assets son operativos hoy y cuales se conservan para futuras adaptaciones
- [done] 8.9 Documentar el set minimo local priorizando assets no cuantizados cuando sean viables en el hardware actual: `qwen_3_4b.safetensors`, `z_image_turbo_bf16.safetensors`, `ae.safetensors`, el patch `Z-Image Turbo ControlNet`, `da3_base.safetensors`, el fallback `depth_anything_v2_vitl_fp32.safetensors`, `wan2.2_ti2v_5B_fp16.safetensors`, `umt5_xxl_fp16.safetensors`, `wan2.2_vae.safetensors`, y documentar aparte la biblioteca heredada `VACE/Wan 2.1` y sus LoRAs
- [done] 8.10 Evaluar y, si hace falta, habilitar rutas fallback para flujos sin implementacion operativa disponible en el baseline actual, incluyendo `VACE_Skyreels_V3_R2V_Merge` con `ComfyUI-GGUF` cuando sea la mejor via alternativa aunque no sea solo por VRAM limitada
- [done] 8.11 Crear variantes derivadas para el baseline minimo y para futuras adaptaciones sin sobrescribir los JSON originales descargados, manteniendo trazabilidad con el workflow base del que nacen
- [done] 8.12 Definir una convencion de entradas y salidas entre Blender y `ComfyUI` para `lineart`, `depth`, `openpose`, `start frame`, referencias y renders finales
- [done] 8.13 Evaluar la automatizacion minima desde Blender para exportar pases de control con nombres y carpetas consistentes
- [done] 8.14 Diseñar la primera interfaz operable para usuarios no tecnicos con presets por caso de uso, rutas estandar y mensajes claros
- [pending] 8.15 Probar un caso de imagen fija y un caso de video corto de punta a punta entrando en `ComfyUI` desde material de prueba cualquiera o desde material ya disponible, validando primero el baseline minimo y registrando aparte los workflows base que aun no tengan derivacion operativa; la validacion Blender -> `ComfyUI` completa queda para una fase posterior cuando Blender este listo
- [done] 8.16 Documentar troubleshooting para VRAM insuficiente, nodos faltantes, modelos mal ubicados, tiempos de render, reanudacion de iteraciones y ausencia temporal de una implementacion nativa para un flujo
- [done] 8.17 Diseñar una validacion atomica y una validacion por composicion para los workflows derivados, definiendo tests E2E lo mas simples pero suficientes posibles, preferiblemente disparables desde WhatsApp, donde el output de una prueba pueda convertirse en input de la siguiente para comprobar no solo cada flujo aislado sino tambien la cadena operativa real
- [pending] 8.18 Ejecutar la validacion diseñada para los workflows derivados y sus composiciones, registrar evidencia, conservar artefactos de entrada y salida y dejar claramente que partes quedaron aprobadas, cuales siguen pendientes y cuales requieren fallback o revision
- [done] 8.19 Preparar una smoke validation minima que permita ejecutar `8.18` con un gate barato de funcionamiento real, usando imagenes pequenas y clips de video pequenos para comprobar solo que cada workflow carga, corre y guarda salida sin exigir calidad alta ni comparativas finas
- [pending] 8.20 Extender la misma estructura operativa creada en `8.19` para exponer `ComfyUI` y sus validaciones desde WhatsApp, sin crear runners, manifiestos, contratos ni rutas de evidencia paralelas; el runner de `ComfyUI` debe pasar a implementar una interfaz `runner` reutilizable tambien por otras aplicaciones, y el puente de `studio-actions` debe reutilizar y ampliar ese mismo contrato, los mismos identificadores de casos, la misma publicacion de artefactos y la misma forma de reportar estado para que sirva tanto para lanzar smoke tests y validaciones de `8.18` como para habilitar ya el uso real de `ComfyUI` desde la UI actual

Entregables por tarea:

- [done] 8.1 `docs/comfyui/usecases.md`
- [done] 8.2 `docs/comfyui/interface.md`
- [done] 8.3 `docs/comfyui/hardware-profiles.md`
- [done] 8.4 `docs/comfyui/baseline-minimo-rtx3060-8gb-12gb.md`
- [done] 8.5 `docs/comfyui/workflow-audit.md`
- [done] 8.6 `docs/comfyui/workflow-map.md`
- [done] 8.7 `configs/comfyui/custom-nodes-manifest.md`
- [done] 8.8 `configs/comfyui/models-manifest.md`
- [done] 8.9 `configs/comfyui/model-set-baseline-minimo-rtx3060-8gb-12gb.md`
- [done] 8.10 `docs/comfyui/fallback-paths.md`
- [done] 8.11 workflows derivados versionados en `ComfyUIWorkflows/local/`
- [done] 8.12 `docs/comfyui/blender-bridge.md`
- [done] 8.13 `docs/comfyui/blender-export-automation.md`
- [done] 8.14 presets operativos en `configs/comfyui/presets/`
- [done] 8.15 `docs/comfyui/e2e-validation.md`
- [done] 8.16 `docs/comfyui/troubleshooting.md`
- [done] 8.17 `docs/comfyui/atomic-composed-whatsapp-validation.md`
- [pending] 8.18 `docs/comfyui/atomic-composed-whatsapp-validation-results.md`
- [done] 8.19 `docs/comfyui/workflow-smoke-validation.md`
- [pending] 8.20 `docs/architecture/runner-interface.md`
- [pending] 8.20 `docs/comfyui/whatsapp-comfyui-extension.md`

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
6. Productizacion de workflows ComfyUI para Blender
7. Capa de acciones seguras para WhatsApp
8. UX sin consola
9. Backup, update y validacion final

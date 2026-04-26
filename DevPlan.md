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

## Fase 8: Productizacion de workflows ComfyUI para render de video e imagen

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
- [done] 8.15 Probar un caso de imagen fija y un caso de video corto de punta a punta entrando en `ComfyUI` desde material de prueba cualquiera o desde material ya disponible, validando primero el baseline minimo y registrando aparte los workflows base que aun no tengan derivacion operativa; la validacion Blender -> `ComfyUI` completa queda para una fase posterior cuando Blender este listo
- [done] 8.16 Documentar troubleshooting para VRAM insuficiente, nodos faltantes, modelos mal ubicados, tiempos de render, reanudacion de iteraciones y ausencia temporal de una implementacion nativa para un flujo
- [done] 8.17 Diseñar una validacion atomica y una validacion por composicion para los workflows derivados, definiendo tests E2E lo mas simples pero suficientes posibles, preferiblemente disparables desde WhatsApp, donde el output de una prueba pueda convertirse en input de la siguiente para comprobar no solo cada flujo aislado sino tambien la cadena operativa real
- [pending] 8.18 Ejecutar la validacion diseñada para los workflows derivados y sus composiciones, registrar evidencia, conservar artefactos de entrada y salida y dejar claramente que partes quedaron aprobadas, cuales siguen pendientes y cuales requieren fallback o revision
- [done] 8.19 Preparar una smoke validation minima que permita ejecutar `8.18` con un gate barato de funcionamiento real, usando imagenes pequenas y clips de video pequenos para comprobar solo que cada workflow carga, corre y guarda salida sin exigir calidad alta ni comparativas finas
- [done] 8.20 Extender la misma estructura operativa creada en `8.19` para exponer `ComfyUI` y sus validaciones desde WhatsApp, sin crear runners, manifiestos, contratos ni rutas de evidencia paralelas; el runner de `ComfyUI` debe pasar a implementar una interfaz `runner` reutilizable tambien por otras aplicaciones, y el puente de `studio-actions` debe reutilizar y ampliar ese mismo contrato, los mismos identificadores de casos, la misma publicacion de artefactos y la misma forma de reportar estado para que sirva tanto para lanzar smoke tests y validaciones de `8.18` como para habilitar ya el uso real de `ComfyUI` desde la UI actual
- [done] 8.21 Diseñar, derivar y validar un workflow general de renderizacion de video para este sistema, reutilizando primero los workflows locales ya desarrollados en `OpenClaw` (`UC-VID-01`, `UC-VID-02`, `UC-VID-04`) y completando solo lo que falte con templates nativos de `ComfyUI` y, en ultimo termino, referencias externas; el workflow debe aceptar como obligatorios un video base, un prompt de escena/estilo y una seleccion valida de `1` a `3` controles activos entre bordes, pose y profundidad; debe soportar como opcionales anclajes de identidad por color o por descripcion textual posicional sobre el frame inicial, de modo que referencias visuales de personaje u objeto puedan asociarse a entidades concretas sin romper el caso base; debe mostrar el frame inicial para inspeccion, conservar el aspect ratio del video de entrada, escoger una resolucion adecuada al hardware local, subdividir clips largos en subsecciones iterables, encadenar una mejora posterior hasta `Full HD` y dejar abierta una etapa adicional opcional de aumento de FPS despues del render principal y antes del upscale final, dejando evidencia real de una corrida local usando `blenderTest.mp4` como fixture base de `8.15`
- [done] 8.21.1 Especificar el workflow general, su contrato funcional, sus prioridades de producto y su relacion con `8.15`, `8.18` y `8.20`, dejando claro que la V1 solo exige video base, prompt, preview y una combinacion valida de `1` a `3` controles activos
- [done] 8.21.2 Derivar una primera variante `V1` en `ComfyUIWorkflows/local/` que reutilice `UC-VID-01` y `UC-VID-02`, preserve aspect ratio, muestre el primer frame y permita activar o desactivar bordes, pose y profundidad sin exigir los tres a la vez
- [done] 8.21.3 Ejecutar una validacion real local de la variante `V1` usando `blenderTest.mp4`, conservar artefactos, publicar evidencia revisable y dejar documentado que partes del workflow general ya funcionan de verdad en este sistema
- [done] 8.21.4 Añadir soporte opcional para anclajes de identidad, incluyendo asociacion entre colores del video base o descripciones textuales posicionales del sujeto en el frame inicial y referencias visuales de personaje u objeto, sin romper la ejecucion del caso base sin anclajes
- [done] 8.21.5 Añadir soporte para subdividir clips largos en subsecciones iterables, con una convencion estable para recomposicion temporal y evidencia por segmento
- [done] 8.21.6 Añadir una etapa de mejora final o upscale hasta `Full HD`, reutilizando preferentemente `UC-VID-04` o un template local equivalente y dejando claro si queda integrada en el mismo workflow o como paso encadenado posterior; la rama opcional de interpolacion FPS previa a la salida ya puede activarse en la V1 funcional con un modo local de mezcla temporal lineal y `fps_objetivo`, pero sigue pendiente valorar una variante generativa tipo `Wan 2.2` para stopmotion exigente sin bloquear el cierre funcional actual

Regla de cierre para `8.21`:

- `8.21` no deberia marcarse como `done` solo porque exista el documento de diseño
- `8.21` puede avanzar por etapas cerrando `8.21.1`, `8.21.2`, `8.21.3`, etc.
- la primera etapa realmente valiosa es `8.21.3`, porque certifica una `V1` corriendo de verdad en esta maquina
- `8.21` solo deberia considerarse completamente cerrada cuando, como minimo, `8.21.1`, `8.21.2` y `8.21.3` esten hechas y exista un criterio explicito para lo que sigue pendiente en `8.21.4`, `8.21.5` y `8.21.6`
- mientras `8.21` siga en depuracion, los workflows funcionales publicados en `ComfyUI` no deberian esconder el camino critico en nodos opacos; deben dejar visibles nodos y valores diagnosticos suficientes para entender por donde se pierden frames, `fps` o controles

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
- [done] 8.20 `docs/architecture/runner-interface.md`
- [done] 8.20 `docs/comfyui/whatsapp-comfyui-extension.md`
- [done] 8.21.1 `docs/comfyui/general-video-render-workflow.md`
- [done] 8.21.2 workflow derivado `V1` versionado en `ComfyUIWorkflows/local/`
- [done] 8.21.3 evidencia y resultados de corrida real local con `blenderTest.mp4`, incluyendo `docs/comfyui/general-video-render-workflow-results.md`
- [done] 8.21.4 documentacion y artefactos de soporte para anclajes de identidad por color o por descripcion posicional
- [done] 8.21.5 documentacion y artefactos de segmentacion por subsecciones
- [done] 8.21.6 documentacion y artefactos de mejora final a `Full HD`, incluyendo la rama opcional de interpolacion FPS previa a la salida ya publicada en la V1 funcional

## Fase 9: MVP 3D en ComfyUI con `SF3D` y composicion posterior en `Blender`

Objetivo:
Convertir la exploracion 3D en una cadena `MVP` reproducible, portable y
facil de operar dentro de `ComfyUI`, usando `Stable Fast 3D (SF3D)` como
baseline para `image -> 3D`, tratando `text -> 3D` como puente
`texto -> imagen semilla -> SF3D`, y dejando `Hunyuan3D` como linea futura
separada a traves de su repo oficial, fuera de los workflows `ComfyUI` de esta
fase. La escena compleja debe seguir tratandose como composicion progresiva de
activos en `Blender`, con preferencia por generar por separado objetos,
personajes y envolventes reutilizables.

Hipotesis operativa:

- para el `MVP`, importan mas la sencillez operativa, la portabilidad, la
  futura dockerizacion y la velocidad de iteracion que la maxima fidelidad
  posible en zonas no visibles
- `ComfyUI` debe quedarse con la ruta de menor friccion:
  `image -> SF3D -> Blender`
- `text -> 3D` en esta fase no debe exigirse como `text-to-3D` nativo dentro
  del mismo grafo; debe resolverse como `texto -> imagen -> SF3D`
- `Blender` debe quedar como herramienta complementaria para inspeccion,
  cleanup, materiales, catalogacion, layout y animacion controlada
- `Hunyuan3D` sigue siendo interesante, pero no debe bloquear ni contaminar el
  `MVP` en `ComfyUI`; si se retoma despues, deberia hacerse via repo oficial,
  `API` o addon propio, no via wrappers comunitarios de `ComfyUI`
- para interiorismo, paisajismo y escenas complejas sigue siendo preferible
  generar `assets` independientes como muebles, personajes y envolventes antes
  que perseguir una escena completa cerrada de una sola vez

Tareas:

- [done] 9.1 Inventariar y priorizar casos de uso reales para objetos, personajes, interiorismo y paisajismo, separando entregables de `asset` aislado, `set` de activos y escena compuesta, e identificando expresamente familias como muebles, personajes y envolventes
- [done] 9.2 Evaluar los stacks candidatos mas prometedores para `text/image -> 3D`, empezando por `Hunyuan 3D`, `InstantMesh` y `Stable Fast 3D (SF3D)`, y cerrar la decision de `MVP` con `SF3D` como baseline en `ComfyUI`, dejando `Hunyuan3D` como linea futura via repo oficial
- [done] 9.3 Definir perfiles de hardware objetivo para la linea 3D, distinguiendo baseline local, perfil adaptable y referencia de alto VRAM o remota, pero tomando `SF3D` como baseline real del `MVP` en `ComfyUI`
- [done] 9.4 Definir los contratos de entrada y salida para la linea 3D: prompt, imagenes de referencia, alpha o mascara si aplica, categoria de activo (`objeto`, `personaje`, `envolvente`), escala aproximada, orientacion, unidades, pivot coherente, formatos de exportacion (`glb`, `obj`, `fbx` si aplica), texturas y convencion de carpetas
- [done] 9.5 Auditar custom nodes, modelos y dependencias auxiliares requeridas por el baseline `SF3D`, separando lo que queda dentro del `MVP` de `ComfyUI` y lo que pasa a linea futura externa como `Hunyuan3D`
- [done] 9.6 Descargar, ubicar y documentar los assets necesarios para el baseline `SF3D` elegido y dejar aparte, sin bloquear el `MVP`, los requisitos de una futura linea `Hunyuan3D` oficial
- [done] 9.7 Definir la interfaz objetivo por caso de uso, con sesion guiada principal, modo experto opcional, presets operativos y mensajes legibles para usuario no tecnico, pero tratando `imagen -> 3D` como ruta directa y `texto -> 3D` como puente a imagen semilla
- [done] 9.8 Diseñar la taxonomia de casos de uso 3D del producto y asignar identificadores estables, proponiendo al menos `UC-3D-01` objeto/personaje desde texto, `UC-3D-02` objeto/personaje desde imagen, `UC-3D-03` set de activos o escena interior/exterior desde texto y `UC-3D-04` set de activos o escena interior/exterior desde imagen
- [done] 9.9 Diseñar, derivar y validar un workflow general de generacion de objetos y personajes 3D para este sistema, tomando `SF3D` como motor principal del `MVP` y priorizando una salida que ya pueda inspeccionarse, catalogarse como `asset` y aprovecharse en `Blender`
- [done] 9.9.1 Especificar el workflow general para `UC-3D-01` y `UC-3D-02`, su contrato funcional, sus limites de producto y su relacion con `9.13`, `9.14` y `9.15`, ya realineados a `SF3D`
- [done] 9.9.2 Derivar una primera variante `V1` para `UC-3D-01` y otra para `UC-3D-02` en `ComfyUIWorkflows/local/`, alineadas con `SF3D` y sustituyendo como baseline `MVP` a los experimentos previos basados en `Hunyuan`
- [done] 9.9.3 Ejecutar una validacion real local de ambas variantes `SF3D`, conservando artefactos, importandolos en `Blender` y dejando documentado que partes ya funcionan de verdad en este sistema
- [done] 9.10 Definir el minimo de calidad aceptable para objetos y personajes: malla cerrada o reparable, orientacion coherente, escala controlable, pivot util para composicion, texturas exportables y tiempo de generacion razonable en el baseline local
- [pending] 9.11 Diseñar, derivar y validar un workflow general de generacion de escenas 3D, priorizando composicion por activos y envolventes generados con `SF3D` y `Blender`, y dejando la escena monolitica como ruta secundaria o comparativa
- [done] 9.11.1 Especificar el workflow general para `UC-3D-03` y `UC-3D-04`, dejando explicito si cada variante entrega escena completa, `blockout` navegable, set de activos desagregado por categorias o propuesta hibrida lista para ensamblar en `Blender`
- [done] 9.11.2 Derivar una primera variante `V1` para `UC-3D-03` y otra para `UC-3D-04` en `ComfyUIWorkflows/local/`, pero ya alineadas con composicion de activos y no con una dependencia del baseline `Hunyuan`
- [pending] 9.11.3 Ejecutar una validacion real local de la linea de escenas, conservando artefactos, documentando limites observados y dejando claro si el cierre `V1` se logra con escena final, `blockout`, set de activos reutilizable o composicion parcial util
- [done] 9.12 Definir el puente `ComfyUI -> Blender` para importacion, inspeccion, cleanup ligero, reparacion basica, materiales, catalogacion de `assets`, empaquetado y handoff a composicion y animacion controlada
- [done] 9.13 Preparar validaciones atomicas y por composicion para los workflows 3D, incluyendo fixtures, criterios de `pass/fail`, evidencia revisable y composiciones entre generacion de `assets`, importacion y revision en `Blender`
- [done] 9.14 Ejecutar la validacion diseñada para los workflows 3D y sus composiciones, pero ya sobre la linea `SF3D` replanificada, registrando evidencia y dejando claramente que partes quedaron aprobadas, cuales siguen pendientes y cuales requieren fallback o una futura linea externa `Hunyuan3D`
- [done] 9.15 Extender la misma estructura operativa de `runner`, presets y publicacion de artefactos para exponer la linea 3D desde WhatsApp, sin crear contratos paralelos y manteniendo el mismo alias aunque cambie el baseline tecnico
- [done] 9.16 Documentar troubleshooting para mallas rotas, texturas ausentes, ejes incorrectos, escalas absurdas, OOM, dependencias faltantes, tiempos excesivos y escenas demasiado ambiciosas para el baseline local
- [done] 9.17 Definir rutas fallback cuando la generacion 3D local no llegue: degradar a `blockout`, generar assets por separado, simplificar el caso de uso o derivar a una futura linea externa `Hunyuan3D` o a un perfil remoto

Regla de cierre para la linea 3D:

- `9.9` no deberia marcarse como `done` solo porque existan benchmarks o una
  validacion historica de `Hunyuan`; necesita al menos una variante
  `image -> 3D` con `SF3D` y un puente `texto -> imagen -> SF3D` corriendo de
  verdad y con importacion verificable en `Blender`
- las pruebas previas con `Hunyuan` via wrappers comunitarios de `ComfyUI`
  deben leerse como exploracion tecnica o anexo historico, no como cierre del
  `MVP`
- `9.11` puede cerrarse en una primera etapa si entrega un `blockout`, set de
  activos desagregado o composicion util y reutilizable en `Blender`, pero no
  debe presentarse como escena final limpia si aun no lo es
- para interiorismo, paisajismo o escenas pobladas, debe considerarse exito
  valido que la cadena produzca por separado muebles, personajes y envolventes
  con los que luego pueda montarse una escena mas satisfactoria y controlable
  en `Blender`
- ningun workflow 3D del `MVP` deberia depender de wrappers comunitarios de
  `Hunyuan`, de `pytorch3d` o de un perfil `24 GB+` disfrazado de baseline
- mientras la linea 3D siga en depuracion, los workflows publicados en
  `ComfyUI` no deberian esconder pasos criticos de escala, orientacion,
  texturizado o exportacion; deben dejar visibles suficientes puntos de
  diagnostico

Entregables por tarea:

- [done] 9.1 `docs/comfyui/3d-usecases.md`
- [done] 9.2 `docs/comfyui/3d-stack-evaluation.md`
- [done] 9.3 `docs/comfyui/3d-hardware-profiles.md`
- [done] 9.4 `docs/comfyui/3d-io-contract.md`
- [done] 9.5 `configs/comfyui/3d-custom-nodes-manifest.md`
- [done] 9.6 `configs/comfyui/3d-models-manifest.md`
- [done] 9.7 `docs/comfyui/3d-interface.md`
- [done] 9.8 `docs/comfyui/3d-usecase-map.md`
- [done] 9.9.1 `docs/comfyui/general-3d-object-workflow.md`
- [done] 9.9.2 workflows derivados `V1` `SF3D` versionados en `ComfyUIWorkflows/local/`
- [done] 9.9.3 evidencia y resultados de corrida real local para `UC-3D-01` y `UC-3D-02`, incluyendo `docs/comfyui/general-3d-object-workflow-results.md`
- [done] 9.10 criterios de calidad y aceptacion en `docs/comfyui/3d-quality-bar.md`
- [done] 9.11.1 `docs/comfyui/general-3d-scene-workflow.md`
- [done] 9.11.2 workflows derivados `V1` alineados con composicion por activos en `ComfyUIWorkflows/local/`
- [pending] 9.11.3 evidencia y resultados de corrida real local para `UC-3D-03` y `UC-3D-04`, incluyendo `docs/comfyui/general-3d-scene-workflow-results.md`
- [done] 9.12 `docs/comfyui/3d-blender-bridge.md`
- [done] 9.13 `docs/comfyui/3d-atomic-composed-validation.md`
- [done] 9.14 `docs/comfyui/3d-atomic-composed-validation-results.md`
- [done] 9.15 `docs/comfyui/3d-whatsapp-extension.md`
- [done] 9.16 `docs/comfyui/3d-troubleshooting.md`
- [done] 9.17 `docs/comfyui/3d-fallback-paths.md`

## Fase 10: Linea 3D nativa con `Hunyuan3D` fuera de `ComfyUI`

Objetivo:
Tras la fase 9, conservar lo que si quedo claro del trabajo 3D
(`UC-3D-*`, contrato de I/O, puente a `Blender`, validaciones y lenguaje de
producto), pero trasladar la ejecucion principal de `image -> 3D` a una linea
nativa basada en `Hunyuan3D`, operada fuera de `ComfyUI` mediante su propia
`web UI` y/o `API` local. La meta no es reabrir la exploracion, sino sustituir
la ambiguedad de los wrappers 3D en `ComfyUI` por una aplicacion separada, mas
limpia de depurar y mas coherente con la calidad visual buscada.

Hipotesis operativa:

- la fase 9 deja una base util de taxonomia, contratos y handoff, pero no
  demuestra una calidad visual suficiente para sostener `SF3D` como apuesta
  principal de producto
- el problema mas costoso hoy no es solo de compatibilidad tecnica, sino de
  ambiguedad operativa: mezclar `ComfyUI` de imagen/video con un stack 3D
  fragil complica diagnostico, mantenimiento y comunicacion de producto
- una linea nativa `Hunyuan3D` separada permite tener dos aplicaciones
  conviviendo sin confusion: `ComfyUI` para imagen/video y `Hunyuan3D` para 3D
- para el baseline local, importa mas cerrar una ruta clara y visualmente
  defendible que insistir en que todo viva dentro de `ComfyUI`
- `SF3D` y los workflows 3D de `ComfyUI` deben conservarse como benchmark
  tecnico, evidencia historica o fallback secundario, no como promesa vigente
  del producto 3D

Tareas:

- [done] 10.1 Consolidar la lectura final de la fase 9, distinguiendo `pass tecnico` de `fail visual`, y dejar por escrito el criterio oficial que justifica el replanteo
- [done] 10.2 Elegir la variante nativa objetivo de `Hunyuan3D` para la maquina local, explicitando si el baseline realista es `mini`, `turbo`, `shape-only` u otra combinacion y dejando fuera de alcance el camino que no quepa de verdad en el hardware disponible
- [done] 10.3 Definir la arquitectura operativa de la nueva linea: proceso local, `web UI`, `API`, carpetas de artefactos, logs y convivencia con `ComfyUI`
- [done] 10.4 Transponer `UC-3D-01`, `UC-3D-02`, `UC-3D-03` y `UC-3D-04` a la nueva linea nativa, manteniendo alias de producto y separando con claridad lo que sigue siendo `texto -> imagen` de lo que pasa a `imagen -> 3D`
- [done] 10.5 Redefinir perfiles de hardware, tiempos y barra de calidad para la linea nativa, distinguiendo ejecucion local, texturizado, `shape-only` y perfiles remotos si fueran necesarios
- [done] 10.6 Preparar una instalacion reproducible de `Hunyuan3D` nativo, con dependencias, pesos, comando de arranque y aislamiento suficiente para no romper la instalacion principal de `ComfyUI`
- [done] 10.7 Reusar y adaptar el contrato de entrada y salida de la fase 9 para la nueva linea, manteniendo formatos, nomenclatura, puente a `Blender` y criterios de catalogacion
- [done] 10.8 Diseñar la interfaz operativa de la linea nativa para usuario no tecnico, dejando claro cuando se usa la `web UI`, cuando se usa la `API` y que mensajes de estado debe recibir el operador
- [done] 10.9 Preparar una bateria de smoke tests y validaciones revisables para la aplicacion nativa, incluyendo logs, evidencia y comparativas honestas frente al baseline `SF3D`
- [done] 10.10 Ejecutar una validacion real local de `UC-3D-02` y `UC-3D-01` sobre `Hunyuan3D` nativo, con artefactos conservados, importacion en `Blender` y lectura visual explicita
- [done] 10.11 Replantear `UC-3D-03` y `UC-3D-04` como composicion por activos, `blockout` o envolventes sobre la nueva linea, evitando volver a vender escena monolitica donde no la haya
- [done] 10.12 Reescribir troubleshooting, fallbacks y mensajes de producto para reflejar que la ruta 3D principal ya no vive en `ComfyUI`
- [done] 10.13 Integrar la linea nativa con `Blender`, `runner` y futuros puntos de automatizacion, sin ocultar que el motor 3D corre en una aplicacion separada
- [done] 10.14 Cerrar la decision `go/no-go` sobre retirar `SF3D` del camino principal del producto y relegarlo a benchmark tecnico, anexo historico o contingencia secundaria

Regla de cierre para la linea 3D nativa:

- la fase 10 no se cierra por instalar `Hunyuan3D`; necesita al menos una
  corrida real `imagen -> 3D` con calidad visual claramente superior a la
  obtenida en la fase 9
- la nueva linea debe convivir con `ComfyUI` sin compartir el mismo runtime
  fragil ni crear confusion de operador sobre que aplicacion resuelve que
- las validaciones deben distinguir de forma explicita entre ejecucion
  tecnica, handoff a `Blender` y calidad visual util de producto
- `UC-3D-03` y `UC-3D-04` pueden cerrarse primero como `asset_set`,
  `blockout` o envolvente util; no deben presentarse como escena final limpia
  si la tecnologia no llega ahi

Entregables por tarea:

- [done] 10.1 `docs/hunyuan3d/phase-10-native-transition.md`
- [done] 10.4 `docs/hunyuan3d/usecase-map.md`
- [done] 10.2 `docs/hunyuan3d/hardware-profiles.md`
- [done] 10.3 `docs/hunyuan3d/native-runtime-architecture.md`
- [done] 10.5 ampliacion de `docs/hunyuan3d/hardware-profiles.md` con tiempos objetivo y barra de calidad
- [done] 10.6 `docs/hunyuan3d/installation.md` + `scripts/apps/install-hunyuan3d.sh` + `configs/systemd-user/hunyuan3d.service.template`
- [done] 10.7 `docs/hunyuan3d/io-contract.md`
- [done] 10.8 `docs/hunyuan3d/interface.md`
- [done] 10.9 `docs/hunyuan3d/smoke-validation.md` + `scripts/apps/hunyuan3d-smoke-validation.sh`
- [done] 10.10 `docs/hunyuan3d/validation-results.md` (smoke `PASS=10 FAIL=0`, glb `842 KB`, `23.376` vertices, inferencia `3.2 s`)
- [done] 10.11 `docs/hunyuan3d/scene-composition.md`
- [done] 10.12 `docs/hunyuan3d/troubleshooting.md` + `docs/hunyuan3d/fallback-paths.md`
- [done] 10.13 `src/openclaw_studio/runners/hunyuan3d.py` + registro en `registry.py` + `docs/hunyuan3d/runner-integration.md`
- [done] 10.14 `docs/hunyuan3d/sf3d-decision.md`

## Fase 11: Reapertura 3D en `ComfyUI` con `Trellis2 GGUF` por Calidad Visual

Objetivo:
Investigar `TRELLIS.2` con cuantizaciones `GGUF` dentro de `ComfyUI` como
candidato real para la ruta principal de generacion 3D local, reabriendo la
decision anterior si la mejora visual compensa la complejidad tecnica. La
prioridad de esta fase no es instalar otro stack por curiosidad, sino comprobar
si la calidad observada en la via `Trellis2 GGUF` supera claramente lo probado
con `SF3D` y `Hunyuan3D-2mini-Turbo`.

Hipotesis operativa:

- la calidad visual manda: si `Trellis2 GGUF` produce assets claramente mejores
  en el hardware local, debe tener opcion de desplazar la ruta vigente
- mantener la generacion 3D dentro de `ComfyUI` puede reducir friccion a largo
  plazo, porque la carga/descarga de modelos y el encadenado con imagen,
  limpieza, multivista, remesh, texturizado y exportacion viven en el mismo
  grafo
- la separacion nativa de `Hunyuan3D` sigue siendo valida como ruta estable ya
  integrada, pero no debe bloquear una alternativa de mayor calidad si aparece
- el riesgo principal no es conceptual, sino reproducibilidad: `TRELLIS.2`
  oficial apunta a perfiles de VRAM altos, y la via low-VRAM depende de
  cuantizaciones y wrappers comunitarios recientes

Tareas:

- [done] 11.1 Registrar la motivacion, fuentes tecnicas, riesgos y criterios de go/no-go para `Trellis2 GGUF` como nueva investigacion de calidad dentro de `ComfyUI`
- [done] 11.2 Preparar un entorno `ComfyUI` experimental aislado para `Trellis2 GGUF`, sin contaminar el runtime principal ya validado
- [done] 11.3 Auditar custom nodes, wheels y dependencias requeridas por `visualbruno/ComfyUI-Trellis2` y el soporte `GGUF` modular
- [done] 11.4 Descargar solo el set minimo de modelos `Trellis2 GGUF` para una prueba `512` low-VRAM, evitando bajar la suite completa a ciegas
- [done] 11.5 Derivar y comprobar un workflow minimo `UC-3D-02` `image -> Trellis2 GGUF Q4_K_M -> textured glb` y una variante opcional con limpieza de fondo
- [in progress] 11.6 Ejecutar una comparativa local con el mismo fixture usado por `SF3D` y con al menos una imagen creativa real
- [pending] 11.7 Importar outputs en `Blender`, registrar vertices/caras/texturas, y conservar artefactos revisables
- [in progress] 11.8 Comparar visualmente `SF3D`, `Hunyuan3D-2mini-Turbo` y `Trellis2 GGUF` bajo el mismo criterio de producto; decision cualitativa actual favorece claramente Trellis
- [in progress] 11.9 Cerrar decision `go/no-go`: mantener `Hunyuan3D` nativo, mover el producto 3D de vuelta a `ComfyUI` con `Trellis2 GGUF`, o conservar ambas rutas por perfil

Entregables por tarea:

- [done] 11.1 `docs/comfyui/trellis2-gguf-quality-investigation.md`
- [done] 11.2-11.3 `scripts/apps/comfyui-trellis2-gguf-validation.sh`
- [done] 11.5 `docs/comfyui/trellis2-gguf-interface.md` con evidencia API de Q4 texturizado
- [done] 11.4 evidencia local de modelos minimos en `~/ComfyUI-trellis2-lab/models/trellis2_gguf_minimum/`
- [in progress] 11.6-11.9 `docs/comfyui/trellis2-gguf-validation-results.md` registra el `.glb` Trellis Q4 texturizado; falta importarlo en `Blender` y cerrar comparativa formal

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
6. Productizacion de workflows ComfyUI para render de video e imagen
7. Productizacion de workflows ComfyUI para generacion de objetos y escenas 3D
8. Linea 3D nativa separada de ComfyUI
9. Capa de acciones seguras para WhatsApp
10. UX sin consola
11. Backup, update y validacion final

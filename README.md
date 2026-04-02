# OpenClaw Workstation

Repositorio para preparar una workstation Linux dedicada a `OpenClaw` como
asistente creativo local, usando WhatsApp como interfaz y aplicaciones del
sistema como backends seguros.

El foco actual del repo es:

- Blender
- ComfyUI
- ComfyUI-Manager
- Otras apps graficas del sistema

## Resultado esperado

- una instalacion Linux dedicada en un disco extraible
- un usuario de trabajo no privilegiado
- `OpenClaw` ejecutandose sin `root`
- acceso a apps creativas locales por acciones seguras
- uso cotidiano desde WhatsApp con una wake word y lenguaje natural despues
- 0 acceso operativo desde `OpenClaw` a discos internos no montados ni dados al usuario
- automontaje de GNOME deshabilitado y verificado
- bootstrap reproducible mediante `.env` y scripts
- mantenimiento simple para el adulto responsable

## Precondiciones

- Linux instalado en un disco extraible conectado a un equipo con otros discos internos
- una sesion grafica GNOME o compatible para lanzar apps GUI
- un usuario de trabajo normal
- `sudo` solo para instalacion y ajustes del sistema, nunca para el runtime normal
- los discos que no deben tocarse quedan fuera de `fstab` y del uso diario
- un canal enlazable como WhatsApp
- acceso a modelos o APIs de IA cuando el flujo lo requiera

## Idea principal

La fuente de verdad del setup es `.env`.

Flujo:

1. Ajustas `.env`.
2. Ejecutas el bootstrap en `audit`.
3. Ejecutas el bootstrap en `apply`.
4. Reejecutas el bootstrap cuando cambies rutas, politicas o servicios.

La meta es poder cambiar `.env` y converger el sistema otra vez sin rehacer la
instalacion a mano.

## Estado as-built de este repo

Hoy el repo ya implementa y documenta:

- bootstrap declarativo basado en `.env`
- checks de precondiciones
- hardening de discos, montajes y GNOME
- hardening base de `~/.openclaw`
- instalacion o actualizacion reproducible de OpenClaw
- provision de `systemd --user` para OpenClaw
- servicio `openclaw-node` opcional y deshabilitado por defecto en este perfil
- provision operativa de ComfyUI y `ComfyUI-Manager`
- wrappers locales para Blender y ComfyUI
- instalacion automatizable de `comfyui.service` desde el propio repo
- plugin local `studio-actions` para `before_dispatch`
- primeras acciones seguras para Blender y ComfyUI
- backup, restore, update y healthcheck de la workstation
- accesos directos `.desktop` para tareas administrativas comunes

Validado en este sistema:

- `bootstrapPending=false` en `openclaw status --all --json`
- `studio-actions` cargado como plugin `hook-only`
- wake word obligatoria en WhatsApp: `studio`
- mensajes sin wake word en WhatsApp se consumen en silencio y no pasan al agente general
- `scripts/apps/blender.sh smoke-test` genera `.blend` y `.png`
- `scripts/openclaw/test-studio-actions-plugin.sh` ejecuta acciones seguras de Blender
- `comfyui.service` queda `enabled` y escucha en `127.0.0.1:8188`
- `scripts/openclaw/test-studio-actions-plugin.sh` ejecuta acciones seguras de ComfyUI
- GNOME con `automount=false` y `automount-open=false`
- `openclaw status --all --json` reporta WhatsApp enlazado
- validacion real desde WhatsApp el 2 de abril de 2026: `studio abre blender` funciona y `studio, como esta blender?` responde correctamente
- `openclaw-node.service` queda deshabilitado para evitar ciclos de pairing no usados
- existen `backup`, `restore`, `update` y `workstation-health`

Pendiente de cierre final del plan:

- crear y migrar al usuario runtime dedicado en lugar de `eric`

Mejora futura no bloqueante:

- exponer el primer workflow real de video en ComfyUI

## Estructura del repo

```text
.
├── README.md
├── DevPlan.md
├── SAD.md
├── .env.example
├── configs/
├── docs/
├── plugins/
└── scripts/
```

## Configuracion declarativa

Variables importantes en [`.env.example`](/home/eric/Documents/OpenClaw/.env.example):

- `WORK_USER`
- `WORK_HOME`
- `STUDIO_DIR`
- `OPENCLAW_STATE_DIR`
- `OPENCLAW_INSTALL_METHOD`
- `OPENCLAW_PACKAGE_SPEC`
- `OPENCLAW_ENABLE_NODE_SERVICE`
- `OPENCLAW_DESKTOP_SHORTCUTS_ENABLE`
- `OPENCLAW_USAGE_PROFILE`
- `PRIMARY_CHAT_CHANNEL`
- `OPENCLAW_STUDIO_ACTIONS_ENABLE`
- `OPENCLAW_STUDIO_ACTIONS_PLUGIN_DIR`
- `OPENCLAW_STUDIO_ACTIONS_COMMAND_PREFIX`
- `OPENCLAW_STUDIO_ACTIONS_CHANNELS`
- `OPENCLAW_STUDIO_ACTIONS_ALLOW_GROUP_MESSAGES`
- `OPENCLAW_ALLOWED_BLENDER_PROJECTS_DIR`
- `BLENDER_BIN`
- `COMFYUI_DIR`
- `COMFYUI_REPO_URL`
- `COMFYUI_REPO_REF`
- `COMFYUI_VENV_DIR`
- `COMFYUI_HOST`
- `COMFYUI_PORT`
- `COMFYUI_INSTALL`
- `COMFYUI_INSTALL_REQUIREMENTS`
- `COMFYUI_ENABLE_SERVICE`
- `COMFYUI_MANAGER_INSTALL`
- `COMFYUI_MANAGER_INSTALL_METHOD`
- `COMFYUI_MANAGER_ENABLE`
- `COMFYUI_MANAGER_USE_LEGACY_UI`
- `COMFYUI_MANAGER_DIR`
- `COMFYUI_MANAGER_REPO_URL`
- `COMFYUI_MANAGER_REPO_REF`
- `COMFYUI_MANAGER_INSTALL_REQUIREMENTS`
- `OPENCLAW_ALLOWED_COMFYUI_OUTPUT_DIR`
- `OPENCLAW_BACKUP_DIR`
- `OPENCLAW_BACKUP_INCLUDE_CREDENTIALS`
- `OPENCLAW_BACKUP_INCLUDE_COMFY_OUTPUTS`
- `DISABLE_GNOME_AUTOMOUNT`
- `HARDEN_OPENCLAW`
- `ENABLE_OPENCLAW_SERVICES`

## Bootstrap recomendado

```bash
cp .env.example .env
editor .env
scripts/bootstrap/show-config.sh
scripts/bootstrap/apply-workstation.sh audit
scripts/bootstrap/apply-workstation.sh apply
```

`scripts/bootstrap/apply-workstation.sh` orquesta:

- validacion de precondiciones
- checks de usuario y grupos peligrosos
- verificacion de discos y montajes
- desactivacion de automontaje de GNOME
- instalacion de dependencias base del host
- instalacion o validacion de OpenClaw
- hardening base de OpenClaw
- preparacion del workspace creativo
- registro del plugin `studio-actions`
- provision de servicios de usuario
- instalacion opcional de accesos directos de escritorio
- setup base de ComfyUI y del manager integrado de ComfyUI
- diagnostico final

## Uso desde WhatsApp

La UX actual en WhatsApp exige una wake word al inicio:

- `studio`

Despues de la wake word ya se admite lenguaje natural sencillo:

- `studio abre blender`
- `studio como esta blender`
- `studio crea proyecto castillo`
- `studio abre proyecto castillo`
- `studio haz una prueba de blender`
- `studio abre comfyui`
- `studio inicia comfyui`
- `studio reinicia comfyui`
- `studio como esta comfyui`

Tambien existe modo tecnico:

- `studio`
- `studio blender status`
- `studio blender new castillo`
- `studio blender open castillo`
- `studio blender smoke-test prueba-ws`
- `studio comfyui status`
- `studio comfyui start`
- `studio comfyui restart`
- `studio comfyui open`
- `studio comfyui stop`

Comportamiento importante:

- si el mensaje no empieza con `studio`, el plugin lo consume en silencio en WhatsApp
- ese mensaje no debe llegar al agente general
- el canal actual se usa desde el chat contigo mismo, no desde un contacto aparte llamado `OpenClaw`

## Operacion diaria de ComfyUI

El runtime operativo de ComfyUI queda como un servicio de usuario llamado
`comfyui.service`.

Para instalar o regenerar la unidad desde el propio repo:

```bash
scripts/apps/comfyui.sh install-service
```

Para operacion diaria:

```bash
scripts/apps/comfyui.sh service-status
scripts/apps/comfyui.sh start-service
scripts/apps/comfyui.sh restart-service
scripts/apps/comfyui.sh stop-service
scripts/apps/comfyui.sh open-ui
```

En la practica, reiniciar ComfyUI equivale a reiniciar `comfyui.service`.

## Primeras pruebas utiles

```bash
scripts/bootstrap/show-config.sh
scripts/bootstrap/apply-workstation.sh audit
scripts/doctor/openclaw-status.sh
scripts/doctor/workstation-health.sh
scripts/services/user-services.sh status
scripts/apps/blender.sh status
scripts/apps/blender.sh smoke-test blender-smoke
scripts/apps/comfyui.sh status
scripts/apps/comfyui.sh install-service
scripts/apps/comfyui.sh service-status
scripts/apps/comfyui.sh restart-service
scripts/apps/comfyui.sh open-ui
scripts/openclaw/install-studio-actions-plugin.sh apply
scripts/openclaw/test-studio-actions-plugin.sh "studio como esta blender"
scripts/openclaw/test-studio-actions-plugin.sh "studio crea proyecto whatsapp-demo"
scripts/openclaw/test-studio-actions-plugin.sh "studio como esta comfyui"
scripts/openclaw/test-studio-actions-plugin.sh "studio reinicia comfyui"
scripts/openclaw/test-studio-actions-plugin.sh "studio abre comfyui"
scripts/openclaw/backup.sh audit
scripts/openclaw/update.sh audit
```

## Documentacion

- Plan por fases y estado: [`DevPlan.md`](/home/eric/Documents/OpenClaw/DevPlan.md)
- Arquitectura del sistema: [`SAD.md`](/home/eric/Documents/OpenClaw/SAD.md)
- Acciones seguras: [`docs/architecture/actions.md`](/home/eric/Documents/OpenClaw/docs/architecture/actions.md)
- Bootstrap: [`docs/operations/bootstrap.md`](/home/eric/Documents/OpenClaw/docs/operations/bootstrap.md)
- Uso por WhatsApp: [`docs/operations/whatsapp.md`](/home/eric/Documents/OpenClaw/docs/operations/whatsapp.md)
- Uso diario: [`docs/operations/daily-use.md`](/home/eric/Documents/OpenClaw/docs/operations/daily-use.md)
- Mantenimiento admin: [`docs/operations/admin-maintenance.md`](/home/eric/Documents/OpenClaw/docs/operations/admin-maintenance.md)
- Backup y updates: [`docs/operations/backup-and-updates.md`](/home/eric/Documents/OpenClaw/docs/operations/backup-and-updates.md)
- Checklist de aceptacion: [`docs/operations/acceptance.md`](/home/eric/Documents/OpenClaw/docs/operations/acceptance.md)
- Blender: [`docs/operations/blender.md`](/home/eric/Documents/OpenClaw/docs/operations/blender.md)
- ComfyUI: [`docs/operations/comfyui.md`](/home/eric/Documents/OpenClaw/docs/operations/comfyui.md)
- Discos y automontaje: [`docs/security/disks-and-automount.md`](/home/eric/Documents/OpenClaw/docs/security/disks-and-automount.md)

## Secretos y datos locales

- [`.env`](/home/eric/Documents/OpenClaw/.env) es local y no se versiona
- `.gitignore` excluye `.env` y `.codex`
- no se deben guardar en Git tokens, sesiones ni credenciales reales

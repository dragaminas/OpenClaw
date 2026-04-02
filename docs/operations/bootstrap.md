# Bootstrap Operativo

## Flujo recomendado

```bash
cp .env.example .env
editor .env
scripts/bootstrap/show-config.sh
scripts/bootstrap/apply-workstation.sh audit
scripts/bootstrap/apply-workstation.sh apply
```

Cuando cambies `.env`, vuelve a ejecutar:

```bash
scripts/bootstrap/apply-workstation.sh audit
scripts/bootstrap/apply-workstation.sh apply
```

La idea es converger el sistema a partir de la configuracion declarativa, no
mantener una lista larga de pasos manuales.

## Que hace el bootstrap

`scripts/bootstrap/apply-workstation.sh` orquesta:

- precondiciones
- dependencias base del host
- checks de usuario
- discos y montajes
- ajustes de GNOME
- validacion o instalacion de OpenClaw
- hardening base de OpenClaw
- preparacion del workspace creativo
- registro del plugin `studio-actions`
- provision de servicios `systemd --user`
- instalacion opcional de accesos directos `.desktop`
- setup de ComfyUI y del manager integrado de ComfyUI
- provision o regeneracion de `comfyui.service`
- diagnostico final

## Modos

- `audit`: solo comprueba y reporta
- `apply`: aplica cambios seguros e idempotentes en la medida de lo posible

## Variables especialmente importantes

- `WORK_USER`
- `WORK_HOME`
- `STUDIO_DIR`
- `OPENCLAW_STATE_DIR`
- `OPENCLAW_INSTALL_METHOD`
- `OPENCLAW_PACKAGE_SPEC`
- `OPENCLAW_ENABLE_NODE_SERVICE`
- `OPENCLAW_DESKTOP_SHORTCUTS_ENABLE`
- `OPENCLAW_STUDIO_ACTIONS_ENABLE`
- `OPENCLAW_STUDIO_ACTIONS_COMMAND_PREFIX`
- `ENABLE_OPENCLAW_SERVICES`
- `COMFYUI_INSTALL`
- `COMFYUI_REPO_REF`
- `COMFYUI_ENABLE_SERVICE`
- `COMFYUI_MANAGER_INSTALL_METHOD`
- `DISABLE_GNOME_AUTOMOUNT`
- `HARDEN_OPENCLAW`

## Verificacion posterior

```bash
scripts/doctor/openclaw-status.sh
scripts/doctor/workstation-health.sh
scripts/services/user-services.sh status
scripts/apps/blender.sh status
scripts/apps/comfyui.sh status
scripts/apps/comfyui.sh service-status
scripts/apps/comfyui.sh restart-service
openclaw plugins inspect studio-actions --json
```

Si el objetivo es probar WhatsApp, añade:

```bash
scripts/openclaw/test-studio-actions-plugin.sh "studio como esta blender"
```

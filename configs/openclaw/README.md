# OpenClaw Config Templates

Este directorio queda reservado para plantillas o fragmentos de configuracion
relacionados con OpenClaw.

Hoy el repo configura OpenClaw principalmente por script, usando:

- `OPENCLAW_INSTALL_METHOD`
- `OPENCLAW_PACKAGE_SPEC`
- `OPENCLAW_ENABLE_NODE_SERVICE`
- `OPENCLAW_USAGE_PROFILE`
- `OPENCLAW_ALLOWED_BLENDER_PROJECTS_DIR`
- `OPENCLAW_ALLOWED_COMFYUI_OUTPUT_DIR`
- `plugins.load.paths`
- `plugins.entries.studio-actions.config.commandPrefix`
- `plugins.entries.studio-actions.config.channels`
- `plugins.entries.studio-actions.config.allowGroupMessages`

Tambien se asume una operacion local con gateway en loopback y servicios
`systemd --user`.

En esta workstation el servicio `openclaw-node.service` queda como opcional.
Para el caso de uso actual se deja deshabilitado por defecto y solo se activa si
`OPENCLAW_ENABLE_NODE_SERVICE=true`.

Las plantillas no deben incluir secretos reales.

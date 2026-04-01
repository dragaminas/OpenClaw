# OpenClaw Config Templates

Este directorio queda reservado para plantillas o fragmentos de configuracion
relacionados con OpenClaw.

Hoy el repo configura OpenClaw principalmente por script, usando:

- `plugins.load.paths`
- `plugins.entries.studio-actions.config.commandPrefix`
- `plugins.entries.studio-actions.config.channels`
- `plugins.entries.studio-actions.config.allowGroupMessages`

Tambien se asume una operacion local con gateway en loopback y servicios
`systemd --user`.

Las plantillas no deben incluir secretos reales.

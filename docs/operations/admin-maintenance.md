# Mantenimiento Admin

## Tareas rapidas

```bash
scripts/doctor/workstation-health.sh
scripts/services/user-services.sh status
scripts/services/user-services.sh restart
scripts/openclaw/backup.sh apply
scripts/openclaw/update.sh audit
```

## Accesos directos

Con `scripts/desktop/install-shortcuts.sh apply` quedan accesos directos en
`~/.local/share/applications` para:

- `OpenClaw Health`
- `Restart Studio Services`
- `OpenClaw Backup`

## Politica actual del host

- `openclaw-gateway.service` es obligatorio
- `comfyui.service` es obligatorio para la UX diaria
- `openclaw-node.service` queda deshabilitado por defecto en este perfil
- el usuario de runtime no deberia permanecer en `sudo` ni `adm`

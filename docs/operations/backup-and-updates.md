# Backup y Updates

## Backup ligero

Por defecto el backup incluye configuracion y estado ligero, y excluye secretos
innecesarios y artefactos pesados.

```bash
scripts/openclaw/backup.sh audit
scripts/openclaw/backup.sh apply
```

Exclusiones por defecto:

- `~/.openclaw/credentials`
- `~/.openclaw/agents/main/agent/auth-profiles.json`
- `ComfyUI/models`
- `ComfyUI/output`

## Restore

Usa solo archivos de backup generados por este repo.

```bash
scripts/openclaw/restore.sh audit /ruta/al/backup.tar.gz
scripts/openclaw/restore.sh apply /ruta/al/backup.tar.gz
```

## Update segura de OpenClaw

```bash
scripts/openclaw/update.sh audit
scripts/openclaw/update.sh apply
```

En `apply` el flujo hace:

1. backup ligero
2. update o reinstalacion de OpenClaw
3. convergencia de servicios
4. `openclaw doctor --repair --non-interactive`
5. healthcheck final

## Checklist post-update

- `scripts/doctor/workstation-health.sh`
- `openclaw status --all --json`
- `scripts/openclaw/test-studio-actions-plugin.sh "studio como esta comfyui"`
- `scripts/openclaw/test-studio-actions-plugin.sh "studio crea proyecto update-check"`
- `scripts/apps/comfyui.sh status`

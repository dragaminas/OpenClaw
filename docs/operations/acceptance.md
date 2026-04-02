# Aceptacion

## Checklist actual

- [x] `bootstrapPending=false`
- [x] WhatsApp enlazado en `openclaw status --all --json`
- [x] validacion real desde WhatsApp el 2 de abril de 2026: `studio abre blender` abre Blender y `studio, como esta blender?` responde estado
- [x] `openclaw-gateway.service` habilitado y activo
- [x] `comfyui.service` habilitado y activo
- [x] `openclaw-node.service` deshabilitado por politica local
- [x] `scripts/hardening/check-mounts.sh` confirma NVMe internos no montados
- [x] `scripts/openclaw/test-studio-actions-plugin.sh` valida acciones seguras de Blender
- [x] `scripts/openclaw/test-studio-actions-plugin.sh` valida acciones seguras de ComfyUI
- [x] existen runbooks de backup, restore y update
- [x] existen accesos directos `.desktop` para health, restart y backup

## Incidencias actuales

- queda pendiente retirar a `eric` de `sudo` y `adm` para cumplir el objetivo de usuario no privilegiado

## Backlog de mejoras

- exponer el primer workflow real de imagen o video en ComfyUI
- añadir backups opcionales por proyecto creativo
- ampliar accesos directos para tareas de soporte

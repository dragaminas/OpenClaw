# ComfyUI

## Estado actual

El repo ya contempla una provision declarativa de ComfyUI y `ComfyUI-Manager`,
pero todavia no expone ComfyUI por la misma capa segura de WhatsApp que Blender.

Actualmente se cubre:

- clonacion o actualizacion del repo
- creacion del venv
- recreacion del venv si falta `pip`
- instalacion opcional de `requirements`
- provision de `comfyui.service` en `systemd --user`
- instalacion de `ComfyUI-Manager`

## Flujo previsto

1. Ajustar variables `COMFYUI_*` en `.env`
2. Ejecutar `scripts/apps/install-comfyui.sh audit`
3. Ejecutar `scripts/apps/install-comfyui.sh apply`
4. Ejecutar `scripts/apps/install-comfyui-manager.sh apply`
5. Ejecutar `scripts/services/install-comfyui-service.sh audit`
6. Si ya estan las dependencias, activar `COMFYUI_ENABLE_SERVICE=true`
7. Ejecutar `scripts/services/install-comfyui-service.sh apply`

## Estado esperado

- repo clonado en `COMFYUI_DIR`
- venv creado en `COMFYUI_VENV_DIR`
- `main.py` presente
- servicio `comfyui.service` disponible en `systemd --user`
- `ComfyUI-Manager` instalado en `custom_nodes/comfyui-manager`

## Variables importantes

- `COMFYUI_DIR`
- `COMFYUI_REPO_URL`
- `COMFYUI_REPO_REF`
- `COMFYUI_VENV_DIR`
- `COMFYUI_HOST`
- `COMFYUI_PORT`
- `COMFYUI_INSTALL`
- `COMFYUI_CREATE_VENV`
- `COMFYUI_RECREATE_VENV_IF_PIP_MISSING`
- `COMFYUI_INSTALL_REQUIREMENTS`
- `COMFYUI_ENABLE_SERVICE`
- `COMFYUI_MANAGER_INSTALL`
- `COMFYUI_MANAGER_DIR`
- `COMFYUI_MANAGER_REPO_URL`
- `COMFYUI_MANAGER_REPO_REF`
- `COMFYUI_MANAGER_INSTALL_REQUIREMENTS`

## Diagnostico rapido

```bash
scripts/apps/comfyui.sh status
scripts/apps/comfyui.sh manager-status
scripts/apps/comfyui.sh check-port
scripts/apps/comfyui.sh service-status
```

## Nota sobre Python

Si el venv se crea sin `pip`, normalmente faltara `python3-venv` o
`python3.12-venv` en el host.

## Pendiente

- validar arranque estable del servicio
- validar escucha real en `COMFYUI_PORT`
- exponer acciones seguras de ComfyUI por WhatsApp

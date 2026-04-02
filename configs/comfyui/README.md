# ComfyUI Config

Este directorio queda reservado para ajustes y archivos relacionados con la
instalacion local de ComfyUI.

Hoy el repo usa principalmente variables en `.env` para controlar:

- ruta del repo
- branch, tag o alias `latest-stable` basado en la ultima release oficial
- ruta del venv
- host y puerto
- instalacion de requirements
- activacion del servicio de usuario
- instalacion del manager integrado de ComfyUI o del flujo legacy

La plantilla operativa principal del servicio vive en
[`configs/systemd-user/comfyui.service.template`](/home/eric/Documents/OpenClaw/configs/systemd-user/comfyui.service.template).

Para instalar o regenerar la unidad de usuario desde el wrapper principal:

```bash
scripts/apps/comfyui.sh install-service
```

Para migrar al manager integrado recomendado por upstream:

```bash
scripts/apps/install-comfyui-manager.sh apply
```

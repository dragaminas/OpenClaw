# ComfyUI Config

Este directorio queda reservado para ajustes y archivos relacionados con la
instalacion local de ComfyUI.

Hoy el repo usa principalmente variables en `.env` para controlar:

- ruta del repo
- branch o ref
- ruta del venv
- host y puerto
- instalacion de requirements
- activacion del servicio de usuario
- instalacion de `ComfyUI-Manager`

La plantilla operativa principal del servicio vive en
[`configs/systemd-user/comfyui.service.template`](/home/eric/Documents/OpenClaw/configs/systemd-user/comfyui.service.template).

# ComfyUI

## Estado actual

El repo ya contempla una provision declarativa de ComfyUI y `ComfyUI-Manager`,
y ahora expone una primera capa segura de ComfyUI por el mismo plugin de
WhatsApp.

Actualmente se cubre:

- clonacion o actualizacion del repo
- resolucion opcional de la ultima release estable de ComfyUI con `COMFYUI_REPO_REF=latest-stable`
- creacion del venv
- recreacion del venv si falta `pip`
- instalacion opcional de `requirements`
- provision de `comfyui.service` en `systemd --user`
- instalacion de `comfyui.service` desde el wrapper principal de ComfyUI
- instalacion del manager integrado de ComfyUI
- migracion del `ComfyUI-Manager` legacy en `custom_nodes` a backup cuando se usa el manager integrado
- arranque y parada controlados del servicio
- reinicio controlado del servicio
- apertura de la interfaz web local
- acciones seguras minimas via `studio-actions`

## Flujo previsto

1. Ajustar variables `COMFYUI_*` en `.env`
2. Ejecutar `scripts/apps/install-comfyui.sh audit`
3. Ejecutar `scripts/apps/install-comfyui.sh apply`
4. Ejecutar `scripts/apps/install-comfyui-manager.sh apply`
5. Ejecutar `scripts/services/install-comfyui-service.sh audit`
6. Si ya estan las dependencias, activar `COMFYUI_ENABLE_SERVICE=true`
7. Ejecutar `scripts/apps/comfyui.sh install-service`

## Defaults actuales

- `COMFYUI_REPO_REF=latest-stable` para seguir la ultima release estable publicada por ComfyUI
- `COMFYUI_MANAGER_INSTALL_METHOD=core` para usar el manager integrado recomendado por upstream
- `COMFYUI_MANAGER_ENABLE=true` para arrancar ComfyUI con `--enable-manager`
- `COMFYUI_MANAGER_USE_LEGACY_UI=false` para usar la UI nueva del manager

Si necesitas una instalacion totalmente determinista, fija `COMFYUI_REPO_REF` a
un tag concreto en `.env`.

## Operacion diaria

ComfyUI se opera como servicio de usuario `systemd --user`. En la practica,
reiniciar ComfyUI equivale a reiniciar `comfyui.service`.

Comandos recomendados:

```bash
scripts/apps/comfyui.sh install-service
scripts/apps/comfyui.sh service-status
scripts/apps/comfyui.sh start-service
scripts/apps/comfyui.sh restart-service
scripts/apps/comfyui.sh stop-service
scripts/apps/comfyui.sh open-ui
```

Script de bajo nivel para auditar o regenerar la unidad:

```bash
scripts/services/install-comfyui-service.sh audit
scripts/services/install-comfyui-service.sh apply
```

## Estado esperado

- repo clonado en `COMFYUI_DIR`
- venv creado en `COMFYUI_VENV_DIR`
- `main.py` presente
- `manager_requirements.txt` presente
- servicio `comfyui.service` disponible en `systemd --user`
- paquete Python `comfyui_manager` instalado en el venv
- si existia `custom_nodes/comfyui-manager*`, queda migrado fuera de `custom_nodes` a `.legacy-manager-backups/`

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
- `COMFYUI_MANAGER_INSTALL_METHOD`
- `COMFYUI_MANAGER_ENABLE`
- `COMFYUI_MANAGER_USE_LEGACY_UI`
- `COMFYUI_MANAGER_DIR`
- `COMFYUI_MANAGER_REPO_URL`
- `COMFYUI_MANAGER_REPO_REF`
- `COMFYUI_MANAGER_INSTALL_REQUIREMENTS`

## Diagnostico rapido

```bash
scripts/apps/comfyui.sh status
scripts/apps/comfyui.sh install-service
scripts/apps/comfyui.sh manager-status
scripts/apps/comfyui.sh check-port
scripts/apps/comfyui.sh service-status
scripts/apps/comfyui.sh start-service
scripts/apps/comfyui.sh restart-service
scripts/apps/comfyui.sh open-ui
```

## Prueba del wrapper seguro

```bash
scripts/actions/comfyui-action.sh status
scripts/actions/comfyui-action.sh start
scripts/actions/comfyui-action.sh restart
scripts/actions/comfyui-action.sh open
scripts/actions/comfyui-action.sh stop
```

## Prueba del puente local

```bash
scripts/openclaw/test-studio-actions-plugin.sh "studio como esta comfyui"
scripts/openclaw/test-studio-actions-plugin.sh "studio inicia comfyui"
scripts/openclaw/test-studio-actions-plugin.sh "studio reinicia comfyui"
scripts/openclaw/test-studio-actions-plugin.sh "studio abre comfyui"
```

## Uso esperado desde WhatsApp

- `studio como esta comfyui`
- `studio inicia comfyui`
- `studio reinicia comfyui`
- `studio abre comfyui`
- `studio para comfyui`

## Nota sobre Python

Si el venv se crea sin `pip`, normalmente faltara `python3-venv` o
`python3.12-venv` en el host.

## Nota sobre el Manager

Para instalaciones manuales, la recomendacion actual de ComfyUI es usar el
manager integrado en core con `manager_requirements.txt` y `--enable-manager`.
El metodo `custom_nodes/comfyui-manager` queda como flujo legacy y el repo lo
mantiene solo para compatibilidad o migracion.

## Pendiente

- exponer workflows reales de imagen o video sobre esta base

## Productizacion de workflows

El inventario inicial de casos de uso para la Fase 8 vive en
`docs/comfyui/usecases.md`.

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

## Runner canonico

La smoke validation implementada en `8.19` ya introduce la primera forma de
runner reutilizable para `ComfyUI`:

```bash
scripts/apps/comfyui-smoke-validation.sh --run-id smoke-light-5
scripts/apps/comfyui-smoke-validation.sh --run-id smoke-demo-vid04 --case-id SMK-VID-04-01
```

La evolucion prevista no es crear otro stack distinto para WhatsApp, sino
convertir este runner en la implementacion `ComfyUI` de la interfaz canonica
definida en `docs/architecture/runner-interface.md`.

Eso significa reutilizar:

- el mismo `run_id`
- los mismos `case_id`
- los mismos manifiestos
- la misma evidencia
- los mismos estados

La capa segura del contrato ya se puede invocar tambien con:

```bash
scripts/actions/runner-action.sh describe comfyui
scripts/actions/runner-action.sh list-targets comfyui validate_smoke
scripts/actions/runner-action.sh status comfyui smoke-light-5
scripts/actions/runner-action.sh result comfyui smoke-light-5
```

## Prueba del puente local

```bash
scripts/openclaw/test-studio-actions-plugin.sh "studio como esta comfyui"
scripts/openclaw/test-studio-actions-plugin.sh "studio inicia comfyui"
scripts/openclaw/test-studio-actions-plugin.sh "studio reinicia comfyui"
scripts/openclaw/test-studio-actions-plugin.sh "studio abre comfyui"
scripts/openclaw/test-studio-actions-plugin.sh "studio comfyui workflows"
scripts/openclaw/test-studio-actions-plugin.sh "studio que hace prepara-video"
scripts/openclaw/test-studio-actions-plugin.sh "studio compara prepara-video y render-video"
scripts/openclaw/test-studio-actions-plugin.sh "studio comfyui abre workflow prepara-video"
scripts/openclaw/test-studio-actions-plugin.sh "studio comfyui ruta workflow prepara-video"
scripts/openclaw/test-studio-actions-plugin.sh "studio comfyui smoke"
scripts/openclaw/test-studio-actions-plugin.sh "studio comfyui smoke SMK-VID-04-01"
scripts/openclaw/test-studio-actions-plugin.sh "studio comfyui estado <run_id>"
scripts/openclaw/test-studio-actions-plugin.sh "studio comfyui evidencia <run_id>"
```

## Uso esperado desde WhatsApp

- `studio como esta comfyui`
- `studio inicia comfyui`
- `studio reinicia comfyui`
- `studio abre comfyui`
- `studio para comfyui`
- `studio comfyui workflows`
- `studio que hace prepara-video`
- `studio comfyui que hace prepara-video`
- `studio compara prepara-video y render-video`
- `studio comfyui abre workflow <alias>`
- `studio comfyui ruta workflow <alias>`
- `studio comfyui smoke`
- `studio comfyui smoke <case_id>`
- `studio comfyui validate atomic <test_id>`
- `studio comfyui validate composed <test_id>`
- `studio comfyui estado <run_id>`
- `studio comfyui cancela <run_id>`
- `studio comfyui evidencia <run_id>`

`validate_atomic` y `validate_composed` hoy ya entran por el mismo runner, pero
responden `unsupported` hasta que `8.18` implemente la ejecucion real.

## Biblioteca visible en ComfyUI

Los workflows OpenClaw publicados para inspeccion manual viven como templates
nativos bajo:

- `~/ComfyUI/custom_nodes/openclaw-workflows/example_workflows/`

La fuente de verdad sigue siendo `ComfyUIWorkflows/local/` en el repo. La
biblioteca local publica symlinks o copias hacia esos JSON canonicos y deja los
aliases humanos del catalogo Python como nombre visible:

- `prepara-video`
- `render-video`
- `render-frame`
- `explora-estilos`

Si `ComfyUI` ya estaba abierto antes de crear por primera vez el modulo
`openclaw-workflows`, conviene reiniciarlo para que registre la ruta
`/api/workflow_templates/openclaw-workflows/...`.

`studio comfyui abre workflow <alias>` ya no solo abre la UI: ahora abre
`ComfyUI` con la query `?template=<alias>&source=openclaw-workflows`, para que
el canvas cargue el template exacto de `OpenClaw` en vez de dejar al usuario en
el ultimo grafo que tenia abierto.

`studio comfyui workflows` ahora devuelve una descripcion explicita de cada
workflow, incluyendo que hace, su entrada obligatoria y la salida principal.
Ademas, `studio que hace <alias>` y `studio comfyui que hace <alias>` explican
un workflow concreto usando el mismo catalogo canonico.

Para estas preguntas asesoradas, `studio-actions` ya no responde con un bloque
fijo. Ahora prepara contexto del workflow real y lo inyecta al agente general
via `before_prompt_build`, para que la respuesta pueda ser mas libre e
interactiva sin perder grounding.

## Nota sobre Python

Si el venv se crea sin `pip`, normalmente faltara `python3-venv` o
`python3.12-venv` en el host.

## Nota sobre el Manager

Para instalaciones manuales, la recomendacion actual de ComfyUI es usar el
manager integrado en core con `manager_requirements.txt` y `--enable-manager`.
El metodo `custom_nodes/comfyui-manager` queda como flujo legacy y el repo lo
mantiene solo para compatibilidad o migracion.

## Pendiente

- implementar `validate_atomic`
- implementar `validate_composed`

## Productizacion de workflows

El inventario inicial de casos de uso para la Fase 8 vive en
`docs/comfyui/usecases.md`.

La definicion de interfaz guiada y la base Python para contratos y sesiones vive
en `docs/comfyui/interface.md` y `src/openclaw_studio/`.

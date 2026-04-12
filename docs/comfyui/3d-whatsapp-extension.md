# Extension de la Linea 3D a WhatsApp

Este documento implementa la tarea `9.15` del `DevPlan`.
Describe como exponer `UC-3D-*` desde la misma estructura de `runner`,
catalogo, presets y publicacion de artefactos ya usada en la linea de
imagen/video.

## Decision principal

La linea 3D no debe abrir contratos nuevos para WhatsApp.

Debe reutilizar:

- el mismo catalogo Python
- los mismos aliases amigables
- la misma biblioteca `openclaw-workflows`
- la misma idea de `preset`

## Superficie visible

Consultas asesoradas:

- `studio comfyui workflows`
- `studio que hace texto-a-3d`
- `studio que hace imagen-a-3d`
- `studio que hace imagen-a-escena-3d`
- `studio compara imagen-a-3d y imagen-a-escena-3d`

Presets que deberian poder invocarse cuando la operacion exista:

- `uc-3d-01-text-to-asset-sf3d-bridge`
- `uc-3d-02-image-to-asset-sf3d-single-image`
- `uc-3d-03-text-to-scene-sf3d-asset-pack-bridge`
- `uc-3d-04-image-to-scene-sf3d-asset-pack`

## Respuesta de producto esperada

La respuesta corta al chat deberia decir:

- si se generara un `asset` o un `set`
- si la ruta es `shape-first`
- si la escena se descompone
- si el stack local esta bloqueado

Ejemplo:

```text
run_id=uc-3d-02-demo-1
status=prepared_runtime_pending_model_access
target=uc-3d-02-image-to-asset-sf3d-single-image
message=La ruta baseline ya esta alineada con Stable Fast 3D; falta cerrar la extension y el acceso al modelo para validar el .glb real.
```

## Regla

WhatsApp no deberia preguntar por nodos ni por modelos.
Deberia hablar en terminos de:

- `asset`
- `set`
- `blockout`
- `pieza`
- `envolvente`

# Arquitectura Operativa de la Linea `Hunyuan3D` Nativa

Este documento implementa la tarea `10.3` del `DevPlan`.
Define como debe convivir la nueva app 3D con `ComfyUI` y `Blender` sin volver
al acoplamiento fragil de la fase 9.

## Principio rector

La linea 3D ya no debe vivir dentro del mismo runtime de `ComfyUI`.

Arquitectura objetivo:

- `ComfyUI` para imagen, video y semillas visuales
- `Hunyuan3D` nativo para inferencia 3D
- `Blender` para inspeccion, cleanup y ensamblaje

La separacion debe ser real en:

- proceso
- `venv`
- puertos
- logs
- carpetas de artefactos

## Componentes canonicos

| Componente | Rol | Puerto recomendado | Regla |
| --- | --- | --- | --- |
| `ComfyUI` | imagen, video, semillas y preproceso | `8188` | no cargar aqui la logica 3D principal |
| `Hunyuan3D Gradio` | interfaz operativa manual | `7860` | baseline para operador humano |
| `Hunyuan3D API` | automatizacion y futuros bridges | `8081` | lanzar con flags explicitas, no confiar en defaults implicitos |
| `Blender` | inspeccion, import, cleanup y catalogacion | n/a | etapa normal de producto |

## Regla de procesos

En el perfil `minimum` no deberiamos operar asi:

- `ComfyUI` generando pesado
- `Hunyuan3D Gradio` abierto
- `Hunyuan3D API` sirviendo inferencia

Todo a la vez sobre la misma `RTX 3060 12 GB`.

Regla recomendada:

1. generar o preparar imagen en `ComfyUI` si hace falta
2. dejar `ComfyUI` en reposo
3. correr la inferencia 3D en `Hunyuan3D`
4. importar resultado en `Blender`

## Runtime en disco

Separacion recomendada:

```text
/home/eric/ComfyUI/
/home/eric/Hunyuan3D-2/
/home/eric/Hunyuan3D-2/.venv/
/home/eric/Documents/OpenClaw/
```

Regla:

- nunca instalar dependencias de `Hunyuan3D` en el `venv` de `ComfyUI`
- nunca instalar wrappers de `ComfyUI` como sustituto de la app nativa

## Carpeta de artefactos

La raiz de trabajo 3D debe conservar la estructura de la fase 9, pero con un
ramal explicito para `Hunyuan3D`:

```text
$STUDIO_DIR/Assets3D/<project>/<entity_id>/
├── input/
│   ├── refs/
│   ├── multiview/
│   ├── masks/
│   └── manifests/
├── comfyui/
│   ├── output/
│   ├── temp/
│   └── logs/
├── hunyuan3d/
│   ├── requests/
│   ├── output/
│   ├── previews/
│   └── logs/
└── blender/
    ├── imports/
    ├── exports/
    └── catalog/
```

Lectura:

- `comfyui/` conserva semillas o preprocesados cuando existan
- `hunyuan3d/` pasa a ser la fuente canonica del `glb` 3D
- `blender/` sigue siendo la etapa de handoff y normalizacion final

## Modos de operacion

### Modo 1: `UC-3D-02` directo

Ruta:

1. operador abre `Hunyuan3D Gradio`
2. carga imagen de referencia
3. ejecuta `shape-first`
4. guarda `glb`
5. importa en `Blender`

Aqui `ComfyUI` no es obligatorio.

### Modo 2: `UC-3D-01` con puente

Ruta:

1. `ComfyUI` genera imagen semilla
2. la imagen se publica en `input/refs/`
3. `Hunyuan3D` consume esa imagen
4. el `glb` sale por la rama `hunyuan3d/output/`
5. `Blender` lo inspecciona

Aqui `ComfyUI` sigue siendo util, pero solo como fase previa.

### Modo 3: automatizacion por `API`

Ruta:

1. un `runner` o script local prepara la imagen
2. llama a `Hunyuan3D API`
3. recibe `glb`
4. registra manifest, logs y preview
5. deja el asset listo para `Blender`

Esta es la ruta correcta para integraciones futuras.

### Modo 4: escena por piezas

Ruta:

1. se decide la lista de activos
2. cada activo corre como `UC-3D-02`
3. los `glb` se catalogan por separado
4. `Blender` compone

No debemos volver a prometer escena monolitica como baseline.

## Servidor `API`

El repo oficial `Hunyuan3D-2` expone `api_server.py`.
Su lectura operativa nos deja estas reglas:

- el `API` puede correr separado de la `web UI`
- `model_path` y `tex_model_path` deben fijarse de forma explicita
- `enable_tex` debe tratarse como opt-in y no como baseline local, pero si
  puede activarse en corridas de prueba sobre `3060`

Comando recomendado para `shape-first` local:

```bash
python api_server.py \
  --host 127.0.0.1 \
  --port 8081 \
  --model_path tencent/Hunyuan3D-2mini
```

Lectura:

- en el repo oficial el `API` ya nace orientado a `2mini-Turbo`
- esto encaja bien con la decision de `minimum`

## Solicitud minima sugerida al `API`

Para `UC-3D-02`, el contrato minimo deberia conservar:

- imagen base
- `seed`
- `num_inference_steps`
- `guidance_scale`
- `octree_resolution`
- `texture=false`

La textura no deberia activarse por defecto en `12 GB`.
Si se activa, debe quedar anotado como corrida exploratoria y no como ruta
estable asumida.

Solicitud exploratoria permitida:

- mismo contrato base
- `texture=true`
- misma disciplina de logs y evidencia
- comparativa visual frente a `shape-first`

## Observabilidad

Cada corrida deberia dejar:

- imagen de entrada final usada
- manifest de solicitud
- comando o modo de arranque usado
- log del servicio `Hunyuan3D`
- `glb` de salida
- preview para revision humana
- resultado de importacion en `Blender`

Si la corrida activa textura, deberia dejar ademas:

- marca explicita de que fue una prueba con textura
- tiempo total diferenciado
- lectura visual resumida de si compensa o no

## Reglas de convivencia con `Blender`

La integracion principal sigue siendo por archivo:

- exportar `glb`
- importar a `Blender`
- normalizar escala, pivote y orientacion

El addon oficial de `Blender` debe leerse como opcion futura o secundaria.
La fase 10 no necesita depender de el para cerrar su primer baseline.

## Reglas de convivencia con `ComfyUI`

- `ComfyUI` no debe volver a ser el host principal del 3D
- `ComfyUI` si puede seguir generando:
  - imagen semilla
  - alpha o mascara
  - variantes visuales de referencia
- la mano final sobre la malla debe pasar por `Hunyuan3D` y `Blender`

## Regla de producto

La arquitectura correcta no es:

- un unico `ComfyUI` intentando cargarlo todo

La arquitectura correcta si puede ser:

- una app clara para imagen y video
- otra app clara para 3D
- un contrato comun de artefactos
- `Blender` como punto estable de handoff

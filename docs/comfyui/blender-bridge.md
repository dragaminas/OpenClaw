# Puente Blender -> ComfyUI

Este documento implementa la tarea `8.12` del `DevPlan`.
Define una convencion de entradas y salidas para conectar exports de Blender
con los workflows derivados de `ComfyUI`.

## Raiz de trabajo

Se toma como base `STUDIO_DIR`, que hoy se crea desde
`scripts/openclaw/setup-workspace.sh`.

Convencion propuesta por plano:

```text
$STUDIO_DIR/Exports/<proyecto>/<shot>/
├── blender/
│   ├── frames/
│   ├── controls/
│   ├── refs/
│   └── manifests/
└── comfyui/
    ├── input/
    ├── output/
    ├── temp/
    └── logs/
```

## Entradas canonicas

| Tipo | Ruta sugerida | Uso |
| --- | --- | --- |
| `lineart` | `blender/controls/<shot>__lineart__v001.mp4` | control principal para video |
| `depth` | `blender/controls/<shot>__depth__v001.mp4` | control opcional |
| `openpose` | `blender/controls/<shot>__openpose__v001.mp4` | control opcional |
| `start frame` | `blender/frames/<shot>__start__v001.png` | still o semilla para imagen/video |
| `end frame` | `blender/frames/<shot>__end__v001.png` | referencia futura para `UC-VID-03` |
| referencias de personaje | `blender/refs/character_<nn>.png` | consistencia visual |
| referencias de estilo | `blender/refs/style_<nn>.png` | look y materialidad |

## Salidas canonicas

| Tipo | Ruta sugerida |
| --- | --- |
| paquete preprocess | `comfyui/output/preprocess/<shot>/` |
| imagen final | `comfyui/output/stills/<shot>/` |
| video renderizado | `comfyui/output/video/<shot>/` |
| video mejorado | `comfyui/output/enhanced/<shot>/` |

## Nombres de archivo

Regla:

`<shot>__<artefacto>__v###.<ext>`

Ejemplos:

- `sh010__lineart__v001.mp4`
- `sh010__depth__v001.mp4`
- `sh010__start__v001.png`
- `sh010__render__v001.mp4`

## Manifest minimo por shot

Cada shot deberia poder generar un manifiesto ligero en:

`blender/manifests/<shot>__inputs__v001.json`

Campos recomendados:

- `project_id`
- `shot_id`
- `fps`
- `frame_start`
- `frame_end`
- `width`
- `height`
- `lineart_path`
- `depth_path`
- `openpose_path`
- `start_frame_path`
- `end_frame_path`
- `reference_images`

## Expectativa de los workflows derivados

Las derivaciones locales se normalizan para esperar rutas como estas:

- `input/still/shot_010_start.png`
- `input/controls/shot_010_lineart.mp4`
- `input/controls/shot_010_depth.mp4`
- `input/references/character_01.png`

Esto no obliga a usar esas rutas exactas fuera de ComfyUI, pero si a mapear
las exportaciones de Blender a una estructura estable antes de ejecutar.

## Reglas de producto

- Blender nombra y exporta
- el bridge reubica o vincula
- ComfyUI consume materiales ya normalizados
- el resultado vuelve a una carpeta de `comfyui/output/` asociada al mismo
  `shot`

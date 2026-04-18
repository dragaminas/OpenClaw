# Contrato de Entrada y Salida para la Linea Nativa `Hunyuan3D`

Este documento implementa la tarea `10.7` del `DevPlan`.
Adapta el contrato de I/O de la fase 9 (`docs/comfyui/3d-io-contract.md`) a
la nueva linea nativa, manteniendo formatos, nomenclatura, puente a `Blender`
y criterios de catalogacion, y añadiendo lo especifico de operar con
`Hunyuan3D` como aplicacion separada.

## Principio

El contrato de producto no cambia.
Lo que cambia es el motor de inferencia.
Las entradas, las salidas y el puente a `Blender` deben ser compatibles con
los mismos alias, carpetas y nombres ya establecidos en la fase 9.

## Raiz de trabajo

La raiz de la fase 9 se conserva, pero se añade el ramal `hunyuan3d/`:

```text
$STUDIO_DIR/Assets3D/<project>/<entity_id>/
├── input/
│   ├── refs/
│   ├── multiview/
│   ├── masks/
│   └── manifests/
├── comfyui/          ← semillas o preprocesos cuando los haya
│   ├── output/
│   ├── temp/
│   └── logs/
├── hunyuan3d/        ← nueva fuente canonica del glb 3D
│   ├── requests/
│   ├── output/
│   ├── previews/
│   └── logs/
└── blender/
    ├── imports/
    ├── exports/
    └── catalog/
```

## Entradas canonicas

Igual que en la fase 9, con las siguientes precisiones para `Hunyuan3D`:

| Campo | Tipo | Obligatorio | Uso |
| --- | --- | --- | --- |
| `prompt` | texto | solo en `UC-3D-01` y `UC-3D-03` | descripcion para generacion de semilla en `ComfyUI` |
| `imagen_referencia` | imagen | si para `UC-3D-02` y `UC-3D-04` | imagen de entrada directa a `Hunyuan3D` |
| `imagenes_adicionales` | lista de imagenes | no | vistas extra si el modo multivista aplica |
| `categoria_activo` | enum | no | `objeto`, `personaje`, `envolvente` |
| `tipo_escena` | enum | si para `UC-3D-03/04` | `interior`, `exterior`, `paisaje` |
| `escala_aproximada` | texto | no | tamano orientativo para correccion en `Blender` |
| `modo_texturizado` | enum | no | `shape_first` baseline, `texture_if_possible` opt-in |
| `salida_objetivo` | enum | no | `asset`, `asset_set`, `blockout`, `envolvente` |
| `seed` | entero | no | reproducibilidad de la corrida |
| `num_inference_steps` | entero | no | calidad frente a velocidad |
| `guidance_scale` | decimal | no | adherencia al input visual |
| `octree_resolution` | entero | no | nivel de detalle de la malla |

## Contrato especifico de la solicitud a `Hunyuan3D API`

Para `UC-3D-02` (caso baseline):

```json
{
  "image": "<ruta local o base64>",
  "seed": 42,
  "num_inference_steps": 10,
  "guidance_scale": 5.0,
  "octree_resolution": 256,
  "texture": false
}
```

Para corrida exploratoria con textura:

```json
{
  "image": "<ruta local o base64>",
  "seed": 42,
  "num_inference_steps": 10,
  "guidance_scale": 5.0,
  "octree_resolution": 256,
  "texture": true
}
```

La textura no debe activarse por defecto en el perfil `minimum`.
Si se activa, debe quedar anotado en el manifest.

## Salidas canonicas

| Artefacto | Formato | Ruta | Obligatorio |
| --- | --- | --- | --- |
| mesh principal | `glb` | `hunyuan3d/output/<entity_id>__mesh__v###.glb` | si |
| preview | `png` | `hunyuan3d/previews/<entity_id>__preview__v###.png` | si |
| manifest de corrida | `json` | `hunyuan3d/requests/<entity_id>__request__v###.json` | si |
| log de corrida | `txt` | `hunyuan3d/logs/<entity_id>__run__v###.log` | si |
| texturas | `png` | `hunyuan3d/output/<entity_id>__texture__v###.png` | si aplica |

## Naming

Se conserva el patron de la fase 9:

`<entity_id>__<artefacto>__v###.<ext>`

Ejemplos:

- `chair_a01__mesh__v001.glb`
- `hero_b01__preview__v001.png`
- `room_c03__request__v001.json`

## Manifest minimo por corrida

```json
{
  "project_id": "...",
  "entity_id": "...",
  "use_case_id": "UC-3D-02",
  "motor": "hunyuan3d-2mini-turbo",
  "mode": "shape_first",
  "low_vram_mode": true,
  "imagen_referencia": "input/refs/<entity_id>__ref__v001.png",
  "prompt": null,
  "asset_category": "objeto",
  "escala_aproximada": null,
  "modo_texturizado": "shape_first",
  "hardware_profile": "minimum",
  "seed": 42,
  "num_inference_steps": 10,
  "guidance_scale": 5.0,
  "octree_resolution": 256,
  "texture": false,
  "salida_objetivo": "asset",
  "output_glb": "hunyuan3d/output/<entity_id>__mesh__v001.glb",
  "output_preview": "hunyuan3d/previews/<entity_id>__preview__v001.png",
  "run_timestamp": "...",
  "run_duration_s": null,
  "notes": ""
}
```

## Normalizacion en el puente a `Blender`

Se conserva el canon de la fase 9:

- unidad: `metros`
- `up axis`: `+Z`
- `forward axis`: `-Y`
- pivot canonico segun categoria

El `glb` de `Hunyuan3D` puede salir con orientacion o escala diferente
dependiendo del modelo y del input. La normalizacion es tarea del bridge,
no del motor de inferencia.

## Diferencias respecto al contrato de la fase 9

| Aspecto | Fase 9 | Fase 10 |
| --- | --- | --- |
| Motor | `ComfyUI + SF3D` | `Hunyuan3D` nativo |
| Host del `glb` | `ComfyUI/output/openclaw/uc-3d-*/` | `Assets3D/.../hunyuan3d/output/` |
| Interfaz de invocacion | nodo en grafo `ComfyUI` | `Web UI` en `7860` o `API` en `8081` |
| Parametros de inferencia | nodos `ComfyUI` | campos de la `API` o formulario `Gradio` |
| Textura | nodo opcional en grafo | `texture=true` opt-in en la solicitud |

## Relacion con otros documentos

- arquitectura del runtime: `docs/hunyuan3d/native-runtime-architecture.md`
- perfiles de hardware: `docs/hunyuan3d/hardware-profiles.md`
- puente a `Blender`: `docs/comfyui/3d-blender-bridge.md` (sigue vigente)
- troubleshooting: `docs/hunyuan3d/troubleshooting.md`

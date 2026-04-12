# Contrato de Entrada y Salida para la Linea 3D

Este documento implementa la tarea `9.4` del `DevPlan`.
Define los parametros canonicos y la convencion de artefactos para objetos,
personajes, envolventes y escenas 3D.

## Objetivo

Evitar contratos paralelos entre:

- `UC-3D-01` y `UC-3D-02`
- `UC-3D-03` y `UC-3D-04`
- `ComfyUI`
- `Blender`
- la futura capa conversacional

## Raiz de trabajo

Convencion propuesta:

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
└── blender/
    ├── imports/
    ├── exports/
    └── catalog/
```

`entity_id` puede representar:

- un `asset`
- una `envolvente`
- una `scene-proxy`

## Entradas canonicas

| Campo | Tipo | Obligatorio | Uso |
| --- | --- | --- | --- |
| `prompt` | texto | segun caso | descripcion principal |
| `imagen_referencia` | imagen | segun caso | imagen base principal |
| `imagenes_adicionales` | lista de imagenes | no | vistas extra o referencias de apoyo |
| `alpha_o_mascara` | imagen | no | separar foreground o region de interes |
| `categoria_activo` | enum | no | `objeto`, `personaje`, `envolvente` |
| `tipo_escena` | enum | no | `interior`, `exterior`, `paisaje` |
| `escala_aproximada` | texto | no | tamano objetivo o clase de tamano |
| `modo_texturizado` | enum | no | `shape_first`, `texture_if_possible`, `multiview_priority` |
| `salida_objetivo` | enum | no | `asset`, `asset_set`, `blockout`, `envolvente` |

## Reglas para vistas

- si solo hay una imagen, el contrato debe asumir inferencia de caras no
  visibles
- si hay varias vistas, deben pasarse en `imagenes_adicionales` y conservar
  orden explicito: `front`, `back`, `left`, `right` cuando sea posible
- si una vista es dudosa, es mejor omitirla que mezclar vistas incompatibles

## Normalizacion geometrica objetivo

Regla de producto:

- el output bruto puede llegar con eje o escala imperfectos
- el contrato de publicacion hacia `Blender` debe normalizar a un canon estable

Canon recomendado tras el bridge:

- unidad objetivo: `metros`
- `up axis`: `+Z`
- `forward axis`: `-Y`
- pivot objetivo:
  - `objeto`: base centrada
  - `personaje`: suelo entre los pies
  - `envolvente`: origen del layout o esquina documentada

## Salidas canonicas

| Artefacto | Formato principal | Obligatorio | Uso |
| --- | --- | --- | --- |
| mesh principal | `glb` | si | intercambio con `Blender` |
| mesh alternativo | `obj` | no | depuracion o pipelines auxiliares |
| malla por partes | `zip` o carpeta | no | composicion por activos |
| preview | `png` o visor `3D` | si | revision humana |
| metadata | `json` | si | trazabilidad y handoff |
| texturas | `png` u otro mapa | si aplica | materiales o repaint |

`fbx` no es formato de salida primaria de `ComfyUI` aqui.
Si hace falta, se exporta desde `Blender` despues de normalizar.

## Naming

Regla:

`<entity_id>__<artefacto>__v###.<ext>`

Ejemplos:

- `chair_a01__mesh__v001.glb`
- `hero_b01__preview__v001.png`
- `room_c03__parts__v001.zip`
- `garden_d02__manifest__v001.json`

## Manifest minimo por corrida

Ruta sugerida:

`input/manifests/<entity_id>__contract__v001.json`

Campos minimos:

- `project_id`
- `entity_id`
- `use_case_id`
- `prompt`
- `image_reference_path`
- `additional_image_paths`
- `asset_category`
- `scene_type`
- `scale_hint`
- `texture_mode`
- `hardware_profile`
- `workflow_ref`
- `output_target`

Campos de salida:

- `mesh_path`
- `mesh_parts_path`
- `preview_path`
- `textures_path`
- `orientation_after_bridge`
- `units_after_bridge`

## Reglas de producto

- el contrato de `UC-3D-01` y `UC-3D-03` puede usar una imagen staged como
  puente, pero debe declararlo de forma explicita
- la capa conversacional debe pedir primero el tipo de entrega y no solo el
  prompt
- si la escena no cabe en un mesh util, el contrato correcto es `asset_set` o
  `blockout`, no inventar una falsa escena final

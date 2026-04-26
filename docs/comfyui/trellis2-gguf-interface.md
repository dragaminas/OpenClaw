# Interfaz Operativa de Trellis2 GGUF en ComfyUI

Este documento implementa las tareas `11.2`, `11.3` y `11.5` del `DevPlan`.
Define la interfaz canonica para la linea experimental `UC-3D-02`
`image -> Trellis2 GGUF Q4_K_M -> textured glb` dentro de un runtime
`ComfyUI` aislado, sin contaminar el runtime principal.

## Principio

La fase 11 no reemplaza por defecto la linea nativa `Hunyuan3D`.
Primero debe demostrar mejora visual real en igualdad de fixture.

La interfaz de producto para la operadora no debe exponer detalles de wheels
ni de cuantizacion. Debe hablar en terminos de:

- `asset 3D`
- `calidad visual`
- `tiempo estimado`
- `resultado listo para Blender`

## Runtime canonico aislado

Ruta objetivo del laboratorio:

```text
~/ComfyUI-trellis2-lab
```

Reglas:

- no instalar `ComfyUI-Trellis2` ni `ComfyUI-GGUF` en `~/ComfyUI` principal
- todo experimento de fase 11 se ejecuta en el runtime aislado
- los resultados se publican en una carpeta de benchmarks separada

Artefactos de benchmark:

```text
$STUDIO_DIR/Assets3D/benchmarks/trellis2-gguf/<benchmark_id>/<run_stamp>/
```

## Dependencias minimas de fase 11

Custom nodes esperados en el runtime aislado:

- `ComfyUI-Trellis2`
- `ComfyUI-GGUF`

Set minimo de modelos para prueba `512` low-VRAM:

- `dinov3-vitl16-pretrain-lvd1689m.safetensors`
- `ss_dec_conv3d_16l8_fp16.safetensors`
- `shape_dec_next_dc_f16c32_fp16.safetensors`
- `tex_dec_next_dc_f16c32_fp16.safetensors`
- `slat_flow_img2shape_dit_1_3B_512_bf16_Q4_K_M.gguf`
- `slat_flow_imgshape2tex_dit_1_3B_512_bf16_Q4_K_M.gguf`
- `ss_flow_img_dit_1_3B_64_bf16_Q4_K_M.gguf`

## Superficies de uso

### 1) Administrador tecnico (preflight y corte go/no-go)

Comando canonico:

```bash
bash scripts/apps/comfyui-trellis2-gguf-validation.sh
```

Salida esperada:

- resumen `txt` y `json` del preflight
- inventario de nodos instalados
- verificacion del set minimo de modelos
- verificacion de `o_voxel` con kernel CUDA compatible con la GPU actual
- estado final: `pass_preflight` o `blocked_*`

### 2) Operacion guiada en ComfyUI (cuando el preflight pase)

Objetivo: cargar fixture, ejecutar grafo `UC-3D-02`, exportar `glb`, importar en Blender.

Entrada canonica:

- fixture historico: `/home/eric/ComfyUI/input/openclaw_object_ref.png`
- imagen creativa real: una referencia de producto con silueta limpia

Salida canonica:

- `glb` versionado
- preview renderizado del `glb`
- metrica minima: vertices/caras/tamano/tiempo

### 3) Capa de producto (mensaje para usuaria no tecnica)

Mensajes de estado recomendados:

| Estado | Mensaje |
| --- | --- |
| `running` | "Estoy generando un asset 3D de mayor calidad visual. Te aviso cuando el glb este listo." |
| `blocked_missing_runtime` | "Esta mejora 3D aun no esta instalada en esta maquina. Uso la ruta 3D estable actual." |
| `blocked_missing_models` | "Faltan modelos de calidad para esta ruta. Se mantiene la ruta 3D estable mientras se prepara." |
| `finished` | "Tu asset 3D esta listo para revisarlo en Blender." |

## Especificacion de workflow V1 (`UC-3D-02`)

Esta fase deja definida la interfaz del workflow, no su declaracion como
baseline de producto.

### Variante A: `image -> Trellis2 GGUF Q4_K_M -> textured glb`

Entradas:

- `entrada_base` (obligatoria)
- `categoria_activo` (objeto/personaje)
- `modo_texturizado` (shape-first o textura)

Pipeline esperado:

1. `LoadImage`
2. normalizacion de fondo/silueta
3. `Trellis2ImageCondGenerator`
4. `Trellis2SparseGenerator`
5. `Trellis2ShapeGenerator`
6. `Trellis2TexSlatGenerator`
7. `Trellis2DecodeLatents` con `texture_slat`
8. `Trellis2OvoxelExportToGLB`
9. `Trellis2ExportMesh`

Salida:

- `comfyui/output/openclaw/uc-3d-02/<run_id>__mesh_trellis2_gguf__v001.glb`

Evidencia local de cierre `11.5`:

- `prompt_id=c2afb541-3890-4df0-9029-ad7c92d5530b`
- `output=/home/eric/ComfyUI-trellis2-lab/output/openclaw/e2e_trellis_gguf_q4_textured_ovoxel_00001_.glb`
- `runtime=108.72s`
- `material=PBRMaterial`
- `baseColorTexture=1024x1024 RGBA`
- `metallicRoughnessTexture=1024x1024 RGB`
- `uv=(147695, 2)`

### Variante B opcional: `image -> bg-clean -> Trellis2 GGUF -> glb`

Igual que variante A, pero con limpieza de fondo previa cuando la entrada tenga
fondo complejo.

## Comandos canonicos de fase 11

Preparar layout ejecutable de modelos:

```bash
bash scripts/apps/comfyui-trellis2-gguf-prepare-layout.sh
```

Este paso tambien fija `o_voxel` al wheel Linux `Torch270/cp312`, que en esta
maquina incluye kernel `sm_86` para la RTX 3090. El wheel Linux `Torch291/cp312`
incluido en el custom node no sirve para esta GPU y falla en decode con
`CUDA error: no kernel image is available for execution on the device`.
Tambien fija `flex_gemm` al wheel `Torch270/cp312` con `sm_86` y compila
`nvdiffrast` contra el Torch local cuando el rasterizador CUDA no abre; ambos
son necesarios para empaquetar texturas reales en el GLB con
`Trellis2OvoxelExportToGLB`.

Preflight:

```bash
bash scripts/apps/comfyui-trellis2-gguf-validation.sh
```

Preflight con imagen creativa adicional:

```bash
TRELLIS2_GGUF_CREATIVE_IMAGE=/ruta/a/imagen_creativa.png \
  bash scripts/apps/comfyui-trellis2-gguf-validation.sh
```

Levantar el laboratorio en navegador:

```bash
cd ~/ComfyUI-trellis2-lab
.venv/bin/python main.py --listen 127.0.0.1 --port 8190 --disable-auto-launch
```

URL:

```text
http://127.0.0.1:8190
```

## Criterio de cierre de interfaz

La interfaz de fase 11 se considera preparada cuando:

- existe runtime aislado definido y verificable
- existen checks reproducibles de nodos y modelos
- existe especificacion de entradas/salidas del flujo `UC-3D-02`
- existe reporte canonico de estado y bloqueo

La migracion de baseline solo se habilita despues de evidencia visual comparada
contra `SF3D` y `Hunyuan3D-2mini-Turbo`.

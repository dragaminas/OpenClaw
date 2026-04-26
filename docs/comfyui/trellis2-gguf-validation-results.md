# Resultados de Validacion Trellis2 GGUF en ComfyUI

Este documento implementa la salida canonica de las tareas `11.6` a `11.9`
del `DevPlan`, con corte as-built `2026-04-25`.

## Estado

- estado: `pass_preflight`
- decision de corte: `go_tecnico_trellis_q4_textured`
- fecha de corte: `2026-04-26`
- objetivo comparativo: `SF3D` vs `Hunyuan3D-2mini-Turbo` vs `Trellis2 GGUF`
- e2e minimo API: `success`
- e2e Q4 texturizado API: `success`

## Lectura correcta del resultado

Este corte demuestra estas cosas concretas:

- el runtime aislado `~/ComfyUI-trellis2-lab` existe
- `ComfyUI-Trellis2` y `ComfyUI-GGUF` estan presentes
- el set minimo `512/Q4_K_M` esta descargado
- el layout ejecutable esperado por `Trellis2LoadModel` esta preparado con
  symlinks hacia los modelos descargados
- el laboratorio arranca y carga los custom nodes sin errores de importacion
- el gate ya distingue modelos descargados de layout ejecutable por workflow
- el workflow minimo por API completo `image -> Trellis2 -> glb` ya genera un
  `.glb` con `backend=sdpa`, `conv_backend=spconv` y `o_voxel` compatible
  `sm_86`
- el workflow Q4 texturizado por API genera un GLB con `PBRMaterial`, UVs y
  texturas embebidas usando `Trellis2TexSlatGenerator` y
  `Trellis2OvoxelExportToGLB`

Este corte no demuestra todavia:

- importacion de un `.glb` Trellis en `Blender`
- comparativa visual real contra `SF3D` y `Hunyuan3D-2mini-Turbo`
- mejora visual de `Trellis2 GGUF` sobre `Hunyuan3D`, porque falta revision
  visual/import Blender y una imagen creativa real adicional

## Que se ejecuto de verdad

Comando ejecutado:

```bash
bash scripts/apps/comfyui-trellis2-gguf-validation.sh
```

Resultado del preflight:

- `status=pass_preflight`
- `run_dir=/home/eric/Studio/Assets3D/benchmarks/trellis2-gguf/openclaw_object_ref/20260425T135058Z`

Prueba e2e minima por API:

- `prompt_id=88fb4164-deb6-461c-a79f-b3e6a3022241`
- `status=success`
- `tiempo=289.63s`
- `output=/home/eric/ComfyUI-trellis2-lab/output/openclaw/e2e_trellis_spconv_min_00001_.glb`
- `tamano=206133424 bytes`

Prueba e2e Q4 texturizada por API:

- `prompt_id=c2afb541-3890-4df0-9029-ad7c92d5530b`
- `status=success`
- `tiempo=108.72s`
- `output=/home/eric/ComfyUI-trellis2-lab/output/openclaw/e2e_trellis_gguf_q4_textured_ovoxel_00001_.glb`
- `tamano=10035316 bytes`
- `visual=TextureVisuals`
- `material=PBRMaterial`
- `baseColorTexture=1024x1024 RGBA`
- `metallicRoughnessTexture=1024x1024 RGB`
- `uv=(147695, 2)`

Runtime detectado en esta maquina durante el corte:

- `python=3.12.3`
- `comfyui_python=3.12.3`
- `torch=2.9.1+cu128`
- `gpu=NVIDIA GeForce RTX 3090, driver 580.126.09, 24576 MiB`

## Bloqueos observados

Bloqueos concretos publicados por el script:

- ninguno a nivel de preflight

Ya no bloquea en este corte:

- runtime aislado
- custom nodes `ComfyUI-Trellis2` y `ComfyUI-GGUF`
- set minimo `512/Q4_K_M` (`7/7`)
- layout `models/microsoft/TRELLIS.2-4B` y
  `models/microsoft/TRELLIS-image-large`
- carga DINOv3 con config local `hidden_size=1024`
- ausencia de `flash_attn` para la atencion principal, usando `sdpa`
- `flex_gemm` incompatible con RTX 3090, usando `spconv`
- `o_voxel` sin kernel compatible, usando el wheel Linux `Torch270/cp312`
  que expone `sm_86`
- `nvdiffrast` sin kernel/ABI compatible para rasterizar texturas, compilado
  desde fuente contra `torch=2.9.1+cu128`
- `flex_gemm` sin kernel compatible en el tramo `grid_sample_3d` del export
  texturizado, usando el wheel Linux `Torch270/cp312` que expone `sm_86`

No bloqueante en este corte:

- `ComfyUI` principal no estaba escuchando en `127.0.0.1:8188`
- el laboratorio se probo aparte en `127.0.0.1:8190` y llego a
  `Starting server` con los nodos cargados

## Evidencia producida

Artefactos canonicos generados:

- `/home/eric/Studio/Assets3D/benchmarks/trellis2-gguf/openclaw_object_ref/20260425T125859Z/reports/trellis2_gguf_validation_summary.txt`
- `/home/eric/Studio/Assets3D/benchmarks/trellis2-gguf/openclaw_object_ref/20260425T125859Z/reports/trellis2_gguf_validation_summary.json`
- `/home/eric/Studio/Assets3D/benchmarks/trellis2-gguf/openclaw_object_ref/20260425T125859Z/reports/installed_nodes.txt`
- `/home/eric/Studio/Assets3D/benchmarks/trellis2-gguf/openclaw_object_ref/20260425T125859Z/reports/minimum_models_check.txt`
- `/home/eric/Studio/Assets3D/benchmarks/trellis2-gguf/openclaw_object_ref/20260425T125859Z/reports/workflow_model_layout_check.txt`
- `/home/eric/Studio/Assets3D/benchmarks/trellis2-gguf/openclaw_object_ref/20260425T135058Z/reports/o_voxel_cuda_check.txt`
- `/home/eric/ComfyUI-trellis2-lab/output/openclaw/e2e_trellis_spconv_min_00001_.glb`
- `/home/eric/ComfyUI-trellis2-lab/output/openclaw/e2e_trellis_gguf_q4_remap_00001_.glb`
- `/home/eric/ComfyUI-trellis2-lab/output/openclaw/e2e_trellis_gguf_q4_textured_ovoxel_00001_.glb`

Contexto de baseline ya existente para comparacion futura:

- outputs `SF3D` detectados en `ComfyUI/output/openclaw/uc-3d-01/` y `ComfyUI/output/openclaw/uc-3d-02/`
- output `Hunyuan3D` detectado como `mesh_shape_v2mini.glb` en
  `ComfyUI/output/openclaw/uc-3d-02/`

## Tabla de cierre por tarea

| Tarea | Estado de corte | Lectura |
| --- | --- | --- |
| `11.2` entorno aislado | `done` | existe `~/ComfyUI-trellis2-lab` y arranca en puerto de laboratorio |
| `11.3` auditoria de dependencias | `done` | checklist y reporte reproducible de nodos/runtime/modelos |
| `11.4` descarga set minimo | `done` | set minimo presente (`7/7`) en `models/trellis2_gguf_minimum/` |
| `11.5` workflow minimo `UC-3D-02` | `done` | workflow Q4 texturizado comprobado por API y GLB con PBRMaterial |
| `11.6` comparativa local | `in progress` | Trellis Q4 ya supera cualitativamente candidatos previos; falta guardar comparativa formal con imagen creativa |
| `11.7` import Blender y metrica mesh | `pending` | ya existe output Trellis texturizado; falta importarlo y medirlo en Blender |
| `11.8` comparativa visual honesta | `in progress` | decision cualitativa favorece Trellis; falta reporte visual formal |
| `11.9` decision go/no-go | `in progress` | go tecnico para Trellis Q4 texturizado; falta decidir integracion de producto |

## Decision go/no-go de este corte

Decision: **`go_tecnico_trellis_q4_textured`**

Motivo:

- el usuario confirma que Trellis es claramente superior a los candidatos
  previos probados
- ya existe un GLB Q4 texturizado con material PBR, texturas y UVs
- falta import Blender y comparativa formal para cerrar la promocion de producto

Implicacion operativa:

- Trellis2 GGUF Q4 pasa a candidato principal tecnico para la ruta 3D
- `Hunyuan3D` queda como fallback estable hasta integrar Trellis en producto
- `SF3D` queda como benchmark historico

## Proximo gate para cambiar la decision

Para reevaluar a `go` en fase 11 se requiere, como minimo:

1. generar al menos un `glb` Trellis con el fixture historico
2. importar el `glb` en Blender y registrar vertices/caras
3. comparar visualmente contra `SF3D` y `Hunyuan3D-2mini-Turbo`

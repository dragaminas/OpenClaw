# Manifest de Custom Nodes ComfyUI

Este documento implementa la tarea `8.7` del `DevPlan`.
Resume las dependencias de custom nodes relevantes para el baseline minimo y
para la biblioteca base de workflows, usando evidencia del runtime local cuando
es posible.

## Estado resumido

| Paquete | Rol | Clase | Estado local | Evidencia |
| --- | --- | --- | --- | --- |
| `comfyui-videohelpersuite` | carga y guardado de video `VHS_*` | bloqueante | presente | `VHS_LoadVideo`, `VHS_VideoCombine`, `VHS_VideoInfo` en `object_info` |
| `comfyui_controlnet_aux` | `Canny`, `Openpose`, preprocess auxiliares | bloqueante | presente | `CannyEdgePreprocessor`, `OpenposePreprocessor`, `DepthAnythingV2Preprocessor` |
| `ComfyUI-DepthAnythingV3` | profundidad V3 exacta usada por workflows de Mickmumpitz | bloqueante para reproducir ese resultado exacto | presente | `DownloadAndLoadDepthAnythingV3Model`, `DepthAnything_V3` |
| `comfyui-depthanythingv2` | fallback de profundidad local | recomendada | presente | `DownloadAndLoadDepthAnythingV2Model`, `DepthAnything_V2` |
| `comfyui-kjnodes` | resize y utilidades varias | bloqueante | presente | `ImageResizeKJv2`, `GGUFLoaderKJ` |
| `comfyui-impact-pack` | branching y utilidades de flujo | bloqueante | presente | `ImpactSwitch`, `ImpactCompare` |
| `comfyui_essentials` | lotes de imagen y utilidades | bloqueante | presente | `ImageBatchMultiple+`, `SimpleMathSlider+`, `SimpleMathDual+` |
| `comfyui-easy-use` | limpieza de VRAM y utilidades | recomendada | presente | `easy cleanGpuUsed` |
| `ComfyUI-WanVideoWrapper` | nodos Wan/VACE | bloqueante para video Wan | presente | `WanVideoVACEStartToEndFrame` |
| `wanvaceadvanced` | sampling Wan/VACE avanzado | recomendada para AI Renderer | presente | `WanVacePhantomSimpleV2`, `TrimVideoLatent` |
| `Wan22FirstLastFrameToVideoLatent` | start/end frame con Wan 2.2 5B | recomendada para `UC-VID-03` | presente | `Wan22FirstLastFrameToVideoLatent`, `Wan22FirstLastFrameToVideoLatentTiledVAE` |
| `comfyui-mickmumpitz-nodes` | resolucion y switches propios | bloqueante para los workflows Mickmumpitz | presente | `ResolutionPicker`, `WanResolutionPicker`, `PreprocessSwitch` |
| `rgthree-comfy` | labels y utilidades frontend | recomendada | presente en disco | los labels no aparecen en `object_info`, pero estan embebidos en los workflows |
| `RES4LYF` | dependencia mencionada en notas | futura/opcional | presente en disco | aparece instalado, no bloquea baseline actual |
| `ComfyUI-GGUF` | fallback cuantizado real | futura/opcional | ausente como plugin dedicado | no hay carpeta propia; solo hooks via `GGUFLoaderKJ` |

## Lectura correcta del runtime

Hay nodos que no aparecen en `object_info` y eso no significa automaticamente
que el stack este roto.

Casos observados:

- `Label (rgthree)` es decoracion de workflow
- `SetNode` y `GetNode` no aparecieron en `object_info`; se tratan aqui como
  utilidades de estructura del workflow, no como evidencia primaria del backend

## Dependencias bloqueantes por caso

### `UC-IMG-02`

- `comfyui-kjnodes`
- `comfyui-videohelpersuite`
- soporte core para `QwenImageDiffsynthControlnet` y `ModelPatchLoader`

### `UC-VID-01`

- `comfyui-videohelpersuite`
- `comfyui_controlnet_aux`
- `ComfyUI-DepthAnythingV3` si se quiere reproducir el pipeline exacto del autor
- `comfyui-kjnodes`
- `comfyui-mickmumpitz-nodes`

### `UC-VID-02`

- `comfyui-videohelpersuite`
- `ComfyUI-WanVideoWrapper`
- `wanvaceadvanced`
- `comfyui-impact-pack`
- `comfyui_essentials`
- `comfyui-easy-use`
- `comfyui-mickmumpitz-nodes`

### `UC-VID-03`

- `Wan22FirstLastFrameToVideoLatent`
- stack Wan 2.2 core de ComfyUI

## Dependencias recomendadas

- `rgthree-comfy` para legibilidad y trazabilidad visual de los JSON
- `comfyui-depthanythingv2` como ruta de continuidad si no se quiere usar `V3`
  o si el modelo `V3` aun no esta descargado
- `RES4LYF` por si se decide seguir la nota incrustada en el workflow base

## Dependencias futuras

- `ComfyUI-GGUF` para habilitar de verdad la ruta de fallback cuantizada
- nodos o plugins adicionales solo cuando aporten una variante clara de
  `medium` o `maximum`

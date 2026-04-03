# Missing Nodes y Estado Actual

Este archivo registra los nodos que faltaban en los workflows base y como
quedo resuelto el runtime local.

## Nodos detectados como faltantes

- `DownloadAndLoadDepthAnythingV3Model`
- `DepthAnything_V3`
- `SimpleMathSlider+`

## Resolucion aplicada

Se instalaron o actualizaron estos paquetes en
`/home/eric/ComfyUI/custom_nodes/`:

- `ComfyUI-DepthAnythingV3`
- `comfyui_essentials`
- `Wan22FirstLastFrameToVideoLatent`

## Verificacion local

Tras reiniciar `ComfyUI`, `object_info` ya expone:

- `DownloadAndLoadDepthAnythingV3Model`
- `DepthAnything_V3`
- `SimpleMathSlider+`
- `SimpleMathDual+`
- `Wan22FirstLastFrameToVideoLatent`
- `Wan22FirstLastFrameToVideoLatentTiledVAE`

## Lectura correcta

El problema de nodos faltantes quedo resuelto.

Si un workflow sigue sin correr, el siguiente lugar a revisar es:

- `configs/comfyui/models-manifest.md`
- ubicacion real de modelos en `/home/eric/ComfyUI/models/`

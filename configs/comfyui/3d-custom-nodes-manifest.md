# Manifiesto de Custom Nodes para la Linea 3D

Este documento implementa la tarea `9.5` del `DevPlan`.
Audita los custom nodes y dependencias auxiliares de la linea `3D` con corte
`2026-04-12`.

## Entorno auditado

- `ComfyUI`: `/home/eric/ComfyUI`
- `python`: `/home/eric/ComfyUI/.venv/bin/python`
- version Python: `3.12.3`
- `torch`: `2.11.0+cu130`
- GPU: `RTX 3060 12 GB`

## Estado local observado

Custom nodes presentes hoy:

- `ComfyUI-3D-Pack`
- `ComfyUI-DepthAnythingV3`
- `ComfyUI-WanVideoWrapper`
- `Wan22FirstLastFrameToVideoLatent`
- `comfyui-depthanythingv2`
- `comfyui-impact-pack`
- `comfyui-kjnodes`
- `comfyui-mickmumpitz-nodes`
- `openclaw-hunyuan3d-lite`
- `openclaw-workflows`
- `stable-fast-3d`

Custom nodes 3D prioritarios ausentes hoy:

- ninguno del baseline historico `MVP`
- para la investigacion nueva `Trellis2 GGUF`: `visualbruno/ComfyUI-Trellis2`
  y soporte `GGUF` modular equivalente al usado por la via del video

## Clasificacion

| Item | Rol | Estado local | Prioridad | Lectura |
| --- | --- | --- | --- | --- |
| `stable-fast-3d` oficial | baseline `MVP` para `single image -> 3D` | presente y cargando nodos | bloqueante resuelto | es la ruta correcta para esta fase |
| `ComfyUI-3D-Pack` | suite comparativa para `SF3D`, `Hunyuan` y otros stacks | presente pero `IMPORT FAILED` | secundaria | hoy cae por `pytorch3d`, no debe bloquear el `MVP` |
| `openclaw-hunyuan3d-lite` | runtime historico de exploracion | presente | historica | solo conserva evidencia previa, no cierra la fase |
| `ComfyUI-Trellis2` | candidato `Trellis2 GGUF` para calidad visual | ausente | investigacion | debe probarse primero en entorno aislado |
| soporte `ComfyUI-GGUF` modular | carga de cuantizaciones Trellis2 low-VRAM | ausente | investigacion | ruta comunitaria/WIP; validar antes de integrarla |
| visor `Preview 3D` compatible | preview en canvas | no verificado | recomendada | no bloquea export, si bloquea inspeccion comoda |
| toolchain `gcc/g++` | compilaciones auxiliares en Linux | no auditado aun | experimental | relevante sobre todo para nodos que compilan extensiones |

## Dependencias auxiliares y riesgo

La extension oficial `stable-fast-3d` pide, entre otras cosas:

- `numpy 1.26.4`
- `gpytoolbox 0.2.0`
- `pynanoinstantmeshes 0.0.3`
- `texture_baker/`
- `uv_unwrapper/`
- acceso al repo gated `stabilityai/stable-fast-3d`

Lectura para esta maquina hoy:

- `numpy 2.x` ya se corrigio a `1.26.4`
- `pynanoinstantmeshes`, `uv_unwrapper` y `texture_baker` ya quedaron instalados
- los nodos `StableFast3DLoader`, `StableFast3DSampler`, `StableFast3DSave` y
  `StableFast3DPreview` ya se exponen en `ComfyUI`
- el bloqueo real restante es el acceso gated al modelo en `Hugging Face`

## Recomendacion de instalacion

Orden recomendado:

1. clonar `stable-fast-3d` oficial en `custom_nodes`
2. alinear dependencias de su `requirements.txt`
3. compilar `texture_baker` y `uv_unwrapper`
4. confirmar que aparecen `StableFast3DLoader`, `StableFast3DSampler` y `StableFast3DSave`
5. solo despues cerrar la validacion real de `UC-3D-02`

## Conclusion

La dependencia bloqueante real de la fase `9` ya no es la extension de
`SF3D`, sino el acceso al modelo gated `stabilityai/stable-fast-3d`.

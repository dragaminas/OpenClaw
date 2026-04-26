# Investigacion Trellis2 GGUF en ComfyUI para 3D Local

Este documento abre una investigacion nueva para evaluar `TRELLIS.2` con
cuantizaciones `GGUF` dentro de `ComfyUI` como candidato serio para la linea
3D local.

## Motivo

La evidencia acumulada hasta ahora tiene una conclusion incomoda pero clara:

- `SF3D` funciono tecnicamente, exporto `glb` e importo en `Blender`, pero fue
  pobre visualmente.
- `Hunyuan3D-2mini-Turbo` nativo funciono localmente y con baja VRAM, pero la
  validacion registrada aun no demuestra una ventaja visual suficiente frente a
  los mejores ejemplos recientes de `ComfyUI`.
- Los resultados mostrados en el video de referencia para `Trellis2 GGUF`
  parecen visualmente superiores a todo lo probado localmente.
- Si la calidad visual cambia de forma sustancial, merece reabrirse la decision
  anterior de sacar el 3D principal de `ComfyUI`.

Video de referencia:

```text
https://www.youtube.com/watch?v=FuFm8zBHDWI
```

Lectura del video: la via investigada no es `Hunyuan3D`, sino `Trellis2 GGUF`
en `ComfyUI`.

## Hipotesis

`TRELLIS.2` con modelos `GGUF` puede ofrecer mejor calidad visual que `SF3D` y
que la configuracion local actual de `Hunyuan3D-2mini-Turbo`, manteniendo una
operacion mas ergonomica para OpenClaw porque:

- vive dentro de `ComfyUI`
- reutiliza el gestor de carga y descarga de modelos de `ComfyUI`
- evita alternar manualmente entre servicios `ComfyUI` y `Hunyuan3D`
- permite encadenar generacion de imagen, limpieza de fondo, multi-view,
  remesh, texturizado y exportacion dentro del mismo grafo

Esta hipotesis solo debe aceptarse si hay evidencia visual local real.

## Fuentes Tecnicas

| Fuente | Rol | URL |
| --- | --- | --- |
| `microsoft/TRELLIS.2` | repo oficial, arquitectura y baseline de calidad | `https://github.com/microsoft/TRELLIS.2` |
| `visualbruno/ComfyUI-Trellis2` | wrapper ComfyUI activo | `https://github.com/visualbruno/ComfyUI-Trellis2` |
| `Aero-Ex/Trellis2-GGUF` | cuantizaciones comunitarias GGUF | `https://huggingface.co/Aero-Ex/Trellis2-GGUF` |
| `Aero-Ex/ComfyUI-GGUF` | soporte GGUF modular usado por la via del video | `https://huggingface.co/Aero-Ex/ComfyUI-GGUF` |

## Lectura de Riesgo

La ruta oficial de `TRELLIS.2` no es low-VRAM: el README oficial indica Linux,
CUDA Toolkit y GPU NVIDIA con al menos `24 GB` como requisito practico probado
en `A100/H100`.

Ademas, la ruta mostrada en el video y el wrapper `ComfyUI-Trellis2` tienen una
salvedad operativa importante: la documentacion principal del wrapper declara
la prueba base en `Windows 11`, `Python 3.11` y `Torch 2.7.0 + cu128`, y sus
comandos visibles priorizan wheels de `Windows`. Esto no descarta Linux, pero
si significa que no debemos asumir que el tutorial del video sea directamente
reproducible en Ubuntu.

Puntos a verificar antes de invertir en descarga de modelos:

- existencia de wheels `Linux` compatibles con la version local de `Python`,
  `Torch` y `CUDA`
- compatibilidad con el runtime actual de OpenClaw (`Python 3.12`,
  `Torch 2.11.0+cu130`, `CUDA 13.0`)
- posibilidad de usar un entorno paralelo con `Python 3.11` y `Torch 2.7/2.8`
  si las wheels disponibles no encajan con el `ComfyUI` principal
- si el camino realista para Linux exige compilar `cumesh`, `nvdiffrast`,
  `nvdiffrec_render`, `flex_gemm` u `o_voxel`

La promesa low-VRAM viene de:

- cuantizaciones `GGUF`
- modelos auxiliares reducidos o cargados por etapas
- descarga/carga selectiva dentro de `ComfyUI`
- wrappers comunitarios recientes

Por tanto, esta no debe tratarse como una dependencia estable del producto
hasta pasar una validacion local. Es una investigacion de calidad.

## Stack Candidato

### Custom Nodes

| Componente | Estado esperado | Riesgo |
| --- | --- | --- |
| `visualbruno/ComfyUI-Trellis2` | requerido | alto: muchas dependencias, wheels y cambios recientes |
| `Aero-Ex/ComfyUI-GGUF` o equivalente | requerido para GGUF modular | medio/alto: WIP y comunitario |
| visor/export 3D de ComfyUI | recomendado | bajo |
| nodos de background removal | recomendado | medio: mejora calidad de entrada |

### Modelos

`Aero-Ex/Trellis2-GGUF` expone una suite modular grande. No se debe descargar
todo a ciegas. La prueba minima debe priorizar una variante `512` `Q4_K_M` o
equivalente y solo los decoders/encoders indispensables.

Piezas observadas en la suite:

- `Vision/dinov3-vitl16-pretrain-lvd1689m.safetensors`
- `decoders/Stage1/ss_dec_conv3d_16l8_fp16.safetensors`
- `decoders/Stage2/shape_dec_next_dc_f16c32_fp16.safetensors`
- `decoders/Stage2/tex_dec_next_dc_f16c32_fp16.safetensors`
- `shape/slat_flow_img2shape_dit_1_3B_512_bf16_Q4_K_M.gguf`
- `texture/slat_flow_imgshape2tex_dit_1_3B_512_bf16_Q4_K_M.gguf`
- `refiner/ss_flow_img_dit_1_3B_64_bf16_Q4_K_M.gguf`
- `pipeline.json`
- `texturing_pipeline.json`

## Estrategia de Instalacion

La primera prueba no debe contaminar el `ComfyUI` principal validado. Ruta
recomendada:

1. crear un `ComfyUI` paralelo o perfil experimental, por ejemplo
   `~/ComfyUI-trellis2-lab`
2. elegir runtime objetivo antes de instalar:
   - preferido para compatibilidad con el video: `Python 3.11` + `Torch 2.7/2.8`
   - solo si hay wheels disponibles: runtime actual `Python 3.12` + `Torch 2.11`
3. clonar `visualbruno/ComfyUI-Trellis2` en `custom_nodes`
4. instalar sus `requirements.txt`
5. instalar o compilar las wheels necesarias para Linux
6. instalar el soporte `GGUF` modular usado por la via del video
7. descargar solo modelos `512` `Q4_K_M` necesarios
8. ejecutar una prueba `image -> mesh -> glb`
9. importar el resultado en `Blender`

Despues de validar calidad, se decide si se integra al `ComfyUI` principal.

## Fixtures de Comparacion

La investigacion debe usar los mismos inputs que ya existen en la evidencia
historica:

| Fixture | Uso |
| --- | --- |
| `/home/eric/ComfyUI/input/openclaw_object_ref.png` | comparativa directa contra `SF3D` |
| imagen creativa real de objeto/personaje con silueta limpia | lectura visual de producto |
| al menos una referencia multi-view si se prepara | validar ventaja real de Trellis2 |

## Matriz de Comparacion

| Motor | Estado previo | Criterio nuevo |
| --- | --- | --- |
| `SF3D` | `pass tecnico / fail visual` | baseline negativo historico |
| `Hunyuan3D-2mini-Turbo` | `pass smoke` | comprobar si mejora visualmente con input real |
| `Trellis2 GGUF` | pendiente | candidato si mejora calidad sin romper operacion |

## Criterios de Go/No-Go

### `go`

- genera `glb` importable en `Blender`
- mejora visualmente a `SF3D` con el mismo input
- no es peor que `Hunyuan3D-2mini-Turbo` en objeto/personaje aislado
- cabe en la `RTX 3060 12 GB` o en un perfil low-VRAM razonable
- el workflow puede vivir en `ComfyUI` sin bloquear imagen/video
- el coste de instalacion queda documentado y reproducible

### `no-go`

- exige `24 GB+` reales pese a usar `GGUF`
- produce mallas fragmentadas o inutiles en fixtures locales
- depende de una combinacion de wheels no reproducible en Linux local
- mejora screenshots de demo pero no exporta assets solidos para `Blender`
- obliga a romper el `ComfyUI` principal o sus workflows de imagen/video

## Resultado Esperado de la Investigacion

La investigacion se cierra con un documento de resultados que incluya:

- version de `ComfyUI`, Python, Torch y CUDA
- custom nodes instalados y commits
- modelos descargados y tamanos
- VRAM pico observada
- tiempos de generacion
- rutas de outputs
- importacion Blender
- comparativa visual honesta frente a `SF3D` y `Hunyuan3D`

Archivo sugerido:

```text
docs/comfyui/trellis2-gguf-validation-results.md
```

## Estado operativo actual de la fase 11

La investigacion ya tiene superficie canonica de uso y validacion:

- interfaz operativa y contrato de uso en
  `docs/comfyui/trellis2-gguf-interface.md`
- gate reproducible de preflight y auditoria en
  `scripts/apps/comfyui-trellis2-gguf-validation.sh`
- resultados as-built y decision de corte en
  `docs/comfyui/trellis2-gguf-validation-results.md`

El estado actual no promociona `Trellis2 GGUF` como baseline de producto.
Primero debe superar el gate de instalacion y producir evidencia visual local
comparable frente a `SF3D` y `Hunyuan3D-2mini-Turbo`.

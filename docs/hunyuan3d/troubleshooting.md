# Troubleshooting de la Linea Nativa `Hunyuan3D`

Este documento implementa la tarea `10.12` del `DevPlan`.
Actualiza los procedimientos de diagnostico para reflejar que la ruta 3D
principal ya no vive en `ComfyUI`, sino en `Hunyuan3D` como aplicacion
separada.

## Principio

El operador debe saber distinguir entre:

- un fallo de `ComfyUI` (imagen, video, semilla)
- un fallo de `Hunyuan3D` (inferencia 3D, malla, textura)
- un fallo del puente a `Blender` (escala, orientacion, handoff)

No mezclar diagnostico entre apps.

---

## Problemas de instalacion y arranque

### App no arranca: `ModuleNotFoundError`

Sintomas:

- `python3 gradio_app.py` cae con `ModuleNotFoundError`

Acciones:

- verificar que el `venv` de `Hunyuan3D` esta activado antes de lanzar
- ejecutar `source ~/Hunyuan3D-2/.venv/bin/activate` primero
- si la dependencia falta: `pip install <dependencia>` dentro del `venv`
- nunca instalar en el `venv` de `ComfyUI`

### CUDA no disponible en el venv

Sintomas:

- `torch.cuda.is_available()` devuelve `False`
- la inferencia cae o corre en CPU y tarda horas

Acciones:

- verificar que el `torch` instalado en el `venv` de `Hunyuan3D` corresponde
  a la version de CUDA del driver actual
- `nvidia-smi` para ver la version del driver
- reinstalar `torch` con el comando correcto de `https://pytorch.org/get-started/locally/`
- no compartir el `torch` del `venv` de `ComfyUI`

### App arranca pero el modelo no carga

Sintomas:

- `Gradio` arranca pero la inferencia falla desde el primer intento
- log muestra `OSError` o `FileNotFoundError` apuntando a un peso no encontrado

Acciones:

- verificar que los pesos estan en `~/.cache/huggingface/hub/`
- si no: `python3 -c "from huggingface_hub import snapshot_download; snapshot_download('tencent/Hunyuan3D-2mini')"`
- comprobar conexion a internet si la descarga falla

### Puerto `7860` o `8081` ya en uso

Sintomas:

- `OSError: [Errno 98] Address already in use`

Acciones:

- `lsof -i :7860` o `lsof -i :8081` para ver que proceso lo ocupa
- si es una instancia anterior de `Hunyuan3D`: `kill <pid>`
- si es otro proceso: cambiar el puerto con `--port`

---

## Problemas de inferencia

### OOM durante la inferencia

Sintomas:

- `CUDA out of memory` en el log
- la corrida cae antes de generar el `glb`

Acciones:

- asegurarse de que `ComfyUI` esta en reposo antes de lanzar `Hunyuan3D`
- verificar que se esta usando `--low_vram_mode`
- cerrar el visor `Gradio` si hay previews acumuladas en memoria
- reducir `octree_resolution` en la solicitud `API`
- no intentar textura en la misma corrida

Si la OOM persiste con solo `Hunyuan3D` activo y `ComfyUI` en reposo:

- el perfil `minimum` no soporta la corrida actual
- degradar a `blockout` o pasar el caso a un perfil superior

### Inferencia termina pero el `glb` sale vacio o con `0 bytes`

Sintomas:

- el endpoint `API` devuelve respuesta pero el archivo salvado no tiene
  contenido util

Acciones:

- revisar el log del servidor API: `~/logs/hunyuan3d/api_server.log`
- verificar ruta de escritura del output con permisos correctos
- intentar la misma corrida desde la `web UI` para comprobar si el problema
  es el endpoint o la inferencia en si

### La malla sale distorsionada o solo con la cara frontal

Sintomas:

- al rotar en `Blender` las caras traseras son planas o irreconocibles
- el activo no es usable en composicion

Acciones:

- el problema en una sola vista es esperado para algunas categorias
- intentar con mejor crop o fondo neutro de la referencia
- si el activo es un personaje, asegurarse de que el sujeto ocupa la mayor
  parte del frame
- si sigue sin mejorar, considerar modo multivista o pasar a fallback

---

## Problemas del puente a Blender

### `Blender` no importa el `glb`

Sintomas:

- `bpy.ops.import_scene.gltf` falla con error

Acciones:

- verificar que el `glb` es valido con `file <ruta_glb>` (debe decir `glTF`)
- comprobar que la version de `Blender` soporta `glTF 2.0` (cualquier Blender
  reciente lo hace)
- si el `glb` esta corrupto, relanzar la corrida

### Escala absurda tras importar

Sintomas:

- el activo importado en `Blender` tiene `0.001` o `1000` metros de altura

Acciones:

- aplicar el factor de escala corrector al importar
- la normalizacion canonica de unidad es `metros` con `+Z` arriba
- fijar escala en `Blender` con `S + valor + Enter` si la importacion no la
  corrige

### Ejes incorrectos

Sintomas:

- el activo aparece boca abajo o rotado 90 grados

Acciones:

- aplicar rotacion de correccion en `Blender`
- el canon de la fase 10 es `up=+Z`, `forward=-Y`
- documentar la rotacion observada en el manifest para referencias futuras

---

## Convivencia con ComfyUI

### `ComfyUI` y `Hunyuan3D` activos a la vez y la GPU se satura

Acciones:

- no lanzar inferencia pesada en ambas apps al mismo tiempo sobre `RTX 3060`
- seguir el orden: `ComfyUI` genera semilla -> queda en reposo -> `Hunyuan3D`
  hace la inferencia 3D
- si ambas deben correr al mismo tiempo, usar un perfil remoto

### Dependencias contaminadas entre venvs

Sintomas:

- `import error` que apunta a una version de `torch` que funciona en un venv
  pero no en el otro

Acciones:

- nunca usar `pip install --system` ni instalar cosas en el entorno base
- cada app tiene su propio `venv`
- si hay contaminacion, recrear el `venv` afectado desde cero

---

## Mensajes de producto para la usuaria final

| Problema observado | Mensaje para la usuaria |
| --- | --- |
| OOM | "La maquina esta ocupada. Espera un momento y vuelve a intentarlo." |
| Modelo no cargado | "El motor 3D todavia esta arrancando. Intent otra vez en un minuto." |
| Output vacio | "Algo fallo en la generacion. Lo estoy revisando." |
| Malla solo de frente | "Este activo se ve mejor desde una sola vista. Puedo darte el shape como proxy o pedir una vista mejor." |
| Escena monolitica imposible | "Esta referencia tiene demasiados elementos para un solo bloque. Conviene hacerlo por piezas." |

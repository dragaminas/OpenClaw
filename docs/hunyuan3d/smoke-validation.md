# Smoke Validation para la Linea Nativa `Hunyuan3D`

Este documento implementa la tarea `10.9` del `DevPlan`.
Define la bateria de smoke tests para verificar que la app nativa arrancar,
acepta una imagen, genera un `glb` y lo deja publicado para `Blender`.

## Objetivo

Smoke tests minimos y baratos para verificar la linea nativa antes de
lanzar la validacion real de `10.10`.

No sustituyen la evidencia real de producto.
Son el gate que desbloquea `10.10`.

## Gate `PF-H3D-00` — precondiciones de instalacion

Criterios de `pass`:

- existe `~/Hunyuan3D-2/gradio_app.py`
- existe `~/Hunyuan3D-2/.venv/bin/python3`
- el `venv` tiene `torch` con `cuda_is_available()==True`
- el `venv` tiene `trimesh` y `huggingface_hub`
- existe cache del modelo `tencent/Hunyuan3D-2mini` en `~/.cache/huggingface/hub/`
- existe el directorio de artefactos `$STUDIO_DIR/Assets3D/`

Accion si falla: ejecutar `bash scripts/apps/install-hunyuan3d.sh`.

## Gate `PF-H3D-01` — arranque de la API

Criterios de `pass`:

- el proceso `api_server.py` arranca sin error en `127.0.0.1:8081`
- `GET http://127.0.0.1:8081/` devuelve respuesta HTTP
- el log local no muestra `CUDA out of memory` ni `ImportError`

## Gate `PF-H3D-02` — corrida smoke `UC-3D-02`

Criterios de `pass`:

- se envia una imagen fixture de `256x256 px` al `API`
- el `API` devuelve un `glb` con tamano mayor a `1 KB`
- el `glb` es un fichero binario valido (cabecera `glTF`)
- el `glb` se guarda en la carpeta de artefactos canonica
- el log de la corrida se registra

## Gate `PF-H3D-03` — importacion en `Blender`

Criterios de `pass`:

- `Blender` importa el `glb` de la corrida smoke sin error fatal
- el numero de vertices es mayor que `100`
- el objeto importado es visible al renombrar y exportar

## Imagen fixture

La imagen fixture usa el mismo patron de la fase 9:
una imagen sencilla de un objeto aislado sobre fondo neutro.

Ruta recomendada para el fixture smoke:

```text
$STUDIO_DIR/Assets3D/smoke_test/h3d_smoke_01/input/refs/h3d_smoke_01__ref__v001.png
```

Si no existe, puede usarse cualquier imagen `png` del sistema entre `128x128`
y `512x512` con un objeto visible en primer plano.

## Script de validacion

El script canonico esta en:

```text
scripts/apps/hunyuan3d-smoke-validation.sh
```

Ejecutarlo con:

```bash
bash scripts/apps/hunyuan3d-smoke-validation.sh
```

## Comparativa con la linea `SF3D`

Ademas de los gates anteriores, la evidencia smoke debe incluir una
comparativa minima:

- mismo fixture de entrada que algun caso registrado con `SF3D`
- o una descripcion textual de la diferencia visual observada

Esta comparativa es el dato principal que justifica o no el cambio de motor.

## Relacion con `10.10`

Los gates `PF-H3D-00` a `PF-H3D-03` deben pasar antes de abrir `10.10`.
Si alguno falla, `10.10` no debe abrirse hasta depurar el bloqueo.

## Tabla resumen de gates

| Gate | Que verifica | `pass` si... |
| --- | --- | --- |
| `PF-H3D-00` | instalacion | todo instalado y modelo cacheado |
| `PF-H3D-01` | arranque API | respuesta HTTP sin error |
| `PF-H3D-02` | corrida smoke | `glb` generado y guardado |
| `PF-H3D-03` | importacion Blender | objeto importado con vertices |

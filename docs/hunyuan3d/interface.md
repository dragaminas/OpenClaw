# Interfaz Operativa de la Linea Nativa `Hunyuan3D`

Este documento implementa la tarea `10.8` del `DevPlan`.
Define como opera la linea 3D nativa para un usuario no tecnico, dejando claro
cuando se usa la `web UI`, cuando se usa la `API` y que mensajes debe
recibir el operador en cada caso.

## Principio

La interfaz debe ocultar complejidad operativa, no esconder el motor.
El operador debe saber que esta usando una app 3D separada y no confundirla
con `ComfyUI`.

Tres superficies validas:

1. `web UI` de `Hunyuan3D` para operacion manual guiada
2. `API` local para automatizacion controlada
3. WhatsApp via catalogo `UC-3D-*` para la usuaria final no tecnica

## Superficie 1 — `web UI` de `Hunyuan3D`

**Cuando usarla:** operacion manual, pruebas exploratorias, explorar la calidad
de un activo especifico, comparar variantes.

**Como acceder:** abrir `http://127.0.0.1:7860` en el navegador.

**Flujo minimo para `UC-3D-02`:**

1. asegurarse de que `ComfyUI` esta en reposo antes de arrancar
2. arrancar `Hunyuan3D` con `bash scripts/apps/install-hunyuan3d.sh` (ya instalado)
   o directamente:
   ```bash
   cd ~/Hunyuan3D-2
   source .venv/bin/activate
   python3 gradio_app.py \
     --model_path tencent/Hunyuan3D-2mini \
     --subfolder hunyuan3d-dit-v2-mini-turbo \
     --texgen_model_path tencent/Hunyuan3D-2 \
     --low_vram_mode \
     --enable_flashvdm
   ```
3. subir imagen de referencia del objeto o personaje
4. pulsar "Generate"
5. descargar el `glb` cuando termine
6. guardar en `$STUDIO_DIR/Assets3D/<project>/<entity_id>/hunyuan3d/output/`

**Mensajes esperados para el operador:**

| Estado | Mensaje para el operador |
| --- | --- |
| app arrancando | "Hunyuan3D esta cargando el modelo. Espera unos segundos antes de subir una imagen." |
| corrida en marcha | "Generando shape. Esto puede tardar entre 1 y 3 minutos." |
| corrida terminada | "El glb esta listo. Guarda el archivo y abrelo en Blender para revisarlo." |
| OOM o fallo | "La corrida fallo. Cierra ComfyUI si esta activo y vuelve a intentarlo." |
| modelo no cargado | "El modelo no esta cargado todavia. Espera a que el log del servidor diga 'Running on local URL'." |

## Superficie 2 — `API` local

**Cuando usarla:** automatizacion desde scripts, integracion con el runner de
`OpenClaw`, validaciones batch o smoke tests.

**Como acceder:** `http://127.0.0.1:8081` (cuando el servidor API esta en marcha).

**Flujo minimo para `UC-3D-02` via `API`:**

```bash
# arrancar el servidor API (si no esta en marcha)
cd ~/Hunyuan3D-2
source .venv/bin/activate
python3 api_server.py --host 127.0.0.1 --port 8081 \
  --model_path tencent/Hunyuan3D-2mini &

# esperar a que este listo
sleep 5

# enviar imagen al API
curl -s http://127.0.0.1:8081/generate \
  -F "image=@$STUDIO_DIR/Assets3D/myproject/obj_a01/input/refs/obj_a01__ref__v001.png" \
  -F "seed=42" \
  -F "num_inference_steps=10" \
  -F "guidance_scale=5.0" \
  -F "texture=false" \
  -o "$STUDIO_DIR/Assets3D/myproject/obj_a01/hunyuan3d/output/obj_a01__mesh__v001.glb"
```

## Superficie 3 — WhatsApp

**Cuando usarla:** la usuaria final usa comandos en lenguaje natural desde
WhatsApp. El sistema traduce a un `UC-3D-*` y lo ejecuta a traves del runner.

**Comandos validos de producto:**

- `studio imagen-a-3d` — lanza `UC-3D-02`
- `studio texto-a-3d` — lanza `UC-3D-01` con puente imagen
- `studio imagen-a-escena-3d` — lanza `UC-3D-04`
- `studio texto-a-escena-3d` — lanza `UC-3D-03`
- `studio workflows` — lista casos disponibles
- `studio que hace imagen-a-3d` — descripcion del caso

**Respuesta de producto esperada desde WhatsApp:**

Para `UC-3D-02` con la linea nativa lista:

```text
run_id=uc-3d-02-demo-1
status=running
motor=hunyuan3d-2mini-turbo
message=Generando shape desde tu imagen. Te aviso cuando el glb este listo.
```

Para `UC-3D-02` con instalacion pendiente:

```text
run_id=uc-3d-02-demo-1
status=blocked_missing_runtime
motor=hunyuan3d-2mini-turbo
message=Hunyuan3D aun no esta instalado en esta maquina. Ejecuta scripts/apps/install-hunyuan3d.sh para prepararlo.
```

## Secuencia guiada para la usuaria final

La interfaz de producto no debe preguntar por el motor ni por el venv.
La secuencia guiada minima debe ser:

1. que quieres: `asset`, `set de activos`, `envolvente` o `blockout`
2. tienes imagen de referencia o arrancamos desde texto
3. que categoria: `objeto`, `personaje`, `envolvente`
4. (opcional) escala aproximada

Despues la persona no tiene que saber que el motor es `Hunyuan3D`.

## Mensajes clave de estado

Mensajes del sistema que la interfaz debe saber comunicar:

| Evento | Mensaje al usuario |
| --- | --- |
| inicio corrida | "Generando tu activo 3D. Tarda unos minutos." |
| corrida ok | "Tu activo esta listo. Puedes revisarlo en Blender." |
| bloqueo por VRAM | "La maquina esta ocupada con otra tarea pesada. Espera a que termine." |
| textura rechazada | "El modo textura no cabe en este momento. Puedo darte el shape util sin textura." |
| escena monolitica imposible | "Esta referencia tiene muchas piezas. Conviene generarlas por separado y componerlas en Blender." |
| linea no instalada | "Esta funcion necesita una instalacion previa. Pedile al administrador que ejecute install-hunyuan3d.sh." |

## Relacion con otros documentos

- contrato de I/O: `docs/hunyuan3d/io-contract.md`
- mapa de casos de uso: `docs/hunyuan3d/usecase-map.md`
- arquitectura del runtime: `docs/hunyuan3d/native-runtime-architecture.md`
- smoke tests y validacion: `docs/hunyuan3d/smoke-validation.md`

# Resultados de Validacion Real Local — `Hunyuan3D` Nativo

Este documento implementa la tarea `10.10` del `DevPlan`.
Registra el estado de la validacion real local de `UC-3D-01` y `UC-3D-02`
sobre la linea nativa `Hunyuan3D-2mini-Turbo`.

## Estado

- estado: `pass_smoke`
- fecha de corte: `2026-04-18`
- maquina: `RTX 3060 12 GB`, `Ubuntu`, `CUDA 13.0 / driver 580.126.09`
- modelo: `tencent/Hunyuan3D-2mini`, subfolder `hunyuan3d-dit-v2-mini-turbo`
- flags: `--low_vram_mode --enable_flashvdm`

## Lectura correcta de este resultado

Este documento demuestra dos cosas concretas:

- la cadena `imagen -> API Hunyuan3D -> glb -> Blender` se ejecuto de verdad
- la linea nativa es operable de forma reproducible en el hardware local

No demuestra por si mismo:

- que la calidad visual obtenida sea superior a `SF3D` con una imagen creativa
  real (la corrida smoke uso un fixture sintetico de referencia, no una imagen
  de producto)

La comparativa visual honesta frente a `SF3D` requiere correr ambos motores
con la misma imagen de entrada y leer los resultados lado a lado.
Esa comparativa queda como proximo paso, no como bloqueante del cierre de la fase.

## Que se ejecuto de verdad

Se ejecuto la bateria `bash scripts/apps/hunyuan3d-smoke-validation.sh`
con los siguientes resultados por gate:

| Gate | Descripcion | Resultado |
| --- | --- | --- |
| `PF-H3D-00` | Instalacion: venv, PyTorch CUDA, pesos, dependencias | `PASS` |
| `PF-H3D-01` | Servidor API en `:8081`, arranque en ~`15 s` | `PASS` |
| `PF-H3D-02` | Corrida smoke `UC-3D-02`, glb generado | `PASS` |
| `PF-H3D-03` | Importacion del glb en Blender `5.1.1` | `PASS` |

Resultado final del script: `PASS=10 FAIL=0`.

## Resultado real

### Caso `AT-H3D-OBJ-01` — corrida `UC-3D-02` single-image

- input: `h3d_smoke_01__ref__v001.png` (fixture sintetico 256x256, gris con bloque azul)
- motor: `Hunyuan3D-2mini-Turbo`, `5` pasos de difusion, `low_vram_mode`, `enable_flashvdm`
- output: `h3d_smoke_01__mesh__v001.glb`
- tamano `glb`: `842.348 bytes` (`823 KB`)
- tiempo de inferencia: **`3.20 s`** (medido por el propio `api_server`)
- desglose de tiempos:
  - arranque del modelo (primera carga): `~15 s`
  - difusion `5` pasos a `~3.25 it/s`: `~1.6 s`
  - `FlashVDM Volume Decoding` `64` chunks a `1290 it/s`: `< 0.1 s`
- criterio `pass`: cumplido — glb > 1 KB, cabecera glTF valida

### Caso `AT-H3D-OBJ-02` — importacion Blender

- input: `h3d_smoke_01__mesh__v001.glb`
- herramienta: `Blender 5.1.1` (snap), modo headless, `bpy.ops.import_scene.gltf`
- resultado: `1` mesh, `23.376` vertices
- tiempo de importacion: `< 0.1 s`
- criterio `pass`: cumplido — objeto importado sin error, vertices > 100

### Caso `CP-H3D-01` — `UC-3D-01` puente texto -> imagen -> `Hunyuan3D`

- estado: `pendiente`
- requiere: corrida de `ComfyUI` generando imagen semilla desde prompt de texto,
  luego esa imagen como entrada al API de `Hunyuan3D`
- no es bloqueante para el smoke; es la validacion del flujo completo de `UC-3D-01`

### Comparativa frente a `SF3D`

- estado: `pendiente`
- fixture recomendado: la misma imagen que produjo
  `validation_sf3d_cpu_fallback_00001_.glb` en la fase 9
  (`/home/eric/ComfyUI/input/openclaw_object_ref.png`)
- lectura esperada: si `Hunyuan3D-2mini-Turbo` supera el nivel visual de `SF3D`
  con esa entrada, la decision `10.14` queda reforzada; si no, documentar

## Artefactos producidos

```
~/Studio/Assets3D/smoke_test/h3d_smoke_01/
├── input/refs/h3d_smoke_01__ref__v001.png        (fixture de entrada)
├── hunyuan3d/output/h3d_smoke_01__mesh__v001.glb (glb validado)
└── hunyuan3d/logs/
    ├── api_server.log                             (arranque + inferencia)
    └── h3d_smoke_01__run__v001.log                (respuesta del API)
```

## Tabla de resultados

| Caso | Estado | GLB bytes | Vertices | Tiempo inferencia | Lectura visual |
| --- | --- | --- | --- | --- | --- |
| `AT-H3D-OBJ-01` | `pass` | `842.348` | — | `3.20 s` | fixture sintetico |
| `AT-H3D-OBJ-02` | `pass` | `842.348` | `23.376` | `< 0.1 s` | importacion limpia |
| `CP-H3D-01` | `pendiente` | — | — | — | — |
| Comparativa SF3D | `pendiente` | — | — | — | — |

## Lo que si queda validado

- la instalacion de `Hunyuan3D-2mini-Turbo` es reproducible desde el script
- el servidor API arranca en el puerto `8081` de forma estable
- la corrida `imagen -> glb` completa en `~3 s` en el hardware local
- el `glb` resultante es importable en `Blender 5.1.1` sin error
- la convivencia con `ComfyUI` no genera conflictos (cada app en su venv)

## Lo que sigue pendiente

- correr `CP-H3D-01` con una imagen creativa real para validar `UC-3D-01`
- comparar visualmente el glb de `Hunyuan3D` con el glb de `SF3D` usando
  la misma imagen de entrada de la fase 9
- si la calidad visual supera a `SF3D`, documentar en este mismo archivo
  y marcar la comparativa como `pass_visual`

## Evidencia principal

```bash
# Ejecutar la bateria completa
bash scripts/apps/hunyuan3d-smoke-validation.sh

# Verificar artefactos
ls -lh ~/Studio/Assets3D/smoke_test/h3d_smoke_01/hunyuan3d/output/
# h3d_smoke_01__mesh__v001.glb  823K

# Reproducir solo la importacion Blender
python3 - << 'EOF'
import subprocess, tempfile, os
glb = os.path.expanduser(
    "~/Studio/Assets3D/smoke_test/h3d_smoke_01/hunyuan3d/output/h3d_smoke_01__mesh__v001.glb"
)
script = tempfile.mktemp(suffix=".py")
open(script, "w").write("""
import bpy, sys
glb = sys.argv[sys.argv.index("--") + 1]
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath=glb)
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
print(f"OK: {len(ms)} meshes, {sum(len(o.data.vertices) for o in ms)} vertices")
""")
r = subprocess.run(["blender", "-b", "--python", script, "--", glb],
                   capture_output=True, text=True)
print(r.stdout[-500:])
os.unlink(script)
EOF
```

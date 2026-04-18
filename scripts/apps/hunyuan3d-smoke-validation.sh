#!/usr/bin/env bash
# scripts/apps/hunyuan3d-smoke-validation.sh
#
# Smoke validation para la linea nativa Hunyuan3D.
# Verifica los gates PF-H3D-00 a PF-H3D-03.
# Ver docs/hunyuan3d/smoke-validation.md para especificacion completa.
#
# Uso:
#   bash scripts/apps/hunyuan3d-smoke-validation.sh
#
# Variables de entorno respetadas:
#   HUNYUAN3D_DIR   — ruta de instalacion (por defecto ~/Hunyuan3D-2)
#   STUDIO_DIR      — directorio de trabajo creativo (por defecto ~/Studio)
#   H3D_API_PORT    — puerto del servidor API (por defecto 8081)
#   FIXTURE_IMAGE   — imagen fixture a usar (se crea si no existe)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$(dirname "$SCRIPT_DIR")/lib"
source "$LIB_DIR/common.sh" 2>/dev/null || true

HUNYUAN3D_DIR="${HUNYUAN3D_DIR:-$HOME/Hunyuan3D-2}"
STUDIO_DIR="${STUDIO_DIR:-$HOME/Studio}"
H3D_API_PORT="${H3D_API_PORT:-8081}"
VENV_PYTHON="$HUNYUAN3D_DIR/.venv/bin/python3"

SMOKE_BASE="$STUDIO_DIR/Assets3D/smoke_test/h3d_smoke_01"
SMOKE_INPUT="$SMOKE_BASE/input/refs"
SMOKE_OUTPUT="$SMOKE_BASE/hunyuan3d/output"
SMOKE_LOGS="$SMOKE_BASE/hunyuan3d/logs"
FIXTURE_IMAGE="${FIXTURE_IMAGE:-$SMOKE_INPUT/h3d_smoke_01__ref__v001.png}"
OUTPUT_GLB="$SMOKE_OUTPUT/h3d_smoke_01__mesh__v001.glb"

PASS=0
FAIL=0
API_PID=""

log_gate() { echo "[smoke-h3d] GATE $1: $2"; }
log_pass() { echo "[smoke-h3d] PASS:  $*"; ((PASS+=1)) || true; }
log_fail() { echo "[smoke-h3d] FAIL:  $*" >&2; ((FAIL+=1)) || true; }
log_info() { echo "[smoke-h3d] INFO:  $*"; }
log_skip() { echo "[smoke-h3d] SKIP:  $*"; }

# ---------------------------------------------------------------------------
# GATE PF-H3D-00: verificar instalacion
# ---------------------------------------------------------------------------
log_gate "PF-H3D-00" "Verificando instalacion de Hunyuan3D ..."

if [[ -f "$HUNYUAN3D_DIR/gradio_app.py" ]]; then
    log_pass "gradio_app.py encontrado en $HUNYUAN3D_DIR"
else
    log_fail "gradio_app.py NO encontrado. Ejecuta: bash scripts/apps/install-hunyuan3d.sh"
    exit 1
fi

if [[ -x "$VENV_PYTHON" ]]; then
    log_pass "venv python encontrado: $VENV_PYTHON"
else
    log_fail "venv python NO encontrado en $VENV_PYTHON"
    exit 1
fi

if "$VENV_PYTHON" -c "import torch; assert torch.cuda.is_available()" 2>/dev/null; then
    log_pass "torch con CUDA disponible"
else
    log_fail "torch sin CUDA — la inferencia no funcionara en GPU"
    FAIL=$((FAIL+1))
fi

for PKG in trimesh huggingface_hub; do
    if "$VENV_PYTHON" -c "import $PKG" 2>/dev/null; then
        log_pass "dependencia $PKG ok"
    else
        log_fail "dependencia $PKG NO encontrada"
    fi
done

if ls ~/.cache/huggingface/hub/ 2>/dev/null | grep -q "Hunyuan"; then
    log_pass "modelo cacheado en ~/.cache/huggingface/hub/"
else
    log_fail "modelo Hunyuan NO encontrado en cache. Ejecuta install-hunyuan3d.sh"
    FAIL=$((FAIL+1))
fi

# ---------------------------------------------------------------------------
# Preparar carpetas de artefactos
# ---------------------------------------------------------------------------
mkdir -p "$SMOKE_INPUT" "$SMOKE_OUTPUT" "$SMOKE_LOGS"

# ---------------------------------------------------------------------------
# Preparar imagen fixture si no existe
# ---------------------------------------------------------------------------
if [[ ! -f "$FIXTURE_IMAGE" ]]; then
    log_info "Fixture no encontrado. Generando imagen de prueba minima ..."
    "$VENV_PYTHON" - <<PYEOF
from PIL import Image
import os
img = Image.new("RGB", (256, 256), color=(200, 200, 200))
# dibujar un rectangulo como proxy de objeto
for x in range(80, 180):
    for y in range(60, 200):
        img.putpixel((x, y), (100, 120, 180))
os.makedirs(os.path.dirname("$FIXTURE_IMAGE"), exist_ok=True)
img.save("$FIXTURE_IMAGE")
print("Fixture creado: $FIXTURE_IMAGE")
PYEOF
    if [[ -f "$FIXTURE_IMAGE" ]]; then
        log_pass "Fixture creado: $FIXTURE_IMAGE"
    else
        log_fail "No se pudo crear el fixture. Instala Pillow o proporciona FIXTURE_IMAGE."
        exit 1
    fi
else
    log_pass "Fixture encontrado: $FIXTURE_IMAGE"
fi

# ---------------------------------------------------------------------------
# GATE PF-H3D-01: arranque del servidor API
# ---------------------------------------------------------------------------
log_gate "PF-H3D-01" "Verificando servidor API en puerto $H3D_API_PORT ..."

if nc -z 127.0.0.1 "$H3D_API_PORT" 2>/dev/null; then
    log_pass "Servidor API ya en marcha en puerto $H3D_API_PORT"
    API_EXTERNAL=1
else
    log_info "Servidor API no esta activo. Arrancando en segundo plano ..."

    cd "$HUNYUAN3D_DIR"
    source ".venv/bin/activate"
    python3 api_server.py \
        --host 127.0.0.1 \
        --port "$H3D_API_PORT" \
        --model_path tencent/Hunyuan3D-2mini \
        >> "$SMOKE_LOGS/api_server.log" 2>&1 &
    API_PID=$!
    deactivate 2>/dev/null || true
    cd - >/dev/null

    log_info "Esperando a que el servidor API arranque (PID=$API_PID) ..."
    WAIT=0
    while [[ $WAIT -lt 60 ]]; do
        sleep 3
        WAIT=$((WAIT+3))
        if nc -z 127.0.0.1 "$H3D_API_PORT" 2>/dev/null; then
            break
        fi
    done

    if nc -z 127.0.0.1 "$H3D_API_PORT" 2>/dev/null; then
        log_pass "Servidor API respondiendo en puerto $H3D_API_PORT"
    else
        log_fail "Servidor API no responde despues de $WAIT segundos"
        log_fail "Revisa: $SMOKE_LOGS/api_server.log"
        FAIL=$((FAIL+1))
    fi
fi

# ---------------------------------------------------------------------------
# GATE PF-H3D-02: corrida smoke UC-3D-02
# ---------------------------------------------------------------------------
log_gate "PF-H3D-02" "Enviando imagen fixture al API ..."

RUN_LOG="$SMOKE_LOGS/h3d_smoke_01__run__v001.log"

if nc -z 127.0.0.1 "$H3D_API_PORT" 2>/dev/null; then
    set +e
    # El API espera JSON con imagen en base64, no multipart
    "$VENV_PYTHON" - >> "$RUN_LOG" 2>&1 <<PYEOF
import base64, json, sys, urllib.request, urllib.error, os

fixture = "$FIXTURE_IMAGE"
output  = "$OUTPUT_GLB"
port    = int("$H3D_API_PORT")

with open(fixture, "rb") as fh:
    img_b64 = base64.b64encode(fh.read()).decode()

payload = json.dumps({
    "image": img_b64,
    "seed": 42,
    "num_inference_steps": 5,
    "guidance_scale": 5.0,
    "texture": False,
}).encode()

req = urllib.request.Request(
    f"http://127.0.0.1:{port}/generate",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = resp.read()
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "wb") as fh:
        fh.write(data)
    print(f"OK: {len(data)} bytes -> {output}")
except urllib.error.HTTPError as e:
    body = e.read().decode(errors="replace")
    print(f"ERR HTTP {e.code}: {body}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERR: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF
    CURL_EXIT=$?
    set -e

    if [[ $CURL_EXIT -eq 0 ]] && [[ -f "$OUTPUT_GLB" ]]; then
        GLB_SIZE=$(wc -c < "$OUTPUT_GLB" 2>/dev/null || echo 0)
        if [[ $GLB_SIZE -gt 1000 ]]; then
            log_pass "glb generado: $OUTPUT_GLB ($GLB_SIZE bytes)"
        else
            log_fail "glb generado pero demasiado pequeño ($GLB_SIZE bytes) — posible fallo de inferencia"
        fi
    else
        log_fail "La corrida smoke fallo o no genero glb. Revisa: $RUN_LOG"
        FAIL=$((FAIL+1))
    fi
else
    log_skip "PF-H3D-02: servidor API no disponible — no se puede ejecutar corrida smoke"
    FAIL=$((FAIL+1))
fi

# ---------------------------------------------------------------------------
# GATE PF-H3D-03: importacion en Blender
# ---------------------------------------------------------------------------
log_gate "PF-H3D-03" "Verificando importacion del glb en Blender ..."

if [[ -f "$OUTPUT_GLB" ]] && command -v blender >/dev/null 2>&1; then
    BLENDER_LOG="$SMOKE_LOGS/h3d_smoke_01__blender__v001.log"

    # Usamos python subprocess con capture_output=True porque el snap Blender
    # omite redirecciones de shell (escribe a /dev/tty) pero si responde a pipes.
    set +e
    python3 - << PYEOF >> "$BLENDER_LOG" 2>&1
import subprocess, sys, shutil

blender_bin = shutil.which("blender")
glb = "$OUTPUT_GLB"

script_src = '''
import bpy, sys
glb_path = sys.argv[sys.argv.index("--") + 1]
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
try:
    bpy.ops.import_scene.gltf(filepath=glb_path)
except Exception as e:
    print(f"[smoke-h3d] BLENDER_ERR: {e}")
    sys.exit(1)
imported = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if not imported:
    print("[smoke-h3d] BLENDER_ERR: no mesh objects found after import")
    sys.exit(1)
total_verts = sum(len(o.data.vertices) for o in imported)
print(f"[smoke-h3d] BLENDER_OK: {len(imported)} meshes, {total_verts} vertices")
sys.exit(0)
'''

import tempfile, os
with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tf:
    tf.write(script_src)
    script_path = tf.name

try:
    result = subprocess.run(
        [blender_bin, "-b", "--python", script_path, "--", glb],
        capture_output=True, text=True, timeout=120,
    )
    combined = result.stdout + result.stderr
    print(combined)
    sys.exit(result.returncode)
except Exception as e:
    print(f"[smoke-h3d] BLENDER_ERR subprocess: {e}")
    sys.exit(1)
finally:
    os.unlink(script_path)
PYEOF
    BLENDER_EXIT=$?
    set -e

    if [[ $BLENDER_EXIT -eq 0 ]]; then
        VERT_INFO=$(grep "BLENDER_OK" "$BLENDER_LOG" | tail -1)
        log_pass "Blender: $VERT_INFO"
    else
        log_fail "Blender no importo correctamente el glb. Revisa: $BLENDER_LOG"
        FAIL=$((FAIL+1))
    fi
else
    if [[ ! -f "$OUTPUT_GLB" ]]; then
        log_skip "PF-H3D-03: glb no disponible — saltar importacion Blender"
    else
        log_skip "PF-H3D-03: Blender no encontrado — saltar importacion"
    fi
fi

# ---------------------------------------------------------------------------
# Apagar servidor API si lo arrancamos nosotros
# ---------------------------------------------------------------------------
if [[ -n "$API_PID" ]]; then
    log_info "Parando servidor API local (PID=$API_PID) ..."
    kill "$API_PID" 2>/dev/null || true
fi

# ---------------------------------------------------------------------------
# Resumen
# ---------------------------------------------------------------------------
echo ""
echo "[smoke-h3d] =================================================="
echo "[smoke-h3d] Resultado: PASS=$PASS  FAIL=$FAIL"
echo "[smoke-h3d] Artefactos en: $SMOKE_BASE"
if [[ $FAIL -eq 0 ]]; then
    echo "[smoke-h3d] ESTADO: OK — linea nativa lista para 10.10"
else
    echo "[smoke-h3d] ESTADO: BLOQUEADO — revisar fallos antes de abrir 10.10"
fi
echo "[smoke-h3d] =================================================="

[[ $FAIL -eq 0 ]] && exit 0 || exit 1

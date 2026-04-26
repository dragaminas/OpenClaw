#!/usr/bin/env bash
# scripts/apps/install-hunyuan3d.sh
#
# Instalacion reproducible de Hunyuan3D-2 nativo.
# Compatible con la arquitectura definida en docs/hunyuan3d/installation.md
#
# Uso:
#   bash scripts/apps/install-hunyuan3d.sh
#
# Variables de entorno respetadas:
#   HUNYUAN3D_DIR   — ruta de instalacion (por defecto ~/Hunyuan3D-2)
#   SKIP_MODEL_DOWNLOAD — si se define, omite la descarga de pesos
#   MODEL_REPO      — repo HF a precachear (por defecto tencent/Hunyuan3D-2mini)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$(dirname "$SCRIPT_DIR")/lib"
# shellcheck source=scripts/lib/common.sh
source "$LIB_DIR/common.sh" 2>/dev/null || true

REPO_URL="https://github.com/Tencent-Hunyuan/Hunyuan3D-2.git"
HUNYUAN3D_DIR="${HUNYUAN3D_DIR:-$HOME/Hunyuan3D-2}"
VENV_DIR="$HUNYUAN3D_DIR/.venv"
LOGS_DIR="$HOME/logs/hunyuan3d"
MODEL_REPO="${MODEL_REPO:-tencent/Hunyuan3D-2mini}"

log_info() { echo "[install-hunyuan3d] INFO: $*"; }
log_ok()   { echo "[install-hunyuan3d] OK:   $*"; }
log_err()  { echo "[install-hunyuan3d] ERR:  $*" >&2; }

# ---------------------------------------------------------------------------
# 1. Clonar repo si no existe
# ---------------------------------------------------------------------------
log_info "Verificando directorio de instalacion: $HUNYUAN3D_DIR"
if [[ -d "$HUNYUAN3D_DIR" ]]; then
    log_ok "Directorio ya existe, omitiendo clone."
else
    log_info "Clonando $REPO_URL ..."
    git clone --depth 1 "$REPO_URL" "$HUNYUAN3D_DIR"
    log_ok "Repo clonado correctamente."
fi

cd "$HUNYUAN3D_DIR"

# ---------------------------------------------------------------------------
# 2. Crear venv aislado si no existe
# ---------------------------------------------------------------------------
if [[ -d "$VENV_DIR" ]]; then
    log_ok "Venv ya existe en $VENV_DIR"
else
    log_info "Creando venv en $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
    log_ok "Venv creado."
fi

PYTHON="$VENV_DIR/bin/python3"
PIP="$VENV_DIR/bin/pip"

# ---------------------------------------------------------------------------
# 3. Instalar dependencias base del repo
# ---------------------------------------------------------------------------
log_info "Actualizando pip y wheel ..."
"$PIP" install --upgrade pip wheel setuptools -q

if [[ -f "requirements.txt" ]]; then
    log_info "Instalando requirements.txt ..."
    "$PIP" install -r requirements.txt -q
    log_ok "requirements.txt instalado."
else
    log_err "No se encontro requirements.txt en $HUNYUAN3D_DIR"
    log_err "Verifica que el repo se clono correctamente."
    exit 1
fi

# ---------------------------------------------------------------------------
# 4. Instalar dependencias auxiliares canonicas
# ---------------------------------------------------------------------------
log_info "Instalando dependencias auxiliares ..."
"$PIP" install -q \
    "huggingface_hub>=0.19" \
    "trimesh" \
    "gradio>=5,<6" \
    "sentencepiece" \
    "tiktoken"

log_ok "Dependencias auxiliares instaladas."

# ---------------------------------------------------------------------------
# 5. Verificar torch + CUDA
# ---------------------------------------------------------------------------
log_info "Verificando PyTorch con soporte CUDA ..."
if "$PYTHON" -c "import torch; assert torch.cuda.is_available(), 'CUDA no disponible'" 2>/dev/null; then
    TORCH_VER=$("$PYTHON" -c "import torch; print(torch.__version__)" 2>/dev/null)
    log_ok "PyTorch $TORCH_VER con CUDA disponible."
else
    log_err "CUDA no disponible en el venv actual."
    log_err "Instala manualmente el torch correcto para tu driver CUDA:"
    log_err "  https://pytorch.org/get-started/locally/"
    log_err "El resto de la instalacion puede continuar, pero la inferencia fallara."
fi

# ---------------------------------------------------------------------------
# 6. Descargar pesos del modelo baseline
# ---------------------------------------------------------------------------
if [[ -n "${SKIP_MODEL_DOWNLOAD:-}" ]]; then
    log_info "SKIP_MODEL_DOWNLOAD activado — omitiendo descarga de pesos."
else
    log_info "Descargando pesos de $MODEL_REPO a ~/.cache/huggingface/hub ..."
    log_info "Esto puede tardar varios minutos la primera vez."
    MODEL_REPO="$MODEL_REPO" "$PYTHON" - <<'PYEOF'
from huggingface_hub import snapshot_download
import os

model_repo = os.environ.get("MODEL_REPO", "tencent/Hunyuan3D-2mini")
print(f"[install-hunyuan3d] Descargando {model_repo} ...")
path = snapshot_download(repo_id=model_repo)
print(f"[install-hunyuan3d] Pesos cacheados en: {path}")
PYEOF
    log_ok "Pesos descargados correctamente."
fi

# ---------------------------------------------------------------------------
# 7. Crear directorio de logs
# ---------------------------------------------------------------------------
mkdir -p "$LOGS_DIR"
log_ok "Directorio de logs: $LOGS_DIR"

# ---------------------------------------------------------------------------
# 8. Verificacion rapida de importaciones clave
# ---------------------------------------------------------------------------
log_info "Verificando importaciones clave ..."
"$PYTHON" -c "import trimesh; print('[install-hunyuan3d] trimesh ok')"
"$PYTHON" -c "import huggingface_hub; print('[install-hunyuan3d] huggingface_hub ok')"

# Verificar que gradio_app.py existe
if [[ -f "$HUNYUAN3D_DIR/gradio_app.py" ]]; then
    log_ok "gradio_app.py encontrado."
else
    log_err "gradio_app.py no encontrado en $HUNYUAN3D_DIR"
    log_err "Verifica que el repo es el oficial Hunyuan3D-2."
    exit 1
fi

# Verificar que api_server.py existe
if [[ -f "$HUNYUAN3D_DIR/api_server.py" ]]; then
    log_ok "api_server.py encontrado."
else
    log_err "api_server.py no encontrado — la integracion API no estara disponible."
fi

# ---------------------------------------------------------------------------
# 9. Sincronizar plantilla de servicio systemd (siempre, para aplicar cambios)
# ---------------------------------------------------------------------------
SYSTEMD_TEMPLATE="$SCRIPT_DIR/../../configs/systemd-user/hunyuan3d.service.template"
SYSTEMD_DIR="$HOME/.config/systemd/user"
SYSTEMD_SERVICE="$SYSTEMD_DIR/hunyuan3d.service"

if [[ -f "$SYSTEMD_TEMPLATE" ]]; then
    mkdir -p "$SYSTEMD_DIR"
    cp "$SYSTEMD_TEMPLATE" "$SYSTEMD_SERVICE"
    systemctl --user daemon-reload 2>/dev/null || true
    log_ok "Unidad systemd sincronizada: $SYSTEMD_SERVICE"
    log_info "Para activar el servicio: systemctl --user enable --now hunyuan3d.service"
else
    log_err "No se encontro la plantilla $SYSTEMD_TEMPLATE"
fi

# ---------------------------------------------------------------------------
# 10. Compilar extensiones CUDA (best-effort)
# ---------------------------------------------------------------------------
log_info "Intentando compilar extensiones CUDA (custom_rasterizer, differentiable_renderer)..."
HUNYUAN3D_DIR="$HUNYUAN3D_DIR" bash "$SCRIPT_DIR/hunyuan3d.sh" compile-extensions \
  2>&1 && log_ok "Extensiones CUDA compiladas." \
  || log_err "No se pudieron compilar las extensiones CUDA (la generacion de forma 3D funciona igual)."
log_info "Si la compilacion fallo, ejecuta: scripts/apps/hunyuan3d.sh compile-extensions"

# ---------------------------------------------------------------------------
# 11. Parche de memoria: CPU offload para HunyuanDiT (text-to-3D en GPUs <=12 GB)
# ---------------------------------------------------------------------------
# El pipeline HunyuanDiT (texto→imagen) carga ~8 GB en VRAM. Sin offload, no
# queda espacio para el modelo de forma 3D en tarjetas de 12 GB (ej. RTX 3060).
# El parche reemplaza .to(device) por enable_model_cpu_offload() para que el
# modelo resida en RAM durante startup y sólo ocupe VRAM durante inferencia.
T2I_FILE="$HUNYUAN3D_DIR/hy3dgen/text2image.py"
if [[ -f "$T2I_FILE" ]]; then
    if grep -q "enable_model_cpu_offload" "$T2I_FILE"; then
        log_ok "Parche CPU offload ya aplicado en text2image.py."
    else
        # Reemplaza .to(device) por enable_model_cpu_offload() en __init__
        T2I_FILE="$T2I_FILE" python3 - <<'PYEOF'
import re, os
path = os.environ['T2I_FILE']
txt = open(path).read()
# Remove .to(device) call chained on the pipeline constructor
txt = re.sub(r'(\)\s*)\.to\(device\)', r'\1', txt)
# Insert enable_model_cpu_offload after self.pipe assignment
txt = re.sub(
    r'(self\.pipe\s*=\s*AutoPipelineForText2Image\.from_pretrained\([^)]+\))',
    r'\1\n        # CPU offload: model stays in RAM, moves to GPU only during inference.\n        # Required on GPUs <=12 GB to leave room for the 3D shape model.\n        self.pipe.enable_model_cpu_offload()',
    txt)
# Fix torch.Generator to use stored self.device instead of self.pipe.device
txt = txt.replace('torch.Generator(device=self.pipe.device)', 'torch.Generator(device=self.device)')
open(path, 'w').write(txt)
print("Parche aplicado.")
PYEOF
        if grep -q "enable_model_cpu_offload" "$T2I_FILE"; then
            log_ok "Parche CPU offload aplicado en $T2I_FILE."
        else
            log_err "El parche CPU offload no pudo aplicarse automaticamente."
            log_info "Edita manualmente $T2I_FILE: cambia .to(device) por .enable_model_cpu_offload()"
        fi
    fi
else
    log_err "No se encontro $T2I_FILE – omitiendo parche CPU offload."
fi

# ---------------------------------------------------------------------------
# 12. Parche loader shape: fallback de .safetensors a .ckpt para Hunyuan3D-2.1
# ---------------------------------------------------------------------------
SHAPE_PIPELINES_FILE="$HUNYUAN3D_DIR/hy3dgen/shapegen/pipelines.py"
if [[ -f "$SHAPE_PIPELINES_FILE" ]]; then
    if grep -q "falling back to checkpoint file" "$SHAPE_PIPELINES_FILE"; then
        log_ok "Parche fallback .safetensors/.ckpt ya aplicado en pipelines.py."
    else
        log_info "Aplicando parche fallback .safetensors/.ckpt en pipelines.py ..."
        SHAPE_PIPELINES_FILE="$SHAPE_PIPELINES_FILE" python3 - <<'PYEOF'
import os
from pathlib import Path

path = Path(os.environ["SHAPE_PIPELINES_FILE"])
txt = path.read_text()
old = """        # load ckpt
        if use_safetensors:
            ckpt_path = ckpt_path.replace('.ckpt', '.safetensors')
        if not os.path.exists(ckpt_path):
            raise FileNotFoundError(f"Model file {ckpt_path} not found")
        logger.info(f"Loading model from {ckpt_path}")
"""
new = """        # load ckpt
        if use_safetensors:
            safetensors_path = ckpt_path
            if ckpt_path.endswith('.ckpt'):
                safetensors_path = ckpt_path.replace('.ckpt', '.safetensors')
                ckpt_fallback_path = ckpt_path
            else:
                ckpt_fallback_path = ckpt_path.replace('.safetensors', '.ckpt')

            if os.path.exists(safetensors_path):
                ckpt_path = safetensors_path
            elif os.path.exists(ckpt_fallback_path):
                logger.warning(
                    f"Safetensors checkpoint {safetensors_path} not found; "
                    f"falling back to checkpoint file {ckpt_fallback_path}"
                )
                ckpt_path = ckpt_fallback_path
                use_safetensors = False
            else:
                raise FileNotFoundError(f"Model file {safetensors_path} not found")
        elif not os.path.exists(ckpt_path):
            safetensors_fallback_path = ckpt_path.replace('.ckpt', '.safetensors')
            if os.path.exists(safetensors_fallback_path):
                logger.warning(
                    f"Checkpoint file {ckpt_path} not found; "
                    f"falling back to safetensors {safetensors_fallback_path}"
                )
                ckpt_path = safetensors_fallback_path
                use_safetensors = True
            else:
                raise FileNotFoundError(f"Model file {ckpt_path} not found")
        logger.info(f"Loading model from {ckpt_path}")
"""
if old not in txt:
    raise SystemExit("No se encontro el bloque esperado en pipelines.py")
path.write_text(txt.replace(old, new))
print("Parche aplicado.")
PYEOF
        if grep -q "falling back to checkpoint file" "$SHAPE_PIPELINES_FILE"; then
            log_ok "Parche fallback .safetensors/.ckpt aplicado en $SHAPE_PIPELINES_FILE."
        else
            log_err "El parche fallback .safetensors/.ckpt no pudo aplicarse automaticamente."
        fi
    fi
else
    log_err "No se encontro $SHAPE_PIPELINES_FILE – omitiendo parche fallback .safetensors/.ckpt."
fi

# ---------------------------------------------------------------------------
# 13. Descargar model-viewer.min.js local (elimina dependencia de CDN externo)
# ---------------------------------------------------------------------------
# gradio_app.py copia assets/model-viewer.min.js a gradio_cache/outputs/ al
# arrancar. Sin este archivo los iframes del viewer 3D no cargan nada.
MV_JS="$HUNYUAN3D_DIR/assets/model-viewer.min.js"
MV_URL="https://cdn.jsdelivr.net/npm/@google/model-viewer@3.1.1/dist/model-viewer.min.js"
if [[ -f "$MV_JS" && -s "$MV_JS" ]]; then
    log_ok "model-viewer.min.js ya existe en assets/."
else
    log_info "Descargando model-viewer.min.js desde jsDelivr ..."
    if curl -fsSL -o "$MV_JS" "$MV_URL"; then
        log_ok "model-viewer.min.js descargado ($(du -h "$MV_JS" | cut -f1))."
    else
        log_err "No se pudo descargar model-viewer.min.js."
        log_info "Descargalo manualmente desde: $MV_URL"
        log_info "y guardalo en: $MV_JS"
    fi
fi

# ---------------------------------------------------------------------------
# 14. Parche de rutas estaticas: /static → /outputs en gradio_app.py y templates
# ---------------------------------------------------------------------------
# FastAPI.mount("/static") toma precedencia sobre la ruta interna de Gradio,
# provocando 404 en fuentes IBMPlexSans, CSS y JS del cliente Gradio.
# El JS roto hace que el formulario envie data:[] al backend → generacion falla.
# Fix: el mount de outputs se registra en /outputs; Gradio conserva /static.
GRADIO_APP="$HUNYUAN3D_DIR/gradio_app.py"
TMPL_PLAIN="$HUNYUAN3D_DIR/assets/modelviewer-template.html"
TMPL_TEXTURED="$HUNYUAN3D_DIR/assets/modelviewer-textured-template.html"

if grep -q 'mount("/outputs"' "$GRADIO_APP" 2>/dev/null; then
    log_ok "Parche /static→/outputs ya aplicado en gradio_app.py."
else
    log_info "Aplicando parche /static→/outputs en gradio_app.py y templates HTML..."
    GRADIO_APP="$GRADIO_APP" TMPL_PLAIN="$TMPL_PLAIN" TMPL_TEXTURED="$TMPL_TEXTURED" \
    python3 - <<'PYEOF'
import os, re

def patch_file(path, replacements):
    with open(path) as f:
        txt = f.read()
    for old, new in replacements:
        txt = txt.replace(old, new)
    with open(path, 'w') as f:
        f.write(txt)

# gradio_app.py: rename mount path and update iframe URL + print message
patch_file(os.environ['GRADIO_APP'], [
    ('app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")',
     'app.mount("/outputs", StaticFiles(directory=static_dir, html=True), name="outputs")'),
    ('/static/{rel_path}', '/outputs/{rel_path}'),
])
print("[install-hunyuan3d] gradio_app.py parchado.")

# HTML templates: todas las referencias /static/ → /outputs/
for key in ('TMPL_PLAIN', 'TMPL_TEXTURED'):
    path = os.environ.get(key, '')
    if path and os.path.isfile(path):
        with open(path) as f:
            txt = f.read()
        txt = txt.replace('/static/', '/outputs/')
        with open(path, 'w') as f:
            f.write(txt)
        print(f"[install-hunyuan3d] {os.path.basename(path)} parchado.")
PYEOF
    if grep -q 'mount("/outputs"' "$GRADIO_APP" 2>/dev/null; then
        log_ok "Parche /static→/outputs aplicado correctamente."
    else
        log_err "El parche no pudo aplicarse en gradio_app.py."
        log_info "Edita manualmente: app.mount(\"/static\") → app.mount(\"/outputs\")"
        log_info "y en los templates HTML: /static/ → /outputs/"
    fi
fi

# ---------------------------------------------------------------------------
# 15. Parche compatibilidad Gradio 6: conservar CSS/theme al montar FastAPI
# ---------------------------------------------------------------------------
# Hunyuan3D usa gr.mount_gradio_app(app, demo, path="/"). En Gradio 6 el
# theme/css definidos en gr.Blocks() se trasladaron al mount/launch; si no se
# pasan, la app puede renderizar una pagina aparentemente correcta pero con el
# cliente de Gradio inconsistente o sin reaccionar a clicks.
if grep -q "_mount_params = inspect.signature(gr.mount_gradio_app)" "$GRADIO_APP" 2>/dev/null; then
    log_ok "Parche compatibilidad Gradio 6 ya aplicado en gradio_app.py."
else
    log_info "Aplicando parche compatibilidad Gradio 6 en gradio_app.py ..."
    GRADIO_APP="$GRADIO_APP" python3 - <<'PYEOF'
import os
from pathlib import Path

path = Path(os.environ["GRADIO_APP"])
txt = path.read_text()

if "import inspect" not in txt:
    txt = txt.replace("import shutil\n", "import shutil\nimport inspect\n", 1)

txt = txt.replace("    return demo\n", "    return demo, custom_css\n")

old = """    demo = build_app()
    app = gr.mount_gradio_app(app, demo, path="/")
    uvicorn.run(app, host=args.host, port=args.port, workers=1)
"""
new = """    demo, _grad_css = build_app()
    _mount_params = inspect.signature(gr.mount_gradio_app).parameters
    _mount_kwargs = {}
    if "css" in _mount_params and _grad_css:
        _mount_kwargs["css"] = _grad_css
    if "theme" in _mount_params:
        _mount_kwargs["theme"] = gr.themes.Base()
    app = gr.mount_gradio_app(app, demo, path="/", **_mount_kwargs)
    uvicorn.run(app, host=args.host, port=args.port, workers=1,
                log_level="info", access_log=True)
"""
if old in txt:
    txt = txt.replace(old, new)
else:
    old_gradio6 = """    demo, _grad_css = build_app()
    # Gradio 6 moved theme/css from gr.Blocks() to mount_gradio_app()/launch().
    # gr.mount_gradio_app() overrides blocks.css with "" if css is not passed.
    # Pass both explicitly so the Base theme and custom_css are actually applied.
    app = gr.mount_gradio_app(app, demo, path="/",
                               css=_grad_css if _grad_css else None,
                               theme=gr.themes.Base())
    uvicorn.run(app, host=args.host, port=args.port, workers=1,
                log_level="info", access_log=True)
"""
    if old_gradio6 not in txt:
        raise SystemExit("No se encontro el bloque esperado de montaje Gradio")
    txt = txt.replace(old_gradio6, new)

path.write_text(txt)
print("[install-hunyuan3d] parche Gradio 6 aplicado.")
PYEOF
    if grep -q "_mount_params = inspect.signature(gr.mount_gradio_app)" "$GRADIO_APP" 2>/dev/null; then
        log_ok "Parche compatibilidad Gradio 6 aplicado correctamente."
    else
        log_err "El parche compatibilidad Gradio 6 no pudo aplicarse automaticamente."
    fi
fi

# ---------------------------------------------------------------------------
# 16. Resumen final
# ---------------------------------------------------------------------------
echo ""
log_ok "=========================================================="
log_ok "Instalacion completada."
log_ok "  Directorio: $HUNYUAN3D_DIR"
log_ok "  Venv:       $VENV_DIR"
log_ok ""
log_ok "Para compilar extensiones CUDA (necesario para textura):"
log_ok "  scripts/apps/hunyuan3d.sh compile-extensions"
log_ok ""
log_ok "Para arrancar como servicio systemd:"
log_ok "  systemctl --user enable --now hunyuan3d.service"
log_ok "  scripts/apps/hunyuan3d.sh wait-ready"
log_ok ""
log_ok "Para operacion diaria:"
log_ok "  scripts/apps/hunyuan3d.sh status"
log_ok "  scripts/apps/hunyuan3d.sh start-service"
log_ok "  scripts/apps/hunyuan3d.sh open-ui"
log_ok ""
log_ok "NOTA GPU: --enable_t23d requiere ~9 GB de VRAM libre."
log_ok "  Si ComfyUI esta activo, para ComfyUI antes de arrancar Hunyuan3D:"
log_ok "  scripts/apps/comfyui.sh stop-service"
log_ok "  scripts/apps/hunyuan3d.sh start-service"
log_ok ""
log_ok "Ver docs/hunyuan3d/installation.md para guia completa."
log_ok "=========================================================="

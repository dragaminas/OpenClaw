# Instalacion Reproducible de `Hunyuan3D` Nativo

Este documento implementa la tarea `10.6` del `DevPlan`.
Define como instalar la app nativa `Hunyuan3D` de forma aislada y reproducible,
sin romper `ComfyUI` ni el entorno de `OpenClaw`.

## Premisas

- la instalacion debe ser reproducible desde este repo
- los pesos del modelo deben cachearse localmente en `~/.cache/huggingface/`
- el `venv` de `Hunyuan3D` no debe mezclar dependencias con el `venv` de `ComfyUI`
- el proceso 3D debe poder arrancarse y pararse sin afectar `ComfyUI`
- en el baseline local `RTX 3060 12 GB` se usa `Hunyuan3D-2mini-Turbo`

## Rutas canonicas

| Artefacto | Ruta |
| --- | --- |
| Repo clonado | `~/Hunyuan3D-2/` |
| Entorno virtual | `~/Hunyuan3D-2/.venv/` |
| Cache de modelos | `~/.cache/huggingface/hub/` |
| Logs de servicio | `~/logs/hunyuan3d/` |
| Artefactos 3D | `$STUDIO_DIR/Assets3D/` |

## Script de instalacion

El script canonico esta en:

```text
scripts/apps/install-hunyuan3d.sh
```

Ejecutarlo con:

```bash
bash scripts/apps/install-hunyuan3d.sh
```

El script:

1. clona el repo oficial `Hunyuan3D-2` si no existe ya
2. crea el `venv` aislado dentro del directorio clonado
3. instala las dependencias declaradas en `requirements.txt`
4. instala las dependencias nativas requeridas (`onnxruntime`, `trimesh`, `huggingface_hub`)
5. descarga el modelo baseline `tencent/Hunyuan3D-2mini` con los subfolderes necesarios
6. verifica que el `gradio_app.py` existe y arranca sin error de importacion

## Dependencias externas requeridas

| Dependencia | Version minima orientativa | Notas |
| --- | --- | --- |
| `Python` | `3.10+` | dentro del venv |
| `PyTorch` | `2.0+` con `CUDA 11.8` o superior | debe coincidir con el driver local |
| `torch-nightly` o release | segun repo oficial | ver `requirements.txt` del repo |
| `diffusers` | segun repo oficial | no instalar en el venv de ComfyUI |
| `huggingface_hub` | `>=0.19` | para descarga de pesos |
| `trimesh` | cualquier version reciente | para post-proceso de mallas |
| `onnxruntime-gpu` | segun repo oficial | para texturizado si se activa |

## Comando de arranque — `web UI`

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

Puerto: `http://127.0.0.1:7860`

## Comando de arranque — `API`

```bash
cd ~/Hunyuan3D-2
source .venv/bin/activate
python3 api_server.py \
  --host 127.0.0.1 \
  --port 8081 \
  --model_path tencent/Hunyuan3D-2mini
```

Puerto: `http://127.0.0.1:8081`

## Verificacion rapida de la instalacion

Despues de instalar, comprobar:

```bash
# activar el venv
source ~/Hunyuan3D-2/.venv/bin/activate

# comprobar importaciones clave
python3 -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
python3 -c "import trimesh; print('trimesh ok')"
python3 -c "import huggingface_hub; print('hf_hub ok')"

# comprobar que el modelo esta cacheado
ls ~/.cache/huggingface/hub/ | grep Hunyuan
```

## Descarga de pesos

La descarga puede hacerse a traves del script de instalacion o manualmente:

```bash
source ~/Hunyuan3D-2/.venv/bin/activate
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='tencent/Hunyuan3D-2mini',
    cache_dir='~/.cache/huggingface/hub'
)
"
```

Los pesos del modelo `2mini` son varios GB. La descarga solo ocurre una vez.

## Archivo de servicio `systemd --user`

Una vez validado el arranque manual, puede registrarse como servicio de
usuario para que arranque automaticamente:

```ini
# ~/.config/systemd/user/hunyuan3d.service
[Unit]
Description=Hunyuan3D-2 Gradio App
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/Hunyuan3D-2
ExecStart=%h/Hunyuan3D-2/.venv/bin/python3 gradio_app.py \
  --model_path tencent/Hunyuan3D-2mini \
  --subfolder hunyuan3d-dit-v2-mini-turbo \
  --texgen_model_path tencent/Hunyuan3D-2 \
  --low_vram_mode \
  --enable_flashvdm
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

Activar con:

```bash
systemctl --user enable --now hunyuan3d.service
```

El archivo de plantilla esta en:
`configs/systemd-user/hunyuan3d.service.template`

## Notas de aislamiento

- nunca usar `pip install` dentro del `venv` de `ComfyUI` para dependencias de
  `Hunyuan3D`
- nunca usar `pip install` dentro del `venv` de `Hunyuan3D` para dependencias
  de `ComfyUI`
- si una dependencia conflictiva aparece, aislarla en el `venv` correspondiente
  y no buscar un entorno comun
- el modo de convivencia descrito en `docs/hunyuan3d/native-runtime-architecture.md`
  es la referencia operativa cuando ambas apps corren en la misma sesion

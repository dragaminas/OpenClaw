from __future__ import annotations

"""Runner canónico para la línea nativa Hunyuan3D.

Implementa el contrato Runner del sistema para integrar Hunyuan3D como
aplicación separada, sin acoplar su lógica al runner de ComfyUI.

Ver docs/hunyuan3d/runner-integration.md para la especificación.
"""

import json
import os
import subprocess
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import (
    Runner,
    RunnerDescription,
    RunnerTarget,
    RunStatus,
    RunResult,
    StartRunRequest,
    StartRunResponse,
)


RUNNER_ID = "hunyuan3d"

_SUPPORTED_OPERATION_KINDS = ["generate_3d_asset", "smoke_test"]
_SUPPORTED_TARGET_KINDS = ["uc_3d_asset", "smoke_suite"]

_UC_3D_TARGETS = {
    "UC-3D-01": RunnerTarget(
        target_id="UC-3D-01",
        display_label="Texto a objeto o personaje 3D (Hunyuan3D nativo)",
        target_kind="uc_3d_asset",
        operation_kind="generate_3d_asset",
        metadata={"alias": "texto-a-3d", "motor": "hunyuan3d-2mini-turbo"},
    ),
    "UC-3D-02": RunnerTarget(
        target_id="UC-3D-02",
        display_label="Imagen a objeto o personaje 3D (Hunyuan3D nativo)",
        target_kind="uc_3d_asset",
        operation_kind="generate_3d_asset",
        metadata={"alias": "imagen-a-3d", "motor": "hunyuan3d-2mini-turbo"},
    ),
    "UC-3D-03": RunnerTarget(
        target_id="UC-3D-03",
        display_label="Texto a set de activos o escena 3D (Hunyuan3D nativo)",
        target_kind="uc_3d_asset",
        operation_kind="generate_3d_asset",
        metadata={"alias": "texto-a-escena-3d", "motor": "hunyuan3d-2mini-turbo"},
    ),
    "UC-3D-04": RunnerTarget(
        target_id="UC-3D-04",
        display_label="Imagen a set de activos o escena 3D (Hunyuan3D nativo)",
        target_kind="uc_3d_asset",
        operation_kind="generate_3d_asset",
        metadata={"alias": "imagen-a-escena-3d", "motor": "hunyuan3d-2mini-turbo"},
    ),
}

_DEFAULT_API_URL = "http://127.0.0.1:8081"
_DEFAULT_EVIDENCE_ROOT = os.path.expanduser("~/Studio/Assets3D")

_BLOCKED_MISSING_RUNTIME = "blocked_missing_runtime"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hunyuan3d_dir() -> Path:
    return Path(os.environ.get("HUNYUAN3D_DIR", os.path.expanduser("~/Hunyuan3D-2")))


def _api_url() -> str:
    return os.environ.get("HUNYUAN3D_API_URL", _DEFAULT_API_URL)


def _is_api_alive() -> bool:
    """Verifica que el servidor API de Hunyuan3D responde."""
    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen(_api_url() + "/", timeout=2):
            return True
    except (urllib.error.URLError, OSError):
        return False


def _is_installed() -> bool:
    """Verifica que la instalación mínima de Hunyuan3D existe."""
    h3d = _hunyuan3d_dir()
    return (h3d / "gradio_app.py").exists() and (h3d / ".venv" / "bin" / "python3").exists()


def _make_run_id(target_id: str | None) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    prefix = (target_id or "h3d").lower().replace("-", "")
    return f"{prefix}-{ts}"


def _blocked_response(
    request: StartRunRequest,
    run_id: str,
    reason: str,
) -> StartRunResponse:
    return StartRunResponse(
        runner_id=RUNNER_ID,
        operation_kind=request.operation_kind,
        target_id=request.target_id,
        run_id=run_id,
        accepted=False,
        status=_BLOCKED_MISSING_RUNTIME,
        message=reason,
    )


class Hunyuan3DRunner(Runner):
    """Runner para la línea nativa Hunyuan3D.

    Encapsula la interacción con el servidor API de Hunyuan3D y la publicación
    de artefactos en la carpeta de trabajo canónica.

    Esta clase implementa el contrato Runner del sistema. La integración con
    WhatsApp y con el plugin de studio-actions pasa por el registro de runners,
    no por crear un nuevo canal directo.
    """

    def describe(self) -> RunnerDescription:
        return RunnerDescription(
            runner_id=RUNNER_ID,
            display_label="Hunyuan3D — línea nativa 3D",
            supported_operation_kinds=_SUPPORTED_OPERATION_KINDS,
            supported_target_kinds=_SUPPORTED_TARGET_KINDS,
            supports_cancel=False,
            supports_progress=False,
            default_evidence_root=_DEFAULT_EVIDENCE_ROOT,
        )

    def list_targets(self, operation_kind: str) -> list[RunnerTarget]:
        if operation_kind == "generate_3d_asset":
            return list(_UC_3D_TARGETS.values())
        if operation_kind == "smoke_test":
            return [
                RunnerTarget(
                    target_id="smoke-suite",
                    display_label="Smoke tests Hunyuan3D",
                    target_kind="smoke_suite",
                    operation_kind="smoke_test",
                )
            ]
        return []

    def start_run(self, request: StartRunRequest) -> StartRunResponse:
        run_id = request.run_id or _make_run_id(request.target_id)

        if not _is_installed():
            return _blocked_response(
                request,
                run_id,
                "Hunyuan3D no está instalado en esta máquina. "
                "Ejecuta: bash scripts/apps/install-hunyuan3d.sh",
            )

        if not _is_api_alive():
            return _blocked_response(
                request,
                run_id,
                "El servidor API de Hunyuan3D no está en marcha. "
                f"Arranca con api_server.py en {_api_url()}",
            )

        if request.operation_kind == "smoke_test":
            return self._start_smoke_run(request, run_id)

        if request.operation_kind == "generate_3d_asset":
            return self._start_generate_run(request, run_id)

        return StartRunResponse(
            runner_id=RUNNER_ID,
            operation_kind=request.operation_kind,
            target_id=request.target_id,
            run_id=run_id,
            accepted=False,
            status="fail_compile",
            message=f"Operación no reconocida: {request.operation_kind!r}",
        )

    def _start_generate_run(
        self,
        request: StartRunRequest,
        run_id: str,
    ) -> StartRunResponse:
        import urllib.error
        import urllib.request

        target_id = request.target_id or "UC-3D-02"
        entity_id = request.inputs.get("entity_id") or run_id
        project_id = request.inputs.get("project_id", "default")

        evidence_root = Path(_DEFAULT_EVIDENCE_ROOT)
        entity_dir = evidence_root / project_id / entity_id
        output_dir = entity_dir / "hunyuan3d" / "output"
        log_dir = entity_dir / "hunyuan3d" / "logs"
        manifest_dir = entity_dir / "hunyuan3d" / "requests"
        output_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        manifest_dir.mkdir(parents=True, exist_ok=True)

        output_glb = output_dir / f"{entity_id}__mesh__v001.glb"
        log_path = log_dir / f"{entity_id}__run__v001.log"
        manifest_path = manifest_dir / f"{entity_id}__request__v001.json"

        image_path = request.inputs.get("imagen_referencia")
        if not image_path and target_id in ("UC-3D-02", "UC-3D-04"):
            return StartRunResponse(
                runner_id=RUNNER_ID,
                operation_kind=request.operation_kind,
                target_id=target_id,
                run_id=run_id,
                accepted=False,
                status="fail_compile",
                message=f"{target_id} requiere imagen_referencia en inputs.",
            )

        seed = int(request.inputs.get("seed", 42))
        steps = int(request.inputs.get("num_inference_steps", 10))
        guidance = float(request.inputs.get("guidance_scale", 5.0))
        octree_res = int(request.inputs.get("octree_resolution", 256))
        texture = bool(request.inputs.get("texture", False))

        manifest: dict[str, Any] = {
            "run_id": run_id,
            "project_id": project_id,
            "entity_id": entity_id,
            "use_case_id": target_id,
            "motor": "hunyuan3d-2mini-turbo",
            "mode": "shape_first",
            "low_vram_mode": True,
            "imagen_referencia": str(image_path),
            "seed": seed,
            "num_inference_steps": steps,
            "guidance_scale": guidance,
            "octree_resolution": octree_res,
            "texture": texture,
            "hardware_profile": "minimum",
            "requested_by": request.requested_by,
            "channel": request.channel,
            "started_at": _utc_now(),
            "output_glb": str(output_glb),
            "status": "running",
            "notes": "",
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        # Invocar la API de forma síncrona
        api_url = _api_url() + "/generate"
        start_time = time.monotonic()

        try:
            with open(image_path, "rb") as img_file:  # type: ignore[arg-type]
                image_bytes = img_file.read()

            boundary = "----OC3DBoundary"
            body_parts = [
                f"--{boundary}\r\nContent-Disposition: form-data; "
                f'name="image"; filename="input.png"\r\nContent-Type: image/png'
                f"\r\n\r\n".encode()
                + image_bytes,
                f'--{boundary}\r\nContent-Disposition: form-data; name="seed"\r\n\r\n{seed}'.encode(),
                f'--{boundary}\r\nContent-Disposition: form-data; name="num_inference_steps"\r\n\r\n{steps}'.encode(),
                f'--{boundary}\r\nContent-Disposition: form-data; name="guidance_scale"\r\n\r\n{guidance}'.encode(),
                f'--{boundary}\r\nContent-Disposition: form-data; name="octree_resolution"\r\n\r\n{octree_res}'.encode(),
                f'--{boundary}\r\nContent-Disposition: form-data; name="texture"\r\n\r\n{"true" if texture else "false"}'.encode(),
                f"--{boundary}--\r\n".encode(),
            ]
            body = b"\r\n".join(body_parts)

            req = urllib.request.Request(
                api_url,
                data=body,
                headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=600) as resp:
                glb_data = resp.read()

            elapsed = time.monotonic() - start_time
            output_glb.write_bytes(glb_data)

            manifest["status"] = "pass"
            manifest["run_duration_s"] = round(elapsed, 1)
            manifest["output_glb"] = str(output_glb)
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            return StartRunResponse(
                runner_id=RUNNER_ID,
                operation_kind=request.operation_kind,
                target_id=target_id,
                run_id=run_id,
                accepted=True,
                status="pass",
                message=(
                    f"glb generado en {elapsed:.1f}s. "
                    f"Importa en Blender: {output_glb}"
                ),
                manifest_path=str(manifest_path),
                evidence_path=str(entity_dir),
                artifact_refs=[str(output_glb)],
            )

        except (urllib.error.URLError, OSError, FileNotFoundError) as exc:
            elapsed = time.monotonic() - start_time
            err_msg = str(exc)
            log_path.write_text(
                f"[{_utc_now()}] ERROR: {err_msg}\n", encoding="utf-8"
            )
            manifest["status"] = "fail_runtime"
            manifest["run_duration_s"] = round(elapsed, 1)
            manifest["notes"] = err_msg
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            return StartRunResponse(
                runner_id=RUNNER_ID,
                operation_kind=request.operation_kind,
                target_id=target_id,
                run_id=run_id,
                accepted=True,
                status="fail_runtime",
                message=f"La corrida falló: {err_msg}",
                manifest_path=str(manifest_path),
            )

    def _start_smoke_run(
        self,
        request: StartRunRequest,
        run_id: str,
    ) -> StartRunResponse:
        script = Path(__file__).parents[3] / "scripts" / "apps" / "hunyuan3d-smoke-validation.sh"
        if not script.exists():
            return StartRunResponse(
                runner_id=RUNNER_ID,
                operation_kind=request.operation_kind,
                target_id=request.target_id,
                run_id=run_id,
                accepted=False,
                status="fail_compile",
                message=f"Script de smoke no encontrado: {script}",
            )

        result = subprocess.run(
            ["bash", str(script)],
            capture_output=True,
            text=True,
            timeout=300,
        )
        status = "pass" if result.returncode == 0 else "fail_runtime"
        return StartRunResponse(
            runner_id=RUNNER_ID,
            operation_kind=request.operation_kind,
            target_id=request.target_id,
            run_id=run_id,
            accepted=True,
            status=status,
            message=result.stdout[-2000:] if result.stdout else result.stderr[-2000:],
        )

    def get_run_status(self, run_id: str) -> RunStatus:
        """Hunyuan3D corre de forma síncrona; el estado final ya está en el manifest."""
        return RunStatus(
            runner_id=RUNNER_ID,
            operation_kind="generate_3d_asset",
            target_id=None,
            run_id=run_id,
            status="pass",
            message="Las corridas de Hunyuan3D son sincrónas. Consulta el manifest para el resultado.",
        )

    def cancel_run(
        self,
        run_id: str,
        *,
        requested_by: str,
        channel: str,
    ) -> RunStatus:
        return RunStatus(
            runner_id=RUNNER_ID,
            operation_kind="generate_3d_asset",
            target_id=None,
            run_id=run_id,
            status="cancelled",
            message="Cancelación no soportada en corridas síncronas de Hunyuan3D.",
        )

    def get_run_result(self, run_id: str) -> RunResult:
        return RunResult(
            runner_id=RUNNER_ID,
            operation_kind="generate_3d_asset",
            target_id=None,
            run_id=run_id,
            status="pass",
            message="Consulta el manifest para resultado detallado.",
        )

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import time
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openclaw_studio.comfyui_general_video_v1 import (
    DEFAULT_CONTROL_WIDTH,
    DEFAULT_RENDER_FRAME_RATE,
    patch_general_video_v1_runtime,
    write_general_video_v1_workflow,
)
from openclaw_studio.comfyui_smoke_validation import (
    ComfyApiClient,
    SmokeValidationError,
    WorkflowCompiler,
)


DEFAULT_TARGET_ID = "general-video-v1"
DEFAULT_FIXTURE_RELPATH = Path(
    "Validation/comfyui/e2e/blender-test/fixtures/blender-test__base__v001.mp4"
)
DEFAULT_REPO_FIXTURE_NAME = "blenderTest.mp4"
DEFAULT_COMFY_INPUT_REL = "blender/blender-test__base__v001.mp4"


class GeneralVideoV1ValidationRunner:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.repo_root = Path(args.repo_root).resolve()
        self.studio_dir = Path(args.studio_dir).resolve()
        self.comfyui_dir = Path(args.comfyui_dir).resolve()
        self.comfy_input_dir = self.comfyui_dir / "input"
        self.comfy_output_dir = self.comfyui_dir / "output"
        self.base_url = f"http://{args.comfyui_host}:{args.comfyui_port}"
        self.run_id = args.run_id or datetime.now(timezone.utc).strftime(
            "general-video-v1-%Y%m%d-%H%M%S"
        )
        self.validation_root = (
            self.studio_dir
            / "Validation"
            / "comfyui"
            / "e2e"
            / "blender-test"
            / DEFAULT_TARGET_ID
            / self.run_id
        )
        self.fixtures_dir = self.validation_root / "fixtures"
        self.logs_dir = self.validation_root / "logs"
        self.manifests_dir = self.validation_root / "manifests"
        self.evidence_dir = self.validation_root / "evidence"
        self.output_prefix_root = f"openclaw/general-video-v1/{self.run_id}"
        self.client = ComfyApiClient(self.base_url)

    def run(self) -> dict[str, Any]:
        self.ensure_runtime_ready()
        self.validation_root.mkdir(parents=True, exist_ok=True)
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.manifests_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        workflow_path = write_general_video_v1_workflow(self.repo_root)
        fixture_info = self.stage_fixture()
        use_borders, use_pose, use_depth = parse_controls(self.args.controls)

        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
        patch_general_video_v1_runtime(
            workflow,
            input_video_rel=fixture_info["comfy_input_rel"],
            output_prefix_root=self.output_prefix_root,
            frame_load_cap=self.args.frame_load_cap,
            custom_width=self.args.control_width,
            render_frame_rate=self.args.render_frame_rate,
            enable_fps_interpolation=self.args.enable_fps_interpolation,
            target_fps=self.args.target_fps,
            use_borders=use_borders,
            use_pose=use_pose,
            use_depth=use_depth,
            fast_validation=not self.args.full_quality,
        )

        object_info = self.client.get_object_info()
        try:
            prompt = WorkflowCompiler(workflow, object_info).compile()
        except Exception as error:
            return self.write_failure_summary(
                status="fail_compile",
                message=f"No se pudo compilar la V1 general de video: {error}",
                workflow_path=workflow_path,
                fixture_info=fixture_info,
                active_controls=render_active_controls(
                    use_borders=use_borders,
                    use_pose=use_pose,
                    use_depth=use_depth,
                ),
            )

        patched_workflow_path = self.logs_dir / "general-video-v1.workflow.json"
        patched_workflow_path.write_text(
            json.dumps(workflow, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        prompt_path = self.logs_dir / "general-video-v1.prompt.json"
        prompt_path.write_text(
            json.dumps(prompt, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )

        try:
            queue_response = self.client.queue_prompt(prompt)
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            return self.write_failure_summary(
                status="fail_runtime",
                message=f"ComfyUI rechazo el prompt: {body}",
                workflow_path=workflow_path,
                fixture_info=fixture_info,
                active_controls=render_active_controls(
                    use_borders=use_borders,
                    use_pose=use_pose,
                    use_depth=use_depth,
                ),
            )

        prompt_id = queue_response["prompt_id"]
        started = time.monotonic()
        try:
            history = self.client.wait_for_prompt(
                prompt_id,
                timeout_seconds=self.args.timeout_seconds,
                poll_interval_seconds=5.0,
            )
        except SmokeValidationError as error:
            return self.write_failure_summary(
                status="fail_runtime",
                message=str(error),
                workflow_path=workflow_path,
                fixture_info=fixture_info,
                active_controls=render_active_controls(
                    use_borders=use_borders,
                    use_pose=use_pose,
                    use_depth=use_depth,
                ),
                prompt_id=prompt_id,
            )

        elapsed_seconds = time.monotonic() - started
        resolved_outputs = self.find_outputs()
        status, message = self.evaluate_outputs(resolved_outputs)
        manifest = {
            "run_id": self.run_id,
            "status": status,
            "message": message,
            "target_id": DEFAULT_TARGET_ID,
            "prompt_id": prompt_id,
            "elapsed_seconds": elapsed_seconds,
            "workflow_path": str(workflow_path),
            "patched_workflow_path": str(patched_workflow_path),
            "prompt_path": str(prompt_path),
            "fixture": fixture_info,
            "active_controls": render_active_controls(
                use_borders=use_borders,
                use_pose=use_pose,
                use_depth=use_depth,
            ),
            "render_profile": {
                "frame_load_cap": self.args.frame_load_cap,
                "control_width": self.args.control_width,
                "render_frame_rate": self.args.render_frame_rate,
                "enable_fps_interpolation": self.args.enable_fps_interpolation,
                "target_fps": self.args.target_fps,
                "full_quality": self.args.full_quality,
            },
            "expected_outputs": expected_output_labels(),
            "resolved_outputs": resolved_outputs,
            "history": history,
        }
        manifest_path = self.manifests_dir / "run.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )

        summary = {
            "run_id": self.run_id,
            "status": status,
            "message": message,
            "target_id": DEFAULT_TARGET_ID,
            "operation_kind": "validate_general_video_v1",
            "workflow_path": str(workflow_path),
            "validation_root": str(self.validation_root),
            "summary_path": str(self.manifests_dir / "summary.json"),
            "evidence_path": str(self.evidence_dir / "summary.md"),
            "prompt_id": prompt_id,
            "fixture": fixture_info,
            "active_controls": manifest["active_controls"],
            "artifact_refs": flatten_output_refs(resolved_outputs),
            "resolved_outputs": resolved_outputs,
            "elapsed_seconds": elapsed_seconds,
            "full_quality": self.args.full_quality,
        }
        summary_path = self.manifests_dir / "summary.json"
        summary_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        self.write_summary_markdown(summary)
        return summary

    def ensure_runtime_ready(self) -> None:
        stats = self.client.get_system_stats()
        if "system" not in stats:
            raise SmokeValidationError("ComfyUI no devolvio system_stats validos.")

    def stage_fixture(self) -> dict[str, str]:
        source_path = resolve_fixture_source(
            repo_root=self.repo_root,
            studio_dir=self.studio_dir,
            explicit_fixture_path=self.args.fixture_path,
        )
        staged_fixture_path = self.fixtures_dir / source_path.name
        shutil.copy2(source_path, staged_fixture_path)

        comfy_input_path = self.comfy_input_dir / DEFAULT_COMFY_INPUT_REL
        comfy_input_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, comfy_input_path)

        return {
            "source_path": str(source_path),
            "staged_fixture_path": str(staged_fixture_path),
            "comfy_input_path": str(comfy_input_path),
            "comfy_input_rel": DEFAULT_COMFY_INPUT_REL,
            "sha256": sha256_file(source_path),
        }

    def find_outputs(self) -> dict[str, list[str]]:
        results: dict[str, list[str]] = {}
        for label, prefix in expected_output_prefixes(self.comfy_output_dir, self.output_prefix_root).items():
            parent = prefix.parent
            stem = prefix.name
            matches: list[str] = []
            if parent.exists():
                for candidate in sorted(parent.glob(f"{stem}*")):
                    if candidate.is_file():
                        matches.append(str(candidate))
            results[label] = matches
        return results

    def evaluate_outputs(self, resolved_outputs: dict[str, list[str]]) -> tuple[str, str]:
        missing = [
            label
            for label, matches in resolved_outputs.items()
            if not matches
        ]
        if missing:
            return (
                "fail_runtime",
                "La corrida termino, pero faltan artefactos esperados: "
                + ", ".join(missing),
            )
        return (
            "pass",
            "La V1 general de video genero frame inicial, controles y render final.",
        )

    def write_failure_summary(
        self,
        *,
        status: str,
        message: str,
        workflow_path: Path,
        fixture_info: dict[str, str],
        active_controls: list[str],
        prompt_id: str | None = None,
    ) -> dict[str, Any]:
        summary = {
            "run_id": self.run_id,
            "status": status,
            "message": message,
            "target_id": DEFAULT_TARGET_ID,
            "operation_kind": "validate_general_video_v1",
            "workflow_path": str(workflow_path),
            "validation_root": str(self.validation_root),
            "summary_path": str(self.manifests_dir / "summary.json"),
            "evidence_path": str(self.evidence_dir / "summary.md"),
            "prompt_id": prompt_id,
            "fixture": fixture_info,
            "active_controls": active_controls,
            "artifact_refs": [],
            "resolved_outputs": {},
        }
        summary_path = self.manifests_dir / "summary.json"
        summary_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        self.write_summary_markdown(summary)
        return summary

    def write_summary_markdown(self, summary: dict[str, Any]) -> None:
        lines = [
            "# Validacion General Video Render V1",
            "",
            f"- run_id: `{summary['run_id']}`",
            f"- status: `{summary['status']}`",
            f"- target_id: `{summary['target_id']}`",
            f"- workflow_path: `{summary['workflow_path']}`",
            f"- validation_root: `{summary['validation_root']}`",
        ]
        if summary.get("prompt_id"):
            lines.append(f"- prompt_id: `{summary['prompt_id']}`")
        if summary.get("elapsed_seconds") is not None:
            lines.append(f"- tiempo: `{summary['elapsed_seconds']:.1f}` segundos")
        if summary.get("active_controls"):
            lines.append(
                "- controles activos: "
                + ", ".join(f"`{item}`" for item in summary["active_controls"])
            )
        fixture = summary.get("fixture") or {}
        if fixture:
            lines.extend(
                (
                    f"- fixture_source: `{fixture.get('source_path', '')}`",
                    f"- fixture_sha256: `{fixture.get('sha256', '')}`",
                    f"- comfy_input_rel: `{fixture.get('comfy_input_rel', '')}`",
                )
            )
        lines.extend(("", f"- mensaje: {summary['message']}", ""))

        resolved_outputs = summary.get("resolved_outputs") or {}
        if resolved_outputs:
            lines.extend(
                (
                    "| Artefacto | Outputs |",
                    "| --- | --- |",
                )
            )
            for label, matches in resolved_outputs.items():
                joined = "<br>".join(f"`{match}`" for match in matches) if matches else "_faltante_"
                lines.append(f"| `{label}` | {joined} |")
            lines.append("")

        summary_md = self.evidence_dir / "summary.md"
        summary_md.write_text("\n".join(lines), encoding="utf-8")


def expected_output_prefixes(
    comfy_output_dir: Path,
    output_prefix_root: str,
) -> dict[str, Path]:
    return {
        "first_frame": comfy_output_dir / f"{output_prefix_root}/first_frame",
        "preprocess_depth": comfy_output_dir / f"{output_prefix_root}/preprocess_depth",
        "preprocess_outline": comfy_output_dir / f"{output_prefix_root}/preprocess_outline",
        "preprocess_pose": comfy_output_dir / f"{output_prefix_root}/preprocess_pose",
        "render": comfy_output_dir / f"{output_prefix_root}/render",
    }


def expected_output_labels() -> list[str]:
    return list(
        (
            "first_frame",
            "preprocess_depth",
            "preprocess_outline",
            "preprocess_pose",
            "render",
        )
    )


def flatten_output_refs(resolved_outputs: dict[str, list[str]]) -> list[str]:
    flattened: list[str] = []
    for matches in resolved_outputs.values():
        flattened.extend(matches)
    return flattened


def render_active_controls(
    *,
    use_borders: bool,
    use_pose: bool,
    use_depth: bool,
) -> list[str]:
    controls: list[str] = []
    if use_borders:
        controls.append("bordes")
    if use_pose:
        controls.append("pose")
    if use_depth:
        controls.append("profundidad")
    return controls


def parse_controls(raw_value: str) -> tuple[bool, bool, bool]:
    normalized_tokens = {
        normalize_control_token(token)
        for token in raw_value.split(",")
        if token.strip()
    }

    use_borders = bool(normalized_tokens & {"bordes", "outline", "edges"})
    use_pose = "pose" in normalized_tokens
    use_depth = bool(normalized_tokens & {"profundidad", "depth"})

    if not any((use_borders, use_pose, use_depth)):
        raise ValueError(
            "Debes activar al menos un control en --controls, por ejemplo "
            "'bordes,pose,profundidad'."
        )

    unknown_tokens = normalized_tokens - {
        "bordes",
        "outline",
        "edges",
        "pose",
        "profundidad",
        "depth",
    }
    if unknown_tokens:
        raise ValueError(
            "No reconozco estos controles: " + ", ".join(sorted(unknown_tokens))
        )

    return use_borders, use_pose, use_depth


def normalize_control_token(raw_value: str) -> str:
    return raw_value.strip().lower().replace("-", "_").replace(" ", "_")


def resolve_fixture_source(
    *,
    repo_root: Path,
    studio_dir: Path,
    explicit_fixture_path: str | None,
) -> Path:
    candidates: list[Path] = []
    if explicit_fixture_path:
        candidates.append(Path(explicit_fixture_path).expanduser())
    candidates.append(studio_dir / DEFAULT_FIXTURE_RELPATH)
    candidates.append(repo_root / DEFAULT_REPO_FIXTURE_NAME)

    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()

    raise FileNotFoundError(
        "No encontre el fixture blenderTest.mp4 ni su copia staged de 8.15."
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validacion local real para la V1 general de render de video."
    )
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--studio-dir",
        default=os.environ.get("STUDIO_DIR", str(Path.home() / "Studio")),
    )
    parser.add_argument(
        "--comfyui-dir",
        default=os.environ.get("COMFYUI_DIR", str(Path.home() / "ComfyUI")),
    )
    parser.add_argument(
        "--comfyui-host",
        default=os.environ.get("COMFYUI_HOST", "127.0.0.1"),
    )
    parser.add_argument(
        "--comfyui-port",
        type=int,
        default=int(os.environ.get("COMFYUI_PORT", "8188")),
    )
    parser.add_argument("--run-id")
    parser.add_argument("--fixture-path")
    parser.add_argument("--frame-load-cap", type=int, default=2)
    parser.add_argument("--control-width", type=int, default=DEFAULT_CONTROL_WIDTH)
    parser.add_argument("--render-frame-rate", type=int, default=DEFAULT_RENDER_FRAME_RATE)
    parser.add_argument(
        "--enable-fps-interpolation",
        action="store_true",
        help="Activa la rama opcional de interpolacion FPS en la V1 funcional.",
    )
    parser.add_argument(
        "--target-fps",
        type=float,
        default=24.0,
        help="FPS objetivo para la rama opcional de interpolacion.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument(
        "--controls",
        default="bordes,pose,profundidad",
        help="Lista separada por comas con 1 a 3 controles activos.",
    )
    parser.add_argument(
        "--full-quality",
        action="store_true",
        help="Desactiva el atajo de validacion rapida y usa la configuracion completa.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    runner = GeneralVideoV1ValidationRunner(args)
    summary = runner.run()

    print(f"run_id={summary['run_id']}")
    print(f"status={summary['status']}")
    print(f"target_id={summary['target_id']}")
    print(f"validation_root={summary['validation_root']}")
    if summary.get("prompt_id"):
        print(f"prompt_id={summary['prompt_id']}")
    print(f"workflow_path={summary['workflow_path']}")
    print("active_controls=" + ",".join(summary.get("active_controls", [])))
    print(f"message={summary['message']}")
    for output_path in summary.get("artifact_refs", []):
        print(f"artifact={output_path}")

    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

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
    DEFAULT_ENABLE_FINAL_UPSCALE,
    DEFAULT_ENABLE_SEGMENTATION,
    DEFAULT_RENDER_FRAME_RATE,
    patch_general_video_v1_runtime,
    write_general_video_v1_workflow,
)
from openclaw_studio.comfyui_openclaw_workflow_nodes import (
    DEFAULT_FINAL_TARGET_HEIGHT,
    DEFAULT_FINAL_TARGET_WIDTH,
    DEFAULT_SEGMENT_LENGTH_FRAMES,
    DEFAULT_SEGMENT_OVERLAP_FRAMES,
    plan_segment_selection,
)
from openclaw_studio.comfyui_smoke_validation import (
    ComfyApiClient,
    SmokeValidationError,
    WorkflowCompiler,
)
from openclaw_studio.video_metadata import read_mp4_video_metadata


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
        identity_anchors = self.stage_identity_anchors()
        active_controls = render_active_controls(
            use_borders=use_borders,
            use_pose=use_pose,
            use_depth=use_depth,
        )
        video_metadata = read_mp4_video_metadata(fixture_info["source_path"])
        segment_plans = self.build_segment_plans(video_metadata)

        segment_results: list[dict[str, Any]] = []
        for segment_plan in segment_plans:
            segment_result = self.run_segment(
                workflow_path=workflow_path,
                fixture_info=fixture_info,
                use_borders=use_borders,
                use_pose=use_pose,
                use_depth=use_depth,
                active_controls=active_controls,
                identity_anchors=identity_anchors,
                segment_plan=segment_plan,
            )
            segment_results.append(segment_result)
            if segment_result["status"] != "pass":
                break

        status, message = self.aggregate_segment_results(segment_results)
        artifact_refs = flatten_segment_output_refs(segment_results)
        resolved_outputs = (
            segment_results[0]["resolved_outputs"]
            if len(segment_results) == 1 and segment_results
            else {}
        )
        recomposition_manifest = self.write_recomposition_manifest(segment_results)

        manifest = {
            "run_id": self.run_id,
            "status": status,
            "message": message,
            "target_id": DEFAULT_TARGET_ID,
            "workflow_path": str(workflow_path),
            "fixture": fixture_info,
            "video_metadata": {
                "frame_count": video_metadata.frame_count,
                "duration_seconds": video_metadata.duration_seconds,
                "fps": video_metadata.fps,
            },
            "active_controls": active_controls,
            "render_profile": {
                "frame_load_cap": self.args.frame_load_cap,
                "control_width": self.args.control_width,
                "render_frame_rate": self.args.render_frame_rate,
                "enable_fps_interpolation": self.args.enable_fps_interpolation,
                "target_fps": self.args.target_fps,
                "enable_color_identity": self.args.enable_color_identity,
                "enable_segmentation": self.args.enable_segmentation,
                "segment_length_frames": self.args.segment_length_frames,
                "segment_overlap_frames": self.args.segment_overlap_frames,
                "enable_final_upscale": self.args.enable_final_upscale,
                "final_width": self.args.final_width,
                "final_height": self.args.final_height,
                "full_quality": self.args.full_quality,
            },
            "identity_anchors": identity_anchors,
            "expected_outputs": expected_output_labels(),
            "resolved_outputs": resolved_outputs,
            "segment_results": segment_results,
            "recomposition_manifest_path": str(recomposition_manifest),
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
            "fixture": fixture_info,
            "video_metadata": manifest["video_metadata"],
            "active_controls": active_controls,
            "artifact_refs": artifact_refs,
            "resolved_outputs": resolved_outputs,
            "segment_results": segment_results,
            "elapsed_seconds": sum(
                float(result.get("elapsed_seconds") or 0.0)
                for result in segment_results
            ),
            "full_quality": self.args.full_quality,
            "identity_anchors": identity_anchors,
            "recomposition_manifest_path": str(recomposition_manifest),
        }
        first_prompt_id = next(
            (result.get("prompt_id") for result in segment_results if result.get("prompt_id")),
            None,
        )
        if first_prompt_id:
            summary["prompt_id"] = first_prompt_id
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

    def stage_identity_anchors(self) -> list[dict[str, str]]:
        anchors: list[dict[str, str]] = []
        references_dir = self.comfy_input_dir / "references"
        references_dir.mkdir(parents=True, exist_ok=True)

        for slot_index in (1, 2, 3):
            color = str(getattr(self.args, f"identity_color_{slot_index}") or "").strip()
            entity = str(getattr(self.args, f"identity_entity_{slot_index}") or "").strip()
            prompt_anchor = str(
                getattr(self.args, f"identity_prompt_anchor_{slot_index}") or ""
            ).strip()
            reference_source = str(getattr(self.args, f"identity_ref_{slot_index}") or "").strip()

            anchor: dict[str, str] = {}
            if color:
                anchor["color"] = color
            if entity:
                anchor["entity"] = entity
            if prompt_anchor:
                anchor["prompt_anchor"] = prompt_anchor

            if reference_source:
                source_path = Path(reference_source).expanduser().resolve()
                if not source_path.is_file():
                    raise FileNotFoundError(
                        f"No encontre la referencia de identidad {source_path}."
                    )
                target_name = f"{self.run_id}__identity_anchor_{slot_index:02d}{source_path.suffix or '.png'}"
                comfy_reference_path = references_dir / target_name
                shutil.copy2(source_path, comfy_reference_path)
                anchor["reference_image_source_path"] = str(source_path)
                anchor["reference_image_relpath"] = f"references/{target_name}"

            if anchor:
                anchors.append(anchor)

        return anchors

    def build_segment_plans(self, video_metadata) -> list[Any]:
        requested_enabled = bool(self.args.enable_segmentation)
        first_plan = plan_segment_selection(
            total_frame_count=video_metadata.frame_count,
            source_fps=video_metadata.fps,
            enabled=requested_enabled,
            segment_length_frames=self.args.segment_length_frames,
            overlap_frames=self.args.segment_overlap_frames,
            segment_index=self.args.segment_index,
        )

        if self.args.single_segment_only or not first_plan.should_segment:
            return [first_plan]

        return [
            plan_segment_selection(
                total_frame_count=video_metadata.frame_count,
                source_fps=video_metadata.fps,
                enabled=True,
                segment_length_frames=self.args.segment_length_frames,
                overlap_frames=self.args.segment_overlap_frames,
                segment_index=index,
            )
            for index in range(1, first_plan.segment_count + 1)
        ]

    def run_segment(
        self,
        *,
        workflow_path: Path,
        fixture_info: dict[str, str],
        use_borders: bool,
        use_pose: bool,
        use_depth: bool,
        active_controls: list[str],
        identity_anchors: list[dict[str, str]],
        segment_plan,
    ) -> dict[str, Any]:
        segment_label = (
            f"segment_{segment_plan.segment_index:03d}"
            if segment_plan.should_segment
            else "single"
        )
        output_prefix_root = (
            f"{self.output_prefix_root}/segments/{segment_label}"
            if segment_plan.should_segment
            else self.output_prefix_root
        )
        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
        patch_general_video_v1_runtime(
            workflow,
            input_video_rel=fixture_info["comfy_input_rel"],
            output_prefix_root=output_prefix_root,
            frame_load_cap=self.args.frame_load_cap,
            custom_width=self.args.control_width,
            render_frame_rate=self.args.render_frame_rate,
            enable_fps_interpolation=self.args.enable_fps_interpolation,
            target_fps=self.args.target_fps,
            use_borders=use_borders,
            use_pose=use_pose,
            use_depth=use_depth,
            enable_color_identity=self.args.enable_color_identity,
            identity_anchors=identity_anchors,
            enable_segmentation=self.args.enable_segmentation,
            segment_length_frames=self.args.segment_length_frames,
            segment_overlap_frames=self.args.segment_overlap_frames,
            segment_index=segment_plan.segment_index,
            enable_final_upscale=self.args.enable_final_upscale,
            final_width=self.args.final_width,
            final_height=self.args.final_height,
            fast_validation=not self.args.full_quality,
        )

        object_info = self.client.get_object_info()
        try:
            prompt = WorkflowCompiler(workflow, object_info).compile()
        except Exception as error:
            return {
                "segment_label": segment_label,
                "status": "fail_compile",
                "message": f"No se pudo compilar la V1 general de video: {error}",
                "workflow_path": str(workflow_path),
                "active_controls": active_controls,
                "segment_plan": serialize_segment_plan(segment_plan),
                "resolved_outputs": {},
            }

        workflow_basename = "general-video-v1.workflow.json"
        prompt_basename = "general-video-v1.prompt.json"
        if segment_plan.should_segment:
            workflow_basename = f"{segment_label}.workflow.json"
            prompt_basename = f"{segment_label}.prompt.json"
        patched_workflow_path = self.logs_dir / workflow_basename
        patched_workflow_path.write_text(
            json.dumps(workflow, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        prompt_path = self.logs_dir / prompt_basename
        prompt_path.write_text(
            json.dumps(prompt, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )

        try:
            queue_response = self.client.queue_prompt(prompt)
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            return {
                "segment_label": segment_label,
                "status": "fail_runtime",
                "message": f"ComfyUI rechazo el prompt: {body}",
                "workflow_path": str(workflow_path),
                "patched_workflow_path": str(patched_workflow_path),
                "prompt_path": str(prompt_path),
                "active_controls": active_controls,
                "segment_plan": serialize_segment_plan(segment_plan),
                "resolved_outputs": {},
            }

        prompt_id = queue_response["prompt_id"]
        started = time.monotonic()
        try:
            history = self.client.wait_for_prompt(
                prompt_id,
                timeout_seconds=self.args.timeout_seconds,
                poll_interval_seconds=5.0,
            )
        except SmokeValidationError as error:
            return {
                "segment_label": segment_label,
                "status": "fail_runtime",
                "message": str(error),
                "prompt_id": prompt_id,
                "workflow_path": str(workflow_path),
                "patched_workflow_path": str(patched_workflow_path),
                "prompt_path": str(prompt_path),
                "active_controls": active_controls,
                "segment_plan": serialize_segment_plan(segment_plan),
                "resolved_outputs": {},
            }

        elapsed_seconds = time.monotonic() - started
        resolved_outputs = self.find_outputs(output_prefix_root)
        status, message = self.evaluate_outputs(resolved_outputs)
        return {
            "segment_label": segment_label,
            "status": status,
            "message": message,
            "prompt_id": prompt_id,
            "elapsed_seconds": elapsed_seconds,
            "workflow_path": str(workflow_path),
            "patched_workflow_path": str(patched_workflow_path),
            "prompt_path": str(prompt_path),
            "active_controls": active_controls,
            "segment_plan": serialize_segment_plan(segment_plan),
            "resolved_outputs": resolved_outputs,
            "history": history,
            "artifact_refs": flatten_output_refs(resolved_outputs),
        }

    def aggregate_segment_results(
        self,
        segment_results: list[dict[str, Any]],
    ) -> tuple[str, str]:
        if not segment_results:
            return "fail_runtime", "No se llego a ejecutar ningun segmento."

        for result in segment_results:
            if result["status"] != "pass":
                return (
                    result["status"],
                    f"{result['segment_label']}: {result['message']}",
                )

        if len(segment_results) == 1:
            return segment_results[0]["status"], segment_results[0]["message"]

        return (
            "pass",
            "La V1 general de video genero segmentos iterables con render base y mejora final por segmento.",
        )

    def write_recomposition_manifest(
        self,
        segment_results: list[dict[str, Any]],
    ) -> Path:
        manifest_path = self.manifests_dir / "recomposition.json"
        segment_entries = []
        for result in segment_results:
            plan = result.get("segment_plan") or {}
            index = int(plan.get("segment_index", 1))
            overlap = int(plan.get("overlap_frames", 0))
            segment_entries.append(
                {
                    "segment_label": result["segment_label"],
                    "segment_index": index,
                    "segment_start_frame": plan.get("segment_start_frame"),
                    "segment_end_frame": plan.get("segment_end_frame"),
                    "drop_leading_frames_for_concat": 0 if index == 1 else overlap,
                    "render_outputs": result.get("resolved_outputs", {}).get("render", []),
                    "final_outputs": result.get("resolved_outputs", {}).get(
                        "render_final_full_hd", []
                    ),
                }
            )

        manifest = {
            "run_id": self.run_id,
            "segment_count": len(segment_results),
            "segment_entries": segment_entries,
            "notes": (
                "La recomposicion temporal debe respetar segment_index ascendente y "
                "descartar los overlap_frames iniciales de cada segmento a partir del segundo."
            ),
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        return manifest_path

    def find_outputs(self, output_prefix_root: str) -> dict[str, list[str]]:
        results: dict[str, list[str]] = {}
        for label, prefix in expected_output_prefixes(
            self.comfy_output_dir, output_prefix_root
        ).items():
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
        identity_anchors: list[dict[str, str]] | None = None,
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
            "identity_anchors": identity_anchors or [],
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
        identity_anchors = summary.get("identity_anchors") or []
        if identity_anchors:
            lines.append("- identidad_color: `true`")
            for index, anchor in enumerate(identity_anchors, start=1):
                parts = []
                if anchor.get("color"):
                    parts.append(f"color=`{anchor['color']}`")
                if anchor.get("entity"):
                    parts.append(f"entidad=`{anchor['entity']}`")
                if anchor.get("prompt_anchor"):
                    parts.append(f"prompt_anchor=`{anchor['prompt_anchor']}`")
                if anchor.get("reference_image_relpath"):
                    parts.append(f"ref=`{anchor['reference_image_relpath']}`")
                lines.append(f"- anclaje_{index}: " + ", ".join(parts))
        fixture = summary.get("fixture") or {}
        if fixture:
            lines.extend(
                (
                    f"- fixture_source: `{fixture.get('source_path', '')}`",
                    f"- fixture_sha256: `{fixture.get('sha256', '')}`",
                    f"- comfy_input_rel: `{fixture.get('comfy_input_rel', '')}`",
                )
            )
        video_metadata = summary.get("video_metadata") or {}
        if video_metadata:
            lines.extend(
                (
                    f"- frames_video: `{video_metadata.get('frame_count', 0)}`",
                    f"- duracion_video: `{video_metadata.get('duration_seconds', 0.0):.3f}` s",
                    f"- fps_video: `{video_metadata.get('fps', 0.0):.3f}`",
                )
            )
        lines.extend(("", f"- mensaje: {summary['message']}", ""))

        segment_results = summary.get("segment_results") or []
        if segment_results:
            lines.extend(
                (
                    "## Segmentos",
                    "",
                    "| Segmento | Estado | Frames | Outputs clave |",
                    "| --- | --- | --- | --- |",
                )
            )
            for result in segment_results:
                plan = result.get("segment_plan") or {}
                frame_range = (
                    f"{int(plan.get('segment_start_frame', 0)) + 1}-{int(plan.get('segment_end_frame', 0))}"
                    if plan.get("segment_end_frame") is not None
                    else "-"
                )
                output_refs = result.get("resolved_outputs", {}).get(
                    "render_final_full_hd",
                    [],
                ) or result.get("resolved_outputs", {}).get("render", [])
                output_cell = (
                    "<br>".join(f"`{path}`" for path in output_refs)
                    if output_refs
                    else "_faltante_"
                )
                lines.append(
                    f"| `{result.get('segment_label', '-')}` | `{result.get('status', '-')}` | `{frame_range}` | {output_cell} |"
                )
            lines.extend(
                (
                    "",
                    f"- recomposicion_manifest: `{summary.get('recomposition_manifest_path', '')}`",
                    "",
                )
            )

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
        "render_final_full_hd": comfy_output_dir / f"{output_prefix_root}/final_full_hd",
    }


def expected_output_labels() -> list[str]:
    return list(
        (
            "first_frame",
            "preprocess_depth",
            "preprocess_outline",
            "preprocess_pose",
            "render",
            "render_final_full_hd",
        )
    )


def flatten_output_refs(resolved_outputs: dict[str, list[str]]) -> list[str]:
    flattened: list[str] = []
    for matches in resolved_outputs.values():
        flattened.extend(matches)
    return flattened


def flatten_segment_output_refs(segment_results: list[dict[str, Any]]) -> list[str]:
    flattened: list[str] = []
    for result in segment_results:
        flattened.extend(result.get("artifact_refs", []))
    return flattened


def serialize_segment_plan(segment_plan) -> dict[str, Any]:
    return {
        "enabled_requested": bool(segment_plan.enabled_requested),
        "should_segment": bool(segment_plan.should_segment),
        "reason": segment_plan.reason,
        "total_frame_count": int(segment_plan.total_frame_count),
        "source_fps": float(segment_plan.source_fps),
        "segment_length_frames": int(segment_plan.segment_length_frames),
        "overlap_frames": int(segment_plan.overlap_frames),
        "segment_index": int(segment_plan.segment_index),
        "segment_count": int(segment_plan.segment_count),
        "segment_start_frame": int(segment_plan.segment_start_frame),
        "segment_end_frame": int(segment_plan.segment_end_frame),
        "selected_frame_count": int(segment_plan.selected_frame_count),
    }


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
    parser.add_argument(
        "--enable-color-identity",
        action="store_true",
        help="Activa la capa opcional de identidad por color o anclaje posicional.",
    )
    parser.add_argument(
        "--enable-segmentation",
        action="store_true",
        default=DEFAULT_ENABLE_SEGMENTATION,
        help="Activa la iteracion por subsecciones usando la misma V1 funcional.",
    )
    parser.add_argument(
        "--segment-length-frames",
        type=int,
        default=DEFAULT_SEGMENT_LENGTH_FRAMES,
        help="Longitud objetivo de cada subseccion cuando la segmentacion esta activa.",
    )
    parser.add_argument(
        "--segment-overlap-frames",
        type=int,
        default=DEFAULT_SEGMENT_OVERLAP_FRAMES,
        help="Solape temporal entre subsecciones consecutivas.",
    )
    parser.add_argument(
        "--segment-index",
        type=int,
        default=1,
        help="Indice 1-based del segmento a usar cuando se fuerza una sola subseccion.",
    )
    parser.add_argument(
        "--single-segment-only",
        action="store_true",
        help="Ejecuta solo el segmento indicado por --segment-index.",
    )
    parser.add_argument(
        "--disable-final-upscale",
        action="store_true",
        help="Desactiva la mejora final Full HD y deja la rama en bypass visible.",
    )
    parser.add_argument(
        "--final-width",
        type=int,
        default=DEFAULT_FINAL_TARGET_WIDTH,
        help="Ancho objetivo de la mejora final Full HD.",
    )
    parser.add_argument(
        "--final-height",
        type=int,
        default=DEFAULT_FINAL_TARGET_HEIGHT,
        help="Alto objetivo de la mejora final Full HD.",
    )
    for slot_index in (1, 2, 3):
        parser.add_argument(f"--identity-color-{slot_index}")
        parser.add_argument(f"--identity-entity-{slot_index}")
        parser.add_argument(f"--identity-prompt-anchor-{slot_index}")
        parser.add_argument(f"--identity-ref-{slot_index}")
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
    args = parser.parse_args(argv)
    args.enable_final_upscale = not bool(args.disable_final_upscale)
    if args.final_width <= 0 or args.final_height <= 0:
        raise ValueError("final_width y final_height deben ser mayores que cero.")
    return args


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

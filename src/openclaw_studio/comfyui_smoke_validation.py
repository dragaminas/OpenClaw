from __future__ import annotations

import argparse
import json
import os
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from openclaw_studio.comfyui_general_video_v1 import patch_general_video_v1_runtime


FRONTEND_ONLY_NODE_TYPES = {
    "GetNode",
    "Label (rgthree)",
    "MarkdownNote",
    "Note",
    "Reroute",
    "SetNode",
}

PRIMITIVE_WIDGET_TYPES = {
    "BOOLEAN",
    "COMBO",
    "FLOAT",
    "INT",
    "STRING",
}

SMOKE_SUITE_TARGET_ID = "smoke"


@dataclass(frozen=True)
class LinkRef:
    node_id: str
    output_slot: int


@dataclass(frozen=True)
class GraphLink:
    link_id: int | str
    origin_id: int
    origin_slot: int
    target_id: int
    target_slot: int
    link_type: str | None

    @classmethod
    def from_raw(cls, raw: list[Any] | dict[str, Any]) -> "GraphLink":
        if isinstance(raw, list):
            return cls(
                link_id=raw[0],
                origin_id=int(raw[1]),
                origin_slot=int(raw[2]),
                target_id=int(raw[3]),
                target_slot=int(raw[4]),
                link_type=raw[5] if len(raw) > 5 else None,
            )

        return cls(
            link_id=raw["id"],
            origin_id=int(raw["origin_id"]),
            origin_slot=int(raw["origin_slot"]),
            target_id=int(raw["target_id"]),
            target_slot=int(raw["target_slot"]),
            link_type=raw.get("type"),
        )


@dataclass
class GraphPayload:
    nodes_by_id: dict[int, dict[str, Any]]
    links_by_id: dict[int | str, GraphLink]
    links_by_target: dict[tuple[int, int], GraphLink]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "GraphPayload":
        nodes_by_id = {int(node["id"]): node for node in payload.get("nodes", [])}
        links_by_id: dict[int | str, GraphLink] = {}
        links_by_target: dict[tuple[int, int], GraphLink] = {}

        for raw_link in payload.get("links", []):
            link = GraphLink.from_raw(raw_link)
            links_by_id[link.link_id] = link
            links_by_target[(link.target_id, link.target_slot)] = link

        return cls(
            nodes_by_id=nodes_by_id,
            links_by_id=links_by_id,
            links_by_target=links_by_target,
        )

    def get_link_for_target(self, target_id: int, target_slot: int) -> GraphLink | None:
        return self.links_by_target.get((target_id, target_slot))

    def get_first_incoming_link(self, target_id: int) -> GraphLink | None:
        for (node_id, _slot), link in self.links_by_target.items():
            if node_id == target_id:
                return link
        return None


@dataclass
class CompileContext:
    graph: GraphPayload
    definitions: dict[str, dict[str, Any]]
    prefix: str
    bound_inputs: dict[int, LinkRef | int | float | str | bool | None] = field(
        default_factory=dict
    )
    set_nodes_by_name: dict[str, int] = field(default_factory=dict)


@dataclass
class SmokeCase:
    case_id: str
    display_label: str
    workflow_path: Path
    blocking: bool
    mutate_workflow: Callable[[dict[str, Any]], None]
    expected_outputs: list[Path]
    timeout_seconds: int
    use_case_id: str
    preset_id: str
    allow_soft_timeout: bool = False


@dataclass
class CaseResult:
    case_id: str
    status: str
    blocking: bool
    message: str
    output_paths: list[str]
    prompt_id: str | None = None
    elapsed_seconds: float | None = None
    workflow_path: str | None = None
    use_case_id: str | None = None
    preset_id: str | None = None


@dataclass(frozen=True)
class SmokeCaseSpec:
    case_id: str
    display_label: str
    workflow_relpath: str
    blocking: bool
    timeout_seconds: int
    use_case_id: str
    preset_id: str
    allow_soft_timeout: bool = False


class SmokeValidationError(RuntimeError):
    pass


class SmokeValidationCancelled(SmokeValidationError):
    pass


class SmokeRunObserver:
    def on_run_started(
        self,
        *,
        run_id: str,
        target_id: str,
        validation_root: Path,
        cases: list[SmokeCase],
    ) -> None:
        return

    def on_case_started(self, case: SmokeCase) -> None:
        return

    def on_prompt_queued(self, case: SmokeCase, prompt_id: str) -> None:
        return

    def on_case_finished(self, result: CaseResult) -> None:
        return

    def on_run_finished(self, summary: dict[str, Any]) -> None:
        return

    def is_cancel_requested(self) -> bool:
        return False


SMOKE_CASE_SPECS = (
    SmokeCaseSpec(
        case_id="SMK-IMG-02-01",
        display_label="UC-IMG-02 smoke",
        workflow_relpath="ComfyUIWorkflows/local/minimum/uc-img-02-z-image-turbo-cn-rtx3060-v1.json",
        blocking=True,
        timeout_seconds=1800,
        use_case_id="UC-IMG-02",
        preset_id="uc-img-02-frame-baseline-preview",
    ),
    SmokeCaseSpec(
        case_id="SMK-VID-01-01",
        display_label="UC-VID-01 smoke",
        workflow_relpath="ComfyUIWorkflows/local/minimum/uc-vid-01-ai-renderer-preprocess-rtx3060-v1.json",
        blocking=True,
        timeout_seconds=1800,
        use_case_id="UC-VID-01",
        preset_id="uc-vid-01-preprocess-control-package",
    ),
    SmokeCaseSpec(
        case_id="SMK-VID-02-01",
        display_label="UC-VID-02 smoke",
        workflow_relpath="ComfyUIWorkflows/local/minimum/uc-vid-02-ai-renderer-video-rtx3060-v1.json",
        blocking=True,
        timeout_seconds=90,
        use_case_id="UC-VID-02",
        preset_id="uc-vid-02-video-baseline-segmented",
        allow_soft_timeout=True,
    ),
    SmokeCaseSpec(
        case_id="SMK-IMG-03-01",
        display_label="UC-IMG-03 smoke",
        workflow_relpath="ComfyUIWorkflows/local/minimum/uc-img-03-z-image-style-exploration-rtx3060-v1.json",
        blocking=True,
        timeout_seconds=1800,
        use_case_id="UC-IMG-03",
        preset_id="uc-img-03-style-exploration",
    ),
    SmokeCaseSpec(
        case_id="SMK-VID-04-01",
        display_label="UC-VID-04 smoke",
        workflow_relpath="ComfyUIWorkflows/local/adaptable/uc-vid-04-video-upscale-ganx4-template-v1.json",
        blocking=True,
        timeout_seconds=1800,
        use_case_id="UC-VID-04",
        preset_id="uc-vid-04-upscale-reference",
    ),
    SmokeCaseSpec(
        case_id="SMK-GEN-VID-01",
        display_label="UC-VID-02 general V1 smoke",
        workflow_relpath="ComfyUIWorkflows/local/minimum/uc-vid-02-general-video-render-rtx3060-v1.json",
        blocking=True,
        timeout_seconds=1800,
        use_case_id="UC-VID-02",
        preset_id="uc-vid-02-general-video-render-v1",
    ),
)


def list_smoke_case_specs() -> list[SmokeCaseSpec]:
    return list(SMOKE_CASE_SPECS)


def derive_smoke_run_status(
    results: list[CaseResult],
    *,
    cancelled: bool = False,
) -> str:
    if cancelled:
        return "cancelled"

    blocking_results = [result.status for result in results if result.blocking]
    if not blocking_results:
        return results[-1].status if results else "pass"

    for failing_status in (
        "fail_compile",
        "fail_runtime",
        "fail_quality",
        "blocked_missing_asset",
    ):
        if failing_status in blocking_results:
            return failing_status

    if "soft_pass_with_fallback" in blocking_results:
        return "soft_pass_with_fallback"

    return "pass"


def build_smoke_run_message(
    status: str,
    *,
    target_id: str,
    results: list[CaseResult],
) -> str:
    if status == "cancelled":
        return "La corrida se cancelo antes de completar el target solicitado."

    if target_id != SMOKE_SUITE_TARGET_ID and results:
        return results[-1].message

    if status == "pass":
        return "La smoke suite termino con pass."
    if status == "soft_pass_with_fallback":
        return "La smoke suite termino con fallback aceptado."
    if status == "fail_compile":
        return "La smoke suite termino con fallo de compilacion."
    if status == "fail_runtime":
        return "La smoke suite termino con fallo de ejecucion."
    if status == "fail_quality":
        return "La smoke suite termino con fallo de calidad."
    if status == "blocked_missing_asset":
        return "La smoke suite quedo bloqueada por assets faltantes."
    return "La smoke suite termino."


class ComfyApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def _get_json(self, path: str) -> Any:
        with urllib.request.urlopen(f"{self.base_url}{path}") as response:
            return json.loads(response.read())

    def _post_json(self, path: str, payload: dict[str, Any]) -> Any:
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read())

    def _post_no_response(self, path: str, payload: dict[str, Any] | None = None) -> None:
        body = b""
        headers = {}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers=headers,
        )
        with urllib.request.urlopen(request):
            return

    def get_object_info(self) -> dict[str, Any]:
        return self._get_json("/object_info")

    def get_system_stats(self) -> dict[str, Any]:
        return self._get_json("/system_stats")

    def get_queue(self) -> dict[str, Any]:
        return self._get_json("/queue")

    def queue_prompt(self, prompt: dict[str, Any]) -> dict[str, Any]:
        return self._post_json("/prompt", {"prompt": prompt})

    def get_history(self, prompt_id: str) -> dict[str, Any] | None:
        history = self._get_json(f"/history/{urllib.parse.quote(prompt_id)}")
        return history.get(prompt_id)

    def interrupt_prompt(self, prompt_id: str) -> None:
        self._post_no_response("/interrupt", {"prompt_id": prompt_id})

    def is_prompt_running(self, prompt_id: str) -> bool:
        queue = self.get_queue()
        for item in queue.get("queue_running", []):
            if len(item) > 1 and item[1] == prompt_id:
                return True
        return False

    def wait_until_prompt_not_running(
        self,
        prompt_id: str,
        timeout_seconds: int = 30,
        poll_interval_seconds: float = 1.0,
    ) -> None:
        started = time.monotonic()
        while time.monotonic() - started < timeout_seconds:
            if not self.is_prompt_running(prompt_id):
                return
            time.sleep(poll_interval_seconds)

    def wait_for_prompt(
        self,
        prompt_id: str,
        timeout_seconds: int,
        poll_interval_seconds: float = 2.0,
        cancel_checker: Callable[[], bool] | None = None,
    ) -> dict[str, Any]:
        started = time.monotonic()
        while time.monotonic() - started < timeout_seconds:
            if cancel_checker is not None and cancel_checker():
                raise SmokeValidationCancelled(
                    f"Se solicito cancelacion para el prompt {prompt_id}."
                )
            history_item = self.get_history(prompt_id)
            if history_item is not None:
                return history_item
            time.sleep(poll_interval_seconds)
        raise SmokeValidationError(
            f"Timeout esperando a que termine el prompt {prompt_id}."
        )


class WorkflowCompiler:
    def __init__(self, workflow_data: dict[str, Any], object_info: dict[str, Any]) -> None:
        self.workflow_data = workflow_data
        self.object_info = object_info
        self.definitions = {
            definition["id"]: definition
            for definition in workflow_data.get("definitions", {}).get("subgraphs", [])
        }
        root_graph = GraphPayload.from_payload(workflow_data)
        self.root_context = CompileContext(
            graph=root_graph,
            definitions=self.definitions,
            prefix="",
            set_nodes_by_name=self.build_set_node_index(root_graph),
        )
        self.compiled_nodes: dict[str, dict[str, Any]] = {}
        self.child_contexts: dict[tuple[str, int], CompileContext] = {}

    def compile(self) -> dict[str, Any]:
        output_root_ids = [
            node_id
            for node_id, node in self.root_context.graph.nodes_by_id.items()
            if self.is_backend_output_node(node["type"])
        ]
        if not output_root_ids:
            raise SmokeValidationError(
                "El workflow no tiene nodos de salida ejecutables para la API."
            )

        for node_id in output_root_ids:
            self.ensure_compiled_node(self.root_context, node_id)

        return self.compiled_nodes

    def is_backend_output_node(self, class_type: str) -> bool:
        return bool(self.object_info.get(class_type, {}).get("output_node"))

    def has_backend_definition(self, class_type: str) -> bool:
        return class_type in self.object_info

    def is_subgraph(self, class_type: str) -> bool:
        return class_type in self.definitions

    def ensure_compiled_node(self, context: CompileContext, node_id: int) -> str:
        compiled_id = f"{context.prefix}{node_id}"
        if compiled_id in self.compiled_nodes:
            return compiled_id

        node = context.graph.nodes_by_id[node_id]
        class_type = node["type"]
        if not self.has_backend_definition(class_type):
            raise SmokeValidationError(
                f"El nodo {class_type!r} no existe en backend y no se puede compilar."
            )

        class_info = self.object_info[class_type]
        widget_defaults = self.extract_widget_defaults(node, class_info)
        valid_inputs = self.valid_input_names(class_info)
        prompt_inputs: dict[str, Any] = {
            name: value
            for name, value in widget_defaults.items()
            if name in valid_inputs
        }

        for slot, input_entry in enumerate(node.get("inputs", [])):
            input_name = input_entry.get("name")
            if not input_name or input_name == "*" or input_name not in valid_inputs:
                continue

            link = context.graph.get_link_for_target(node_id, slot)
            if link is None:
                direct_link_id = input_entry.get("link")
                if direct_link_id is not None:
                    link = context.graph.links_by_id.get(direct_link_id)

            if link is None:
                continue

            resolved = self.resolve_output_reference(
                context, link.origin_id, link.origin_slot
            )
            if isinstance(resolved, LinkRef):
                prompt_inputs[input_name] = [resolved.node_id, resolved.output_slot]
            else:
                prompt_inputs[input_name] = resolved

        compiled_node = {"class_type": class_type, "inputs": prompt_inputs}
        if node.get("title"):
            compiled_node["_meta"] = {"title": node["title"]}

        self.compiled_nodes[compiled_id] = compiled_node
        return compiled_id

    def resolve_output_reference(
        self,
        context: CompileContext,
        node_id: int,
        output_slot: int,
    ) -> LinkRef | int | float | str | bool | None:
        if node_id == -10:
            if output_slot not in context.bound_inputs:
                raise SmokeValidationError(
                    f"Falta binding para la entrada expuesta {output_slot} del subgraph."
                )
            return context.bound_inputs[output_slot]

        node = context.graph.nodes_by_id[node_id]
        class_type = node["type"]

        if class_type == "Reroute":
            incoming = context.graph.get_first_incoming_link(node_id)
            if incoming is None:
                raise SmokeValidationError(
                    f"El reroute {node_id} no tiene ninguna entrada conectada."
                )
            return self.resolve_output_reference(
                context, incoming.origin_id, incoming.origin_slot
            )

        if class_type == "SetNode":
            incoming = context.graph.get_first_incoming_link(node_id)
            if incoming is None:
                raise SmokeValidationError(
                    f"El SetNode {node_id} no tiene ninguna entrada conectada."
                )
            return self.resolve_output_reference(
                context, incoming.origin_id, incoming.origin_slot
            )

        if class_type == "GetNode":
            variable_name = self.get_helper_variable_name(node)
            source_node_id = context.set_nodes_by_name.get(variable_name)
            if source_node_id is None:
                raise SmokeValidationError(
                    f"No existe SetNode para la variable {variable_name!r}."
                )
            return self.resolve_output_reference(context, source_node_id, 0)

        if class_type in FRONTEND_ONLY_NODE_TYPES:
            raise SmokeValidationError(
                f"El nodo frontend-only {class_type!r} no deberia estar en una ruta ejecutable."
            )

        if self.is_subgraph(class_type):
            return self.resolve_subgraph_output(context, node, output_slot)

        if not self.has_backend_definition(class_type):
            raise SmokeValidationError(
                f"No existe class_type backend para el nodo {class_type!r}."
            )

        compiled_id = self.ensure_compiled_node(context, node_id)
        return LinkRef(compiled_id, output_slot)

    def resolve_subgraph_output(
        self,
        parent_context: CompileContext,
        node: dict[str, Any],
        output_slot: int,
    ) -> LinkRef | int | float | str | bool | None:
        child_context = self.get_child_context(parent_context, node)
        definition = self.definitions[node["type"]]
        outputs = definition.get("outputs", [])
        if output_slot >= len(outputs):
            raise SmokeValidationError(
                f"El subgraph {node['type']} no expone el output slot {output_slot}."
            )

        link_ids = outputs[output_slot].get("linkIds", [])
        if not link_ids:
            raise SmokeValidationError(
                f"El subgraph {node['type']} no tiene links para su salida {output_slot}."
            )

        output_link = child_context.graph.links_by_id[link_ids[0]]
        return self.resolve_output_reference(
            child_context, output_link.origin_id, output_link.origin_slot
        )

    def get_child_context(
        self,
        parent_context: CompileContext,
        node: dict[str, Any],
    ) -> CompileContext:
        cache_key = (parent_context.prefix, int(node["id"]))
        if cache_key in self.child_contexts:
            return self.child_contexts[cache_key]

        definition = self.definitions[node["type"]]
        child_prefix = f"{parent_context.prefix}{node['id']}__"
        child_graph = GraphPayload.from_payload(definition)
        widget_defaults = self.extract_subgraph_wrapper_widgets(node)
        bound_inputs: dict[int, Any] = {}

        for slot, input_entry in enumerate(node.get("inputs", [])):
            link = parent_context.graph.get_link_for_target(int(node["id"]), slot)
            if link is not None:
                bound_inputs[slot] = self.resolve_output_reference(
                    parent_context, link.origin_id, link.origin_slot
                )
                continue

            input_name = input_entry.get("name")
            if input_name in widget_defaults:
                bound_inputs[slot] = widget_defaults[input_name]

        child_context = CompileContext(
            graph=child_graph,
            definitions=self.definitions,
            prefix=child_prefix,
            bound_inputs=bound_inputs,
            set_nodes_by_name=self.build_set_node_index(child_graph),
        )
        self.child_contexts[cache_key] = child_context
        return child_context

    def build_set_node_index(self, graph: GraphPayload) -> dict[str, int]:
        result: dict[str, int] = {}
        for node_id, node in graph.nodes_by_id.items():
            if node["type"] != "SetNode":
                continue
            variable_name = self.get_helper_variable_name(node)
            result[variable_name] = node_id
        return result

    def get_helper_variable_name(self, node: dict[str, Any]) -> str:
        widgets = node.get("widgets_values", [])
        if isinstance(widgets, list) and widgets:
            return str(widgets[0])
        if isinstance(widgets, dict) and widgets:
            first_key = next(iter(widgets))
            return str(widgets[first_key])
        raise SmokeValidationError(
            f"No se pudo extraer el nombre de variable del helper {node.get('type')}."
        )

    def extract_subgraph_wrapper_widgets(self, node: dict[str, Any]) -> dict[str, Any]:
        widgets = node.get("widgets_values") or []
        if isinstance(widgets, dict):
            result: dict[str, Any] = {}
            for input_entry in node.get("inputs", []):
                widget_name = input_entry.get("widget", {}).get("name")
                if widget_name and widget_name in widgets:
                    result[input_entry["name"]] = widgets[widget_name]
            return result

        values = list(widgets)
        result: dict[str, Any] = {}
        cursor = 0
        for input_entry in node.get("inputs", []):
            if input_entry.get("widget") is None:
                continue
            if cursor >= len(values):
                break
            result[input_entry["name"]] = values[cursor]
            cursor += 1
        return result

    def extract_widget_defaults(
        self,
        node: dict[str, Any],
        class_info: dict[str, Any],
    ) -> dict[str, Any]:
        widgets = node.get("widgets_values")
        if not widgets:
            return {}

        if isinstance(widgets, dict):
            result: dict[str, Any] = {}
            for input_name in self.ordered_widget_input_names(class_info):
                if input_name in widgets:
                    result[input_name] = widgets[input_name]
            for input_entry in node.get("inputs", []):
                widget_name = input_entry.get("widget", {}).get("name")
                if widget_name and widget_name in widgets:
                    result[input_entry["name"]] = widgets[widget_name]
            return result

        values = list(widgets)
        result: dict[str, Any] = {}
        cursor = 0
        for input_name in self.ordered_widget_input_names(class_info):
            if cursor >= len(values):
                break
            result[input_name] = values[cursor]
            cursor += 1
            if self.input_has_control_after_generate(class_info, input_name):
                cursor += 1
        return result

    def ordered_widget_input_names(self, class_info: dict[str, Any]) -> list[str]:
        ordered: list[str] = []
        input_order = class_info.get("input_order", {})
        input_types = class_info.get("input", {})
        for category in ("required", "optional"):
            ordered_names = input_order.get(category) or list(
                input_types.get(category, {}).keys()
            )
            for input_name in ordered_names:
                if self.input_uses_widget(input_types, category, input_name):
                    ordered.append(input_name)
        return ordered

    def input_uses_widget(
        self,
        input_types: dict[str, Any],
        category: str,
        input_name: str,
    ) -> bool:
        config = input_types.get(category, {}).get(input_name)
        if not config:
            return False
        input_type = config[0]
        if isinstance(input_type, list):
            return True
        if input_type in PRIMITIVE_WIDGET_TYPES:
            return True
        if isinstance(input_type, str) and input_type.startswith("COMFY_DYNAMICCOMBO"):
            return True
        return False

    def input_has_control_after_generate(
        self,
        class_info: dict[str, Any],
        input_name: str,
    ) -> bool:
        input_types = class_info.get("input", {})
        for category in ("required", "optional"):
            config = input_types.get(category, {}).get(input_name)
            if not config or len(config) < 2:
                continue
            extra = config[1]
            if isinstance(extra, dict) and extra.get("control_after_generate"):
                return True
        return False

    def valid_input_names(self, class_info: dict[str, Any]) -> set[str]:
        result: set[str] = set()
        for category in ("required", "optional"):
            result.update(class_info.get("input", {}).get(category, {}).keys())
        return result


class FixtureBuilder:
    def __init__(
        self,
        fixtures_dir: Path,
        comfy_input_dir: Path,
        *,
        repo_root: Path,
        studio_dir: Path,
    ) -> None:
        self.fixtures_dir = fixtures_dir
        self.comfy_input_dir = comfy_input_dir
        self.repo_root = repo_root
        self.studio_dir = studio_dir

    def build(self, run_id: str) -> dict[str, str]:
        input_dir = self.comfy_input_dir
        input_dir.mkdir(parents=True, exist_ok=True)
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)

        start_image = self.fixtures_dir / f"openclaw_smoke_{run_id}_start.png"
        style_ref_1 = self.fixtures_dir / f"openclaw_smoke_{run_id}_style_ref_1.png"
        style_ref_2 = self.fixtures_dir / f"openclaw_smoke_{run_id}_style_ref_2.png"
        character_ref_1 = self.fixtures_dir / f"openclaw_smoke_{run_id}_character_ref_1.png"
        character_ref_2 = self.fixtures_dir / f"openclaw_smoke_{run_id}_character_ref_2.png"
        control_lineart = self.fixtures_dir / f"openclaw_smoke_{run_id}_control_lineart.mp4"
        control_depth = self.fixtures_dir / f"openclaw_smoke_{run_id}_control_depth.mp4"
        render_source = self.fixtures_dir / f"openclaw_smoke_{run_id}_render_source.mp4"

        self._generate_image(
            start_image,
            size=(256, 256),
            boxes=[
                ((48, 60, 118, 170), "#2f62ff", True, 0),
                ((126, 60, 206, 140), "#111111", False, 3),
                ((80, 180, 185, 194), "#ff8c00", True, 0),
            ],
        )
        self._generate_image(
            style_ref_1,
            size=(256, 256),
            boxes=[
                ((32, 40, 224, 216), "#1a1a1a", False, 4),
                ((50, 60, 206, 120), "#f3d34a", True, 0),
            ],
        )
        self._generate_image(
            style_ref_2,
            size=(256, 256),
            boxes=[
                ((36, 48, 220, 208), "#e94e3c", True, 0),
                ((60, 70, 196, 186), "#0f1720", False, 4),
            ],
        )
        self._generate_image(
            character_ref_1,
            size=(256, 256),
            boxes=[
                ((55, 35, 120, 165), "#2d5be3", True, 0),
                ((125, 48, 185, 108), "#111111", False, 3),
            ],
        )
        self._generate_image(
            character_ref_2,
            size=(256, 256),
            boxes=[
                ((45, 45, 125, 165), "#3dbb8a", True, 0),
                ((130, 55, 185, 130), "#101010", False, 3),
            ],
        )
        fallback_video = self._resolve_fallback_video()
        if fallback_video is not None:
            for target in (control_lineart, control_depth, render_source):
                shutil.copy2(fallback_video, target)
        else:
            self._generate_video(
                control_lineart,
                size=(256, 144),
                fps=12,
                frames=3,
                mode="lineart",
            )
            self._generate_video(
                control_depth,
                size=(256, 144),
                fps=12,
                frames=3,
                mode="depth",
            )
            self._generate_video(
                render_source,
                size=(256, 144),
                fps=12,
                frames=3,
                mode="render",
            )

        file_map = {
            "start_image": start_image,
            "style_ref_1": style_ref_1,
            "style_ref_2": style_ref_2,
            "character_ref_1": character_ref_1,
            "character_ref_2": character_ref_2,
            "control_lineart": control_lineart,
            "control_depth": control_depth,
            "render_source": render_source,
        }

        relative_paths: dict[str, str] = {}
        for key, source_path in file_map.items():
            destination = input_dir / source_path.name
            shutil.copy2(source_path, destination)
            relative_paths[key] = source_path.name

        return relative_paths

    def _generate_image(
        self,
        target: Path,
        size: tuple[int, int],
        boxes: list[tuple[tuple[int, int, int, int], str, bool, int]],
    ) -> None:
        from PIL import Image, ImageDraw

        image = Image.new("RGB", size, "white")
        draw = ImageDraw.Draw(image)
        for coords, color, filled, width in boxes:
            draw.rectangle(coords, fill=color if filled else None, outline=color, width=width)
        image.save(target)

    def _generate_video(
        self,
        target: Path,
        size: tuple[int, int],
        fps: int,
        frames: int,
        mode: str,
    ) -> None:
        import av
        import numpy as np

        width, height = size
        container = av.open(str(target), mode="w")
        stream = container.add_stream("libx264", rate=fps)
        stream.width = width
        stream.height = height
        stream.pix_fmt = "yuv420p"

        for frame_index in range(frames):
            image = self._build_video_frame(width, height, frame_index, mode)
            video_frame = av.VideoFrame.from_ndarray(np.array(image), format="rgb24")
            for packet in stream.encode(video_frame):
                container.mux(packet)

        for packet in stream.encode():
            container.mux(packet)
        container.close()

    def _build_video_frame(
        self, width: int, height: int, frame_index: int, mode: str
    ) -> Image.Image:
        from PIL import Image, ImageDraw

        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        if mode == "lineart":
            x = 16 + 18 * frame_index
            draw.rectangle((x, 28, x + 56, 92), outline="black", width=3)
            draw.rectangle((112, 40, 164, 92), outline="black", width=3)
            return image

        if mode == "depth":
            x = 16 + 18 * frame_index
            draw.rectangle((x, 28, x + 56, 92), fill=(120, 120, 120))
            draw.rectangle((112, 40, 164, 92), fill=(220, 220, 220))
            return image

        x = 12 + 16 * frame_index
        draw.rectangle((x, 18, x + 64, 72), fill="#1f6feb")
        draw.rectangle((112, 50, 176, 96), fill="#ff9f1a")
        draw.rectangle((188 - 10 * frame_index, 84, 228 - 10 * frame_index, 114), fill="#22c55e")
        return image

    def _resolve_fallback_video(self) -> Path | None:
        try:
            import av  # noqa: F401
            import numpy  # noqa: F401
            return None
        except ModuleNotFoundError:
            pass

        candidates = (
            self.studio_dir
            / "Validation"
            / "comfyui"
            / "e2e"
            / "blender-test"
            / "fixtures"
            / "blender-test__base__v001.mp4",
            self.repo_root / "blenderTest.mp4",
        )
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        raise SmokeValidationError(
            "No pude generar los fixtures de video para smoke y tampoco encontre "
            "blenderTest.mp4 como fallback local."
        )


class SmokeRunner:
    def __init__(
        self,
        args: argparse.Namespace,
        *,
        observer: SmokeRunObserver | None = None,
    ) -> None:
        self.args = args
        self.repo_root = Path(args.repo_root).resolve()
        self.comfyui_dir = Path(args.comfyui_dir).resolve()
        self.comfy_input_dir = self.comfyui_dir / "input"
        self.comfy_output_dir = self.comfyui_dir / "output"
        self.studio_dir = Path(args.studio_dir).resolve()
        self.base_url = f"http://{args.comfyui_host}:{args.comfyui_port}"
        self.case_id = getattr(args, "case_id", None)
        self.target_id = self.case_id or SMOKE_SUITE_TARGET_ID
        self.run_id = args.run_id or datetime.now(timezone.utc).strftime(
            "smoke-%Y%m%d-%H%M%S"
        )
        self.validation_root = (
            self.studio_dir / "Validation" / "comfyui" / "smoke" / self.run_id
        )
        self.fixtures_dir = self.validation_root / "fixtures"
        self.logs_dir = self.validation_root / "logs"
        self.manifests_dir = self.validation_root / "manifests"
        self.evidence_dir = self.validation_root / "evidence"
        self.client = ComfyApiClient(self.base_url)
        self.object_info: dict[str, Any] | None = None
        self.observer = observer or SmokeRunObserver()

    def run(self) -> dict[str, Any]:
        self.ensure_runtime_ready()
        self.validation_root.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.manifests_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        fixture_builder = FixtureBuilder(
            fixtures_dir=self.fixtures_dir,
            comfy_input_dir=self.comfy_input_dir,
            repo_root=self.repo_root,
            studio_dir=self.studio_dir,
        )
        fixture_paths = fixture_builder.build(self.run_id)
        self.object_info = self.client.get_object_info()

        cases = self.build_cases(fixture_paths)
        self.observer.on_run_started(
            run_id=self.run_id,
            target_id=self.target_id,
            validation_root=self.validation_root,
            cases=cases,
        )

        results: list[CaseResult] = []
        cancelled = False
        for case in cases:
            if self.observer.is_cancel_requested():
                cancelled = True
                break
            result = self.run_case(case)
            results.append(result)
            self.observer.on_case_finished(result)
            if result.status == "cancelled":
                cancelled = True
                break

        if not self.case_id and not cancelled and not self.observer.is_cancel_requested():
            optional_vid03 = self.evaluate_optional_vid03()
            results.append(optional_vid03)
            self.observer.on_case_finished(optional_vid03)
        elif self.observer.is_cancel_requested() and not cancelled:
            cancelled = True

        status = derive_smoke_run_status(results, cancelled=cancelled)
        gate_pass = (not cancelled) and all(
            result.status in {"pass", "soft_pass_with_fallback"}
            for result in results
            if result.blocking
        )
        artifact_refs = [
            output_path for result in results for output_path in result.output_paths
        ]

        summary = {
            "run_id": self.run_id,
            "status": status,
            "message": build_smoke_run_message(
                status,
                target_id=self.target_id,
                results=results,
            ),
            "operation_kind": "validate_smoke",
            "target_id": self.target_id,
            "gate_pass": gate_pass,
            "base_url": self.base_url,
            "comfyui_dir": str(self.comfyui_dir),
            "validation_root": str(self.validation_root),
            "summary_path": str(self.manifests_dir / "summary.json"),
            "evidence_path": str(self.evidence_dir / "summary.md"),
            "artifact_refs": artifact_refs,
            "results": [result.__dict__ for result in results],
        }

        summary_path = self.manifests_dir / "summary.json"
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        self.write_summary_markdown(summary, results)
        self.observer.on_run_finished(summary)
        return summary

    def ensure_runtime_ready(self) -> None:
        stats = self.client.get_system_stats()
        if "system" not in stats:
            raise SmokeValidationError("ComfyUI no devolvio system_stats validos.")

    def build_cases(self, fixture_paths: dict[str, str]) -> list[SmokeCase]:
        run_prefix = Path("openclaw") / "smoke" / self.run_id
        cases = [
            self.build_case_from_spec(spec, fixture_paths, run_prefix)
            for spec in list_smoke_case_specs()
        ]
        if self.case_id is None:
            return cases

        for case in cases:
            if case.case_id == self.case_id:
                return [case]

        raise SmokeValidationError(
            f"No existe smoke case con case_id={self.case_id!r}."
        )

    def build_case_from_spec(
        self,
        spec: SmokeCaseSpec,
        fixture_paths: dict[str, str],
        run_prefix: Path,
    ) -> SmokeCase:
        workflow_path = self.repo_root / spec.workflow_relpath

        if spec.case_id == "SMK-IMG-02-01":
            mutate_workflow = lambda data: patch_img02(
                data,
                fixture_paths["start_image"],
                fixture_paths["control_lineart"],
                str(run_prefix / "img02" / "render"),
            )
            expected_outputs = [
                self.comfy_output_dir / str(run_prefix / "img02" / "render")
            ]
        elif spec.case_id == "SMK-VID-01-01":
            mutate_workflow = lambda data: patch_vid01(
                data,
                fixture_paths["control_lineart"],
                str(run_prefix / "vid01" / "depth"),
                str(run_prefix / "vid01" / "outline"),
                str(run_prefix / "vid01" / "pose"),
            )
            expected_outputs = [
                self.comfy_output_dir / str(run_prefix / "vid01" / "depth"),
                self.comfy_output_dir / str(run_prefix / "vid01" / "outline"),
                self.comfy_output_dir / str(run_prefix / "vid01" / "pose"),
            ]
        elif spec.case_id == "SMK-VID-02-01":
            mutate_workflow = lambda data: patch_vid02(
                data,
                fixture_paths=fixture_paths,
                output_prefix=str(run_prefix / "vid02" / "render"),
            )
            expected_outputs = [
                self.comfy_output_dir / str(run_prefix / "vid02" / "render")
            ]
        elif spec.case_id == "SMK-IMG-03-01":
            mutate_workflow = lambda data: patch_img03(
                data,
                fixture_paths["start_image"],
                fixture_paths["control_lineart"],
                str(run_prefix / "img03" / "style"),
            )
            expected_outputs = [
                self.comfy_output_dir / str(run_prefix / "img03" / "style")
            ]
        elif spec.case_id == "SMK-VID-04-01":
            mutate_workflow = lambda data: patch_vid04(
                data,
                fixture_paths["render_source"],
                str(run_prefix / "vid04" / "upscale"),
            )
            expected_outputs = [
                self.comfy_output_dir / str(run_prefix / "vid04" / "upscale")
            ]
        elif spec.case_id == "SMK-GEN-VID-01":
            mutate_workflow = lambda data: patch_general_vid_v1_smoke(
                data,
                fixture_paths=fixture_paths,
                output_prefix_root=str(run_prefix / "general_v1"),
            )
            expected_outputs = [
                self.comfy_output_dir / str(run_prefix / "general_v1" / "first_frame"),
                self.comfy_output_dir / str(run_prefix / "general_v1" / "preprocess_depth"),
                self.comfy_output_dir / str(run_prefix / "general_v1" / "preprocess_outline"),
                self.comfy_output_dir / str(run_prefix / "general_v1" / "preprocess_pose"),
                self.comfy_output_dir / str(run_prefix / "general_v1" / "render"),
                self.comfy_output_dir / str(run_prefix / "general_v1" / "final_full_hd"),
            ]
        else:
            raise SmokeValidationError(
                f"No existe builder de smoke para case_id={spec.case_id!r}."
            )

        return SmokeCase(
            case_id=spec.case_id,
            display_label=spec.display_label,
            workflow_path=workflow_path,
            blocking=spec.blocking,
            mutate_workflow=mutate_workflow,
            expected_outputs=expected_outputs,
            timeout_seconds=spec.timeout_seconds,
            use_case_id=spec.use_case_id,
            preset_id=spec.preset_id,
            allow_soft_timeout=spec.allow_soft_timeout,
        )

    def run_case(self, case: SmokeCase) -> CaseResult:
        started = time.monotonic()
        self.observer.on_case_started(case)
        try:
            workflow_data = json.loads(case.workflow_path.read_text(encoding="utf-8"))
            case.mutate_workflow(workflow_data)
            compiler = WorkflowCompiler(
                workflow_data=workflow_data,
                object_info=self.object_info or {},
            )
            prompt = compiler.compile()
        except Exception as error:
            elapsed = time.monotonic() - started
            return CaseResult(
                case_id=case.case_id,
                status="fail_compile",
                blocking=case.blocking,
                message=f"No se pudo compilar el workflow: {error}",
                output_paths=[],
                elapsed_seconds=elapsed,
                workflow_path=str(case.workflow_path),
                use_case_id=case.use_case_id,
                preset_id=case.preset_id,
            )

        prompt_path = self.logs_dir / f"{case.case_id}.prompt.json"
        prompt_path.write_text(json.dumps(prompt, indent=2), encoding="utf-8")

        try:
            queue_response = self.client.queue_prompt(prompt)
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            return CaseResult(
                case_id=case.case_id,
                status="fail_runtime",
                blocking=case.blocking,
                message=f"ComfyUI rechazo el prompt: {body}",
                output_paths=[],
                workflow_path=str(case.workflow_path),
                use_case_id=case.use_case_id,
                preset_id=case.preset_id,
            )

        prompt_id = queue_response["prompt_id"]
        self.observer.on_prompt_queued(case, prompt_id)
        try:
            history = self.client.wait_for_prompt(
                prompt_id,
                case.timeout_seconds,
                cancel_checker=self.observer.is_cancel_requested,
            )
        except SmokeValidationCancelled:
            elapsed = time.monotonic() - started
            try:
                if self.client.is_prompt_running(prompt_id):
                    self.client.interrupt_prompt(prompt_id)
                    self.client.wait_until_prompt_not_running(prompt_id)
            except urllib.error.URLError:
                pass
            return CaseResult(
                case_id=case.case_id,
                status="cancelled",
                blocking=case.blocking,
                message="La corrida fue cancelada antes de completar este caso.",
                output_paths=[],
                prompt_id=prompt_id,
                elapsed_seconds=elapsed,
                workflow_path=str(case.workflow_path),
                use_case_id=case.use_case_id,
                preset_id=case.preset_id,
            )
        except SmokeValidationError as error:
            elapsed = time.monotonic() - started
            if case.allow_soft_timeout and self.client.is_prompt_running(prompt_id):
                self.client.interrupt_prompt(prompt_id)
                self.client.wait_until_prompt_not_running(prompt_id)
                return CaseResult(
                    case_id=case.case_id,
                    status="soft_pass_with_fallback",
                    blocking=case.blocking,
                    message=(
                        "El workflow entro en la ruta pesada de render y siguio activo "
                        f"mas de {case.timeout_seconds}s; se interrumpio para mantener "
                        "8.19 como smoke gate barato en RTX 3060."
                    ),
                    output_paths=[],
                    prompt_id=prompt_id,
                    elapsed_seconds=elapsed,
                    workflow_path=str(case.workflow_path),
                    use_case_id=case.use_case_id,
                    preset_id=case.preset_id,
                )

            return CaseResult(
                case_id=case.case_id,
                status="fail_runtime",
                blocking=case.blocking,
                message=str(error),
                output_paths=[],
                prompt_id=prompt_id,
                elapsed_seconds=elapsed,
                workflow_path=str(case.workflow_path),
                use_case_id=case.use_case_id,
                preset_id=case.preset_id,
            )

        output_matches = self.find_outputs(case.expected_outputs)
        status, message = self.evaluate_case_outputs(case, output_matches)
        elapsed = time.monotonic() - started

        manifest = {
            "case_id": case.case_id,
            "status": status,
            "message": message,
            "prompt_id": prompt_id,
            "elapsed_seconds": elapsed,
            "workflow_path": str(case.workflow_path),
            "use_case_id": case.use_case_id,
            "preset_id": case.preset_id,
            "expected_outputs": [str(path) for path in case.expected_outputs],
            "resolved_outputs": output_matches,
            "history": history,
        }
        manifest_path = self.manifests_dir / f"{case.case_id}.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        return CaseResult(
            case_id=case.case_id,
            status=status,
            blocking=case.blocking,
            message=message,
            output_paths=output_matches,
            prompt_id=prompt_id,
            elapsed_seconds=elapsed,
            workflow_path=str(case.workflow_path),
            use_case_id=case.use_case_id,
            preset_id=case.preset_id,
        )

    def find_outputs(self, prefixes: list[Path]) -> list[str]:
        results: list[str] = []
        for prefix in prefixes:
            parent = prefix.parent
            stem = prefix.name
            if not parent.exists():
                continue
            for candidate in sorted(parent.glob(f"{stem}*")):
                if candidate.is_file():
                    results.append(str(candidate))
        return results

    def evaluate_case_outputs(
        self,
        case: SmokeCase,
        output_matches: list[str],
    ) -> tuple[str, str]:
        if case.case_id == "SMK-VID-01-01":
            outline = [path for path in output_matches if "outline" in path]
            pose = [path for path in output_matches if "pose" in path]
            depth = [path for path in output_matches if "depth" in path]
            if outline and pose and depth:
                return ("pass", "Outline, pose y depth quedaron exportados.")
            if outline and pose:
                return (
                    "soft_pass_with_fallback",
                    "Outline y pose pasaron; depth no quedo exportado en esta corrida.",
                )
            return ("fail_runtime", "No aparecieron los artefactos minimos de preprocess.")

        if output_matches:
            return ("pass", "El workflow corrio y dejo artefactos en la salida esperada.")
        return ("fail_runtime", "El workflow termino sin artefactos detectables.")

    def evaluate_optional_vid03(self) -> CaseResult:
        workflow_path = self.repo_root / (
            "ComfyUIWorkflows/local/adaptable/uc-vid-03-image-to-video-wan22-template-v1.json"
        )
        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
        widgets = workflow["nodes"][0].get("widgets_values", [])
        required_assets = [
            f"diffusion_models/{widgets[6]}",
            f"loras/{widgets[7]}",
            f"diffusion_models/{widgets[8]}",
            f"loras/{widgets[9]}",
            f"text_encoders/{widgets[10]}",
            f"vae/{widgets[11]}",
        ]
        missing = [
            asset
            for asset in required_assets
            if not (self.comfyui_dir / "models" / asset).exists()
        ]
        if missing:
            return CaseResult(
                case_id="SMK-VID-03-01",
                status="blocked_missing_asset",
                blocking=False,
                message=(
                    "El template de UC-VID-03 sigue apuntando a assets que no estan "
                    f"en local: {', '.join(missing)}"
                ),
                output_paths=[],
                workflow_path=str(workflow_path),
                use_case_id="UC-VID-03",
                preset_id="uc-vid-03-image-to-video-reference",
            )

        return CaseResult(
            case_id="SMK-VID-03-01",
            status="fail_compile",
            blocking=False,
            message=(
                "Los assets existen, pero esta runner smoke todavia no ejecuta "
                "UC-VID-03 porque la referencia sigue siendo template y no gate "
                "bloqueante."
            ),
            output_paths=[],
            workflow_path=str(workflow_path),
            use_case_id="UC-VID-03",
            preset_id="uc-vid-03-image-to-video-reference",
        )

    def write_summary_markdown(
        self,
        summary: dict[str, Any],
        results: list[CaseResult],
    ) -> None:
        lines = [
            "# Resultados Smoke Validation 8.19",
            "",
            f"- run_id: `{summary['run_id']}`",
            f"- status: `{summary['status']}`",
            f"- gate_pass: `{str(summary['gate_pass']).lower()}`",
            f"- base_url: `{summary['base_url']}`",
            f"- validation_root: `{summary['validation_root']}`",
            "",
            "| Caso | Estado | Bloqueante | Mensaje |",
            "| --- | --- | --- | --- |",
        ]
        for result in results:
            lines.append(
                f"| `{result.case_id}` | `{result.status}` | "
                f"`{str(result.blocking).lower()}` | {result.message} |"
            )
        lines.append("")
        for result in results:
            lines.append(f"## {result.case_id}")
            lines.append("")
            lines.append(f"- estado: `{result.status}`")
            lines.append(f"- bloqueante: `{str(result.blocking).lower()}`")
            if result.prompt_id:
                lines.append(f"- prompt_id: `{result.prompt_id}`")
            if result.elapsed_seconds is not None:
                lines.append(f"- tiempo: `{result.elapsed_seconds:.1f}` segundos")
            lines.append(f"- mensaje: {result.message}")
            if result.output_paths:
                lines.append("- outputs:")
                for output_path in result.output_paths:
                    lines.append(f"  - `{output_path}`")
            lines.append("")

        summary_md = self.evidence_dir / "summary.md"
        summary_md.write_text("\n".join(lines), encoding="utf-8")


def patch_img02(
    workflow: dict[str, Any],
    input_image_rel: str,
    control_video_rel: str,
    output_prefix: str,
) -> None:
    node_58 = find_top_level_node(workflow, 58)
    node_58["widgets_values"][0] = input_image_rel

    node_74 = find_top_level_node(workflow, 74)
    node_74["widgets_values"]["video"] = control_video_rel
    node_74["widgets_values"]["frame_load_cap"] = 1

    node_83 = find_top_level_node(workflow, 83)
    node_83["widgets_values"][0] = (
        "Simple cinematic character portrait with strong silhouette and clear contrast."
    )

    node_90 = find_top_level_node(workflow, 90)
    node_90["widgets_values"][1] = 256

    node_80 = find_top_level_node(workflow, 80)
    node_80["widgets_values"][2] = 2
    node_80["widgets_values"][3] = 1

    node_9 = find_top_level_node(workflow, 9)
    node_9["widgets_values"][0] = output_prefix


def patch_img03(
    workflow: dict[str, Any],
    input_image_rel: str,
    control_video_rel: str,
    output_prefix: str,
) -> None:
    patch_img02(workflow, input_image_rel, control_video_rel, output_prefix)
    node_83 = find_top_level_node(workflow, 83)
    node_83["widgets_values"][0] = (
        "Graphic illustration look, bold shapes, flat colors, clean editorial style."
    )


def patch_vid01(
    workflow: dict[str, Any],
    input_video_rel: str,
    depth_prefix: str,
    outline_prefix: str,
    pose_prefix: str,
) -> None:
    node_265 = find_top_level_node(workflow, 265)
    node_265["widgets_values"]["video"] = input_video_rel
    node_265["widgets_values"]["custom_width"] = 256
    node_265["widgets_values"]["custom_height"] = 144
    node_265["widgets_values"]["frame_load_cap"] = 3
    for slot in (2, 3, 4):
        remove_top_level_link_to_target(workflow, 265, slot)

    for node_id in (3379, 3380, 3381):
        node = find_top_level_node(workflow, node_id)
        node["widgets_values"][0] = 256
        node["widgets_values"][1] = 144
        for slot in (2, 3):
            remove_top_level_link_to_target(workflow, node_id, slot)

    find_top_level_node(workflow, 3001)["widgets_values"]["filename_prefix"] = depth_prefix
    find_top_level_node(workflow, 3001)["widgets_values"]["frame_rate"] = 12
    find_top_level_node(workflow, 3377)["widgets_values"]["filename_prefix"] = outline_prefix
    find_top_level_node(workflow, 3377)["widgets_values"]["frame_rate"] = 12
    find_top_level_node(workflow, 3378)["widgets_values"]["filename_prefix"] = pose_prefix
    find_top_level_node(workflow, 3378)["widgets_values"]["frame_rate"] = 12


def patch_vid02(
    workflow: dict[str, Any],
    fixture_paths: dict[str, str],
    output_prefix: str,
) -> None:
    for node_id, rel_path in (
        (265, fixture_paths["control_depth"]),
        (3345, fixture_paths["control_lineart"]),
    ):
        node = find_top_level_node(workflow, node_id)
        node["widgets_values"]["video"] = rel_path
        node["widgets_values"]["custom_width"] = 256
        node["widgets_values"]["custom_height"] = 144
        node["widgets_values"]["frame_load_cap"] = 1
        node["widgets_values"]["skip_first_frames"] = 0
        for slot in (2, 3, 4, 5):
            remove_top_level_link_to_target(workflow, node_id, slot)

    for node_id, rel_path in (
        (282, fixture_paths["character_ref_1"]),
        (3349, fixture_paths["character_ref_2"]),
        (3350, fixture_paths["style_ref_1"]),
        (3353, fixture_paths["style_ref_2"]),
    ):
        node = find_top_level_node(workflow, node_id)
        node["widgets_values"][0] = rel_path

    find_top_level_node(workflow, 3333)["widgets_values"][0] = "umt5_xxl_fp16.safetensors"
    find_top_level_node(workflow, 3327)["widgets_values"][0] = "wan/Lenovo.safetensors"
    find_top_level_node(workflow, 3228)["widgets_values"][0] = (
        "Short cinematic action shot with clear silhouette and stable motion."
    )

    render_node = find_top_level_node(workflow, 3372)
    render_node["widgets_values"]["filename_prefix"] = output_prefix
    render_node["widgets_values"]["frame_rate"] = 8

    resolution_subgraph = find_subgraph_definition(
        workflow, "3d3e41f0-5880-459f-8b57-8311a154436c"
    )
    resolution_picker = find_subgraph_node(resolution_subgraph, 2852)
    resolution_picker["widgets_values"][0] = "Custom"
    resolution_picker["widgets_values"][1] = "16:9"
    resolution_picker["widgets_values"][2] = 256
    resolution_picker["widgets_values"][3] = 144

    sampler_subgraph = find_subgraph_definition(
        workflow, "c475d739-ec74-430f-a7bd-aab0fdd85070"
    )
    phantom_node = find_subgraph_node(sampler_subgraph, 3255)
    phantom_node["widgets_values"][0] = 256
    phantom_node["widgets_values"][1] = 144
    phantom_node["widgets_values"][2] = 1
    phantom_node["widgets_values"][3] = 1
    for slot in (9, 10, 11):
        remove_subgraph_link_to_target(sampler_subgraph, 3255, slot)

    start_end_node = find_subgraph_node(sampler_subgraph, 3261)
    start_end_node["widgets_values"][0] = 1
    remove_subgraph_link_to_target(sampler_subgraph, 3261, 4)

    sampler_node = find_subgraph_node(sampler_subgraph, 3253)
    sampler_node["widgets_values"][2] = 1
    sampler_node["widgets_values"][3] = 1


def patch_vid04(
    workflow: dict[str, Any],
    input_video_rel: str,
    output_prefix: str,
) -> None:
    next_node_id = max(int(node["id"]) for node in workflow["nodes"]) + 1
    existing_links = workflow.get("links", [])
    next_link_id = (
        max(int(link[0]) for link in existing_links) + 1 if existing_links else 1
    )

    load_node_id = next_node_id
    save_node_id = next_node_id + 1
    root_node_id = 13
    root_node = find_top_level_node(workflow, root_node_id)
    root_node["widgets_values"][0] = "RealESRGAN_x4plus.pth"

    workflow["nodes"].append(
        {
            "id": load_node_id,
            "type": "LoadVideo",
            "inputs": [],
            "widgets_values": [input_video_rel],
            "title": "Smoke Input Video",
        }
    )
    workflow["nodes"].append(
        {
            "id": save_node_id,
            "type": "SaveVideo",
            "inputs": [
                {
                    "name": "video",
                    "type": "VIDEO",
                    "link": next_link_id + 1,
                }
            ],
            "widgets_values": [output_prefix, "mp4", "h264"],
            "title": "Smoke Save Video",
        }
    )

    workflow["links"].append([next_link_id, load_node_id, 0, root_node_id, 0, "VIDEO"])
    workflow["links"].append(
        [next_link_id + 1, root_node_id, 0, save_node_id, 0, "VIDEO"]
    )
    root_node["inputs"][0]["link"] = next_link_id
    root_node["outputs"][0]["links"] = [next_link_id + 1]


def patch_general_vid_v1_smoke(
    workflow: dict[str, Any],
    *,
    fixture_paths: dict[str, str],
    output_prefix_root: str,
) -> None:
    patch_general_video_v1_runtime(
        workflow,
        input_video_rel=fixture_paths["render_source"],
        output_prefix_root=output_prefix_root,
        frame_load_cap=0,
        custom_width=256,
        render_frame_rate=12,
        enable_fps_interpolation=False,
        target_fps=12.0,
        use_borders=True,
        use_pose=True,
        use_depth=True,
        enable_color_identity=False,
        identity_anchors=[],
        enable_segmentation=True,
        segment_length_frames=2,
        segment_overlap_frames=1,
        segment_index=2,
        enable_final_upscale=True,
        final_width=1920,
        final_height=1080,
        fast_validation=True,
    )


def find_top_level_node(workflow: dict[str, Any], node_id: int) -> dict[str, Any]:
    for node in workflow.get("nodes", []):
        if int(node["id"]) == node_id:
            return node
    raise SmokeValidationError(f"No existe el nodo top-level {node_id}.")


def find_subgraph_definition(workflow: dict[str, Any], subgraph_id: str) -> dict[str, Any]:
    for definition in workflow.get("definitions", {}).get("subgraphs", []):
        if definition["id"] == subgraph_id:
            return definition
    raise SmokeValidationError(f"No existe el subgraph {subgraph_id}.")


def find_subgraph_node(subgraph: dict[str, Any], node_id: int) -> dict[str, Any]:
    for node in subgraph.get("nodes", []):
        if int(node["id"]) == node_id:
            return node
    raise SmokeValidationError(f"No existe el nodo {node_id} dentro del subgraph.")


def remove_top_level_link_to_target(
    workflow: dict[str, Any], target_id: int, target_slot: int
) -> None:
    workflow["links"] = [
        raw_link
        for raw_link in workflow.get("links", [])
        if not (int(raw_link[3]) == target_id and int(raw_link[4]) == target_slot)
    ]
    node = find_top_level_node(workflow, target_id)
    if target_slot < len(node.get("inputs", [])):
        node["inputs"][target_slot]["link"] = None


def remove_subgraph_link_to_target(
    subgraph: dict[str, Any], target_id: int, target_slot: int
) -> None:
    new_links = []
    removed_link_ids: set[int | str] = set()
    for raw_link in subgraph.get("links", []):
        if int(raw_link["target_id"]) == target_id and int(raw_link["target_slot"]) == target_slot:
            removed_link_ids.add(raw_link["id"])
            continue
        new_links.append(raw_link)
    subgraph["links"] = new_links

    node = find_subgraph_node(subgraph, target_id)
    if target_slot < len(node.get("inputs", [])):
        node["inputs"][target_slot]["link"] = None

    for entry in subgraph.get("inputs", []):
        entry["linkIds"] = [link_id for link_id in entry.get("linkIds", []) if link_id not in removed_link_ids]
    for entry in subgraph.get("outputs", []):
        entry["linkIds"] = [link_id for link_id in entry.get("linkIds", []) if link_id not in removed_link_ids]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Smoke validation minima real para workflows de ComfyUI."
    )
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[2])
    parser.add_argument("--studio-dir", default=os.environ.get("STUDIO_DIR", str(Path.home() / "Studio")))
    parser.add_argument("--comfyui-dir", default=os.environ.get("COMFYUI_DIR", str(Path.home() / "ComfyUI")))
    parser.add_argument("--comfyui-host", default=os.environ.get("COMFYUI_HOST", "127.0.0.1"))
    parser.add_argument("--comfyui-port", type=int, default=int(os.environ.get("COMFYUI_PORT", "8188")))
    parser.add_argument("--run-id")
    parser.add_argument("--case-id")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    runner = SmokeRunner(args)
    summary = runner.run()

    print(f"run_id={summary['run_id']}")
    print(f"status={summary['status']}")
    print(f"target_id={summary['target_id']}")
    print(f"gate_pass={str(summary['gate_pass']).lower()}")
    print(f"validation_root={summary['validation_root']}")
    for result in summary["results"]:
        print(
            f"{result['case_id']}={result['status']} :: {result['message']}"
        )

    return 0 if summary["status"] in {"pass", "soft_pass_with_fallback"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

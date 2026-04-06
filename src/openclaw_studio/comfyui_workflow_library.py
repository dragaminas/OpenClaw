from __future__ import annotations

"""Publish OpenClaw workflows as native ComfyUI templates."""

import argparse
import json
import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from openclaw_studio.application.session_engine import normalize_text
from openclaw_studio.contracts.flows import (
    ExecutionVariant,
    FlowDefinition,
    OutputArtifactType,
)
from openclaw_studio.implementations import BUILTIN_FLOW_CATALOG


MODULE_NAME = "openclaw-workflows"
EXAMPLE_WORKFLOWS_DIRNAME = "example_workflows"
MANIFEST_FILENAME = "openclaw-workflows-manifest.json"
MODULE_HELPER_SOURCE_RELPATH = Path(
    "src/openclaw_studio/comfyui_openclaw_workflow_nodes.py"
)
MODULE_HELPER_FILENAME = "openclaw_nodes.py"
MODULE_INIT_TEXT = '''"""OpenClaw workflow templates and helper nodes exposed to ComfyUI."""

from .openclaw_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
'''

FRONTEND_ONLY_NODE_TYPES = {
    "GetNode",
    "Label (rgthree)",
    "MarkdownNote",
    "Note",
    "Reroute",
    "SetNode",
}


@dataclass(frozen=True)
class WorkflowTemplateEntry:
    """One OpenClaw workflow exposed to ComfyUI as a template."""

    use_case_id: str
    friendly_alias: str
    display_label: str
    description: str
    output_label: str
    required_input_labels: tuple[str, ...]
    optional_input_labels: tuple[str, ...]
    variant_id: str
    variant_display_label: str
    source_relpath: str
    source_path: str
    template_filename: str
    template_path: str
    sample_user_request: str = ""
    module_name: str = MODULE_NAME
    loader_hint: str = ""


@dataclass(frozen=True)
class SyncResult:
    """Summary of a sync operation into the local ComfyUI template library."""

    module_name: str
    module_path: str
    templates_dir: str
    manifest_path: str
    created_module: bool
    published_count: int
    entries: tuple[WorkflowTemplateEntry, ...]


def default_repo_root() -> Path:
    """Return the repository root inferred from this module."""

    return Path(__file__).resolve().parents[2]


def default_comfyui_dir() -> Path:
    """Return the local ComfyUI directory from env or sane default."""

    return Path(os.environ.get("COMFYUI_DIR", "~/ComfyUI")).expanduser()


def format_home_path(path: Path | str) -> str:
    """Render a path compactly when it lives under the current home."""

    path_obj = Path(os.path.abspath(os.path.expanduser(str(path))))
    home_path = Path(os.path.abspath(str(Path.home())))
    try:
        relative_to_home = path_obj.relative_to(home_path)
    except ValueError:
        return str(path_obj)
    return str(Path("~") / relative_to_home)


def build_workflow_template_entries(
    repo_root: Path,
    comfyui_dir: Path,
) -> tuple[WorkflowTemplateEntry, ...]:
    """Resolve the preferred source JSON for each flow into template entries."""

    example_dir = comfyui_dir / "custom_nodes" / MODULE_NAME / EXAMPLE_WORKFLOWS_DIRNAME
    entries: list[WorkflowTemplateEntry] = []

    for flow_definition in BUILTIN_FLOW_CATALOG:
        resolved_variant, source_relpath, source_path = _select_source_workflow(
            flow_definition=flow_definition,
            repo_root=repo_root,
        )
        template_filename = f"{flow_definition.friendly_alias}.json"
        template_path = example_dir / template_filename
        entries.append(
            WorkflowTemplateEntry(
                use_case_id=flow_definition.use_case_id,
                friendly_alias=flow_definition.friendly_alias,
                display_label=flow_definition.display_label,
                description=flow_definition.description,
                output_label=_render_output_label(flow_definition.output_type),
                required_input_labels=tuple(
                    flow_definition.get_input_definition(input_key).display_label
                    for input_key in flow_definition.required_input_keys
                ),
                optional_input_labels=tuple(
                    flow_definition.get_input_definition(input_key).display_label
                    for input_key in flow_definition.optional_input_keys
                ),
                sample_user_request=(
                    flow_definition.sample_user_requests[0]
                    if flow_definition.sample_user_requests
                    else ""
                ),
                variant_id=resolved_variant.variant_id,
                variant_display_label=resolved_variant.display_label,
                source_relpath=source_relpath,
                source_path=str(source_path),
                template_filename=template_filename,
                template_path=str(template_path),
                loader_hint=(
                    f"Templates > {MODULE_NAME} > {flow_definition.friendly_alias}"
                ),
            )
        )

    return tuple(entries)


def resolve_workflow_template_entry(
    workflow_ref: str,
    repo_root: Path,
    comfyui_dir: Path,
) -> WorkflowTemplateEntry:
    """Resolve a user-friendly alias or canonical ID to one template entry."""

    normalized_ref = normalize_text(workflow_ref)
    entries = build_workflow_template_entries(repo_root=repo_root, comfyui_dir=comfyui_dir)

    for flow_definition, entry in zip(BUILTIN_FLOW_CATALOG, entries, strict=True):
        candidates = {
            normalize_text(candidate)
            for candidate in (
                flow_definition.match_phrases
                + flow_definition.user_aliases
                + (entry.template_filename.removesuffix(".json"),)
            )
        }
        if normalized_ref in candidates:
            return entry

    raise ValueError(
        f"No pude resolver el workflow {workflow_ref!r}. Usa un alias como "
        "'prepara-video' o un use_case_id como 'UC-VID-01'."
    )


def sync_workflow_templates(repo_root: Path, comfyui_dir: Path) -> SyncResult:
    """Publish the current OpenClaw catalog as native ComfyUI templates."""

    module_dir = comfyui_dir / "custom_nodes" / MODULE_NAME
    templates_dir = module_dir / EXAMPLE_WORKFLOWS_DIRNAME
    manifest_path = module_dir / MANIFEST_FILENAME
    created_module = not module_dir.exists()

    module_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)
    (module_dir / "__init__.py").write_text(MODULE_INIT_TEXT, encoding="utf-8")
    _publish_support_file(
        source_path=(repo_root / MODULE_HELPER_SOURCE_RELPATH).resolve(),
        target_path=module_dir / MODULE_HELPER_FILENAME,
    )

    previous_manifest = _load_manifest(manifest_path)
    previous_filenames = set(previous_manifest.get("managed_filenames", ()))

    entries = build_workflow_template_entries(repo_root=repo_root, comfyui_dir=comfyui_dir)
    current_filenames = {entry.template_filename for entry in entries}

    for stale_filename in sorted(previous_filenames - current_filenames):
        stale_path = templates_dir / stale_filename
        if stale_path.is_symlink() or stale_path.exists():
            stale_path.unlink()

    published_entries: list[WorkflowTemplateEntry] = []
    for entry in entries:
        template_path = Path(entry.template_path)
        source_path = Path(entry.source_path)
        _publish_template_file(source_path=source_path, template_path=template_path)
        published_entries.append(entry)

    manifest_payload = {
        "module_name": MODULE_NAME,
        "module_path": str(module_dir),
        "templates_dir": str(templates_dir),
        "helper_files": [MODULE_HELPER_FILENAME],
        "managed_filenames": sorted(current_filenames),
        "entries": [asdict(entry) for entry in published_entries],
    }
    manifest_path.write_text(
        json.dumps(manifest_payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    return SyncResult(
        module_name=MODULE_NAME,
        module_path=str(module_dir),
        templates_dir=str(templates_dir),
        manifest_path=str(manifest_path),
        created_module=created_module,
        published_count=len(published_entries),
        entries=tuple(published_entries),
    )


def render_sync_result(sync_result: SyncResult) -> str:
    """Render a sync result in a compact line-oriented format."""

    return "\n".join(
        (
            f"module_name={sync_result.module_name}",
            f"module_path={format_home_path(sync_result.module_path)}",
            f"templates_dir={format_home_path(sync_result.templates_dir)}",
            f"manifest_path={format_home_path(sync_result.manifest_path)}",
            f"created_module={str(sync_result.created_module).lower()}",
            f"published={sync_result.published_count}",
        )
    )


def render_workflow_list(entries: tuple[WorkflowTemplateEntry, ...]) -> str:
    """Render the exposed workflow library for terminal or chat output."""

    lines = [
        "Biblioteca OpenClaw disponible en ComfyUI:",
    ]
    for entry in entries:
        lines.extend(
            (
                f"- {entry.friendly_alias} | {entry.use_case_id} | {entry.display_label}",
                f"  Hace: {entry.description}",
                (
                    "  Entrada obligatoria: "
                    f"{_render_input_labels(entry.required_input_labels)}. "
                    f"Salida: {entry.output_label}."
                ),
            )
        )
    lines.append(
        f"carga_desde=Templates > {MODULE_NAME} > <alias>"
    )
    lines.append(
        "pregunta=studio que hace <alias>"
    )
    return "\n".join(lines)


def render_workflow_description(entry: WorkflowTemplateEntry) -> str:
    """Render one resolved workflow entry in a stable format."""

    return "\n".join(
        (
            f"use_case_id={entry.use_case_id}",
            f"alias={entry.friendly_alias}",
            f"workflow={entry.display_label}",
            f"description={entry.description}",
            f"output={entry.output_label}",
            f"required_inputs={_render_input_labels(entry.required_input_labels)}",
            f"optional_inputs={_render_input_labels(entry.optional_input_labels)}",
            f"variant_id={entry.variant_id}",
            f"variant={entry.variant_display_label}",
            f"source={format_home_path(entry.source_path)}",
            f"template={format_home_path(entry.template_path)}",
            f"carga_desde={entry.loader_hint}",
        )
    )


def render_workflow_explanation(entry: WorkflowTemplateEntry) -> str:
    """Render a workflow explanation in explicit, human-readable Spanish."""

    lines = [
        f"Workflow: {entry.friendly_alias} ({entry.use_case_id})",
        f"Nombre: {entry.display_label}",
        f"Hace: {entry.description}",
        (
            "Entrada obligatoria: "
            f"{_render_input_labels(entry.required_input_labels)}."
        ),
        f"Salida principal: {entry.output_label}.",
        f"Variante actual: {entry.variant_display_label}.",
    ]
    if entry.optional_input_labels:
        lines.append(
            "Entradas opcionales: "
            f"{_render_input_labels(entry.optional_input_labels)}."
        )
    if entry.sample_user_request:
        lines.append(f"Ejemplo: {entry.sample_user_request}")
    lines.append(f"Se abre en: {entry.loader_hint}")
    lines.append(f"Comando: studio comfyui abre workflow {entry.friendly_alias}")
    return "\n".join(lines)


def render_workflow_advisory_context(entry: WorkflowTemplateEntry) -> str:
    """Render richer workflow context intended for prompt injection."""

    return "\n".join(_build_workflow_advisory_lines(entry))


def render_workflow_comparison_advisory_context(
    left_entry: WorkflowTemplateEntry,
    right_entry: WorkflowTemplateEntry,
) -> str:
    """Render grounded comparison context for two real workflows."""

    left_required_inputs = set(left_entry.required_input_labels)
    right_required_inputs = set(right_entry.required_input_labels)

    shared_required_inputs = sorted(left_required_inputs & right_required_inputs)
    left_only_required_inputs = sorted(left_required_inputs - right_required_inputs)
    right_only_required_inputs = sorted(right_required_inputs - left_required_inputs)

    lines = [
        "OpenClaw workflow comparison advisory context:",
        f"left_alias={left_entry.friendly_alias}",
        f"left_use_case_id={left_entry.use_case_id}",
        f"left_workflow_name={left_entry.display_label}",
        f"right_alias={right_entry.friendly_alias}",
        f"right_use_case_id={right_entry.use_case_id}",
        f"right_workflow_name={right_entry.display_label}",
        "comparison_summary:",
        f"- left_purpose={left_entry.description}",
        f"- right_purpose={right_entry.description}",
        f"- shared_required_inputs={_render_input_labels(tuple(shared_required_inputs))}",
        f"- left_only_required_inputs={_render_input_labels(tuple(left_only_required_inputs))}",
        f"- right_only_required_inputs={_render_input_labels(tuple(right_only_required_inputs))}",
        f"- left_output={left_entry.output_label}",
        f"- right_output={right_entry.output_label}",
        (
            "- usage_hints="
            "Explica diferencias de proposito, entradas editables, salidas y "
            "cuando conviene usar uno u otro. Si uno produce un artefacto que "
            "alimenta al otro, dilo explicitamente."
        ),
        "",
        "left_workflow:",
    ]
    lines.extend(f"  {line}" for line in _build_workflow_advisory_lines(left_entry, include_heading=False))
    lines.extend(
        (
            "",
            "right_workflow:",
        )
    )
    lines.extend(f"  {line}" for line in _build_workflow_advisory_lines(right_entry, include_heading=False))
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for the ComfyUI workflow library."""

    parser = argparse.ArgumentParser(
        description="Publica workflows OpenClaw como templates visibles en ComfyUI."
    )
    parser.add_argument(
        "--repo-root",
        default=str(default_repo_root()),
        help="Ruta al repo de OpenClaw.",
    )
    parser.add_argument(
        "--comfyui-dir",
        default=str(default_comfyui_dir()),
        help="Ruta al arbol local de ComfyUI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("sync", help="Sincroniza la biblioteca local de templates.")
    subparsers.add_parser("list", help="Lista los workflows visibles en la biblioteca.")

    describe_parser = subparsers.add_parser(
        "describe",
        help="Describe un workflow por alias amigable o use_case_id.",
    )
    describe_parser.add_argument("workflow_ref", help="Alias o use_case_id del workflow.")

    explain_parser = subparsers.add_parser(
        "explain",
        help="Explica en lenguaje claro que hace un workflow.",
    )
    explain_parser.add_argument("workflow_ref", help="Alias o use_case_id del workflow.")

    advisory_parser = subparsers.add_parser(
        "advisory-context",
        help="Devuelve contexto estructurado del workflow real para el agente.",
    )
    advisory_parser.add_argument("workflow_ref", help="Alias o use_case_id del workflow.")

    compare_advisory_parser = subparsers.add_parser(
        "compare-advisory-context",
        help="Devuelve contexto estructurado para comparar dos workflows reales.",
    )
    compare_advisory_parser.add_argument("left_workflow_ref", help="Alias o use_case_id del primer workflow.")
    compare_advisory_parser.add_argument("right_workflow_ref", help="Alias o use_case_id del segundo workflow.")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the ComfyUI workflow library CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).expanduser().resolve()
    comfyui_dir = Path(args.comfyui_dir).expanduser().resolve()

    if args.command == "sync":
        print(render_sync_result(sync_workflow_templates(repo_root, comfyui_dir)))
        return 0

    if args.command == "list":
        sync_result = sync_workflow_templates(repo_root, comfyui_dir)
        print(render_workflow_list(sync_result.entries))
        return 0

    if args.command == "describe":
        sync_workflow_templates(repo_root, comfyui_dir)
        entry = resolve_workflow_template_entry(
            workflow_ref=args.workflow_ref,
            repo_root=repo_root,
            comfyui_dir=comfyui_dir,
        )
        print(render_workflow_description(entry))
        return 0

    if args.command == "explain":
        sync_workflow_templates(repo_root, comfyui_dir)
        entry = resolve_workflow_template_entry(
            workflow_ref=args.workflow_ref,
            repo_root=repo_root,
            comfyui_dir=comfyui_dir,
        )
        print(render_workflow_explanation(entry))
        return 0

    if args.command == "advisory-context":
        sync_workflow_templates(repo_root, comfyui_dir)
        entry = resolve_workflow_template_entry(
            workflow_ref=args.workflow_ref,
            repo_root=repo_root,
            comfyui_dir=comfyui_dir,
        )
        print(render_workflow_advisory_context(entry))
        return 0

    if args.command == "compare-advisory-context":
        sync_workflow_templates(repo_root, comfyui_dir)
        left_entry = resolve_workflow_template_entry(
            workflow_ref=args.left_workflow_ref,
            repo_root=repo_root,
            comfyui_dir=comfyui_dir,
        )
        right_entry = resolve_workflow_template_entry(
            workflow_ref=args.right_workflow_ref,
            repo_root=repo_root,
            comfyui_dir=comfyui_dir,
        )
        print(render_workflow_comparison_advisory_context(left_entry, right_entry))
        return 0

    parser.error(f"Comando no soportado: {args.command}")
    return 2


def _select_source_workflow(
    flow_definition: FlowDefinition,
    repo_root: Path,
) -> tuple[ExecutionVariant, str, Path]:
    """Pick the first concrete JSON file available for one flow."""

    for execution_variant in flow_definition.execution_variants:
        for workflow_relpath in execution_variant.workflow_file_references:
            source_path = (repo_root / workflow_relpath).resolve()
            if source_path.is_file():
                return execution_variant, workflow_relpath, source_path

    raise FileNotFoundError(
        f"No encontre un workflow JSON para {flow_definition.use_case_id} bajo {repo_root}."
    )


def _load_manifest(manifest_path: Path) -> dict[str, object]:
    """Load the previous managed manifest if present."""

    if not manifest_path.is_file():
        return {}
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _publish_template_file(source_path: Path, template_path: Path) -> None:
    """Publish one source workflow into the ComfyUI template library."""

    if template_path.is_symlink() or template_path.exists():
        template_path.unlink()

    shutil.copyfile(source_path, template_path)


def _publish_support_file(source_path: Path, target_path: Path) -> None:
    """Publish one Python helper file into the ComfyUI module directory."""

    if target_path.is_symlink() or target_path.exists():
        target_path.unlink()

    shutil.copyfile(source_path, target_path)


def _render_output_label(output_type: OutputArtifactType) -> str:
    """Render one output artifact type using product-facing language."""

    output_labels = {
        OutputArtifactType.IMAGE: "imagen",
        OutputArtifactType.IMAGE_SET: "set de imagenes",
        OutputArtifactType.CONTROL_PACKAGE: "paquete de controles",
        OutputArtifactType.VIDEO: "video",
        OutputArtifactType.ENHANCED_VIDEO: "video mejorado",
    }
    return output_labels[output_type]


def _render_input_labels(input_labels: tuple[str, ...]) -> str:
    """Join input labels in a compact human-friendly form."""

    return ", ".join(input_labels) if input_labels else "ninguna"


def summarize_workflow_graph(payload: dict[str, Any]) -> dict[str, str]:
    """Build a compact summary of the real workflow graph for advisory turns."""

    nodes = payload.get("nodes", [])
    visible_titles: list[str] = []
    editable_entry_nodes: list[str] = []
    prompt_nodes: list[str] = []
    model_nodes: list[str] = []
    output_nodes: list[str] = []
    node_type_counts: dict[str, int] = {}

    for node in nodes:
        node_type = str(node.get("type", ""))
        if node_type and node_type not in FRONTEND_ONLY_NODE_TYPES:
            node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1

        title = str(node.get("title") or node_type).strip()
        if (
            node_type in {"Label (rgthree)", "MarkdownNote", "Note"}
            and title
            and title not in visible_titles
        ):
            visible_titles.append(title)

        summary_line = _summarize_node(node)
        if _is_editable_entry_node(node):
            editable_entry_nodes.append(summary_line)
        elif _is_prompt_node(node):
            prompt_nodes.append(summary_line)
        elif _is_model_node(node):
            model_nodes.append(summary_line)
        elif _is_output_node(node):
            output_nodes.append(summary_line)

    top_node_types = sorted(
        node_type_counts.items(),
        key=lambda item: (-item[1], item[0]),
    )[:8]

    return {
        "node_count": str(len(nodes)),
        "visible_titles": _render_compact_list(visible_titles[:6]),
        "editable_entry_nodes": _render_compact_list(editable_entry_nodes[:8]),
        "prompt_nodes": _render_compact_list(prompt_nodes[:6]),
        "model_nodes": _render_compact_list(model_nodes[:8]),
        "output_nodes": _render_compact_list(output_nodes[:8]),
        "node_type_counts": _render_compact_list(
            [f"{node_type} x{count}" for node_type, count in top_node_types]
        ),
    }


def _build_workflow_advisory_lines(
    entry: WorkflowTemplateEntry,
    *,
    include_heading: bool = True,
) -> list[str]:
    source_payload = json.loads(Path(entry.source_path).read_text(encoding="utf-8"))
    graph_summary = summarize_workflow_graph(source_payload)

    lines: list[str] = []
    if include_heading:
        lines.append("OpenClaw workflow advisory context:")
    lines.extend(
        (
            f"workflow_alias={entry.friendly_alias}",
            f"use_case_id={entry.use_case_id}",
            f"workflow_name={entry.display_label}",
            f"workflow_description={entry.description}",
            f"output={entry.output_label}",
            f"required_inputs={_render_input_labels(entry.required_input_labels)}",
            f"optional_inputs={_render_input_labels(entry.optional_input_labels)}",
            f"variant={entry.variant_display_label}",
            f"source_path={format_home_path(entry.source_path)}",
            f"template_path={format_home_path(entry.template_path)}",
            f"load_in_ui={entry.loader_hint}",
        )
    )
    if entry.sample_user_request:
        lines.append(f"sample_request={entry.sample_user_request}")

    lines.extend(
        (
            "workflow_graph_summary:",
            f"- node_count={graph_summary['node_count']}",
            f"- visible_titles={graph_summary['visible_titles']}",
            f"- editable_entry_nodes={graph_summary['editable_entry_nodes']}",
            f"- prompt_nodes={graph_summary['prompt_nodes']}",
            f"- model_nodes={graph_summary['model_nodes']}",
            f"- output_nodes={graph_summary['output_nodes']}",
            f"- node_type_counts={graph_summary['node_type_counts']}",
            (
                "- usage_hints="
                "Para explicar como usarlo, prioriza los entry_nodes editables, "
                "luego los prompt_nodes, y trata los model_nodes como "
                "infraestructura que normalmente no se toca."
            ),
        )
    )
    return lines


def _is_editable_entry_node(node: dict[str, Any]) -> bool:
    node_type = str(node.get("type", ""))
    node_title = str(node.get("title") or "").lower()
    if node_type in FRONTEND_ONLY_NODE_TYPES or _is_model_node(node):
        return False
    return (
        node_type in {"LoadImage", "VHS_LoadVideo", "LoadImageMask", "LoadAudio"}
        or ("load" in node_type.lower() and node_type not in {"UNETLoader", "CLIPLoader", "VAELoader", "ModelPatchLoader"})
        or ("input" in node_title and node_type not in FRONTEND_ONLY_NODE_TYPES)
    )


def _is_prompt_node(node: dict[str, Any]) -> bool:
    return str(node.get("type", "")) in {"CLIPTextEncode", "Text Multiline (Code Compatible)"}


def _is_model_node(node: dict[str, Any]) -> bool:
    return str(node.get("type", "")) in {
        "UNETLoader",
        "CLIPLoader",
        "VAELoader",
        "ModelPatchLoader",
        "LoraLoader",
        "DownloadAndLoadDepthAnythingV2Model",
    }


def _is_output_node(node: dict[str, Any]) -> bool:
    node_type = str(node.get("type", ""))
    node_title = str(node.get("title") or "").lower()
    if node_type in FRONTEND_ONLY_NODE_TYPES:
        return False
    return (
        node_type in {"SaveImage", "CreateVideo", "VHS_VideoCombine", "SaveAnimatedWEBP"}
        or node_type.lower().startswith("save")
        or "save" in node_title
        or "output" in node_title
    )


def _summarize_node(node: dict[str, Any]) -> str:
    node_type = str(node.get("type", ""))
    title = str(node.get("title") or node_type).strip()
    primary_value = _extract_primary_widget_value(node.get("widgets_values"))
    if primary_value:
        return f"{title} [{node_type}] -> {primary_value}"
    return f"{title} [{node_type}]"


def _extract_primary_widget_value(raw_value: Any) -> str:
    if isinstance(raw_value, dict):
        for key in (
            "video",
            "image",
            "filename_prefix",
            "text",
            "unet_name",
            "clip_name",
            "vae_name",
            "lora_name",
        ):
            value = raw_value.get(key)
            if value is not None and value != "" and value != []:
                return str(value)
        for value in raw_value.values():
            extracted = _extract_primary_widget_value(value)
            if extracted:
                return extracted
        return ""

    if isinstance(raw_value, list):
        for value in raw_value:
            if isinstance(value, str) and value.strip():
                return value.strip()
        for value in raw_value:
            if isinstance(value, (int, float, bool)):
                return str(value)
        return ""

    if isinstance(raw_value, str):
        return raw_value.strip()

    if isinstance(raw_value, (int, float, bool)):
        return str(raw_value)

    return ""


def _render_compact_list(values: list[str]) -> str:
    return " | ".join(value for value in values if value) if values else "none"


if __name__ == "__main__":
    raise SystemExit(main())

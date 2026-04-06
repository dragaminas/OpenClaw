from __future__ import annotations

"""Publish OpenClaw workflows as native ComfyUI templates."""

import argparse
import json
import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

from openclaw_studio.application.session_engine import normalize_text
from openclaw_studio.contracts.flows import ExecutionVariant, FlowDefinition
from openclaw_studio.implementations import BUILTIN_FLOW_CATALOG


MODULE_NAME = "openclaw-workflows"
EXAMPLE_WORKFLOWS_DIRNAME = "example_workflows"
MANIFEST_FILENAME = "openclaw-workflows-manifest.json"
MODULE_INIT_TEXT = '''"""OpenClaw workflow templates exposed to ComfyUI."""

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
'''


@dataclass(frozen=True)
class WorkflowTemplateEntry:
    """One OpenClaw workflow exposed to ComfyUI as a template."""

    use_case_id: str
    friendly_alias: str
    display_label: str
    variant_id: str
    variant_display_label: str
    source_relpath: str
    source_path: str
    template_filename: str
    template_path: str
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
        lines.append(
            f"- {entry.friendly_alias} | {entry.use_case_id} | {entry.display_label}"
        )
    lines.append(
        f"carga_desde=Templates > {MODULE_NAME} > <alias>"
    )
    return "\n".join(lines)


def render_workflow_description(entry: WorkflowTemplateEntry) -> str:
    """Render one resolved workflow entry in a stable format."""

    return "\n".join(
        (
            f"use_case_id={entry.use_case_id}",
            f"alias={entry.friendly_alias}",
            f"workflow={entry.display_label}",
            f"variant_id={entry.variant_id}",
            f"variant={entry.variant_display_label}",
            f"source={format_home_path(entry.source_path)}",
            f"template={format_home_path(entry.template_path)}",
            f"carga_desde={entry.loader_hint}",
        )
    )


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


if __name__ == "__main__":
    raise SystemExit(main())

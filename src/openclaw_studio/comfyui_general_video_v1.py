from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from openclaw_studio.comfyui_openclaw_workflow_nodes import (
    DEFAULT_FINAL_TARGET_HEIGHT,
    DEFAULT_FINAL_TARGET_WIDTH,
    DEFAULT_FPS_TARGET,
    DEFAULT_SEGMENT_LENGTH_FRAMES,
    DEFAULT_SEGMENT_OVERLAP_FRAMES,
)


GENERAL_VIDEO_V1_WORKFLOW_RELPATH = Path(
    "ComfyUIWorkflows/local/minimum/uc-vid-02-general-video-render-rtx3060-v1.json"
)
BASE_VIDEO_WORKFLOW_RELPATH = Path(
    "ComfyUIWorkflows/local/minimum/uc-vid-02-ai-renderer-video-rtx3060-v1.json"
)
PREPROCESS_WORKFLOW_RELPATH = Path(
    "ComfyUIWorkflows/local/minimum/uc-vid-01-ai-renderer-preprocess-rtx3060-v1.json"
)
IMAGE_WORKFLOW_RELPATH = Path(
    "ComfyUIWorkflows/local/minimum/uc-img-02-z-image-turbo-cn-rtx3060-v1.json"
)

DEFAULT_BASE_VIDEO_REL = "blender/blender-test__base__v001.mp4"
DEFAULT_OUTPUT_PREFIX_ROOT = "openclaw/uc-vid-02-general-v1"
DEFAULT_PROMPT = (
    "Stylized cinematic render of the source clip with stable motion, "
    "clear silhouettes, and strong visual coherence."
)
DEFAULT_CLIP_NAME = "umt5_xxl_fp16.safetensors"
DEFAULT_CONTROL_WIDTH = 512
DEFAULT_PREPROCESS_RESOLUTION = 288
DEFAULT_FRAME_LOAD_CAP = 0
DEFAULT_RENDER_FRAME_RATE = 12
DEFAULT_OPERATIONAL_FALLBACK_FRAME_RATE = 24
DEFAULT_OPERATIONAL_RENDER_STEPS = 8
DEFAULT_ENABLE_FPS_INTERPOLATION = False
DEFAULT_ENABLE_COLOR_IDENTITY = False
DEFAULT_ENABLE_SEGMENTATION = False
DEFAULT_DEFAULT_SEGMENT_INDEX = 1
DEFAULT_ENABLE_FINAL_UPSCALE = True
DEFAULT_USE_BORDERS = True
DEFAULT_USE_POSE = True
DEFAULT_USE_DEPTH = True
RENDER_CORE_SUBGRAPH_ID = "c475d739-ec74-430f-a7bd-aab0fdd85070"
RENDER_START_SELECTOR_SUBGRAPH_ID = "5f517a60-e7b7-4864-8970-f4d91bd5be97"

LEGACY_NODE_IDS_TO_REMOVE = {
    282,
    3001,
    3002,
    3088,
    3345,
    3372,
}

REDUNDANT_ANNOTATION_NODE_IDS = {
    1062,
    1065,
    1069,
    1071,
    2388,
    2393,
    2395,
    2400,
    3177,
    3355,
    3366,
    2394,
    2421,
    2422,
    2423,
    3356,
}

ORPHAN_NODE_IDS_TO_REMOVE = {
    3358,
}

IDENTITY_SLOT_CONFIGS = (
    {
        "slot_index": 1,
        "color_node_id": 4032,
        "entity_node_id": 4033,
        "load_node_id": 3349,
        "resize_node_id": 3362,
        "batch_input_slot": 1,
    },
    {
        "slot_index": 2,
        "color_node_id": 4035,
        "entity_node_id": 4036,
        "load_node_id": 3350,
        "resize_node_id": 3364,
        "batch_input_slot": 2,
    },
    {
        "slot_index": 3,
        "color_node_id": 4038,
        "entity_node_id": 4039,
        "load_node_id": 3353,
        "resize_node_id": 3365,
        "batch_input_slot": 3,
    },
)


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def workflow_path_for(repo_root: Path | None = None) -> Path:
    root = (repo_root or default_repo_root()).resolve()
    return root / GENERAL_VIDEO_V1_WORKFLOW_RELPATH


def derive_general_video_v1_workflow(repo_root: Path | None = None) -> dict[str, Any]:
    root = (repo_root or default_repo_root()).resolve()
    base_workflow = _read_json(root / BASE_VIDEO_WORKFLOW_RELPATH)
    preprocess_workflow = _read_json(root / PREPROCESS_WORKFLOW_RELPATH)
    image_workflow = _read_json(root / IMAGE_WORKFLOW_RELPATH)

    _retitle_base_sections(base_workflow)
    _configure_base_loader(base_workflow)
    _expand_render_core_subgraphs(base_workflow)
    _configure_render_core_defaults(base_workflow)

    _remove_nodes(base_workflow, LEGACY_NODE_IDS_TO_REMOVE)
    _clear_inputs(
        base_workflow,
        (
            (1795, 0),
            (3354, 0),
            (3348, 1),
            (3348, 2),
            (3348, 3),
            (3272, 0),
            (3272, 1),
        ),
    )

    next_order = max(int(node.get("order", 0)) for node in base_workflow["nodes"]) + 1
    cloned_nodes = _build_added_nodes(
        base_workflow=base_workflow,
        preprocess_workflow=preprocess_workflow,
        image_workflow=image_workflow,
        next_order=next_order,
    )
    base_workflow["nodes"].extend(cloned_nodes)

    _wire_general_video_v1(base_workflow)
    _remove_nodes(
        base_workflow,
        REDUNDANT_ANNOTATION_NODE_IDS | ORPHAN_NODE_IDS_TO_REMOVE,
    )
    _layout_general_video_v1(base_workflow)
    _expand_all_nodes_for_debug(base_workflow)
    _sync_top_level_links(base_workflow)
    _refresh_workflow_metadata(base_workflow)
    return base_workflow


def write_general_video_v1_workflow(repo_root: Path | None = None) -> Path:
    root = (repo_root or default_repo_root()).resolve()
    workflow = derive_general_video_v1_workflow(root)
    target_path = root / GENERAL_VIDEO_V1_WORKFLOW_RELPATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        json.dumps(workflow, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return target_path


def patch_general_video_v1_runtime(
    workflow: dict[str, Any],
    *,
    input_video_rel: str,
    output_prefix_root: str,
    frame_load_cap: int = 2,
    custom_width: int = DEFAULT_CONTROL_WIDTH,
    render_frame_rate: int = DEFAULT_RENDER_FRAME_RATE,
    enable_fps_interpolation: bool = DEFAULT_ENABLE_FPS_INTERPOLATION,
    target_fps: float = DEFAULT_FPS_TARGET,
    use_borders: bool = DEFAULT_USE_BORDERS,
    use_pose: bool = DEFAULT_USE_POSE,
    use_depth: bool = DEFAULT_USE_DEPTH,
    enable_color_identity: bool = DEFAULT_ENABLE_COLOR_IDENTITY,
    identity_anchors: list[dict[str, str]] | None = None,
    enable_segmentation: bool = DEFAULT_ENABLE_SEGMENTATION,
    segment_length_frames: int = DEFAULT_SEGMENT_LENGTH_FRAMES,
    segment_overlap_frames: int = DEFAULT_SEGMENT_OVERLAP_FRAMES,
    segment_index: int = DEFAULT_DEFAULT_SEGMENT_INDEX,
    enable_final_upscale: bool = DEFAULT_ENABLE_FINAL_UPSCALE,
    final_width: int = DEFAULT_FINAL_TARGET_WIDTH,
    final_height: int = DEFAULT_FINAL_TARGET_HEIGHT,
    fast_validation: bool = True,
) -> None:
    node_265 = _find_node(workflow, 265)
    node_265["widgets_values"]["video"] = input_video_rel
    node_265["widgets_values"]["custom_width"] = custom_width
    node_265["widgets_values"]["custom_height"] = 0
    node_265["widgets_values"]["frame_load_cap"] = frame_load_cap
    node_265["widgets_values"]["skip_first_frames"] = 0

    _find_node(workflow, 3333)["widgets_values"][0] = DEFAULT_CLIP_NAME

    # Keep all preprocess controls aligned to the same VACE-safe canvas.
    _find_node(workflow, 4003)["widgets_values"][2] = DEFAULT_PREPROCESS_RESOLUTION
    _find_node(workflow, 4004)["widgets_values"][3] = DEFAULT_PREPROCESS_RESOLUTION

    _find_node(workflow, 4005)["widgets_values"]["filename_prefix"] = (
        f"{output_prefix_root}/preprocess_depth"
    )
    _find_node(workflow, 4006)["widgets_values"]["filename_prefix"] = (
        f"{output_prefix_root}/preprocess_outline"
    )
    _find_node(workflow, 4007)["widgets_values"]["filename_prefix"] = (
        f"{output_prefix_root}/preprocess_pose"
    )
    _set_video_combine_frame_rate(workflow, 4005, render_frame_rate)
    _set_video_combine_frame_rate(workflow, 4006, render_frame_rate)
    _set_video_combine_frame_rate(workflow, 4007, render_frame_rate)
    _find_node(workflow, 4021)["widgets_values"][0] = enable_fps_interpolation
    _find_node(workflow, 4022)["widgets_values"][0] = target_fps
    _find_node(workflow, 4020)["widgets_values"]["filename_prefix"] = (
        f"{output_prefix_root}/render"
    )
    _set_video_combine_frame_rate(workflow, 4020, render_frame_rate)
    set_general_video_v1_segmentation(
        workflow,
        enabled=enable_segmentation,
        segment_length_frames=segment_length_frames,
        segment_overlap_frames=segment_overlap_frames,
        segment_index=segment_index,
    )
    set_general_video_v1_final_upscale(
        workflow,
        enabled=enable_final_upscale,
        target_width=final_width,
        target_height=final_height,
    )
    _find_node(workflow, 4064)["widgets_values"]["filename_prefix"] = (
        f"{output_prefix_root}/final_full_hd"
    )
    _set_video_combine_frame_rate(workflow, 4064, render_frame_rate)
    _find_node(workflow, 4009)["widgets_values"][0] = (
        f"{output_prefix_root}/first_frame"
    )
    set_general_video_v1_controls(
        workflow,
        use_borders=use_borders,
        use_pose=use_pose,
        use_depth=use_depth,
    )
    set_general_video_v1_identity_anchors(
        workflow,
        enabled=enable_color_identity,
        anchors=identity_anchors,
    )

    _find_node(workflow, 3268)["widgets_values"][0] = 0
    if fast_validation:
        sampler_node = _find_node(workflow, 3253)
        sampler_node["widgets_values"][2] = 1
        sampler_node["widgets_values"][3] = 1
    _sync_top_level_links(workflow)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deriva el workflow general de video V1 para OpenClaw."
    )
    parser.add_argument("--repo-root", default=default_repo_root())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    target_path = write_general_video_v1_workflow(Path(args.repo_root))
    print(target_path)
    return 0


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_node(workflow: dict[str, Any], node_id: int) -> dict[str, Any]:
    for node in workflow.get("nodes", []):
        if int(node["id"]) == node_id:
            return node
    raise KeyError(f"No existe el nodo {node_id}.")


def _find_subgraph_definition(workflow: dict[str, Any], subgraph_id: str) -> dict[str, Any]:
    for definition in workflow.get("definitions", {}).get("subgraphs", []):
        if definition["id"] == subgraph_id:
            return definition
    raise KeyError(f"No existe el subgraph {subgraph_id!r}.")


def _find_subgraph_node(subgraph: dict[str, Any], node_id: int) -> dict[str, Any]:
    for node in subgraph.get("nodes", []):
        if int(node["id"]) == node_id:
            return node
    raise KeyError(f"No existe el nodo {node_id} en el subgraph.")


def _retitle_base_sections(workflow: dict[str, Any]) -> None:
    _find_node(workflow, 1066)["title"] = "OPENCLAW GENERAL VIDEO RENDER V1"
    _find_node(workflow, 1058)["title"] = (
        "Derivado sobre UC-VID-01 + UC-VID-02 para OpenClaw"
    )


def _configure_base_loader(workflow: dict[str, Any]) -> None:
    node_265 = _find_node(workflow, 265)
    node_265["title"] = "BASE VIDEO"
    node_265["widgets_values"]["video"] = DEFAULT_BASE_VIDEO_REL
    node_265["widgets_values"]["custom_width"] = DEFAULT_CONTROL_WIDTH
    node_265["widgets_values"]["custom_height"] = 0
    node_265["widgets_values"]["frame_load_cap"] = DEFAULT_FRAME_LOAD_CAP
    node_265["widgets_values"]["skip_first_frames"] = 0
    for slot in (2, 3, 4, 5):
        _remove_link_to_target(workflow, 265, slot)


def _configure_render_core_defaults(workflow: dict[str, Any]) -> None:
    _find_node(workflow, 3249)["title"] = "ENCODEA PROMPT FINAL"
    _find_node(workflow, 3249)["widgets_values"][0] = DEFAULT_PROMPT
    _find_node(workflow, 3262)["title"] = "PROMPT NEGATIVO"
    _find_node(workflow, 3228)["title"] = "INFO CONTROL AL RENDER"
    _find_node(workflow, 3261)["title"] = "PREPARA VIDEO DE CONTROL"
    _find_node(workflow, 3294)["title"] = "CODIFICA START IMAGE"
    _find_node(workflow, 3295)["title"] = "ANCLA LATENTE DE REFERENCIA"
    _find_node(workflow, 3287)["title"] = "CUENTA REF IMAGES"
    _find_node(workflow, 3286)["title"] = "MINIMO REF EXTRA"
    _find_node(workflow, 3284)["title"] = "HAY SOLO UNA REF?"
    _find_node(workflow, 3288)["title"] = "DESACTIVA START EXTRA"
    _find_node(workflow, 3280)["title"] = "ELIGE START IMAGE ACTIVA"
    _find_node(workflow, 3292)["title"] = "NOTA DEPENDENCIA RES4LYF"
    _find_node(workflow, 3255)["title"] = "WAN VACE PHANTOM"
    _find_node(workflow, 3258)["title"] = "COMBINA CONDICION NEGATIVA"
    _find_node(workflow, 3257)["title"] = "WAN VIDEO NAG"
    _find_node(workflow, 3253)["title"] = "SAMPLER VIDEO"
    _find_node(workflow, 3268)["title"] = "RECORTA LATENTE EXTRA"
    _find_node(workflow, 3254)["title"] = "LIMPIA GPU TRAS RECORTE"
    _find_node(workflow, 3252)["title"] = "DECODEA FRAMES RENDER"
    _find_node(workflow, 3333)["widgets_values"][0] = DEFAULT_CLIP_NAME
    _find_node(workflow, 2607)["title"] = "INFO VIDEO"
    _find_node(workflow, 2845)["title"] = "SELECCION TAMANO"
    _find_node(workflow, 3272)["title"] = "MEZCLA BORDES + PROFUNDIDAD"
    _find_node(workflow, 280)["title"] = "AJUSTA START IMAGE"
    _find_node(workflow, 3348)["title"] = "BATCH REFS IDENTIDAD"
    _find_node(workflow, 3349)["title"] = "REF ENTIDAD 1"
    _find_node(workflow, 3350)["title"] = "REF ENTIDAD 2"
    _find_node(workflow, 3353)["title"] = "REF ENTIDAD 3"
    _find_node(workflow, 3354)["title"] = "SET REF IMAGES"
    _find_node(workflow, 3359)["title"] = "GET REF IMAGES"
    _find_node(workflow, 3362)["title"] = "AJUSTA REFERENCIA 1"
    _find_node(workflow, 3364)["title"] = "AJUSTA REFERENCIA 2"
    _find_node(workflow, 3365)["title"] = "AJUSTA REFERENCIA 3"
    _find_node(workflow, 3349)["widgets_values"][0] = "references/identity_anchor_01.png"
    _find_node(workflow, 3350)["widgets_values"][0] = "references/identity_anchor_02.png"
    _find_node(workflow, 3353)["widgets_values"][0] = "references/identity_anchor_03.png"
    _find_node(workflow, 3268)["widgets_values"][0] = 0
    _find_node(workflow, 3253)["widgets_values"][2] = DEFAULT_OPERATIONAL_RENDER_STEPS


def _expand_render_core_subgraphs(workflow: dict[str, Any]) -> None:
    main_subgraph = _find_subgraph_definition(workflow, RENDER_CORE_SUBGRAPH_ID)
    selector_subgraph = _find_subgraph_definition(
        workflow, RENDER_START_SELECTOR_SUBGRAPH_ID
    )
    main_sources = {int(node["id"]): node for node in main_subgraph.get("nodes", [])}
    selector_sources = {
        int(node["id"]): node for node in selector_subgraph.get("nodes", [])
    }

    _remove_nodes(workflow, {3228})
    next_order = max(int(node.get("order", 0)) for node in workflow["nodes"]) + 1

    for node_id in (
        3249,
        3262,
        3228,
        3287,
        3286,
        3284,
        3288,
        3280,
        3261,
        3294,
        3295,
        3292,
        3255,
        3258,
        3257,
        3253,
        3268,
        3254,
        3252,
    ):
        source = main_sources.get(node_id) or selector_sources.get(node_id)
        if source is None:
            raise KeyError(f"No existe el nodo {node_id} en los subgrafos base.")
        cloned = copy.deepcopy(source)
        cloned["order"] = next_order
        next_order += 1
        for input_entry in cloned.get("inputs", []):
            if "link" in input_entry:
                input_entry["link"] = None
        for output_entry in cloned.get("outputs", []):
            if "links" in output_entry:
                output_entry["links"] = None
        workflow["nodes"].append(cloned)

    subgraphs = workflow.get("definitions", {}).get("subgraphs", [])
    workflow.setdefault("definitions", {})["subgraphs"] = [
        definition
        for definition in subgraphs
        if definition.get("id")
        not in {RENDER_CORE_SUBGRAPH_ID, RENDER_START_SELECTOR_SUBGRAPH_ID}
    ]


def _remove_nodes(workflow: dict[str, Any], node_ids: set[int]) -> None:
    workflow["links"] = [
        raw_link
        for raw_link in workflow.get("links", [])
        if int(raw_link[1]) not in node_ids and int(raw_link[3]) not in node_ids
    ]
    workflow["nodes"] = [
        node
        for node in workflow.get("nodes", [])
        if int(node["id"]) not in node_ids
    ]


def _clear_inputs(workflow: dict[str, Any], targets: tuple[tuple[int, int], ...]) -> None:
    for target_id, target_slot in targets:
        _remove_link_to_target(workflow, target_id, target_slot)


def _remove_link_to_target(workflow: dict[str, Any], target_id: int, target_slot: int) -> None:
    workflow["links"] = [
        raw_link
        for raw_link in workflow.get("links", [])
        if not (int(raw_link[3]) == target_id and int(raw_link[4]) == target_slot)
    ]


def _build_added_nodes(
    *,
    base_workflow: dict[str, Any],
    preprocess_workflow: dict[str, Any],
    image_workflow: dict[str, Any],
    next_order: int,
) -> list[dict[str, Any]]:
    added_nodes: list[dict[str, Any]] = []

    def clone(
        source_node: dict[str, Any],
        *,
        new_id: int,
        pos: tuple[float, float],
        title: str,
        widgets_overrides: dict[str, Any] | list[Any] | None = None,
    ) -> dict[str, Any]:
        nonlocal next_order
        cloned = copy.deepcopy(source_node)
        cloned["id"] = new_id
        cloned["pos"] = [pos[0], pos[1]]
        cloned["title"] = title
        cloned["order"] = next_order
        next_order += 1
        if widgets_overrides is not None:
            cloned["widgets_values"] = widgets_overrides
        for input_entry in cloned.get("inputs", []):
            if "link" in input_entry:
                input_entry["link"] = None
        for output_entry in cloned.get("outputs", []):
            if "links" in output_entry:
                output_entry["links"] = None
        return cloned

    preprocess_sources = {node["id"]: node for node in preprocess_workflow["nodes"]}
    image_sources = {node["id"]: node for node in image_workflow["nodes"]}
    base_sources = {node["id"]: node for node in base_workflow["nodes"]}

    added_nodes.extend(
        (
            clone(
                preprocess_sources[3371],
                new_id=4001,
                pos=(-1660, -660),
                title="DEPTH MODEL",
            ),
            clone(
                preprocess_sources[3372],
                new_id=4002,
                pos=(-1660, -470),
                title="PREPROCESS DEPTH",
            ),
            clone(
                preprocess_sources[3373],
                new_id=4003,
                pos=(-1240, -660),
                title="PREPROCESS BORDES",
                widgets_overrides=[100, 200, DEFAULT_PREPROCESS_RESOLUTION],
            ),
            clone(
                preprocess_sources[3376],
                new_id=4004,
                pos=(-820, -660),
                title="PREPROCESS POSE",
                widgets_overrides=["enable", "enable", "enable", DEFAULT_PREPROCESS_RESOLUTION, "disable"],
            ),
            clone(
                preprocess_sources[3001],
                new_id=4005,
                pos=(-1660, -230),
                title="SAVE DEPTH CONTROL",
                widgets_overrides=_video_combine_widgets(
                    f"{DEFAULT_OUTPUT_PREFIX_ROOT}/preprocess_depth"
                ),
            ),
            clone(
                preprocess_sources[3377],
                new_id=4006,
                pos=(-1240, -230),
                title="SAVE OUTLINE CONTROL",
                widgets_overrides=_video_combine_widgets(
                    f"{DEFAULT_OUTPUT_PREFIX_ROOT}/preprocess_outline"
                ),
            ),
            clone(
                preprocess_sources[3378],
                new_id=4007,
                pos=(-820, -230),
                title="SAVE POSE CONTROL",
                widgets_overrides=_video_combine_widgets(
                    f"{DEFAULT_OUTPUT_PREFIX_ROOT}/preprocess_pose"
                ),
            ),
        )
    )

    added_nodes.append(
        {
            "id": 4008,
            "type": "GetFrameByIndex",
            "pos": [-380, -780],
            "size": [300, 86],
            "flags": {},
            "order": next_order,
            "mode": 0,
            "inputs": [
                {"name": "frames", "type": "IMAGE", "link": None},
                {"name": "index", "type": "INT", "widget": {"name": "index"}, "link": None},
            ],
            "outputs": [{"name": "IMAGE", "type": "IMAGE", "links": None}],
            "title": "FRAME INICIAL",
            "properties": {
                "cnr_id": "comfy-core",
                "ver": "0.3.76",
                "Node name for S&R": "GetFrameByIndex",
            },
            "widgets_values": [0],
            "shape": 1,
        }
    )
    next_order += 1
    added_nodes.append(
        clone(
            image_sources[9],
            new_id=4009,
            pos=(-30, -820),
            title="GUARDA FRAME INICIAL",
            widgets_overrides=[f"{DEFAULT_OUTPUT_PREFIX_ROOT}/first_frame"],
        )
    )

    bool_properties = {
        "cnr_id": "comfy-core",
        "ver": "0.3.76",
        "Node name for S&R": "PrimitiveBoolean",
    }
    int_properties = {
        "cnr_id": "comfy-core",
        "ver": "0.3.76",
        "Node name for S&R": "PrimitiveInt",
    }
    float_properties = {
        "cnr_id": "comfy-core",
        "ver": "0.3.76",
        "Node name for S&R": "PrimitiveFloat",
    }
    string_properties = {
        "cnr_id": "comfy-core",
        "ver": "0.3.76",
        "Node name for S&R": "PrimitiveString",
    }
    string_multiline_properties = {
        "cnr_id": "comfy-core",
        "ver": "0.3.76",
        "Node name for S&R": "PrimitiveStringMultiline",
    }
    logic_properties = {
        "cnr_id": "ComfyUI-Impact-Pack",
        "ver": "8.21.2",
        "Node name for S&R": "ImpactLogicalOperators",
    }
    added_nodes.append(
        {
            "id": 4048,
            "type": "PrimitiveBoolean",
            "pos": [-2530, 350],
            "size": [260, 58],
            "flags": {},
            "order": next_order,
            "mode": 0,
            "inputs": [],
            "outputs": [{"name": "BOOLEAN", "type": "BOOLEAN", "links": None}],
            "title": "segmentar_clip_largo",
            "properties": bool_properties,
            "widgets_values": [DEFAULT_ENABLE_SEGMENTATION],
            "shape": 1,
        }
    )
    next_order += 1
    for node_id, title, value, pos in (
        (4049, "frames_por_segmento", DEFAULT_SEGMENT_LENGTH_FRAMES, (-2530, 430)),
        (4050, "solape_segmentos", DEFAULT_SEGMENT_OVERLAP_FRAMES, (-2530, 510)),
        (4051, "segmento_actual", DEFAULT_DEFAULT_SEGMENT_INDEX, (-2530, 590)),
    ):
        added_nodes.append(
            {
                "id": node_id,
                "type": "PrimitiveInt",
                "pos": [pos[0], pos[1]],
                "size": [260, 58],
                "flags": {},
                "order": next_order,
                "mode": 0,
                "inputs": [],
                "outputs": [{"name": "INT", "type": "INT", "links": None}],
                "title": title,
                "properties": int_properties,
                "widgets_values": [value],
                "shape": 1,
            }
        )
        next_order += 1
    added_nodes.append(
        {
            "id": 4052,
            "type": "OpenClawSegmentSelector",
            "pos": [-2160, 380],
            "size": [320, 220],
            "flags": {},
            "order": next_order,
            "mode": 0,
            "inputs": [
                {"name": "images", "type": "IMAGE", "link": None},
                {"name": "source_fps", "type": "FLOAT", "link": None},
                {"name": "enabled", "type": "BOOLEAN", "link": None},
                {"name": "segment_length_frames", "type": "INT", "link": None},
                {"name": "overlap_frames", "type": "INT", "link": None},
                {"name": "segment_index", "type": "INT", "link": None},
            ],
            "outputs": [
                {"name": "images", "type": "IMAGE", "links": None},
                {"name": "segmentation_active", "type": "BOOLEAN", "links": None},
                {"name": "segment_count", "type": "INT", "links": None},
                {"name": "segment_start_frame", "type": "INT", "links": None},
                {"name": "segment_end_frame", "type": "INT", "links": None},
                {"name": "selected_frame_count", "type": "INT", "links": None},
                {"name": "summary", "type": "STRING", "links": None},
            ],
            "title": "SELECCIONA SEGMENTO ACTUAL",
            "properties": {
                "cnr_id": "openclaw-workflows",
                "Node name for S&R": "OpenClawSegmentSelector",
            },
            "widgets_values": [],
        }
    )
    next_order += 1
    added_nodes.append(
        {
            "id": 4030,
            "type": "PrimitiveStringMultiline",
            "pos": [1360, -980],
            "size": [300, 210],
            "flags": {},
            "order": next_order,
            "mode": 0,
            "inputs": [],
            "outputs": [{"name": "STRING", "type": "STRING", "links": None}],
            "title": "PROMPT BASE ESCENA + ESTILO",
            "properties": string_multiline_properties,
            "widgets_values": [DEFAULT_PROMPT],
            "shape": 1,
        }
    )
    next_order += 1
    for node_id, title, value, pos in (
        (4010, "usar_bordes", True, (-1660, -980)),
        (4011, "usar_pose", True, (-1660, -900)),
        (4012, "usar_profundidad", True, (-1660, -820)),
    ):
        added_nodes.append(
            {
                "id": node_id,
                "type": "PrimitiveBoolean",
                "pos": [pos[0], pos[1]],
                "size": [220, 58],
                "flags": {},
                "order": next_order,
                "mode": 0,
                "inputs": [],
                "outputs": [{"name": "BOOLEAN", "type": "BOOLEAN", "links": None}],
                "title": title,
                "properties": bool_properties,
                "widgets_values": [value],
                "shape": 1,
            }
        )
        next_order += 1

    added_nodes.append(
        {
            "id": 4031,
            "type": "PrimitiveBoolean",
            "pos": [-1630, 770],
            "size": [260, 58],
            "flags": {},
            "order": next_order,
            "mode": 0,
            "inputs": [],
            "outputs": [{"name": "BOOLEAN", "type": "BOOLEAN", "links": None}],
            "title": "usar_identidad_color",
            "properties": bool_properties,
            "widgets_values": [DEFAULT_ENABLE_COLOR_IDENTITY],
            "shape": 1,
        }
    )
    next_order += 1

    for node_id, title, value, pos in (
        (4032, "color_1", "rojo", (-1300, 880)),
        (4033, "entidad_1 / anclaje_prompt_1", "", (-980, 880)),
        (4035, "color_2", "verde", (-1300, 1210)),
        (4036, "entidad_2 / anclaje_prompt_2", "", (-980, 1210)),
        (4038, "color_3", "azul", (-1300, 1540)),
        (4039, "entidad_3 / anclaje_prompt_3", "", (-980, 1540)),
    ):
        added_nodes.append(
            {
                "id": node_id,
                "type": "PrimitiveString",
                "pos": [pos[0], pos[1]],
                "size": [280, 58],
                "flags": {},
                "order": next_order,
                "mode": 0,
                "inputs": [],
                "outputs": [{"name": "STRING", "type": "STRING", "links": None}],
                "title": title,
                "properties": string_properties,
                "widgets_values": [value],
                "shape": 1,
            }
        )
        next_order += 1

    added_nodes.append(
        {
            "id": 4042,
            "type": "OpenClawIdentityPromptBuilder",
            "pos": [1360, -700],
            "size": [320, 220],
            "flags": {},
            "order": next_order,
            "mode": 0,
            "inputs": [
                {"name": "base_prompt", "type": "STRING", "link": None},
                {"name": "enabled", "type": "BOOLEAN", "link": None},
                {"name": "total_ref_images", "type": "INT", "link": None},
                {"name": "color_1", "type": "STRING", "link": None},
                {"name": "entity_1", "type": "STRING", "link": None},
                {"name": "color_2", "type": "STRING", "link": None},
                {"name": "entity_2", "type": "STRING", "link": None},
                {"name": "color_3", "type": "STRING", "link": None},
                {"name": "entity_3", "type": "STRING", "link": None},
            ],
            "outputs": [
                {"name": "prompt", "type": "STRING", "links": None},
                {"name": "enabled", "type": "BOOLEAN", "links": None},
                {"name": "identity_ref_count", "type": "INT", "links": None},
                {"name": "mapping_count", "type": "INT", "links": None},
                {"name": "summary", "type": "STRING", "links": None},
            ],
            "title": "CAPA IDENTIDAD COLOR -> ENTIDAD",
            "properties": {
                "cnr_id": "openclaw-workflows",
                "Node name for S&R": "OpenClawIdentityPromptBuilder",
            },
            "widgets_values": [],
        }
    )
    next_order += 1

    for node_id, title, operator, pos in (
        (4013, "hay_bordes_o_profundidad", "or", (-1350, -950)),
        (4014, "mezcla_bordes_y_profundidad", "and", (-1350, -850)),
        (4015, "anade_pose_sobre_otros", "and", (-1050, -900)),
    ):
        added_nodes.append(
            {
                "id": node_id,
                "type": "ImpactLogicalOperators",
                "pos": [pos[0], pos[1]],
                "size": [260, 82],
                "flags": {},
                "order": next_order,
                "mode": 0,
                "inputs": [
                    {"name": "bool_a", "type": "BOOLEAN", "link": None},
                    {"name": "bool_b", "type": "BOOLEAN", "link": None},
                ],
                "outputs": [{"name": "BOOLEAN", "type": "BOOLEAN", "links": None}],
                "title": title,
                "properties": logic_properties,
                "widgets_values": [operator],
                "shape": 1,
            }
        )
        next_order += 1

    for node_id, pos, title, blend_value in (
        (4016, (-1080, -640), "elige depth o pose", 1.0),
        (4017, (-790, -640), "elige control primario", 1.0),
        (4018, (-520, -550), "ANADE POSE SI ESTA ACTIVA", 0.35),
    ):
        added_nodes.append(
            clone(
                base_sources[3272],
                new_id=node_id,
                pos=pos,
                title=title,
                widgets_overrides=[False, blend_value, "normal"],
            )
        )

    added_nodes.append(
        clone(
            preprocess_sources[3001],
            new_id=4020,
            pos=(2680, -210),
            title="GUARDA RENDER BASE",
            widgets_overrides=_video_combine_widgets(f"{DEFAULT_OUTPUT_PREFIX_ROOT}/render"),
        )
    )

    added_nodes.append(
        {
            "id": 4021,
            "type": "PrimitiveBoolean",
            "pos": [2140, -860],
            "size": [240, 58],
            "flags": {},
            "order": next_order,
            "mode": 0,
            "inputs": [],
            "outputs": [{"name": "BOOLEAN", "type": "BOOLEAN", "links": None}],
            "title": "usar_interpolacion_fps",
            "properties": bool_properties,
            "widgets_values": [DEFAULT_ENABLE_FPS_INTERPOLATION],
            "shape": 1,
        }
    )
    next_order += 1
    added_nodes.append(
        {
            "id": 4022,
            "type": "PrimitiveFloat",
            "pos": [2140, -780],
            "size": [240, 58],
            "flags": {},
            "order": next_order,
            "mode": 0,
            "inputs": [],
            "outputs": [{"name": "FLOAT", "type": "FLOAT", "links": None}],
            "title": "fps_objetivo",
            "properties": float_properties,
            "widgets_values": [DEFAULT_FPS_TARGET],
            "shape": 1,
        }
    )
    next_order += 1
    added_nodes.append(
        {
            "id": 4023,
            "type": "OpenClawFPSInterpolation",
            "pos": [2380, -860],
            "size": [280, 182],
            "flags": {},
            "order": next_order,
            "mode": 0,
            "inputs": [
                {"name": "images", "type": "IMAGE", "link": None},
                {"name": "source_fps", "type": "FLOAT", "link": None},
                {"name": "target_fps", "type": "FLOAT", "link": None},
                {"name": "enabled", "type": "BOOLEAN", "link": None},
            ],
            "outputs": [
                {"name": "images", "type": "IMAGE", "links": None},
                {"name": "output_fps", "type": "FLOAT", "links": None},
                {"name": "interpolated", "type": "BOOLEAN", "links": None},
                {"name": "inserted_frames", "type": "INT", "links": None},
                {"name": "summary", "type": "STRING", "links": None},
            ],
            "title": "INTERPOLACION FPS OPCIONAL",
            "properties": {
                "cnr_id": "openclaw-workflows",
                "Node name for S&R": "OpenClawFPSInterpolation",
            },
            "widgets_values": [],
        }
    )
    next_order += 1
    added_nodes.append(
        {
            "id": 4060,
            "type": "PrimitiveBoolean",
            "pos": [6120, -720],
            "size": [280, 58],
            "flags": {},
            "order": next_order,
            "mode": 0,
            "inputs": [],
            "outputs": [{"name": "BOOLEAN", "type": "BOOLEAN", "links": None}],
            "title": "usar_mejora_final_full_hd",
            "properties": bool_properties,
            "widgets_values": [DEFAULT_ENABLE_FINAL_UPSCALE],
            "shape": 1,
        }
    )
    next_order += 1
    for node_id, title, value, pos in (
        (4061, "ancho_final", DEFAULT_FINAL_TARGET_WIDTH, (6120, -640)),
        (4062, "alto_final", DEFAULT_FINAL_TARGET_HEIGHT, (6120, -560)),
    ):
        added_nodes.append(
            {
                "id": node_id,
                "type": "PrimitiveInt",
                "pos": [pos[0], pos[1]],
                "size": [240, 58],
                "flags": {},
                "order": next_order,
                "mode": 0,
                "inputs": [],
                "outputs": [{"name": "INT", "type": "INT", "links": None}],
                "title": title,
                "properties": int_properties,
                "widgets_values": [value],
                "shape": 1,
            }
        )
        next_order += 1
    added_nodes.append(
        {
            "id": 4063,
            "type": "OpenClawFinalVideoResize",
            "pos": [6450, -720],
            "size": [320, 200],
            "flags": {},
            "order": next_order,
            "mode": 0,
            "inputs": [
                {"name": "images", "type": "IMAGE", "link": None},
                {"name": "enabled", "type": "BOOLEAN", "link": None},
                {"name": "target_width", "type": "INT", "link": None},
                {"name": "target_height", "type": "INT", "link": None},
            ],
            "outputs": [
                {"name": "images", "type": "IMAGE", "links": None},
                {"name": "upscale_active", "type": "BOOLEAN", "links": None},
                {"name": "output_width", "type": "INT", "links": None},
                {"name": "output_height", "type": "INT", "links": None},
                {"name": "summary", "type": "STRING", "links": None},
            ],
            "title": "MEJORA FINAL FULL HD",
            "properties": {
                "cnr_id": "openclaw-workflows",
                "Node name for S&R": "OpenClawFinalVideoResize",
            },
            "widgets_values": [],
        }
    )
    next_order += 1
    added_nodes.append(
        clone(
            preprocess_sources[3001],
            new_id=4064,
            pos=(7120, -620),
            title="GUARDA RENDER FINAL FULL HD",
            widgets_overrides=_video_combine_widgets(
                f"{DEFAULT_OUTPUT_PREFIX_ROOT}/final_full_hd"
            ),
        )
    )
    added_nodes.extend(
        (
            clone(
                base_sources[3228],
                new_id=4120,
                pos=(4140, 180),
                title="INFO FRAMES RENDER",
            ),
            clone(
                base_sources[3228],
                new_id=4126,
                pos=(4470, -180),
                title="INFO FRAMES INTERPOLADOS",
            ),
            _build_display_any_node(
                node_id=4121,
                pos=(-1810, -560),
                title="FPS BASE CARGADO",
                order=next_order,
            ),
            _build_display_any_node(
                node_id=4122,
                pos=(-1810, -460),
                title="FRAMES VIDEO CARGADOS",
                order=next_order + 1,
            ),
            _build_display_any_node(
                node_id=4129,
                pos=(-1810, -260),
                title="ANCHO CARGADO",
                order=next_order + 2,
            ),
            _build_display_any_node(
                node_id=4130,
                pos=(-1810, -160),
                title="ALTO CARGADO",
                order=next_order + 3,
            ),
            _build_display_any_node(
                node_id=4123,
                pos=(2050, 40),
                title="FRAMES CONTROL AL RENDER",
                order=next_order + 4,
            ),
            _build_display_any_node(
                node_id=4124,
                pos=(4470, 180),
                title="FRAMES SALIDA RENDER",
                order=next_order + 5,
            ),
            _build_display_any_node(
                node_id=4125,
                pos=(5130, -320),
                title="FRAMES SALIDA INTERPOLACION",
                order=next_order + 6,
            ),
            _build_display_any_node(
                node_id=4127,
                pos=(5130, -220),
                title="FPS SALIDA",
                order=next_order + 7,
            ),
            _build_display_any_node(
                node_id=4131,
                pos=(5130, -120),
                title="INTERPOLACION ACTIVA?",
                order=next_order + 8,
            ),
            _build_display_any_node(
                node_id=4132,
                pos=(5130, -20),
                title="FRAMES INSERTADOS",
                order=next_order + 9,
            ),
            _build_display_any_node(
                node_id=4128,
                pos=(5130, 80),
                title="RESUMEN INTERPOLACION",
                order=next_order + 10,
            ),
            _build_display_any_node(
                node_id=4043,
                pos=(-620, 1120),
                title="IDENTIDAD COLOR ACTIVA?",
                order=next_order + 11,
            ),
            _build_display_any_node(
                node_id=4044,
                pos=(-620, 1250),
                title="REFS IDENTIDAD EXTRA",
                order=next_order + 12,
            ),
            _build_display_any_node(
                node_id=4045,
                pos=(-620, 1380),
                title="MAPEOS IDENTIDAD",
                order=next_order + 13,
            ),
            _build_display_any_node(
                node_id=4046,
                pos=(-620, 1510),
                title="RESUMEN IDENTIDAD",
                order=next_order + 14,
            ),
            _build_display_any_node(
                node_id=4047,
                pos=(2180, -900),
                title="PROMPT FINAL RESUELTO",
                order=next_order + 15,
            ),
            _build_display_any_node(
                node_id=4053,
                pos=(-1820, 350),
                title="SEGMENTACION ACTIVA?",
                order=next_order + 16,
            ),
            _build_display_any_node(
                node_id=4054,
                pos=(-1820, 480),
                title="TOTAL SEGMENTOS",
                order=next_order + 17,
            ),
            _build_display_any_node(
                node_id=4055,
                pos=(-1820, 610),
                title="FRAMES SEGMENTO ACTUAL",
                order=next_order + 18,
            ),
            _build_display_any_node(
                node_id=4056,
                pos=(-2160, 650),
                title="RESUMEN SEGMENTACION",
                order=next_order + 19,
            ),
            _build_display_any_node(
                node_id=4065,
                pos=(6790, -720),
                title="MEJORA FINAL ACTIVA?",
                order=next_order + 20,
            ),
            _build_display_any_node(
                node_id=4066,
                pos=(6790, -590),
                title="ANCHO FINAL RESUELTO",
                order=next_order + 21,
            ),
            _build_display_any_node(
                node_id=4067,
                pos=(6790, -460),
                title="ALTO FINAL RESUELTO",
                order=next_order + 22,
            ),
            _build_display_any_node(
                node_id=4068,
                pos=(6450, -420),
                title="RESUMEN MEJORA FINAL",
                order=next_order + 23,
            ),
        )
    )
    next_order += 24
    for node_id in (4005, 4006, 4007, 4020, 4064):
        _promote_video_combine_frame_rate_input(
            next(node for node in added_nodes if int(node["id"]) == node_id)
        )
    return added_nodes


def _video_combine_widgets(filename_prefix: str) -> dict[str, Any]:
    return {
        "frame_rate": DEFAULT_OPERATIONAL_FALLBACK_FRAME_RATE,
        "loop_count": 0,
        "filename_prefix": filename_prefix,
        "format": "video/h264-mp4",
        "pix_fmt": "yuv420p",
        "crf": 19,
        "save_metadata": True,
        "trim_to_audio": False,
        "pingpong": False,
        "save_output": True,
        "videopreview": {"hidden": False, "paused": False, "params": {}},
    }


def _build_display_any_node(
    *,
    node_id: int,
    pos: tuple[float, float],
    title: str,
    order: int,
) -> dict[str, Any]:
    return {
        "id": node_id,
        "type": "Display Any (rgthree)",
        "pos": [pos[0], pos[1]],
        "size": [260, 110],
        "flags": {},
        "order": order,
        "mode": 0,
        "inputs": [
            {
                "dir": 3,
                "localized_name": "source",
                "name": "source",
                "type": "*",
                "link": None,
            }
        ],
        "outputs": [],
        "properties": {
            "cnr_id": "rgthree-comfy",
            "Node name for S&R": "Display Any (rgthree)",
        },
        "widgets_values": [""],
        "title": title,
    }


def _promote_video_combine_frame_rate_input(node: dict[str, Any]) -> None:
    if any(input_entry.get("name") == "frame_rate" for input_entry in node.get("inputs", [])):
        return
    node.setdefault("inputs", []).append(
        {
            "name": "frame_rate",
            "type": "FLOAT",
            "widget": {"name": "frame_rate"},
            "link": None,
        }
    )


def _set_video_combine_frame_rate(
    workflow: dict[str, Any],
    node_id: int,
    frame_rate: int,
) -> None:
    node = _find_node(workflow, node_id)
    _remove_link_to_target(workflow, node_id, 4)
    node["widgets_values"]["frame_rate"] = frame_rate


def set_general_video_v1_controls(
    workflow: dict[str, Any],
    *,
    use_borders: bool,
    use_pose: bool,
    use_depth: bool,
) -> None:
    if not any((use_borders, use_pose, use_depth)):
        raise ValueError(
            "La V1 general de video requiere al menos un control activo."
        )

    _find_node(workflow, 4010)["widgets_values"][0] = use_borders
    _find_node(workflow, 4011)["widgets_values"][0] = use_pose
    _find_node(workflow, 4012)["widgets_values"][0] = use_depth


def set_general_video_v1_segmentation(
    workflow: dict[str, Any],
    *,
    enabled: bool,
    segment_length_frames: int,
    segment_overlap_frames: int,
    segment_index: int,
) -> None:
    _find_node(workflow, 4048)["widgets_values"][0] = enabled
    _find_node(workflow, 4049)["widgets_values"][0] = max(int(segment_length_frames), 1)
    _find_node(workflow, 4050)["widgets_values"][0] = max(int(segment_overlap_frames), 0)
    _find_node(workflow, 4051)["widgets_values"][0] = max(int(segment_index), 1)


def set_general_video_v1_identity_anchors(
    workflow: dict[str, Any],
    *,
    enabled: bool,
    anchors: list[dict[str, str]] | None = None,
) -> None:
    normalized_anchors = list(anchors or [])
    _find_node(workflow, 4031)["widgets_values"][0] = enabled

    for slot_config in IDENTITY_SLOT_CONFIGS:
        anchor_index = slot_config["slot_index"] - 1
        anchor = normalized_anchors[anchor_index] if anchor_index < len(normalized_anchors) else {}
        color_value = str(anchor.get("color", "") or "").strip()
        entity_value = _render_identity_entity_value(anchor)

        _find_node(workflow, slot_config["color_node_id"])["widgets_values"][0] = color_value
        _find_node(workflow, slot_config["entity_node_id"])["widgets_values"][0] = entity_value

        reference_path = str(anchor.get("reference_image_relpath", "") or "").strip()
        if reference_path:
            _find_node(workflow, slot_config["load_node_id"])["widgets_values"][0] = reference_path
            _set_link(
                workflow,
                origin_id=slot_config["resize_node_id"],
                origin_slot=0,
                target_id=3348,
                target_slot=slot_config["batch_input_slot"],
                link_type="IMAGE",
            )
        else:
            _remove_link_to_target(workflow, 3348, slot_config["batch_input_slot"])


def set_general_video_v1_final_upscale(
    workflow: dict[str, Any],
    *,
    enabled: bool,
    target_width: int,
    target_height: int,
) -> None:
    _find_node(workflow, 4060)["widgets_values"][0] = enabled
    _find_node(workflow, 4061)["widgets_values"][0] = max(int(target_width), 2)
    _find_node(workflow, 4062)["widgets_values"][0] = max(int(target_height), 2)


def _render_identity_entity_value(anchor: dict[str, str]) -> str:
    entity = str(anchor.get("entity", "") or "").strip()
    prompt_anchor = str(anchor.get("prompt_anchor", "") or "").strip()
    if entity and prompt_anchor:
        return f"{entity} | {prompt_anchor}"
    return entity or prompt_anchor


def _layout_general_video_v1(workflow: dict[str, Any]) -> None:
    title_node = _find_node(workflow, 1066)
    title_node["pos"] = [-3030, -1290]
    title_node["size"] = [920, 56]

    subtitle_node = _find_node(workflow, 1058)
    subtitle_node["pos"] = [-3030, -1225]
    subtitle_node["size"] = [820, 26]

    note_frame_cap = _find_node(workflow, 2375)
    note_frame_cap["pos"] = [-2370, -970]
    note_frame_cap["size"] = [520, 110]
    note_frame_cap["widgets_values"] = [
        (
            "Uso normal: frame_load_cap=0 para cargar el clip completo y "
            "mantener el fps del video base. Usa un cap 4n+1 solo para "
            "corridas largas o para la ruta de validacion rapida."
        )
    ]

    positions = {
        3326: (-3220, -820),
        3327: (-3220, -680),
        3328: (-3220, -540),
        3329: (-3220, -400),
        3332: (-3220, -250),
        3333: (-3220, -80),
        3335: (-3220, 70),
        3334: (-3220, 250),
        3336: (-3220, 340),
        265: (-2550, -820),
        2607: (-2170, -820),
        2687: (-2170, -560),
        4121: (-2170, 20),
        4122: (-2170, 150),
        4048: (-2530, 350),
        4049: (-2530, 430),
        4050: (-2530, 510),
        4051: (-2530, 590),
        4052: (-2160, 380),
        4053: (-1820, 350),
        4054: (-1820, 480),
        4055: (-1820, 610),
        4056: (-2160, 650),
        2845: (-2550, -300),
        2860: (-2170, -260),
        2859: (-2170, -180),
        4129: (-1810, 20),
        4130: (-1810, 150),
        4008: (-1620, -820),
        4009: (-1270, -880),
        374: (-1600, -600),
        373: (-1600, -520),
        1795: (-1600, -420),
        280: (-1260, -450),
        3354: (-1600, -180),
        3349: (-1630, 860),
        3350: (-1630, 1190),
        3353: (-1630, 1520),
        3362: (-980, 980),
        3364: (-980, 1310),
        3365: (-980, 1640),
        3348: (-980, 1120),
        4010: (-780, -900),
        4011: (-780, -820),
        4012: (-780, -740),
        4001: (-820, -620),
        4002: (-820, -430),
        4005: (-820, -20),
        4003: (-420, -620),
        4006: (-420, -20),
        4004: (-20, -620),
        4007: (-20, -20),
        4013: (260, -880),
        4014: (260, -780),
        4015: (580, -830),
        4016: (260, -380),
        4017: (620, -380),
        3272: (980, -380),
        4018: (980, -160),
        3076: (1400, -900),
        3071: (1400, -820),
        3091: (1400, -740),
        3087: (1400, -660),
        3359: (1400, -580),
        3083: (1400, -500),
        4030: (1040, -980),
        4042: (1040, -700),
        3249: (1710, -900),
        3262: (1710, -620),
        3287: (1710, -340),
        3286: (2050, -230),
        3284: (2050, -340),
        3288: (2390, -230),
        3280: (2740, -340),
        3228: (1710, -80),
        4123: (2050, 300),
        3261: (2050, -80),
        3294: (2050, 220),
        3295: (2390, 220),
        3292: (2740, 320),
        3255: (2740, -60),
        3258: (3090, 220),
        3257: (3090, 0),
        3253: (3440, -140),
        3268: (3790, -140),
        3254: (3790, -10),
        3252: (4140, -20),
        4120: (4140, 180),
        4124: (4470, 180),
        4021: (4470, -560),
        4022: (4470, -470),
        4126: (4470, -180),
        4023: (4800, -560),
        4125: (5130, -360),
        4127: (5130, -220),
        4131: (5130, -80),
        4132: (5130, 60),
        4128: (5130, 200),
        4020: (5480, -620),
        4060: (6120, -720),
        4061: (6120, -640),
        4062: (6120, -560),
        4063: (6450, -720),
        4064: (7120, -620),
        4065: (6790, -720),
        4066: (6790, -590),
        4067: (6790, -460),
        4068: (6450, -420),
        4031: (-1630, 770),
        4032: (-1300, 880),
        4033: (-1300, 980),
        4035: (-1300, 1210),
        4036: (-1300, 1310),
        4038: (-1300, 1540),
        4039: (-1300, 1640),
        4043: (-620, 1120),
        4044: (-620, 1250),
        4045: (-620, 1380),
        4046: (-620, 1510),
        4047: (2180, -900),
    }
    for node_id, pos in positions.items():
        node = _find_node(workflow, node_id)
        node["pos"] = [pos[0], pos[1]]

    _find_node(workflow, 4009)["size"] = [400, 320]
    _find_node(workflow, 4030)["size"] = [300, 210]
    _find_node(workflow, 4042)["size"] = [320, 220]
    _find_node(workflow, 4052)["size"] = [320, 220]
    _find_node(workflow, 3348)["size"] = [320, 140]
    for node_id in (3349, 3350, 3353):
        _find_node(workflow, node_id)["size"] = [300, 250]
    for node_id in (280, 3362, 3364, 3365):
        _find_node(workflow, node_id)["size"] = [220, 60]
    for node_id in (4032, 4033, 4035, 4036, 4038, 4039):
        _find_node(workflow, node_id)["size"] = [280, 58]
    _find_node(workflow, 4056)["size"] = [340, 140]
    _find_node(workflow, 4046)["size"] = [320, 140]
    _find_node(workflow, 4047)["size"] = [420, 180]
    _find_node(workflow, 4063)["size"] = [320, 200]
    _find_node(workflow, 4068)["size"] = [340, 140]

    workflow["groups"] = [
        _group(
            group_id=201,
            title="MODELOS WAN",
            bounding=[-3260, -980, 600, 1430],
            color="#43536b",
        ),
        _group(
            group_id=202,
            title="ENTRADA VIDEO Y SEGMENTACION",
            bounding=[-2590, -980, 1150, 1810],
            color="#6b6650",
        ),
        _group(
            group_id=203,
            title="FRAME INICIAL Y REFERENCIAS",
            bounding=[-1670, -980, 900, 1730],
            color="#56774f",
        ),
        _group(
            group_id=209,
            title="IDENTIDAD COLOR Y ENTIDADES",
            bounding=[-1670, 720, 1380, 1170],
            color="#7a5b44",
        ),
        _group(
            group_id=204,
            title="PREPROCESS CONTROLES",
            bounding=[-900, -980, 980, 1330],
            color="#6d4f7c",
        ),
        _group(
            group_id=205,
            title="SELECCION DE CONTROL",
            bounding=[220, -980, 1140, 760],
            color="#6a5a3e",
        ),
        _group(
            group_id=206,
            title="RENDER GENERAL",
            bounding=[1000, -980, 3560, 1530],
            color="#a1309b",
        ),
        _group(
            group_id=207,
            title="INTERPOLACION FPS",
            bounding=[4440, -980, 1180, 980],
            color="#507a73",
        ),
        _group(
            group_id=208,
            title="MEJORA FINAL Y SALIDA",
            bounding=[5440, -980, 2100, 980],
            color="#3f7284",
        ),
    ]


def _group(
    *,
    group_id: int,
    title: str,
    bounding: list[float],
    color: str,
) -> dict[str, Any]:
    return {
        "id": group_id,
        "title": title,
        "bounding": bounding,
        "color": color,
        "font_size": 24,
        "flags": {},
    }


def _wire_general_video_v1(workflow: dict[str, Any]) -> None:
    # segment selection stays visible before preprocess and can bypass cleanly.
    _add_link(workflow, 265, 0, 4052, 0, "IMAGE")
    _add_link(workflow, 2607, 0, 4052, 1, "FLOAT")
    _add_link(workflow, 4048, 0, 4052, 2, "BOOLEAN")
    _add_link(workflow, 4049, 0, 4052, 3, "INT")
    _add_link(workflow, 4050, 0, 4052, 4, "INT")
    _add_link(workflow, 4051, 0, 4052, 5, "INT")
    _add_link(workflow, 4052, 1, 4053, 0, "BOOLEAN")
    _add_link(workflow, 4052, 2, 4054, 0, "INT")
    _add_link(workflow, 4052, 5, 4055, 0, "INT")
    _add_link(workflow, 4052, 6, 4056, 0, "STRING")

    # preprocess from the selected segment or from the full batch if bypassed.
    _add_link(workflow, 4001, 0, 4002, 0, "DAMODEL")
    for target_id, target_slot in ((4002, 1), (4003, 0), (4004, 0), (4008, 0)):
        _add_link(workflow, 4052, 0, target_id, target_slot, "IMAGE")

    # persist the generated controls
    _add_link(workflow, 4002, 0, 4005, 0, "IMAGE")
    _add_link(workflow, 4003, 0, 4006, 0, "IMAGE")
    _add_link(workflow, 4004, 0, 4007, 0, "IMAGE")
    for target_id in (4005, 4006, 4007):
        _add_link(workflow, 3083, 0, target_id, 4, "FLOAT")

    # first frame preview and references
    _add_link(workflow, 4008, 0, 4009, 0, "IMAGE")
    _add_link(workflow, 4008, 0, 1795, 0, "IMAGE")
    _add_link(workflow, 4008, 0, 280, 0, "IMAGE")
    _add_link(workflow, 280, 0, 3348, 0, "IMAGE")
    _add_link(workflow, 3348, 0, 3354, 0, "IMAGE")

    # base prompt plus optional identity-layer prompt reinforcement.
    _add_link(workflow, 4030, 0, 4042, 0, "STRING")
    _add_link(workflow, 4031, 0, 4042, 1, "BOOLEAN")
    _add_link(workflow, 3287, 0, 4042, 2, "INT")
    _add_link(workflow, 4032, 0, 4042, 3, "STRING")
    _add_link(workflow, 4033, 0, 4042, 4, "STRING")
    _add_link(workflow, 4035, 0, 4042, 5, "STRING")
    _add_link(workflow, 4036, 0, 4042, 6, "STRING")
    _add_link(workflow, 4038, 0, 4042, 7, "STRING")
    _add_link(workflow, 4039, 0, 4042, 8, "STRING")
    _add_link(workflow, 4042, 0, 3249, 1, "STRING")
    _add_link(workflow, 4042, 0, 4047, 0, "STRING")
    _add_link(workflow, 4042, 1, 4043, 0, "BOOLEAN")
    _add_link(workflow, 4042, 2, 4044, 0, "INT")
    _add_link(workflow, 4042, 3, 4045, 0, "INT")
    _add_link(workflow, 4042, 4, 4046, 0, "STRING")

    # boolean control logic
    _add_link(workflow, 4010, 0, 4013, 0, "BOOLEAN")
    _add_link(workflow, 4012, 0, 4013, 1, "BOOLEAN")
    _add_link(workflow, 4010, 0, 4014, 0, "BOOLEAN")
    _add_link(workflow, 4012, 0, 4014, 1, "BOOLEAN")
    _add_link(workflow, 4011, 0, 4015, 0, "BOOLEAN")
    _add_link(workflow, 4013, 0, 4015, 1, "BOOLEAN")

    # false -> pose, true -> depth
    _add_link(workflow, 4004, 0, 4016, 0, "IMAGE")
    _add_link(workflow, 4002, 0, 4016, 1, "IMAGE")
    _add_link(workflow, 4012, 0, 4016, 2, "BOOLEAN")

    # false -> depth/pose, true -> borders
    _add_link(workflow, 4016, 0, 4017, 0, "IMAGE")
    _add_link(workflow, 4003, 0, 4017, 1, "IMAGE")
    _add_link(workflow, 4010, 0, 4017, 2, "BOOLEAN")

    # blend borders + depth when both are active
    _add_link(workflow, 4017, 0, 3272, 0, "IMAGE")
    _add_link(workflow, 4002, 0, 3272, 1, "IMAGE")
    _add_link(workflow, 4014, 0, 3272, 2, "BOOLEAN")

    # optional pose blend over the selected control stream
    _add_link(workflow, 3272, 0, 4018, 0, "IMAGE")
    _add_link(workflow, 4004, 0, 4018, 1, "IMAGE")
    _add_link(workflow, 4015, 0, 4018, 2, "BOOLEAN")

    # selected control goes into the expanded render core.
    _add_link(workflow, 4018, 0, 3228, 0, "IMAGE")
    _add_link(workflow, 3071, 0, 3249, 0, "CLIP")
    _add_link(workflow, 3071, 0, 3262, 0, "CLIP")
    _add_link(workflow, 3076, 0, 3255, 0, "MODEL")
    _add_link(workflow, 3091, 0, 3255, 3, "VAE")
    _add_link(workflow, 3091, 0, 3252, 1, "VAE")
    _add_link(workflow, 3091, 0, 3294, 1, "VAE")
    _add_link(workflow, 3087, 0, 3280, 0, "IMAGE")
    _add_link(workflow, 3087, 0, 3255, 7, "IMAGE")
    _add_link(workflow, 3359, 0, 3287, 0, "IMAGE")
    _add_link(workflow, 3359, 0, 3255, 8, "IMAGE")

    # start image selector that stays visible in the canvas.
    _add_link(workflow, 3287, 0, 3284, 0, "INT")
    _add_link(workflow, 3286, 0, 3284, 1, "INT")
    _add_link(workflow, 3284, 0, 3280, 2, "BOOLEAN")
    _add_link(workflow, 3288, 0, 3280, 1, "*")

    # control stream diagnostics and VACE preparation.
    _add_link(workflow, 3228, 0, 3261, 2, "IMAGE")
    _add_link(workflow, 3228, 0, 3294, 0, "IMAGE")
    _add_link(workflow, 3228, 1, 3255, 9, "INT")
    _add_link(workflow, 3228, 2, 3255, 10, "INT")
    _add_link(workflow, 3228, 3, 3255, 11, "INT")
    _add_link(workflow, 3228, 3, 3261, 4, "INT")
    _add_link(workflow, 3280, 0, 3261, 0, "IMAGE")

    # prompt, reference latent, and sampler chain.
    _add_link(workflow, 3249, 0, 3295, 0, "CONDITIONING")
    _add_link(workflow, 3294, 0, 3295, 1, "LATENT")
    _add_link(workflow, 3295, 0, 3255, 1, "CONDITIONING")
    _add_link(workflow, 3262, 0, 3255, 2, "CONDITIONING")
    _add_link(workflow, 3261, 0, 3255, 5, "IMAGE")
    _add_link(workflow, 3255, 0, 3257, 0, "MODEL")
    _add_link(workflow, 3255, 2, 3258, 0, "CONDITIONING")
    _add_link(workflow, 3255, 3, 3258, 1, "CONDITIONING")
    _add_link(workflow, 3255, 1, 3253, 1, "CONDITIONING")
    _add_link(workflow, 3255, 4, 3253, 3, "LATENT")
    _add_link(workflow, 3255, 5, 3268, 1, "INT")
    _add_link(workflow, 3258, 0, 3257, 1, "CONDITIONING")
    _add_link(workflow, 3258, 0, 3253, 2, "CONDITIONING")
    _add_link(workflow, 3257, 0, 3253, 0, "MODEL")
    _add_link(workflow, 3253, 0, 3268, 0, "LATENT")
    _add_link(workflow, 3268, 0, 3254, 0, "LATENT")
    _add_link(workflow, 3254, 0, 3252, 0, "LATENT")

    # optional FPS interpolation lives after the main render and before output.
    _add_link(workflow, 3252, 0, 4023, 0, "IMAGE")
    _add_link(workflow, 3083, 0, 4023, 1, "FLOAT")
    _add_link(workflow, 4022, 0, 4023, 2, "FLOAT")
    _add_link(workflow, 4021, 0, 4023, 3, "BOOLEAN")
    _add_link(workflow, 4023, 0, 4020, 0, "IMAGE")
    _add_link(workflow, 4023, 1, 4020, 4, "FLOAT")

    # final Full HD stage keeps the post-FPS path visible instead of hiding it.
    _add_link(workflow, 4023, 0, 4063, 0, "IMAGE")
    _add_link(workflow, 4060, 0, 4063, 1, "BOOLEAN")
    _add_link(workflow, 4061, 0, 4063, 2, "INT")
    _add_link(workflow, 4062, 0, 4063, 3, "INT")
    _add_link(workflow, 4063, 0, 4064, 0, "IMAGE")
    _add_link(workflow, 4023, 1, 4064, 4, "FLOAT")
    _add_link(workflow, 4063, 1, 4065, 0, "BOOLEAN")
    _add_link(workflow, 4063, 2, 4066, 0, "INT")
    _add_link(workflow, 4063, 3, 4067, 0, "INT")
    _add_link(workflow, 4063, 4, 4068, 0, "STRING")

    # visible diagnostics for frame counts and FPS decisions.
    _add_link(workflow, 2607, 0, 4121, 0, "FLOAT")
    _add_link(workflow, 2607, 6, 4122, 0, "INT")
    _add_link(workflow, 2607, 8, 4129, 0, "INT")
    _add_link(workflow, 2607, 9, 4130, 0, "INT")
    _add_link(workflow, 3228, 3, 4123, 0, "INT")
    _add_link(workflow, 3252, 0, 4120, 0, "IMAGE")
    _add_link(workflow, 4120, 3, 4124, 0, "INT")
    _add_link(workflow, 4023, 0, 4126, 0, "IMAGE")
    _add_link(workflow, 4126, 3, 4125, 0, "INT")
    _add_link(workflow, 4023, 1, 4127, 0, "FLOAT")
    _add_link(workflow, 4023, 2, 4131, 0, "BOOLEAN")
    _add_link(workflow, 4023, 3, 4132, 0, "INT")
    _add_link(workflow, 4023, 4, 4128, 0, "STRING")


def _add_link(
    workflow: dict[str, Any],
    origin_id: int,
    origin_slot: int,
    target_id: int,
    target_slot: int,
    link_type: str,
) -> None:
    next_link_id = max(int(raw_link[0]) for raw_link in workflow.get("links", [])) + 1
    workflow.setdefault("links", []).append(
        [next_link_id, origin_id, origin_slot, target_id, target_slot, link_type]
    )


def _set_link(
    workflow: dict[str, Any],
    *,
    origin_id: int,
    origin_slot: int,
    target_id: int,
    target_slot: int,
    link_type: str,
) -> None:
    _remove_link_to_target(workflow, target_id, target_slot)
    _add_link(
        workflow,
        origin_id=origin_id,
        origin_slot=origin_slot,
        target_id=target_id,
        target_slot=target_slot,
        link_type=link_type,
    )


def _sync_top_level_links(workflow: dict[str, Any]) -> None:
    nodes_by_id = {int(node["id"]): node for node in workflow.get("nodes", [])}
    for node in workflow.get("nodes", []):
        for input_entry in node.get("inputs", []):
            if "link" in input_entry:
                input_entry["link"] = None
        for output_entry in node.get("outputs", []):
            if "links" in output_entry:
                output_entry["links"] = []

    for raw_link in workflow.get("links", []):
        link_id, origin_id, origin_slot, target_id, target_slot, _ = raw_link
        origin_node = nodes_by_id.get(int(origin_id))
        target_node = nodes_by_id.get(int(target_id))
        if origin_node is not None and int(origin_slot) < len(origin_node.get("outputs", [])):
            origin_node["outputs"][int(origin_slot)]["links"].append(link_id)
        if target_node is not None and int(target_slot) < len(target_node.get("inputs", [])):
            target_node["inputs"][int(target_slot)]["link"] = link_id

    for node in workflow.get("nodes", []):
        for output_entry in node.get("outputs", []):
            if output_entry.get("links") == []:
                output_entry["links"] = None


def _expand_all_nodes_for_debug(workflow: dict[str, Any]) -> None:
    for node in workflow.get("nodes", []):
        flags = dict(node.get("flags", {}))
        flags["collapsed"] = False
        node["flags"] = flags


def _refresh_workflow_metadata(workflow: dict[str, Any]) -> None:
    workflow["last_node_id"] = max(int(node["id"]) for node in workflow.get("nodes", []))
    workflow["last_link_id"] = max(int(raw_link[0]) for raw_link in workflow.get("links", []))


if __name__ == "__main__":
    raise SystemExit(main())

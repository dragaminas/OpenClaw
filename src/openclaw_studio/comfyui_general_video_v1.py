from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


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
DEFAULT_USE_BORDERS = True
DEFAULT_USE_POSE = True
DEFAULT_USE_DEPTH = True

LEGACY_NODE_IDS_TO_REMOVE = {
    282,
    3001,
    3002,
    3088,
    3345,
    3348,
    3349,
    3350,
    3353,
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
    _configure_render_core_defaults(base_workflow)

    _remove_nodes(base_workflow, LEGACY_NODE_IDS_TO_REMOVE)
    _clear_inputs(base_workflow, ((1795, 0), (3354, 0), (3272, 0), (3272, 1)))

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
    _sync_top_level_links(base_workflow)
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
    use_borders: bool = DEFAULT_USE_BORDERS,
    use_pose: bool = DEFAULT_USE_POSE,
    use_depth: bool = DEFAULT_USE_DEPTH,
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
    _find_node(workflow, 4020)["widgets_values"]["filename_prefix"] = (
        f"{output_prefix_root}/render"
    )
    _set_video_combine_frame_rate(workflow, 4020, render_frame_rate)
    _find_node(workflow, 4009)["widgets_values"][0] = (
        f"{output_prefix_root}/first_frame"
    )
    set_general_video_v1_controls(
        workflow,
        use_borders=use_borders,
        use_pose=use_pose,
        use_depth=use_depth,
    )

    render_subgraph = _find_subgraph_definition(
        workflow, "c475d739-ec74-430f-a7bd-aab0fdd85070"
    )
    _find_subgraph_node(render_subgraph, 3268)["widgets_values"][0] = 0
    if fast_validation:
        sampler_node = _find_subgraph_node(render_subgraph, 3253)
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
    _find_node(workflow, 3228)["title"] = "NUCLEO RENDER GENERAL"
    _find_node(workflow, 3228)["widgets_values"][0] = DEFAULT_PROMPT
    _find_node(workflow, 3333)["widgets_values"][0] = DEFAULT_CLIP_NAME
    _find_node(workflow, 2607)["title"] = "INFO VIDEO"
    _find_node(workflow, 2845)["title"] = "SELECCION TAMANO"
    _find_node(workflow, 3272)["title"] = "MEZCLA BORDES + PROFUNDIDAD"
    _find_node(workflow, 280)["title"] = "AJUSTA START IMAGE"
    _find_node(workflow, 3362)["title"] = "AJUSTA REFERENCIA 1"
    _find_node(workflow, 3364)["title"] = "AJUSTA REFERENCIA 2"
    _find_node(workflow, 3365)["title"] = "AJUSTA REFERENCIA 3"
    render_subgraph = _find_subgraph_definition(
        workflow, "c475d739-ec74-430f-a7bd-aab0fdd85070"
    )
    _find_subgraph_node(render_subgraph, 3268)["widgets_values"][0] = 0
    _find_subgraph_node(render_subgraph, 3253)["widgets_values"][2] = (
        DEFAULT_OPERATIONAL_RENDER_STEPS
    )


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
    logic_properties = {
        "cnr_id": "ComfyUI-Impact-Pack",
        "ver": "8.21.2",
        "Node name for S&R": "ImpactLogicalOperators",
    }
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
            pos=(920, -210),
            title="RENDER FINAL",
            widgets_overrides=_video_combine_widgets(f"{DEFAULT_OUTPUT_PREFIX_ROOT}/render"),
        )
    )
    for node_id in (4005, 4006, 4007, 4020):
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
        3326: (-2990, -800),
        3327: (-2990, -670),
        3328: (-2990, -540),
        3329: (-2990, -410),
        3332: (-2990, -250),
        3333: (-2990, -120),
        3335: (-2990, 20),
        3334: (-2990, 150),
        3336: (-2990, 240),
        265: (-2370, -760),
        2607: (-1980, -760),
        2687: (-1980, -510),
        2845: (-2370, -210),
        2860: (-1980, -210),
        2859: (-1980, -150),
        4008: (-1700, -760),
        4009: (-1380, -820),
        374: (-1710, -600),
        373: (-1710, -540),
        1795: (-1710, -460),
        280: (-1400, -480),
        3354: (-1710, -200),
        3362: (-1400, -220),
        3364: (-1400, 120),
        3365: (-1400, 460),
        4010: (-820, -880),
        4011: (-820, -810),
        4012: (-820, -740),
        4001: (-820, -620),
        4002: (-820, -450),
        4005: (-820, -40),
        4003: (-430, -620),
        4006: (-430, -40),
        4004: (-40, -620),
        4007: (-40, -40),
        4013: (-430, -860),
        4014: (-430, -770),
        4015: (-40, -860),
        4016: (360, -720),
        4017: (720, -720),
        3272: (1080, -720),
        4018: (1080, -520),
        3076: (1430, -780),
        3071: (1430, -720),
        3091: (1430, -660),
        3087: (1430, -600),
        3359: (1430, -540),
        3083: (1430, -480),
        3228: (1680, -800),
        4020: (2140, -260),
    }
    for node_id, pos in positions.items():
        node = _find_node(workflow, node_id)
        node["pos"] = [pos[0], pos[1]]

    _find_node(workflow, 4009)["size"] = [400, 320]
    for node_id in (280, 3362, 3364, 3365):
        _find_node(workflow, node_id)["size"] = [220, 60]

    workflow["groups"] = [
        _group(
            group_id=201,
            title="MODELOS WAN",
            bounding=[-3040, -930, 560, 1290],
            color="#43536b",
        ),
        _group(
            group_id=202,
            title="ENTRADA VIDEO",
            bounding=[-2450, -930, 640, 1290],
            color="#6b6650",
        ),
        _group(
            group_id=203,
            title="FRAME INICIAL Y REFERENCIAS",
            bounding=[-1850, -930, 850, 1680],
            color="#56774f",
        ),
        _group(
            group_id=204,
            title="PREPROCESS CONTROLES",
            bounding=[-900, -930, 980, 1290],
            color="#6d4f7c",
        ),
        _group(
            group_id=205,
            title="SELECCION DE CONTROL",
            bounding=[320, -930, 1120, 620],
            color="#6a5a3e",
        ),
        _group(
            group_id=206,
            title="RENDER GENERAL",
            bounding=[1560, -930, 620, 760],
            color="#a1309b",
        ),
        _group(
            group_id=207,
            title="SALIDA Y EVIDENCIA",
            bounding=[2100, -930, 560, 760],
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
    # preprocess from base video
    _add_link(workflow, 4001, 0, 4002, 0, "DAMODEL")
    for target_id, target_slot in ((4002, 1), (4003, 0), (4004, 0), (4008, 0)):
        _add_link(workflow, 265, 0, target_id, target_slot, "IMAGE")

    # persist the generated controls
    _add_link(workflow, 4002, 0, 4005, 0, "IMAGE")
    _add_link(workflow, 4003, 0, 4006, 0, "IMAGE")
    _add_link(workflow, 4004, 0, 4007, 0, "IMAGE")
    for target_id in (4005, 4006, 4007, 4020):
        _add_link(workflow, 3083, 0, target_id, 4, "FLOAT")

    # first frame preview and references
    _add_link(workflow, 4008, 0, 4009, 0, "IMAGE")
    _add_link(workflow, 4008, 0, 1795, 0, "IMAGE")
    _add_link(workflow, 4008, 0, 3354, 0, "IMAGE")

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

    # selected control goes straight into the render core
    _add_link(workflow, 4018, 0, 3228, 5, "IMAGE")
    _add_link(workflow, 3228, 0, 4020, 0, "IMAGE")


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


if __name__ == "__main__":
    raise SystemExit(main())

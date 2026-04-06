from __future__ import annotations

import unittest
from pathlib import Path

from openclaw_studio.comfyui_general_video_v1 import (
    derive_general_video_v1_workflow,
    patch_general_video_v1_runtime,
    set_general_video_v1_controls,
)
from openclaw_studio.comfyui_general_video_v1_validation import parse_controls


def get_node(workflow: dict, node_id: int) -> dict:
    for node in workflow["nodes"]:
        if int(node["id"]) == node_id:
            return node
    raise KeyError(node_id)


class GeneralVideoV1WorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]

    def test_derivation_injects_preview_control_and_render_nodes(self) -> None:
        workflow = derive_general_video_v1_workflow(self.repo_root)
        node_ids = {int(node["id"]) for node in workflow["nodes"]}

        self.assertIn(4008, node_ids)
        self.assertIn(4009, node_ids)
        self.assertIn(4020, node_ids)
        self.assertNotIn(282, node_ids)
        self.assertEqual(get_node(workflow, 1066)["title"], "OPENCLAW GENERAL VIDEO RENDER V1")

    def test_runtime_patch_updates_paths_and_control_flags(self) -> None:
        workflow = derive_general_video_v1_workflow(self.repo_root)

        patch_general_video_v1_runtime(
            workflow,
            input_video_rel="blender/test.mp4",
            output_prefix_root="openclaw/test/general-video-v1",
            frame_load_cap=3,
            custom_width=640,
            render_frame_rate=15,
            use_borders=True,
            use_pose=False,
            use_depth=True,
            fast_validation=True,
        )

        self.assertEqual(get_node(workflow, 265)["widgets_values"]["video"], "blender/test.mp4")
        self.assertEqual(get_node(workflow, 265)["widgets_values"]["custom_width"], 640)
        self.assertEqual(get_node(workflow, 265)["widgets_values"]["custom_height"], 0)
        self.assertEqual(get_node(workflow, 265)["widgets_values"]["frame_load_cap"], 3)
        self.assertEqual(
            get_node(workflow, 4020)["widgets_values"]["filename_prefix"],
            "openclaw/test/general-video-v1/render",
        )
        self.assertTrue(get_node(workflow, 4010)["widgets_values"][0])
        self.assertFalse(get_node(workflow, 4011)["widgets_values"][0])
        self.assertTrue(get_node(workflow, 4012)["widgets_values"][0])

    def test_layout_keeps_main_blocks_separated_and_grouped(self) -> None:
        workflow = derive_general_video_v1_workflow(self.repo_root)

        group_titles = [group["title"] for group in workflow["groups"]]
        self.assertEqual(
            group_titles,
            [
                "MODELOS WAN",
                "ENTRADA VIDEO",
                "FRAME INICIAL Y REFERENCIAS",
                "PREPROCESS CONTROLES",
                "SELECCION DE CONTROL",
                "RENDER GENERAL",
                "SALIDA Y EVIDENCIA",
            ],
        )

        key_nodes = {
            265,
            2607,
            2687,
            2845,
            2859,
            2860,
            2375,
            4008,
            4009,
            374,
            373,
            1795,
            280,
            3354,
            3362,
            3364,
            3365,
            4010,
            4011,
            4012,
            4001,
            4002,
            4003,
            4004,
            4005,
            4006,
            4007,
            4013,
            4014,
            4015,
            4016,
            4017,
            3272,
            4018,
            3076,
            3071,
            3091,
            3087,
            3359,
            3083,
            3228,
            4020,
            3326,
            3327,
            3328,
            3329,
            3332,
            3333,
            3335,
            3334,
            3336,
        }

        boxes = []
        for node_id in key_nodes:
            node = get_node(workflow, node_id)
            pos = node.get("pos") or [0, 0]
            size = node.get("size") or [140, 80]
            boxes.append(
                (
                    node_id,
                    pos[0],
                    pos[1],
                    size[0],
                    size[1],
                )
            )

        for index, left in enumerate(boxes):
            for right in boxes[index + 1 :]:
                self.assertFalse(
                    _overlap(left, right),
                    msg=f"Nodes {left[0]} and {right[0]} should not overlap in the didactic layout.",
                )

    def test_control_setter_rejects_all_controls_disabled(self) -> None:
        workflow = derive_general_video_v1_workflow(self.repo_root)

        with self.assertRaises(ValueError):
            set_general_video_v1_controls(
                workflow,
                use_borders=False,
                use_pose=False,
                use_depth=False,
            )

    def test_parse_controls_accepts_spanish_and_english_aliases(self) -> None:
        self.assertEqual(parse_controls("bordes,pose,profundidad"), (True, True, True))
        self.assertEqual(parse_controls("outline,depth"), (True, False, True))


if __name__ == "__main__":
    unittest.main()


def _overlap(left: tuple[int, float, float, float, float], right: tuple[int, float, float, float, float]) -> bool:
    _, left_x, left_y, left_w, left_h = left
    _, right_x, right_y, right_w, right_h = right
    return (
        left_x < right_x + right_w
        and left_x + left_w > right_x
        and left_y < right_y + right_h
        and left_y + left_h > right_y
    )

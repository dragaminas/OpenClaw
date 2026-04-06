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

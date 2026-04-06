from __future__ import annotations

import unittest
from pathlib import Path

from openclaw_studio.comfyui_general_video_v1 import (
    RENDER_CORE_SUBGRAPH_ID,
    derive_general_video_v1_workflow,
    patch_general_video_v1_runtime,
    set_general_video_v1_controls,
)
from openclaw_studio.comfyui_general_video_v1_validation import parse_controls
from openclaw_studio.comfyui_openclaw_workflow_nodes import (
    plan_identity_anchor_prompt,
)


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
        node_types = {node["type"] for node in workflow["nodes"]}

        self.assertIn(3348, node_ids)
        self.assertIn(3349, node_ids)
        self.assertIn(3350, node_ids)
        self.assertIn(3353, node_ids)
        self.assertIn(4030, node_ids)
        self.assertIn(4031, node_ids)
        self.assertIn(4042, node_ids)
        self.assertIn(4047, node_ids)
        self.assertIn(4048, node_ids)
        self.assertIn(4052, node_ids)
        self.assertIn(4063, node_ids)
        self.assertIn(4064, node_ids)
        self.assertIn(4008, node_ids)
        self.assertIn(4009, node_ids)
        self.assertIn(4020, node_ids)
        self.assertIn(4023, node_ids)
        self.assertIn(3253, node_ids)
        self.assertIn(4128, node_ids)
        self.assertNotIn(282, node_ids)
        self.assertNotIn(RENDER_CORE_SUBGRAPH_ID, node_types)
        self.assertFalse(
            any(
                subgraph["id"] == RENDER_CORE_SUBGRAPH_ID
                for subgraph in workflow.get("definitions", {}).get("subgraphs", [])
            )
        )
        self.assertEqual(get_node(workflow, 1066)["title"], "OPENCLAW GENERAL VIDEO RENDER V1")
        self.assertEqual(get_node(workflow, 265)["widgets_values"]["frame_load_cap"], 0)
        self.assertFalse(get_node(workflow, 4021)["widgets_values"][0])
        self.assertEqual(get_node(workflow, 4022)["widgets_values"][0], 24.0)
        self.assertEqual(
            get_node(workflow, 4020)["widgets_values"]["frame_rate"],
            24,
        )
        self.assertEqual(get_node(workflow, 3253)["widgets_values"][2], 8)
        self.assertEqual(get_node(workflow, 3249)["title"], "ENCODEA PROMPT FINAL")
        self.assertEqual(get_node(workflow, 3228)["title"], "INFO CONTROL AL RENDER")
        self.assertEqual(get_node(workflow, 4128)["type"], "Display Any (rgthree)")
        self.assertEqual(get_node(workflow, 4052)["type"], "OpenClawSegmentSelector")
        self.assertEqual(get_node(workflow, 4042)["type"], "OpenClawIdentityPromptBuilder")
        self.assertEqual(get_node(workflow, 4047)["type"], "Display Any (rgthree)")
        self.assertEqual(get_node(workflow, 4063)["type"], "OpenClawFinalVideoResize")
        self.assertEqual(get_node(workflow, 3348)["type"], "ImageBatchMultiple+")
        self.assertIsNotNone(get_node(workflow, 3348)["inputs"][0]["link"])
        self.assertIsNone(get_node(workflow, 3348)["inputs"][1]["link"])
        self.assertIsNotNone(get_node(workflow, 4052)["inputs"][0]["link"])
        self.assertIsNotNone(get_node(workflow, 3249)["inputs"][1]["link"])
        self.assertIsNotNone(get_node(workflow, 4047)["inputs"][0]["link"])

        for node_id in (4005, 4006, 4007, 4020, 4064):
            frame_rate_input = get_node(workflow, node_id)["inputs"][4]
            self.assertEqual(frame_rate_input["name"], "frame_rate")
            self.assertIsNotNone(frame_rate_input["link"])

    def test_runtime_patch_updates_paths_and_control_flags(self) -> None:
        workflow = derive_general_video_v1_workflow(self.repo_root)

        patch_general_video_v1_runtime(
            workflow,
            input_video_rel="blender/test.mp4",
            output_prefix_root="openclaw/test/general-video-v1",
            frame_load_cap=3,
            custom_width=640,
            render_frame_rate=15,
            enable_fps_interpolation=True,
            target_fps=18.0,
            use_borders=True,
            use_pose=False,
            use_depth=True,
            enable_color_identity=True,
            identity_anchors=[
                {
                    "color": "rojo",
                    "entity": "soldado protagonista",
                    "prompt_anchor": "sujeto a la izquierda",
                    "reference_image_relpath": "references/identity_red.png",
                },
                {
                    "color": "azul",
                    "entity": "dron enemigo",
                },
            ],
            enable_segmentation=True,
            segment_length_frames=17,
            segment_overlap_frames=3,
            segment_index=2,
            enable_final_upscale=True,
            final_width=1920,
            final_height=1080,
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
        self.assertEqual(get_node(workflow, 4020)["widgets_values"]["frame_rate"], 15)
        self.assertIsNone(get_node(workflow, 4020)["inputs"][4]["link"])
        self.assertEqual(
            get_node(workflow, 4064)["widgets_values"]["filename_prefix"],
            "openclaw/test/general-video-v1/final_full_hd",
        )
        self.assertEqual(get_node(workflow, 4064)["widgets_values"]["frame_rate"], 15)
        self.assertIsNone(get_node(workflow, 4064)["inputs"][4]["link"])
        self.assertTrue(get_node(workflow, 4021)["widgets_values"][0])
        self.assertEqual(get_node(workflow, 4022)["widgets_values"][0], 18.0)
        self.assertEqual(get_node(workflow, 3253)["widgets_values"][2], 1)
        self.assertTrue(get_node(workflow, 4048)["widgets_values"][0])
        self.assertEqual(get_node(workflow, 4049)["widgets_values"][0], 17)
        self.assertEqual(get_node(workflow, 4050)["widgets_values"][0], 3)
        self.assertEqual(get_node(workflow, 4051)["widgets_values"][0], 2)
        self.assertTrue(get_node(workflow, 4010)["widgets_values"][0])
        self.assertFalse(get_node(workflow, 4011)["widgets_values"][0])
        self.assertTrue(get_node(workflow, 4012)["widgets_values"][0])
        self.assertTrue(get_node(workflow, 4031)["widgets_values"][0])
        self.assertTrue(get_node(workflow, 4060)["widgets_values"][0])
        self.assertEqual(get_node(workflow, 4061)["widgets_values"][0], 1920)
        self.assertEqual(get_node(workflow, 4062)["widgets_values"][0], 1080)
        self.assertEqual(get_node(workflow, 4032)["widgets_values"][0], "rojo")
        self.assertEqual(
            get_node(workflow, 4033)["widgets_values"][0],
            "soldado protagonista | sujeto a la izquierda",
        )
        self.assertEqual(get_node(workflow, 4035)["widgets_values"][0], "azul")
        self.assertEqual(get_node(workflow, 4036)["widgets_values"][0], "dron enemigo")
        self.assertEqual(
            get_node(workflow, 3349)["widgets_values"][0],
            "references/identity_red.png",
        )
        self.assertIsNotNone(get_node(workflow, 3348)["inputs"][1]["link"])
        self.assertIsNone(get_node(workflow, 3348)["inputs"][2]["link"])

    def test_layout_keeps_main_blocks_separated_and_grouped(self) -> None:
        workflow = derive_general_video_v1_workflow(self.repo_root)

        group_titles = [group["title"] for group in workflow["groups"]]
        self.assertEqual(
            group_titles,
            [
                "MODELOS WAN",
                "ENTRADA VIDEO Y SEGMENTACION",
                "FRAME INICIAL Y REFERENCIAS",
                "IDENTIDAD COLOR Y ENTIDADES",
                "PREPROCESS CONTROLES",
                "SELECCION DE CONTROL",
                "RENDER GENERAL",
                "INTERPOLACION FPS",
                "MEJORA FINAL Y SALIDA",
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
            3348,
            3349,
            3350,
            3353,
            3354,
            3362,
            3364,
            3365,
            4030,
            4031,
            4032,
            4033,
            4035,
            4036,
            4038,
            4039,
            4042,
            4043,
            4044,
            4045,
            4046,
            4047,
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
            3249,
            3262,
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
            4021,
            4022,
            4023,
            4020,
            4120,
            4121,
            4122,
            4048,
            4049,
            4050,
            4051,
            4052,
            4053,
            4054,
            4055,
            4056,
            4123,
            4124,
            4125,
            4126,
            4127,
            4128,
            4129,
            4130,
            4131,
            4132,
            4060,
            4061,
            4062,
            4063,
            4064,
            4065,
            4066,
            4067,
            4068,
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

    def test_identity_prompt_plan_summarizes_color_mapping_and_ref_count(self) -> None:
        plan = plan_identity_anchor_prompt(
            base_prompt="Plano cinematico con personaje estable.",
            enabled=True,
            total_ref_images=3,
            color_1="rojo",
            entity_1="soldado protagonista | sujeto a la izquierda",
            color_2="azul",
            entity_2="dron enemigo",
        )

        self.assertTrue(plan.enabled_requested)
        self.assertEqual(plan.identity_ref_count, 2)
        self.assertEqual(plan.mapping_count, 2)
        self.assertIn("rojo -> soldado protagonista | sujeto a la izquierda", plan.summary)
        self.assertIn("Use the attached reference images", plan.effective_prompt)


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

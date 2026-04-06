from __future__ import annotations

import unittest

from openclaw_studio.comfyui_openclaw_workflow_nodes import (
    plan_final_upscale,
    plan_fps_interpolation,
    plan_segment_selection,
    render_final_upscale_summary,
    render_fps_interpolation_summary,
    render_segment_selection_summary,
)


class OpenClawWorkflowNodeTests(unittest.TestCase):
    def test_plan_bypasses_when_disabled(self) -> None:
        plan = plan_fps_interpolation(
            source_frame_count=12,
            source_fps=12.0,
            target_fps=24.0,
            enabled=False,
        )

        self.assertFalse(plan.should_interpolate)
        self.assertEqual(plan.reason, "disabled")
        self.assertEqual(plan.output_fps, 12.0)
        self.assertEqual(plan.output_frame_count, 12)

    def test_plan_bypasses_when_target_matches_source(self) -> None:
        plan = plan_fps_interpolation(
            source_frame_count=12,
            source_fps=12.0,
            target_fps=12.0,
            enabled=True,
        )

        self.assertFalse(plan.should_interpolate)
        self.assertEqual(plan.reason, "target_matches_source")

    def test_plan_interpolates_for_integer_multiple_ratio(self) -> None:
        plan = plan_fps_interpolation(
            source_frame_count=12,
            source_fps=12.0,
            target_fps=24.0,
            enabled=True,
        )

        self.assertTrue(plan.should_interpolate)
        self.assertEqual(plan.output_fps, 24.0)
        self.assertEqual(plan.output_frame_count, 24)
        self.assertEqual(plan.inserted_frame_count, 12)

    def test_plan_interpolates_for_non_multiple_ratio(self) -> None:
        plan = plan_fps_interpolation(
            source_frame_count=12,
            source_fps=12.0,
            target_fps=20.0,
            enabled=True,
        )

        self.assertTrue(plan.should_interpolate)
        self.assertEqual(plan.output_frame_count, 20)
        self.assertEqual(plan.inserted_frame_count, 8)

    def test_summary_mentions_bypass_or_active_mode(self) -> None:
        bypass = plan_fps_interpolation(
            source_frame_count=2,
            source_fps=12.0,
            target_fps=12.0,
            enabled=True,
        )
        active = plan_fps_interpolation(
            source_frame_count=12,
            source_fps=12.0,
            target_fps=18.0,
            enabled=True,
        )

        self.assertIn("bypass", render_fps_interpolation_summary(bypass))
        self.assertIn("active", render_fps_interpolation_summary(active))
        self.assertIn("linear_blend", render_fps_interpolation_summary(active))

    def test_segment_selection_bypasses_for_short_clip(self) -> None:
        plan = plan_segment_selection(
            total_frame_count=3,
            source_fps=12.0,
            enabled=True,
            segment_length_frames=8,
            overlap_frames=1,
            segment_index=1,
        )

        self.assertFalse(plan.should_segment)
        self.assertEqual(plan.reason, "clip_within_single_segment")
        self.assertEqual(plan.selected_frame_count, 3)

    def test_segment_selection_generates_overlapping_windows(self) -> None:
        plan = plan_segment_selection(
            total_frame_count=10,
            source_fps=12.0,
            enabled=True,
            segment_length_frames=4,
            overlap_frames=1,
            segment_index=3,
        )

        self.assertTrue(plan.should_segment)
        self.assertEqual(plan.segment_count, 3)
        self.assertEqual(plan.segment_start_frame, 6)
        self.assertEqual(plan.segment_end_frame, 10)
        self.assertIn("current=3/3", render_segment_selection_summary(plan))

    def test_final_upscale_plans_fit_inside_target_box(self) -> None:
        plan = plan_final_upscale(
            source_width=256,
            source_height=144,
            target_width=1920,
            target_height=1080,
            enabled=True,
        )

        self.assertTrue(plan.should_resize)
        self.assertEqual(plan.output_width, 1920)
        self.assertEqual(plan.output_height, 1080)
        self.assertIn("active", render_final_upscale_summary(plan))

    def test_final_upscale_bypasses_when_disabled(self) -> None:
        plan = plan_final_upscale(
            source_width=512,
            source_height=512,
            target_width=1920,
            target_height=1080,
            enabled=False,
        )

        self.assertFalse(plan.should_resize)
        self.assertEqual(plan.reason, "disabled")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from openclaw_studio.comfyui_openclaw_workflow_nodes import (
    plan_fps_interpolation,
    render_fps_interpolation_summary,
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


if __name__ == "__main__":
    unittest.main()

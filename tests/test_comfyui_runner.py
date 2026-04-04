from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from openclaw_studio.runners import StartRunRequest
from openclaw_studio.runners.comfyui import ComfyUIRunner


class ComfyUIRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.repo_root = self.root / "repo"
        self.studio_dir = self.root / "Studio"
        self.comfyui_dir = self.root / "ComfyUI"
        self.repo_root.mkdir(parents=True)
        self.studio_dir.mkdir(parents=True)
        self.comfyui_dir.mkdir(parents=True)
        self.runner = ComfyUIRunner(
            repo_root=self.repo_root,
            studio_dir=self.studio_dir,
            comfyui_dir=self.comfyui_dir,
            comfyui_host="127.0.0.1",
            comfyui_port=8188,
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_legacy_summary_is_exposed_via_runner_status(self) -> None:
        run_id = "smoke-light-5"
        manifests_dir = (
            self.studio_dir / "Validation" / "comfyui" / "smoke" / run_id / "manifests"
        )
        evidence_dir = (
            self.studio_dir / "Validation" / "comfyui" / "smoke" / run_id / "evidence"
        )
        manifests_dir.mkdir(parents=True, exist_ok=True)
        evidence_dir.mkdir(parents=True, exist_ok=True)
        (evidence_dir / "summary.md").write_text("# evidence\n", encoding="utf-8")

        summary = {
            "run_id": run_id,
            "gate_pass": True,
            "results": [
                {
                    "case_id": "SMK-IMG-02-01",
                    "status": "pass",
                    "blocking": True,
                    "message": "ok",
                    "output_paths": ["/tmp/render.png"],
                },
                {
                    "case_id": "SMK-VID-02-01",
                    "status": "soft_pass_with_fallback",
                    "blocking": True,
                    "message": "fallback",
                    "output_paths": [],
                },
                {
                    "case_id": "SMK-VID-03-01",
                    "status": "blocked_missing_asset",
                    "blocking": False,
                    "message": "missing",
                    "output_paths": [],
                },
            ],
        }
        (manifests_dir / "summary.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )

        status = self.runner.get_run_status(run_id)

        self.assertEqual(status.run_id, run_id)
        self.assertEqual(status.status, "soft_pass_with_fallback")
        self.assertEqual(status.target_id, "smoke")
        self.assertEqual(
            status.summary_path,
            str(manifests_dir / "summary.json"),
        )
        self.assertEqual(
            status.evidence_path,
            str(evidence_dir / "summary.md"),
        )

    def test_atomic_validation_routes_through_same_runner_as_unsupported(self) -> None:
        response = self.runner.start_run(
            StartRunRequest(
                runner_id="comfyui",
                operation_kind="validate_atomic",
                target_id="AT-IMG-02-01",
                requested_by="tests",
                channel="tests",
            )
        )

        self.assertFalse(response.accepted)
        self.assertEqual(response.status, "unsupported")
        self.assertIn("validate_atomic", response.message)


if __name__ == "__main__":
    unittest.main()

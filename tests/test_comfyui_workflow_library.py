from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from openclaw_studio.comfyui_workflow_library import (
    MODULE_NAME,
    render_workflow_advisory_context,
    render_workflow_comparison_advisory_context,
    build_workflow_template_entries,
    render_workflow_explanation,
    render_workflow_list,
    resolve_workflow_template_entry,
    sync_workflow_templates,
)


class ComfyUIWorkflowLibraryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.comfyui_dir = Path(self.tempdir.name) / "ComfyUI"
        self.comfyui_dir.mkdir(parents=True)
        self.repo_root = Path(__file__).resolve().parents[1]

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_resolve_workflow_template_entry_accepts_alias_and_use_case_id(self) -> None:
        alias_entry = resolve_workflow_template_entry(
            workflow_ref="prepara-video",
            repo_root=self.repo_root,
            comfyui_dir=self.comfyui_dir,
        )
        use_case_entry = resolve_workflow_template_entry(
            workflow_ref="UC-VID-01",
            repo_root=self.repo_root,
            comfyui_dir=self.comfyui_dir,
        )

        self.assertEqual(alias_entry.use_case_id, "UC-VID-01")
        self.assertEqual(alias_entry.friendly_alias, "prepara-video")
        self.assertEqual(use_case_entry.use_case_id, alias_entry.use_case_id)
        self.assertEqual(use_case_entry.template_filename, "prepara-video.json")

        entry_3d = resolve_workflow_template_entry(
            workflow_ref="imagen-a-3d",
            repo_root=self.repo_root,
            comfyui_dir=self.comfyui_dir,
        )
        self.assertEqual(entry_3d.use_case_id, "UC-3D-02")
        self.assertEqual(entry_3d.template_filename, "imagen-a-3d.json")

    def test_sync_creates_template_module_and_manifest(self) -> None:
        sync_result = sync_workflow_templates(
            repo_root=self.repo_root,
            comfyui_dir=self.comfyui_dir,
        )

        module_dir = self.comfyui_dir / "custom_nodes" / MODULE_NAME
        template_path = module_dir / "example_workflows" / "prepara-video.json"
        manifest_path = module_dir / "openclaw-workflows-manifest.json"
        helper_path = module_dir / "openclaw_nodes.py"

        self.assertTrue(sync_result.created_module)
        self.assertTrue((module_dir / "__init__.py").is_file())
        self.assertTrue(helper_path.is_file())
        self.assertTrue(template_path.exists())
        self.assertTrue(manifest_path.is_file())

        manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        managed_filenames = manifest_payload["managed_filenames"]

        self.assertIn("prepara-video.json", managed_filenames)
        self.assertGreaterEqual(sync_result.published_count, 4)
        self.assertEqual(
            build_workflow_template_entries(
                repo_root=self.repo_root,
                comfyui_dir=self.comfyui_dir,
            )[0].module_name,
            MODULE_NAME,
        )

    def test_render_workflow_list_includes_description_inputs_and_question_hint(self) -> None:
        entries = build_workflow_template_entries(
            repo_root=self.repo_root,
            comfyui_dir=self.comfyui_dir,
        )

        rendered = render_workflow_list(entries)

        self.assertIn("Hace:", rendered)
        self.assertIn("Entrada obligatoria:", rendered)
        self.assertIn("Salida:", rendered)
        self.assertIn("pregunta=studio que hace <alias>", rendered)

    def test_render_workflow_explanation_is_human_readable(self) -> None:
        entry = resolve_workflow_template_entry(
            workflow_ref="prepara-video",
            repo_root=self.repo_root,
            comfyui_dir=self.comfyui_dir,
        )

        rendered = render_workflow_explanation(entry)

        self.assertIn("Workflow: prepara-video (UC-VID-01)", rendered)
        self.assertIn("Hace:", rendered)
        self.assertIn("Entrada obligatoria:", rendered)
        self.assertIn("Salida principal:", rendered)
        self.assertIn("Comando: studio comfyui abre workflow prepara-video", rendered)

    def test_render_workflow_explanation_for_3d_alias_is_human_readable(self) -> None:
        entry = resolve_workflow_template_entry(
            workflow_ref="imagen-a-3d",
            repo_root=self.repo_root,
            comfyui_dir=self.comfyui_dir,
        )

        rendered = render_workflow_explanation(entry)

        self.assertIn("Workflow: imagen-a-3d (UC-3D-02)", rendered)
        self.assertIn("Categoria 3D", rendered)
        self.assertIn("Variante actual: Stable Fast 3D single-image baseline.", rendered)
        self.assertIn("Comando: studio comfyui abre workflow imagen-a-3d", rendered)

    def test_render_workflow_advisory_context_mentions_real_graph_structure(self) -> None:
        entry = resolve_workflow_template_entry(
            workflow_ref="prepara-video",
            repo_root=self.repo_root,
            comfyui_dir=self.comfyui_dir,
        )

        rendered = render_workflow_advisory_context(entry)

        self.assertIn("OpenClaw workflow advisory context:", rendered)
        self.assertIn("workflow_alias=prepara-video", rendered)
        self.assertIn("editable_entry_nodes=", rendered)
        self.assertIn("INPUT VIDEO [VHS_LoadVideo]", rendered)
        self.assertIn("output_nodes=", rendered)

    def test_render_workflow_advisory_context_for_3d_alias_mentions_real_graph_structure(self) -> None:
        entry = resolve_workflow_template_entry(
            workflow_ref="imagen-a-3d",
            repo_root=self.repo_root,
            comfyui_dir=self.comfyui_dir,
        )

        rendered = render_workflow_advisory_context(entry)

        self.assertIn("workflow_alias=imagen-a-3d", rendered)
        self.assertIn("editable_entry_nodes=", rendered)
        self.assertIn("LoadImage [LoadImage] -> openclaw_object_ref.png", rendered)
        self.assertIn("StableFast3DSampler x1", rendered)

    def test_render_workflow_comparison_advisory_context_mentions_both_workflows(self) -> None:
        left_entry = resolve_workflow_template_entry(
            workflow_ref="prepara-video",
            repo_root=self.repo_root,
            comfyui_dir=self.comfyui_dir,
        )
        right_entry = resolve_workflow_template_entry(
            workflow_ref="render-video",
            repo_root=self.repo_root,
            comfyui_dir=self.comfyui_dir,
        )

        rendered = render_workflow_comparison_advisory_context(left_entry, right_entry)

        self.assertIn("OpenClaw workflow comparison advisory context:", rendered)
        self.assertIn("left_alias=prepara-video", rendered)
        self.assertIn("right_alias=render-video", rendered)
        self.assertIn("shared_required_inputs=", rendered)
        self.assertIn("left_workflow:", rendered)
        self.assertIn("right_workflow:", rendered)


if __name__ == "__main__":
    unittest.main()

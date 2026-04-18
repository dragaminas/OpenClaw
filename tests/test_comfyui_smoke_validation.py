import unittest

from openclaw_studio.comfyui_smoke_validation import WorkflowCompiler


class WorkflowCompilerTests(unittest.TestCase):
    def test_extract_subgraph_wrapper_widgets_respects_proxy_widget_order(self):
        compiler = WorkflowCompiler.__new__(WorkflowCompiler)
        node = {
            "inputs": [
                {"name": "text", "widget": {"name": "text"}},
                {"name": "width", "widget": {"name": "width"}},
                {"name": "height", "widget": {"name": "height"}},
                {"name": "unet_name", "widget": {"name": "unet_name"}},
                {"name": "clip_name", "widget": {"name": "clip_name"}},
                {"name": "vae_name", "widget": {"name": "vae_name"}},
            ],
            "properties": {
                "proxyWidgets": [
                    ["-1", "text"],
                    ["-1", "width"],
                    ["-1", "height"],
                    ["3", "seed"],
                    ["3", "control_after_generate"],
                    ["-1", "unet_name"],
                    ["-1", "clip_name"],
                    ["-1", "vae_name"],
                ]
            },
            "widgets_values": [
                "",
                768,
                768,
                None,
                None,
                "z_image_turbo_bf16.safetensors",
                "qwen_3_4b.safetensors",
                "ae.safetensors",
            ],
        }

        result = compiler.extract_subgraph_wrapper_widgets(node)

        self.assertEqual(
            result,
            {
                "text": "",
                "width": 768,
                "height": 768,
                "unet_name": "z_image_turbo_bf16.safetensors",
                "clip_name": "qwen_3_4b.safetensors",
                "vae_name": "ae.safetensors",
            },
        )

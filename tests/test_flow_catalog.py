from __future__ import annotations

import unittest

from openclaw_studio.application.session_engine import GuidedSessionEngine
from openclaw_studio.implementations import BUILTIN_FLOW_CATALOG


class BuiltinFlowCatalogAliasTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session_engine = GuidedSessionEngine(BUILTIN_FLOW_CATALOG)

    def test_primary_aliases_are_unique_and_non_empty(self) -> None:
        primary_aliases = [flow.friendly_alias for flow in BUILTIN_FLOW_CATALOG]

        self.assertTrue(all(primary_aliases))
        self.assertEqual(len(primary_aliases), len(set(primary_aliases)))
        for flow in BUILTIN_FLOW_CATALOG:
            self.assertEqual(flow.user_aliases[0], flow.friendly_alias)

    def test_engine_matches_primary_and_spaced_aliases(self) -> None:
        expected_matches = {
            "prepara-video": "UC-VID-01",
            "prepara video": "UC-VID-01",
            "render-video": "UC-VID-02",
            "render video": "UC-VID-02",
            "explora-estilos": "UC-IMG-03",
        }

        for request_text, expected_use_case_id in expected_matches.items():
            with self.subTest(request_text=request_text):
                selected_flow = self.session_engine.select_flow_for_request(
                    f"quiero usar {request_text}"
                )
                self.assertEqual(selected_flow.use_case_id, expected_use_case_id)


if __name__ == "__main__":
    unittest.main()

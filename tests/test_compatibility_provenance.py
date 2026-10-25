"""Compatibility-entry orchestration tests with stubbed pipeline dependencies."""
import runpy
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/health_pipeline/report.py"


class CompatibilityProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.analysis = types.ModuleType("analyse")
        self.analysis.load_config = Mock(return_value={"id": "fixture"})
        self.analysis.analyse = Mock()
        self.publisher = types.ModuleType("publish")
        self.record = {"schema": "fixture-provenance", "identity": "synthetic"}
        self.publisher.build_provenance = Mock(return_value=self.record)
        self.publisher.package = Mock()
        self.publisher.render = Mock()

    def invoke(self, arguments=()):
        with patch.dict(sys.modules, {
            "analyse": self.analysis, "publish": self.publisher,
        }), patch.object(sys, "argv", [str(SCRIPT), *arguments]):
            runpy.run_path(str(SCRIPT), run_name="__main__")

    def test_default_cli_always_passes_provenance(self):
        self.invoke()
        bundle = Path("out/reports/fixture/data")
        self.publisher.build_provenance.assert_called_once_with(
            bundle, "html", "quarto"
        )
        self.publisher.render.assert_called_once_with(
            bundle, bundle.parent / "report.html", "html", "quarto",
            provenance=self.record,
            provenance_out=bundle.parent / "provenance.json",
        )
        self.assertIs(
            self.publisher.render.call_args.kwargs["provenance"], self.record
        )

    def test_explicit_cli_arguments_are_preserved(self):
        self.invoke([
            "--out", "custom-output", "--stakeholder", "custom.json",
            "--classes", "classes.csv", "--quarto", "fixture-quarto",
        ])
        bundle = Path("custom-output/reports/fixture/data")
        self.analysis.load_config.assert_called_once_with("custom.json")
        self.analysis.analyse.assert_called_once_with(
            "custom-output", "custom.json", "classes.csv", bundle
        )
        self.publisher.package.assert_called_once_with(bundle, bundle.parent / "app")
        self.publisher.build_provenance.assert_called_once_with(
            bundle, "html", "fixture-quarto"
        )
        self.publisher.render.assert_called_once_with(
            bundle, bundle.parent / "report.html", "html", "fixture-quarto",
            provenance=self.record,
            provenance_out=bundle.parent / "provenance.json",
        )

    def test_invalid_configuration_stops_before_analysis(self):
        self.analysis.load_config.side_effect = ValueError("invalid fixture config")
        with self.assertRaisesRegex(ValueError, "invalid fixture config"):
            self.invoke()
        self.analysis.analyse.assert_not_called()
        self.publisher.build_provenance.assert_not_called()
        self.publisher.render.assert_not_called()

    def test_analysis_failure_prevents_render(self):
        self.analysis.analyse.side_effect = RuntimeError("fixture analysis failure")
        with self.assertRaisesRegex(RuntimeError, "fixture analysis failure"):
            self.invoke()
        self.publisher.build_provenance.assert_not_called()
        self.publisher.render.assert_not_called()

    def test_provenance_failure_is_not_silently_omitted(self):
        self.publisher.build_provenance.side_effect = RuntimeError("fixture provenance failure")
        with self.assertRaisesRegex(RuntimeError, "fixture provenance failure"):
            self.invoke()
        self.publisher.package.assert_not_called()
        self.publisher.render.assert_not_called()

    def test_package_failure_prevents_render(self):
        self.publisher.package.side_effect = RuntimeError("fixture package failure")
        with self.assertRaisesRegex(RuntimeError, "fixture package failure"):
            self.invoke()
        self.publisher.render.assert_not_called()

    def test_render_failure_propagates(self):
        self.publisher.render.side_effect = RuntimeError("fixture render failure")
        with self.assertRaisesRegex(RuntimeError, "fixture render failure"):
            self.invoke()
        self.publisher.build_provenance.assert_called_once()


if __name__ == "__main__":
    unittest.main()

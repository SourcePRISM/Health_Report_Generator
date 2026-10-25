"""Source contracts; browser layout must be tested separately."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "scripts" / "health_pipeline" / "templates"


def test_trace_outputs_have_separate_accessible_scroll_regions():
    app = (TEMPLATES / "app.R").read_text()
    for output, label in (
        ("metric_value", "Metric values"),
        ("lineage", "Calculation lineage"),
    ):
        pattern = (
            r"div\(class='trace-table-scroll',role='region',tabindex='0',\s*"
            + r"`aria-label`='"
            + re.escape(label)
            + r"',\s*tableOutput\('"
            + re.escape(output)
            + r"'\)\)"
        )
        assert len(re.findall(pattern, app)) == 1


def test_trace_scroll_style_contains_width_without_clipping():
    css = (TEMPLATES / "dashboard.css").read_text()
    match = re.search(
        r"\.trace-controls \.trace-table-scroll\{([^}]+)\}", css
    )
    assert match is not None
    declarations = {
        key.strip(): value.strip()
        for key, value in (
            item.split(":", 1)
            for item in match.group(1).split(";")
            if ":" in item
        )
    }
    assert declarations["width"] == "100%"
    assert declarations["max-width"] == "100%"
    assert declarations["min-width"] == "0"
    assert declarations["overflow-x"] == "auto"
    assert "hidden" not in declarations.values()


def test_trace_download_handlers_preserve_complete_csv_files():
    app = (TEMPLATES / "app.R").read_text()
    for name in ("metrics", "lineage"):
        assert (
            f"downloadHandler(filename=function() '{name}.csv',"
            f"content=function(file) file.copy('{name}.csv',file))"
        ) in app

"""Exact-version Python jobs use an explicitly compatible runner."""
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]
JOB = re.compile(
    r"^  ([A-Za-z0-9_-]+):\n(.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
    re.MULTILINE | re.DOTALL,
)


@pytest.mark.parametrize("name,count", [
    ("validate.yml", 2),
    ("refresh-idd-data.yml", 1),
    ("render-selected-report.yml", 1),
])
def test_exact_python_jobs_use_compatible_runner(name, count):
    text = (ROOT / ".github/workflows" / name).read_text()
    blocks = [
        match.group(2) for match in JOB.finditer(text)
        if "uses: actions/setup-python@" in match.group(2)
    ]
    assert len(blocks) == count
    for block in blocks:
        assert re.search(r"^    runs-on: ubuntu-24\.04$", block, re.MULTILINE)
        assert re.search(
            r"python-version:\s*['\"]3\.11\.6['\"]", block
        )
        assert (
            "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97"
            in block
        )

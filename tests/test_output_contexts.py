"""Context-specific regression fixtures; require existing R/Quarto, no installs."""
import json
import os
from pathlib import Path
import subprocess
from html.parser import HTMLParser

import pytest

pytestmark = pytest.mark.r_quarto

ROOT = Path(__file__).resolve().parents[1]


def run_r(tmp_path, body, payload):
    (tmp_path / 'payload.json').write_text(json.dumps({'payload': payload}))
    code = r"""
.libPaths(c('/opt/health-report-r-library', .libPaths()))
args <- commandArgs(trailingOnly=TRUE)
setwd(file.path(args[1], 'scripts/health_pipeline/templates'))
source('report_helpers.R')
input <- jsonlite::fromJSON(file.path(args[2], 'payload.json'))
""" + body + r"""
jsonlite::write_json(result, file.path(args[2], 'r-result.json'),
                    auto_unbox=TRUE, null='null', pretty=TRUE)
"""
    script = tmp_path / 'fixture.R'
    script.write_text(code)
    run = subprocess.run(
        ['Rscript', '--vanilla', str(script), str(ROOT), str(tmp_path)],
        cwd=tmp_path, capture_output=True, text=True, timeout=90,
        env={**os.environ, 'HOME': str(tmp_path)}
    )
    assert run.returncode == 0, run.stderr
    return json.loads((tmp_path / 'r-result.json').read_text())


def pandoc_ast(tmp_path, text):
    source = tmp_path / 'fixture.md'
    destination = tmp_path / 'fixture-ast.json'
    source.write_text(text)
    run = subprocess.run(
        ['quarto', 'pandoc', '--from=markdown', '--to=json',
         '--output=' + str(destination), str(source)],
        capture_output=True, text=True, timeout=90
    )
    assert run.returncode == 0, run.stderr
    assert destination.is_file(), 'Pandoc produced no explicit AST file'
    tree = json.loads(destination.read_text())
    assert 'pandoc-api-version' in tree and isinstance(tree.get('blocks'), list)
    return tree


def nodes(tree):
    if isinstance(tree, dict):
        if 't' in tree:
            yield tree
        for value in tree.values():
            yield from nodes(value)
    elif isinstance(tree, list):
        for value in tree:
            yield from nodes(value)


def inline_text(items):
    result = ''
    for item in items:
        if item['t'] == 'Str':
            result += item['c']
        elif item['t'] in ('Space', 'SoftBreak', 'LineBreak'):
            result += ' '
        else:
            raise AssertionError('Unexpected non-literal inline node: ' + item['t'])
    return result


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.images.append(dict(attrs))


@pytest.mark.parametrize('payload', [
    'SYNTHETIC_REVIEW" onerror="reviewMarker()',
    "quote ' & <tag> > ü",
])
def test_chart_alt_is_one_literal_attribute(tmp_path, payload):
    result = run_r(tmp_path, r"""
p <- ggplot2::ggplot(data.frame(x=1,y=1), ggplot2::aes(x,y)) + ggplot2::geom_point()
result <- list(html=chart_image(p, input$payload))
""", payload)
    parsed = Images()
    parsed.feed(result['html'])
    assert len(parsed.images) == 1
    image = parsed.images[0]
    assert image['alt'] == payload
    assert not any(key.lower().startswith('on') for key in image)


@pytest.mark.parametrize('payload', [
    r'SYNTHETIC_REVIEW \input{SYNTHETIC_REVIEW_NOT_A_REAL_FILE}',
    'A|B & <x> "quote" \'single\' $math$ `code` [link](file:///tmp/no)',
    'Heading\n```{=latex}\n\\input{SYNTHETIC_REVIEW_NOT_A_REAL_FILE}\n```',
    'Researcher 1.0 — Zürich',
])
def test_markdown_text_is_literal_pandoc_text(tmp_path, payload):
    result = run_r(tmp_path, 'result <- list(text=markdown_text(input$payload))\n', payload)
    tree = pandoc_ast(tmp_path, result['text'])
    assert len(tree['blocks']) == 1
    block = tree['blocks'][0]
    assert block['t'] in ('Para', 'Plain')
    expected = ''.join(' ' if ord(c) < 32 or ord(c) == 127 else c for c in payload)
    assert inline_text(block['c']) == expected


def test_markdown_table_does_not_interpret_cell_markup(tmp_path):
    payload = r'A|B \input{SYNTHETIC_REVIEW_NOT_A_REAL_FILE}'
    result = run_r(tmp_path, r"""
d <- data.frame(Value=input$payload, Count=12, check.names=FALSE)
result <- list(text=paste(markdown_table(d), collapse='\n'))
""", payload)
    tree = pandoc_ast(tmp_path, result['text'])
    assert sum(node['t'] == 'Table' for node in nodes(tree)) == 1
    assert not any(node['t'] in ('RawInline', 'RawBlock', 'Link', 'Image') for node in nodes(tree))
    assert any(node['t'] == 'Str' and 'SYNTHETIC_REVIEW_NOT_A_REAL_FILE' in node['c'] for node in nodes(tree))


def test_pdf_helper_metadata_and_coverage_stay_literal(tmp_path):
    payload = r'SYNTHETIC_REVIEW \input{SYNTHETIC_REVIEW_NOT_A_REAL_FILE}'
    result = run_r(tmp_path, r"""
b <- list(
  cfg=list(presentation=list(display_name=input$payload, layout='technical',
                             detail_level='full', version=input$payload),
           years=c(2021,2025), reference_year=2019, index_base_year=2019,
           geography='CHFL', outputs=c('sources')),
  series=data.frame(dataset_id='fixture', topic='fixture', pathogen_class='viral',
                    source_system='mandatory_reporting_system', year=2021, value=1),
  selection=data.frame(topic='fixture', status='included', group_eligible='true'),
  classes=data.frame(topic='fixture', label=input$payload),
  metrics=data.frame(metric_id=character(), metric_type=character(),
                     subject=character(), year=numeric(), value=numeric(), unit=character()),
  manifest=list(snapshot_id=paste(rep('a',64), collapse=''))
)
result <- list(text=paste(capture.output(audience_document_pdf(b)), collapse='\n'))
""", payload)
    tree = pandoc_ast(tmp_path, result['text'])
    for node in nodes(tree):
        if node['t'] in ('RawInline', 'RawBlock'):
            assert 'SYNTHETIC_REVIEW_NOT_A_REAL_FILE' not in str(node['c'])
    assert any(node['t'] == 'Str' and 'SYNTHETIC_REVIEW_NOT_A_REAL_FILE' in node['c'] for node in nodes(tree))


def test_pdf_qmd_sinks_use_literal_text_encoder():
    methods = (ROOT / 'scripts/health_pipeline/templates/methods.qmd').read_text()
    report = (ROOT / 'scripts/health_pipeline/report_public_health_expert.qmd').read_text()
    for text in (methods, report):
        assert 'markdown_text(p$display_name)' in text
    for expression in ('b$selection$status[i]', 'b$selection$reason[i]'):
        assert 'markdown_text(' + expression + ')' in methods

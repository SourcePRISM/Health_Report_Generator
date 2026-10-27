"""Synthetic selected-artifact contract fixtures; no R, Quarto or real data."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

import verify_selected_report as selected

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'request_id': 'synthetic_request_01', 'audience': 'researcher',
    'selected_ids': ['fixture_a', 'fixture_b'], 'source_run_id': '12345678',
}


def write_json(path, value):
    path.write_text(json.dumps(value, sort_keys=True) + '\n', encoding='utf-8')


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def artifact(tmp_path):
    folder = tmp_path / 'selected'
    data = folder / 'data'
    data.mkdir(parents=True)
    settings = {
        'id': 'researcher', 'title': 'Synthetic title', 'question': 'Synthetic question',
        'outputs': ['sources'], 'presentation': {'layout': 'technical', 'version': 'fixture'},
        'classes_in_main_comparison': ['viral'], 'years': [2021, 2025], 'geography': 'CHFL',
    }
    for name in selected.DATA_FILES:
        (data / name).write_text('fixture,value\nsynthetic,1\n')
    write_json(data / 'stakeholder.json', settings)
    snapshot = {'snapshot_id': 'a' * 64, 'snapshot_path': 'snapshots/' + 'a' * 64}
    write_json(data / 'snapshot.json', snapshot)
    inventory = {name: file_hash(data / name) for name in selected.DATA_FILES}
    manifest = {'schema_version': '2.0', 'stakeholder': 'researcher',
                'snapshot_id': snapshot['snapshot_id'], 'files': inventory}
    write_json(data / 'bundle.json', manifest)
    record = {
        'schema': 'health-report-provenance/1.0',
        'rendered_at_utc': '2026-10-27T10:00:00+00:00',
        'request': {
            'request_id': EXPECTED['request_id'], 'audience': EXPECTED['audience'],
            'selected_dataset_ids': EXPECTED['selected_ids'],
            'lineage_artifact_run_id': EXPECTED['source_run_id'],
            'output_formats': ['html', 'pdf'], 'presentation': settings['presentation'],
            'selected_pathogen_classes': ['viral'], 'selected_labels': ['A', 'B'],
        },
        'effective_parameters': settings,
        'stakeholder': {**{key: settings[key] for key in ('id', 'title', 'question', 'outputs', 'presentation')},
                        'parameters_sha256': inventory['stakeholder.json']},
        'analysis_bundle': {'schema_version': '2.0', 'files': inventory},
        'filters': {key: settings[key] for key in selected.FILTER_KEYS if key in settings},
        'data': {'snapshot_id': snapshot['snapshot_id'], 'canonical_root': None,
                 'snapshot_manifest': 'data/snapshot.json',
                 'lineage_artifact_snapshot_path': snapshot['snapshot_path']},
        'code': {'workflow_config': {'path': selected.WORKFLOW, 'sha256': file_hash(ROOT / selected.WORKFLOW)}},
        'output': {
            'format': 'html', 'documents': ['report.html', 'methods.html'],
            'shared_template': selected.TEMPLATE,
            'shared_template_sha256': file_hash(ROOT / selected.TEMPLATE),
            'presentation_helpers_sha256': {
                name: file_hash(ROOT / 'scripts/health_pipeline/templates' / name)
                for name in selected.HELPERS
            },
        },
    }
    write_json(folder / 'provenance.json', record)
    pdf_record = copy.deepcopy(record)
    pdf_record['rendered_at_utc'] = '2026-10-27T10:00:05+00:00'
    pdf_record['output'].update(format='pdf', documents=['report.pdf', 'methods.pdf'])
    write_json(folder / 'provenance-pdf.json', pdf_record)
    embedded = '<script type="application/json" id="report-provenance">' + json.dumps(record) + '</script>'
    (folder / 'report.html').write_text(
        '<!doctype html><html><body><h1 id="top">Synthetic</h1>'
        '<a href="methods.html#details">Methods</a><a href="report.pdf">PDF</a>'
        '<a href="data/bundle.json">Bundle</a>' + embedded + '</body></html>')
    (folder / 'methods.html').write_text(
        '<!doctype html><html><body><h1 id="details">Methods</h1>'
        '<a href="report.html#top">Report</a>' + embedded + '</body></html>')
    for name in ('report.pdf', 'methods.pdf'):
        (folder / name).write_bytes(b'%PDF-1.4\nSYNTHETIC HEADER FIXTURE ONLY\n%%EOF\n')
    return folder


def verify(folder, **changes):
    return selected.verify_selected_report(folder, **{**EXPECTED, **changes})


def test_valid_selected_set_is_read_only(artifact):
    before = {path.relative_to(artifact).as_posix(): path.read_bytes()
              for path in artifact.rglob('*') if path.is_file()}
    result = verify(artifact)
    after = {path.relative_to(artifact).as_posix(): path.read_bytes()
             for path in artifact.rglob('*') if path.is_file()}
    assert before == after
    assert result['request_id'] == EXPECTED['request_id']
    assert result['snapshot_id'] == 'a' * 64
    assert result['files'] == {name: hashlib.sha256(data).hexdigest() for name, data in before.items()}
    assert 'request_provenance.json' not in result['files']
    assert 'release.json' not in result['files']


@pytest.mark.parametrize('name', (*selected.DOCUMENTS, *selected.SIDECARS,
                                 'data/bundle.json', *('data/' + name for name in selected.DATA_FILES)))
def test_missing_required_file_is_rejected(artifact, name):
    (artifact / name).unlink()
    with pytest.raises(selected.SelectedReportInvalid):
        verify(artifact)


@pytest.mark.parametrize('name', (*selected.DOCUMENTS, *selected.SIDECARS, 'data/bundle.json'))
def test_empty_required_file_is_rejected(artifact, name):
    (artifact / name).write_bytes(b'')
    with pytest.raises(selected.SelectedReportInvalid):
        verify(artifact)


@pytest.mark.parametrize('name', selected.SIDECARS + ('data/bundle.json',))
@pytest.mark.parametrize('text', ('{broken', '[]', '{"duplicate":1,"duplicate":2}', '{"x":NaN}'))
def test_malformed_json_is_rejected(artifact, name, text):
    (artifact / name).write_text(text)
    with pytest.raises(selected.SelectedReportInvalid):
        verify(artifact)


@pytest.mark.parametrize('changes', (
    {'request_id': 'different_request'}, {'audience': 'public'},
    {'selected_ids': ['fixture_b', 'fixture_a']}, {'source_run_id': '99999999'},
    {'selected_ids': []}, {'selected_ids': ['fixture_a', 'fixture_a']},
    {'selected_ids': [1]}, {'request_id': '../unsafe'}, {'source_run_id': ''},
))
def test_independent_expected_identity_is_enforced(artifact, changes):
    with pytest.raises(selected.SelectedReportInvalid):
        verify(artifact, **changes)


@pytest.mark.parametrize('path,value', (
    (('schema',), 'unsupported'),
    (('request', 'request_id'), 'another_request'),
    (('request', 'output_formats'), ['html']),
    (('request', 'selected_pathogen_classes'), ['bacterial']),
    (('effective_parameters', 'geography'), 'CH'),
    (('stakeholder', 'parameters_sha256'), 'f' * 64),
    (('analysis_bundle', 'files', 'metrics.csv'), 'f' * 64),
    (('filters', 'geography'), 'CH'),
    (('data', 'snapshot_id'), 'f' * 64),
    (('data', 'snapshot_manifest'), '/tmp/old/snapshot.json'),
    (('data', 'canonical_root'), '/tmp/old/data'),
    (('data', 'lineage_artifact_snapshot_path'), 'different'),
    (('output', 'format'), 'html'),
    (('output', 'documents'), ['only.pdf']),
    (('output', 'shared_template_sha256'), 'f' * 64),
    (('output', 'presentation_helpers_sha256', 'report_helpers.R'), 'f' * 64),
    (('code', 'workflow_config', 'sha256'), 'f' * 64),
))
def test_pdf_sidecar_mismatches_are_rejected(artifact, path, value):
    record = json.loads((artifact / 'provenance-pdf.json').read_text())
    cursor = record
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    write_json(artifact / 'provenance-pdf.json', record)
    with pytest.raises(selected.SelectedReportInvalid):
        verify(artifact)


def test_bundle_file_tampering_is_rejected(artifact):
    (artifact / 'data/metrics.csv').write_text('tampered\n')
    with pytest.raises(selected.SelectedReportInvalid):
        verify(artifact)


@pytest.mark.parametrize('name', ('../outside.csv', '/tmp/outside.csv', 'bad\\file.csv', 'bad\x00file.csv'))
def test_unsafe_inventory_path_is_rejected_before_read(artifact, name):
    manifest = json.loads((artifact / 'data/bundle.json').read_text())
    manifest['files'][name] = 'f' * 64
    write_json(artifact / 'data/bundle.json', manifest)
    with pytest.raises(selected.SelectedReportInvalid):
        verify(artifact)


def test_unrecorded_analysis_file_is_rejected(artifact):
    (artifact / 'data/unrecorded.csv').write_text('extra\n')
    with pytest.raises(selected.SelectedReportInvalid):
        verify(artifact)


@pytest.mark.parametrize('edit', ('missing', 'duplicate', 'different', 'unterminated'))
def test_embedded_provenance_must_be_unique_and_equal(artifact, edit):
    page = artifact / 'methods.html'
    text = page.read_text()
    if edit == 'missing':
        text = '<html><h1 id="details">No provenance</h1></html>'
    elif edit == 'duplicate':
        text += '<script type="application/json" id="report-provenance">{}</script>'
    elif edit == 'different':
        text = text.replace(EXPECTED['request_id'], 'different_request')
    else:
        text = text.replace('</script>', '')
    page.write_text(text)
    with pytest.raises(selected.SelectedReportInvalid):
        verify(artifact)


@pytest.mark.parametrize('markup', (
    '<a href="missing.html">missing</a>', '<a href="methods.html#absent">anchor</a>',
    '<img src="missing.png">', '<a href="../outside.txt">outside</a>',
    '<a href="%2e%2e/outside.txt">encoded outside</a>', '<a href="/etc/passwd">absolute</a>',
    '<img src="https://example.org/image.png">', '<script src="//example.org/code.js"></script>',
    '<link rel="stylesheet" href="https://example.org/style.css">',
    '<iframe src="https://example.org/frame"></iframe>', '<a href="javascript:alert(1)">bad</a>',
    '<base href="https://example.org/">', '<a href="file:///tmp/no">file</a>',
    '<img src="bad%00name.png">', '<img src="bad%5cname.png">',
))
def test_invalid_references_are_rejected(artifact, markup):
    (artifact.parent / 'outside.txt').write_text('outside artifact')
    page = artifact / 'report.html'
    page.write_text(page.read_text() + markup)
    with pytest.raises(selected.SelectedReportInvalid):
        verify(artifact)


def test_valid_contained_and_external_references_are_accepted(artifact):
    nested = artifact / 'assets'
    nested.mkdir()
    (nested / 'chart.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')
    (nested / 'help.html').write_text('<h1 id="help">Help</h1><a href="../report.html#top">Back</a>')
    page = artifact / 'report.html'
    page.write_text(page.read_text() + '<img src="assets/chart.svg"><img src="data:image/png;base64,AA==">'
                    '<a href="assets/help.html#help">Help</a><a href="https://example.org/">External</a>'
                    '<a href="mailto:example@example.org">Mail</a><a href="tel:123">Phone</a>')
    assert verify(artifact)['audience'] == 'researcher'


@pytest.mark.parametrize('kind', ('file', 'directory', 'root'))
def test_symlinks_are_rejected(artifact, kind):
    if kind == 'root':
        link = artifact.parent / 'artifact-link'
        link.symlink_to(artifact, target_is_directory=True)
        folder = link
    else:
        folder = artifact
        target = artifact / ('data' if kind == 'directory' else 'report.html')
        (artifact / 'symlink').symlink_to(target, target_is_directory=kind == 'directory')
    with pytest.raises(selected.SelectedReportInvalid):
        verify(folder)


def test_nonregular_entry_is_rejected_without_opening(artifact):
    os.mkfifo(artifact / 'synthetic-pipe')
    with pytest.raises(selected.SelectedReportInvalid):
        verify(artifact)


@pytest.mark.parametrize('name', ('report.pdf', 'methods.pdf'))
def test_non_pdf_header_is_rejected(artifact, name):
    (artifact / name).write_bytes(b'not a PDF')
    with pytest.raises(selected.SelectedReportInvalid):
        verify(artifact)


@pytest.mark.parametrize('damaged', (False, True))
def test_cli_returns_success_or_failure_without_rendering(artifact, damaged):
    if damaged:
        (artifact / 'methods.pdf').unlink()
    command = [sys.executable, '-B', str(ROOT / 'scripts/health_pipeline/verify_selected_report.py'),
               '--report-dir', str(artifact), '--request-id', EXPECTED['request_id'],
               '--audience', EXPECTED['audience'], '--source-run-id', EXPECTED['source_run_id'],
               '--selected-ids-json', json.dumps(EXPECTED['selected_ids'])]
    result = subprocess.run(command, capture_output=True, text=True, timeout=30,
                            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    assert result.returncode == (1 if damaged else 0), result.stderr
    assert ('ERROR:' in result.stderr) == damaged


SELECTED_WORKFLOW = '.github/workflows/render-selected-report.yml'
VERIFY_STEP = 'Verify selected report artifact contract'
UPLOAD_STEP = 'Upload selected report and provenance'


def selected_workflow_document():
    import yaml
    return yaml.safe_load((ROOT / SELECTED_WORKFLOW).read_text())


def assert_selected_workflow_gate(document):
    import shlex

    assert document['permissions'] == {'actions': 'read', 'contents': 'read'}
    job = document['jobs']['render']
    assert 'continue-on-error' not in job
    steps = job['steps']
    def one(name):
        indexes = [index for index, item in enumerate(steps) if item.get('name') == name]
        assert len(indexes) == 1
        return indexes[0]
    render_index = one('Render from selected lineage data')
    verify_index = one(VERIFY_STEP)
    upload_index = one(UPLOAD_STEP)
    assert render_index + 1 == verify_index and verify_index + 1 == upload_index
    render, verifier, upload = steps[render_index], steps[verify_index], steps[upload_index]
    for item in (render, verifier, upload):
        assert 'continue-on-error' not in item
    assert 'if' not in render and 'if' not in verifier
    assert upload['if'] == 'success()'
    assert upload['uses'] == 'actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a'
    assert upload['with']['if-no-files-found'] == 'error'
    assert upload['with']['name'] == 'selected-report-${{ inputs.request_id }}'
    assert upload['with']['path'] == 'results/selected_reports/${{ inputs.request_id }}/'
    expected_env = {
        'REQUEST_ID': '${{ inputs.request_id }}', 'AUDIENCE': '${{ inputs.audience }}',
        'SOURCE_RUN_ID': '${{ inputs.lineage_run_id }}',
        'DATASET_IDS_JSON': '${{ inputs.dataset_ids_json }}',
    }
    assert verifier['env'] == expected_env and render['env'] == expected_env
    script = verifier['run']
    assert '${{' not in script and '||' not in script and '|' not in script
    assert shlex.split(script.replace('\\\n', ' ')) == [
        'python', 'scripts/health_pipeline/verify_selected_report.py',
        '--report-dir', 'results/selected_reports/$REQUEST_ID',
        '--request-id', '$REQUEST_ID', '--audience', '$AUDIENCE',
        '--selected-ids-json', '$DATASET_IDS_JSON', '--source-run-id', '$SOURCE_RUN_ID',
    ]
    for token in ('"results/selected_reports/$REQUEST_ID"', '"$REQUEST_ID"',
                  '"$AUDIENCE"', '"$DATASET_IDS_JSON"', '"$SOURCE_RUN_ID"'):
        assert token in script


def test_selected_workflow_verification_contract():
    assert_selected_workflow_gate(selected_workflow_document())


@pytest.mark.parametrize('damage', (
    'missing_verifier', 'verifier_after_upload', 'suppressed_failure',
    'missing_files_warning', 'upload_always', 'wrong_expected_input', 'unquoted_json',
))
def test_selected_workflow_contract_rejects_bypass(damage):
    document = copy.deepcopy(selected_workflow_document())
    steps = document['jobs']['render']['steps']
    verifier = next(item for item in steps if item.get('name') == VERIFY_STEP)
    upload = next(item for item in steps if item.get('name') == UPLOAD_STEP)
    if damage == 'missing_verifier':
        steps.remove(verifier)
    elif damage == 'verifier_after_upload':
        steps.remove(verifier)
        steps.append(verifier)
    elif damage == 'suppressed_failure':
        verifier['continue-on-error'] = True
    elif damage == 'missing_files_warning':
        upload['with']['if-no-files-found'] = 'warn'
    elif damage == 'upload_always':
        upload['if'] = 'always()'
    elif damage == 'wrong_expected_input':
        verifier['env']['AUDIENCE'] = 'self-derived-artifact-audience'
    else:
        verifier['run'] = verifier['run'].replace('"$DATASET_IDS_JSON"', '$DATASET_IDS_JSON')
    with pytest.raises(AssertionError):
        assert_selected_workflow_gate(document)


@pytest.mark.parametrize('exit_code', (0, 7))
def test_selected_workflow_command_preserves_arguments_and_exit_status(tmp_path, exit_code):
    import shutil

    command_root = tmp_path / 'command-fixture'
    script = command_root / 'scripts/health_pipeline/verify_selected_report.py'
    script.parent.mkdir(parents=True)
    script.write_text(
        'import json, os, sys\nfrom pathlib import Path\n'
        'Path(os.environ["CAPTURE_ARGS"]).write_text(json.dumps(sys.argv[1:]))\n'
        'sys.exit(int(os.environ["SYNTHETIC_EXIT"]))\n')
    capture = tmp_path / 'captured-arguments.json'
    request_id = 'synthetic_workflow_01'
    ids = json.dumps(['fixture with spaces', '$(touch UNEXPECTED_SHELL_WRITE)', 'literal;semicolon'])
    environment = {
        **os.environ, 'PATH': str(Path(sys.executable).parent) + os.pathsep + os.environ.get('PATH', ''),
        'PYTHONDONTWRITEBYTECODE': '1', 'REQUEST_ID': request_id, 'AUDIENCE': 'researcher',
        'SOURCE_RUN_ID': '12345678', 'DATASET_IDS_JSON': ids,
        'CAPTURE_ARGS': str(capture), 'SYNTHETIC_EXIT': str(exit_code),
    }
    document = selected_workflow_document()
    verifier = next(item for item in document['jobs']['render']['steps'] if item.get('name') == VERIFY_STEP)
    bash = shutil.which('bash')
    assert bash is not None, 'Existing Bash is required for this Linux workflow contract'
    run = subprocess.run([bash, '--noprofile', '--norc', '-e', '-o', 'pipefail', '-c', verifier['run']],
                         cwd=command_root, env=environment, capture_output=True, text=True, timeout=30)
    assert run.returncode == exit_code, run.stderr
    assert json.loads(capture.read_text()) == [
        '--report-dir', 'results/selected_reports/' + request_id,
        '--request-id', request_id, '--audience', 'researcher',
        '--selected-ids-json', ids, '--source-run-id', '12345678',
    ]
    assert not (command_root / 'UNEXPECTED_SHELL_WRITE').exists()

#!/usr/bin/env python3
"""Read-only verification of one private, stable selected-report artifact set."""
import argparse
import hashlib
import json
import re
import stat
import sys
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

SOURCE_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS = ('report.html', 'methods.html', 'report.pdf', 'methods.pdf')
SIDECARS = ('provenance.json', 'provenance-pdf.json')
DATA_FILES = (
    'series.csv', 'metrics.csv', 'lineage.csv', 'selection.csv', 'sources.csv',
    'checks.csv', 'snapshot.json', 'stakeholder.json', 'pathogen_class.csv',
)
HELPERS = ('report_helpers.R', 'audience_reports.R', 'methods.qmd', 'dashboard.css')
TEMPLATE = 'scripts/health_pipeline/report_public_health_expert.qmd'
WORKFLOW = '.github/workflows/render-selected-report.yml'
AUDIENCES = ('researcher', 'health_institution', 'public')
FILTER_KEYS = (
    'period_type', 'years', 'reference_year', 'index_base_year', 'geography',
    'measures_preferred', 'compare_by', 'classes_in_main_comparison',
    'exclude_from_group_totals', 'sensitivity_exclude', 'source_priority',
    'group_source_systems', 'dimension_filters', 'needs_roles',
)


class SelectedReportInvalid(ValueError):
    """The selected artifact set does not satisfy its publication contract."""


def require(condition, message):
    if not condition:
        raise SelectedReportInvalid(message)


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key.')
        result[key] = value
    return result


def _constant(value):
    raise SelectedReportInvalid('Nonfinite JSON constant: ' + value)


def _loads(text):
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)


def _object(path):
    value = _loads(path.read_text(encoding='utf-8'))
    require(type(value) is dict, 'JSON artifact must be an object: ' + path.name)
    return value


def _relative(value):
    require(type(value) is str and bool(value), 'Invalid inventory path.')
    require('\x00' not in value and '\\' not in value, 'Unsupported inventory path.')
    path = PurePosixPath(value)
    require(not path.is_absolute() and '..' not in path.parts
            and path.as_posix() == value and value != '.', 'Unsafe inventory path.')
    return value


def _hash(value):
    return type(value) is str and re.fullmatch(r'[a-f0-9]{64}', value) is not None


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.references = []
        self.embedded = []
        self.capture = None

    def handle_starttag(self, tag, attrs):
        require(tag != 'base', 'HTML base elements are unsupported.')
        values = dict(attrs)
        if values.get('id'):
            self.ids.add(values['id'])
        if tag == 'a' and values.get('name'):
            self.ids.add(values['name'])
        for name, value in attrs:
            if name in ('href', 'src', 'poster') and value:
                self.references.append((value, tag != 'a' or name != 'href'))
        if tag == 'script' and values.get('id') == 'report-provenance':
            require(sum(name == 'id' for name, _ in attrs) == 1,
                    'Ambiguous provenance element identifier.')
            require(values.get('type', '').lower() == 'application/json',
                    'Provenance script must contain application/json.')
            require('src' not in values, 'Provenance must be embedded, not loaded.')
            require(self.capture is None, 'Nested provenance script.')
            self.capture = []

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data):
        if self.capture is not None:
            self.capture.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.capture is not None:
            self.embedded.append(_loads(''.join(self.capture)))
            self.capture = None


def _reference(root, page, value, asset, pages):
    parts = urlsplit(value.strip())
    scheme = parts.scheme.lower()
    if scheme == 'data':
        return
    if scheme in ('http', 'https') or (not scheme and parts.netloc):
        require(not asset, 'Remote HTML resource is forbidden.')
        require(bool(parts.netloc), 'External hyperlink has no host.')
        return
    if scheme in ('mailto', 'tel'):
        require(not asset, 'Non-resource URL used as an asset.')
        return
    require(not scheme and not parts.netloc, 'Unsupported reference scheme or host.')
    name = unquote(parts.path)
    require('\x00' not in name and '\\' not in name and not name.startswith('/'),
            'Unsupported local resource path.')
    target = (page.parent / name).resolve(strict=True) if name else page
    require(target.is_relative_to(root) and target.is_file(),
            'Local reference escapes artifact root or is not a file.')
    if parts.fragment and target.suffix.lower() == '.html':
        require(target in pages and unquote(parts.fragment) in pages[target].ids,
                'Missing local HTML anchor.')


def _verify(directory, request_id, audience, selected_ids, source_run_id, source_root):
    require(type(request_id) is str and re.fullmatch(r'[A-Za-z0-9_-]{8,40}', request_id),
            'Invalid expected request ID.')
    require(type(audience) is str and audience in AUDIENCES, 'Invalid expected audience.')
    require(type(source_run_id) is str and bool(source_run_id.strip()),
            'Expected source run ID is required.')
    require(type(selected_ids) is list and bool(selected_ids)
            and all(type(value) is str and bool(value) for value in selected_ids),
            'Expected dataset IDs must be a nonempty string list.')
    require(len(selected_ids) == len(set(selected_ids)), 'Duplicate expected dataset IDs.')
    directory = Path(directory)
    require(not directory.is_symlink(), 'Artifact root cannot be a symlink.')
    root = directory.resolve(strict=True)
    require(root.is_dir(), 'Artifact root must be a directory.')
    files = []
    for path in root.rglob('*'):
        mode = path.lstat().st_mode
        require(not stat.S_ISLNK(mode), 'Symlinks are forbidden in artifacts.')
        if stat.S_ISDIR(mode):
            continue
        require(stat.S_ISREG(mode), 'Non-regular artifact entry.')
        files.append(path)
    for name in (*DOCUMENTS, *SIDECARS, 'data/bundle.json',
                 *('data/' + value for value in DATA_FILES)):
        path = root / name
        require(path.is_file() and path.stat().st_size > 0, 'Required artifact missing or empty: ' + name)
    for name in ('report.pdf', 'methods.pdf'):
        with (root / name).open('rb') as handle:
            require(handle.read(5) == b'%PDF-', 'Invalid PDF header: ' + name)

    bundle = _object(root / 'data/bundle.json')
    inventory = bundle.get('files')
    require(bundle.get('schema_version') == '2.0' and bundle.get('stakeholder') == audience,
            'Bundle schema or stakeholder differs.')
    require(_hash(bundle.get('snapshot_id')), 'Invalid bundle snapshot identity.')
    require(type(inventory) is dict and set(DATA_FILES).issubset(inventory),
            'Required analysis inventory missing.')
    for name, expected in inventory.items():
        path = root / 'data' / _relative(name)
        require(name != 'bundle.json' and _hash(expected), 'Invalid analysis inventory entry.')
        require(path.is_file() and path.stat().st_size > 0 and digest(path) == expected,
                'Analysis artifact hash mismatch: ' + name)
    actual_data = {path.relative_to(root / 'data').as_posix()
                   for path in files if path.is_relative_to(root / 'data')}
    require(actual_data == set(inventory) | {'bundle.json'}, 'Unrecorded analysis files.')
    settings = _object(root / 'data/stakeholder.json')
    snapshot = _object(root / 'data/snapshot.json')
    require(settings.get('id') == audience, 'Saved stakeholder differs from expected audience.')
    require(snapshot.get('snapshot_id') == bundle['snapshot_id'], 'Saved snapshot identity differs.')
    source = Path(source_root).resolve(strict=True)
    expected_helpers = {name: digest(source / 'scripts/health_pipeline/templates' / name)
                        for name in HELPERS}
    expected_workflow = {'path': WORKFLOW, 'sha256': digest(source / WORKFLOW)}
    records = {}
    for side, fmt in zip(SIDECARS, ('html', 'pdf')):
        record = _object(root / side)
        require(record.get('schema') == 'health-report-provenance/1.0', 'Unsupported provenance schema.')
        request = record.get('request')
        require(type(request) is dict, 'Request provenance missing.')
        for key, expected in {
            'request_id': request_id, 'audience': audience,
            'selected_dataset_ids': selected_ids, 'lineage_artifact_run_id': source_run_id,
            'output_formats': ['html', 'pdf'],
        }.items():
            require(request.get(key) == expected, 'Expected request identity differs: ' + key)
        require(record.get('effective_parameters') == settings, 'Effective parameters differ from saved settings.')
        require(request.get('presentation') == settings.get('presentation')
                and request.get('selected_pathogen_classes') == settings.get('classes_in_main_comparison'),
                'Selected presentation or class metadata differs.')
        stakeholder = record.get('stakeholder')
        require(type(stakeholder) is dict, 'Stakeholder provenance missing.')
        for key in ('id', 'title', 'question', 'presentation', 'outputs'):
            require(key in settings and stakeholder.get(key) == settings[key], 'Stakeholder metadata differs: ' + key)
        require(stakeholder.get('parameters_sha256') == inventory['stakeholder.json'], 'Parameter digest differs.')
        require(record.get('analysis_bundle') == {'schema_version': bundle['schema_version'], 'files': inventory},
                'Provenance analysis inventory differs.')
        require(record.get('filters') == {key: settings[key] for key in FILTER_KEYS if key in settings},
                'Recorded filters differ from saved settings.')
        data = record.get('data')
        require(type(data) is dict and data.get('snapshot_id') == bundle['snapshot_id'],
                'Provenance snapshot identity differs.')
        require(data.get('snapshot_manifest') == 'data/snapshot.json' and data.get('canonical_root') is None,
                'Selected snapshot reference differs.')
        require(data.get('lineage_artifact_snapshot_path') == snapshot.get('snapshot_path'),
                'Lineage snapshot path differs.')
        output = record.get('output')
        require(type(output) is dict and output.get('format') == fmt
                and output.get('documents') == [f'report.{fmt}', f'methods.{fmt}'],
                'Output format or document identity differs.')
        require(output.get('shared_template') == TEMPLATE
                and output.get('shared_template_sha256') == digest(source / TEMPLATE),
                'Template fingerprint differs from build source.')
        require(output.get('presentation_helpers_sha256') == expected_helpers,
                'Helper fingerprints differ from build source.')
        code = record.get('code')
        require(type(code) is dict and code.get('workflow_config') == expected_workflow,
                'Workflow fingerprint differs from build source.')
        records[fmt] = record
    for key in ('request', 'effective_parameters', 'stakeholder', 'filters', 'data', 'analysis_bundle'):
        require(records['html'][key] == records['pdf'][key], 'HTML/PDF common provenance differs: ' + key)

    pages = {}
    for path in files:
        if path.suffix.lower() == '.html':
            parsed = Page()
            parsed.feed(path.read_text(encoding='utf-8'))
            parsed.close()
            require(parsed.capture is None, 'Unterminated provenance script.')
            pages[path] = parsed
    for name in ('report.html', 'methods.html'):
        require(pages[root / name].embedded == [records['html']],
                'Missing, duplicate or unequal embedded provenance: ' + name)
    for page, parsed in pages.items():
        for value, asset in parsed.references:
            _reference(root, page, value, asset, pages)
    return {
        'request_id': request_id, 'audience': audience, 'source_run_id': source_run_id,
        'selected_dataset_ids': selected_ids, 'snapshot_id': bundle['snapshot_id'],
        'files': {path.relative_to(root).as_posix(): digest(path) for path in sorted(files)},
    }


def verify_selected_report(directory, *, request_id, audience, selected_ids, source_run_id,
                           source_root=SOURCE_ROOT):
    """Verify without writing files, fetching URLs or invoking a renderer.

    Expected identities must come from the caller, not from the artifact itself.
    Trusted local filesystem and stable private workspace are required. This is
    not a PDF parser, CSS/JavaScript analyzer or hostile-concurrency defense.
    """
    try:
        return _verify(directory, request_id, audience, selected_ids, source_run_id, source_root)
    except SelectedReportInvalid:
        raise
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, RecursionError) as exc:
        raise SelectedReportInvalid('Unreadable or malformed selected artifact set: ' + type(exc).__name__) from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report-dir', required=True)
    parser.add_argument('--request-id', required=True)
    parser.add_argument('--audience', required=True)
    parser.add_argument('--selected-ids-json', required=True)
    parser.add_argument('--source-run-id', required=True)
    args = parser.parse_args(argv)
    try:
        result = verify_selected_report(
            args.report_dir, request_id=args.request_id, audience=args.audience,
            selected_ids=_loads(args.selected_ids_json), source_run_id=args.source_run_id,
        )
    except (SelectedReportInvalid, ValueError, TypeError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        return 1
    print('Selected report verified: ' + str(len(result['files'])) + ' files')
    return 0


if __name__ == '__main__':
    sys.exit(main())

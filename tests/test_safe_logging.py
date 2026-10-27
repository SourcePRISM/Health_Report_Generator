"""Synthetic event/privacy and failure-path tests; no report rendering."""
import io
import json
import stat
import sys
from unittest.mock import Mock

import pytest

import process_supervisor as supervisor
from safe_logging import MAX_EVENT_BYTES, emit_event, encode_event
from worker_lock import worker_lock


def invoke(tmp_path, code):
    with worker_lock(tmp_path / 'lock') as fd:
        return supervisor.run_supervised([sys.executable, '-c', code], cwd=tmp_path,
            log_path=tmp_path / 'events.jsonl', lock_fd=fd, timeout=5, grace=0.05)


def test_event_schema_is_bounded():
    line = encode_event('process_finished', exit_code=-9, timed_out=True, elapsed_ms=123)
    record = json.loads(line)
    assert set(record) == {'schema', 'recorded_at_utc', 'event', 'exit_code', 'timed_out', 'elapsed_ms'}
    assert len(line.encode()) <= MAX_EVENT_BYTES
    assert line.count('\n') == 1


@pytest.mark.parametrize('field', ('message', 'request', 'environment', 'headers', 'argv', 'token'))
def test_unapproved_fields_rejected_before_write(field):
    stream = io.StringIO()
    with pytest.raises(ValueError) as error:
        emit_event(stream, 'process_launch_requested', **{field: 'SYNTHETIC_PRIVATE_MARKER'})
    assert stream.getvalue() == ''
    assert 'SYNTHETIC_PRIVATE_MARKER' not in str(error.value)


@pytest.mark.parametrize('event', ('unknown', 'process_finished\n{"forged":true}', '', None, 3))
def test_invalid_event_rejected(event):
    with pytest.raises(ValueError):
        encode_event(event)


@pytest.mark.parametrize('changes', (
    {'exit_code': True}, {'exit_code': 'SYNTHETIC_PRIVATE_MARKER'}, {'exit_code': 2**31},
    {'elapsed_ms': -1}, {'elapsed_ms': float('nan')}, {'elapsed_ms': True}, {'elapsed_ms': 2**63},
    {'timed_out': 1}, {'timed_out': 'false'},
))
def test_outcome_types_rejected(changes):
    fields = {'exit_code': 0, 'timed_out': False, 'elapsed_ms': 1}
    with pytest.raises(ValueError):
        encode_event('process_finished', **{**fields, **changes})


def test_launch_error_code_is_fixed():
    with pytest.raises(ValueError):
        encode_event('process_launch_failed', error_code='SYNTHETIC_PRIVATE_MARKER')
    assert json.loads(encode_event('process_launch_failed', error_code='PROCESS_START_FAILED'))['error_code'] == 'PROCESS_START_FAILED'


@pytest.mark.parametrize('kind', ('short', 'write_error', 'flush_error'))
def test_event_io_errors_propagate_without_fallback(kind):
    stream = Mock()
    if kind == 'short':
        stream.write.return_value = 0
    elif kind == 'write_error':
        stream.write.side_effect = OSError('synthetic write failure')
    else:
        stream.write.side_effect = lambda text: len(text)
        stream.flush.side_effect = OSError('synthetic flush failure')
    with pytest.raises(OSError):
        emit_event(stream, 'process_launch_requested')


def test_raw_stdout_stderr_arguments_and_environment_not_persisted(tmp_path, monkeypatch):
    monkeypatch.setenv('SYNTHETIC_LOG_SECRET', 'SYNTHETIC_ENV_PRIVATE')
    code = "import os,sys; print('SYNTHETIC_STDOUT_PRIVATE'); print(os.environ['SYNTHETIC_LOG_SECRET']); sys.stderr.buffer.write(b'\\xffSYNTHETIC_STDERR_PRIVATE\\n')"
    result = invoke(tmp_path, code)
    assert result.returncode == 0
    log = tmp_path / 'events.jsonl'
    text = log.read_text()
    assert all(marker not in text for marker in ('SYNTHETIC_STDOUT_PRIVATE', 'SYNTHETIC_ENV_PRIVATE', 'SYNTHETIC_STDERR_PRIVATE'))
    assert len(text.encode()) <= 2 * MAX_EVENT_BYTES
    assert len(text.splitlines()) == 2
    assert stat.S_IMODE(log.stat().st_mode) == 0o600


def test_large_child_output_does_not_become_log_payload(tmp_path):
    result = invoke(tmp_path, "import sys; sys.stdout.write('SYNTHETIC_PRIVATE' * 100000)")
    assert result.returncode == 0
    assert (tmp_path / 'events.jsonl').stat().st_size <= 2 * MAX_EVENT_BYTES


def test_initial_log_failure_does_not_launch_child(tmp_path, monkeypatch):
    launch = Mock(side_effect=AssertionError('child must not start'))
    monkeypatch.setattr(supervisor.subprocess, 'Popen', launch)
    monkeypatch.setattr(supervisor, 'emit_event', Mock(side_effect=OSError('synthetic log failure')))
    with pytest.raises(OSError):
        invoke(tmp_path, 'pass')
    launch.assert_not_called()
    assert (tmp_path / 'events.jsonl').read_bytes() == b''


def test_completion_log_failure_occurs_after_cleanup(tmp_path, monkeypatch):
    real_emit = supervisor.emit_event
    real_cleanup = supervisor._cleanup_group
    cleaned = []
    def cleanup(process, grace):
        real_cleanup(process, grace)
        cleaned.append(process.poll())
    def emit(handle, event, **fields):
        if event == 'process_finished':
            raise OSError('synthetic terminal write failure')
        real_emit(handle, event, **fields)
    monkeypatch.setattr(supervisor, '_cleanup_group', cleanup)
    monkeypatch.setattr(supervisor, 'emit_event', emit)
    with pytest.raises(OSError):
        invoke(tmp_path, "print('SYNTHETIC_PRIVATE')")
    assert cleaned == [0]
    assert 'SYNTHETIC_PRIVATE' not in (tmp_path / 'events.jsonl').read_text()


def test_launch_failure_records_only_fixed_code(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor.subprocess, 'Popen', Mock(side_effect=FileNotFoundError('SYNTHETIC_PRIVATE_PATH')))
    with pytest.raises(FileNotFoundError):
        invoke(tmp_path, 'pass')
    text = (tmp_path / 'events.jsonl').read_text()
    records = [json.loads(line) for line in text.splitlines()]
    assert records[-1]['event'] == 'process_launch_failed'
    assert records[-1]['error_code'] == 'PROCESS_START_FAILED'
    assert 'SYNTHETIC_PRIVATE_PATH' not in text

"""Bounded allowlisted supervisor events; never accept raw diagnostic text."""

import json
from datetime import datetime, timezone

SCHEMA = "sourceprism-process-event/1"
MAX_EVENT_BYTES = 512
EVENT_FIELDS = {
    "process_launch_requested": frozenset(),
    "process_launch_failed": frozenset({"error_code"}),
    "process_finished": frozenset({"exit_code", "timed_out", "elapsed_ms"}),
}


def encode_event(event, **fields):
    """Reject arbitrary payloads; no messages, arguments, paths or environment."""
    if type(event) is not str or event not in EVENT_FIELDS or set(fields) != EVENT_FIELDS[event]:
        raise ValueError("Unsupported process event or fields.")
    if event == "process_launch_failed" and (
        type(fields["error_code"]) is not str or fields["error_code"] != "PROCESS_START_FAILED"
    ):
        raise ValueError("Unsupported process error code.")
    if event == "process_finished":
        if type(fields["exit_code"]) is not int or not -(2**31) <= fields["exit_code"] < 2**31:
            raise ValueError("Invalid process exit code.")
        if type(fields["timed_out"]) is not bool:
            raise ValueError("Invalid timeout outcome.")
        if type(fields["elapsed_ms"]) is not int or not 0 <= fields["elapsed_ms"] < 2**63:
            raise ValueError("Invalid elapsed time.")
    record = {
        "schema": SCHEMA,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "event": event,
        **fields,
    }
    payload = json.dumps(record, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n"
    if len(payload.encode("utf-8")) > MAX_EVENT_BYTES:
        raise ValueError("Process event exceeds its size limit.")
    return payload


def emit_event(handle, event, **fields):
    """Write/flush or raise; never fall back to raw output or another stream."""
    payload = encode_event(event, **fields)
    written = handle.write(payload)
    if written != len(payload):
        raise OSError("Incomplete process event write.")
    handle.flush()

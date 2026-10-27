# Structured-only supervisor logging - slice 1

Prepared 2026-10-27. Base: 62f684dfda29764a201da44f65af31a2e3e68bff.
Status: LOCALLY VALIDATED CANDIDATE.
Branch: fix/m1-safe-log-defaults-20261027-zq5cj__9
Evidence: m1-safe-log-slice1.wn38zd4k

## Approved policy and this first implementation boundary

Structured events are the default; unrestricted raw child output is not saved.
process_supervisor now directs child stdout and stderr to DEVNULL, not a file or
pipe. This intentionally removes automatic detailed subprocess diagnostics.
The existing log_path now stores JSONL lifecycle events, not renderer text.
Only launch-requested, fixed-code launch-failed and finished outcomes are allowed.
No free-form messages, requests, arguments, paths, environment or headers are accepted.
Finite typed outcomes and JSON serialization prevent arbitrary event/line injection.
Each event is at most 512 bytes; each ordinary invocation emits at most two events.
The log remains exclusively created with mode 0600. Caller workspace/access
assumptions remain; this slice does not chmod arbitrary existing directories.
There is no raw fallback if event writing/validation fails.

## Process behavior preserved

Argument-list execution, shell=False, inherited ownership descriptor, fresh log,
exit code, timeout and existing process-group cleanup are retained. Initial log
failure stops before launch. Terminal log failure propagates after cleanup.
Launch failures emit a fixed event code, not exception text, then propagate.
Existing caller exception handling is not converted into a universal sanitizer.
The three old assertions expecting child text in logs are deliberately replaced;
new regressions require that stdout, stderr, argument and environment markers
are absent. Ownership and shell-safety checks remain.

## Actual local validation

Focused JUnit: {"errors": 0, "failures": 0, "skipped": 0, "tests": 69}
New safe-log cases: 30, included in the total, not additional.
Checks before final whitespace check: [{"exit_code": 0, "name": "focused-logging-regressions"}, {"exit_code": 0, "name": "pinned-ruff"}]
Targets: tests/test_safe_logging.py, tests/test_process_supervisor.py, tests/test_process_supervisor_integration.py, tests/test_job_worker.py, tests/test_worker_once.py
Assistant preparation sandbox separately passed 41 synthetic cases; those are
not added to local or hosted results. No real report or analytical data is used.

## Remaining scope; do not overclaim M1-12 closure

Optional sanitized private diagnostic capture/export is NOT implemented here.
No generic token/PII detector, global console/CI redactor, log-file-count retention,
rotation or automatic purge is implemented. Historical raw logs and accepted
reports remain untouched. Other CLI/renderer/CI output paths remain outside
this supervisor boundary. Full approved logging policy needs the remaining
route dispositions and later narrowly scoped work; no mandatory requirement
is waived. The cache code inventory includes Python helpers, so future custom
request keys may change; no cache migration/deletion or analytical change occurs.
No renderer, template, data, lockfile, user-facing error code or published
artifact contract is changed by this slice.

M0 and M1 owner decisions remain PENDING. No deployment or M2 work is included.
No staging, commit, push, PR, workflow dispatch, installation, broad suite or
report render is performed by this implementation helper. Synthetic child
processes in focused tests are intentional, not production report runs.

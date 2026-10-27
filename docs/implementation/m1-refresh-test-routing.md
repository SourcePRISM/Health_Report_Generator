# Refresh workflow test-runtime routing correction

Prepared: 2026-10-27.
Status: LOCALLY VALIDATED CANDIDATE.
Base: 49b0e1f6e43dd6f3431f73e65dc6dfa8338b9cce.
Local branch: fix/m1-refresh-test-routing-20261027-ayxh66n9.

## Source-confirmed integration gap

The refresh workflow ran unfiltered python -m pytest -q, unlike the validation
workflow's Python-only selection. This collected the marked R/Quarto fixtures.
The restore script installs into repository .r-library, while those fixtures
launch Rscript --vanilla and explicitly add the container /opt library path.
The refresh test step did not explicitly wire the restored library into that
fixture. This is a routing/environment-wiring finding, not an observed live
refresh failure or proof that all possible runner libraries are absent.

## Bounded correction

Change only the refresh general Python test command to:
python -m pytest -q --strict-markers -m "not r_quarto"

The required validation container job remains the explicit execution gate for
the nine marked context cases. No test assertion, marker or container gate is
removed or weakened. This refresh selection deselects those cases; it does
not report them as passed, nor introduce silent pytest skips. Native refresh
report builds, verification, data download/commit/push and artifact steps are
unchanged. The local helper does not execute those workflow steps.

A new two-case contract covers both validate/fast and refresh/refresh. It
requires strict markers, the exact exclusion, no extra file/test deselection,
and no per-step bypass or failure suppression. The earlier container-routing
contract remains unchanged and is included in focused validation.

## Retained local evidence

Sync receipt: m1-postcache-sync.yh501rg9/sync-result.json
SHA-256: b2616fdd43e3872e8770d3a63661273b3f5222b7772ba50eedd3a7fb657a215b
Evidence directory: m1-refresh-routing._mci3de6

Negative control: the new contract against the original workflow produced
{"errors": 0, "failures": 1, "skipped": 0, "tests": 2}. Only the refresh case failed, as expected.
This is a structural routing-contract reproduction, not a live R/package failure.

After correction, focused CI/container contracts produced:
{"errors": 0, "failures": 0, "skipped": 0, "tests": 20}
The two new routing cases are included in that total, not added to it.
Marked context cases collected: 9. No R/Quarto cases were executed
in this local routing batch; existing hosted evidence is separate.
Command outcomes before the final whitespace check:
[{"exit_code": 1, "name": "original-routing-contract"}, {"exit_code": 0, "name": "focused-ci-contracts"}, {"exit_code": 0, "name": "ruff"}, {"exit_code": 0, "name": "marked-context-collection"}]

## Boundaries

No workflow dispatch, data download, data commit/push, package installation,
report rendering or real analytical calculation was invoked by the helper.
No staging, commit or remote write is authorized by this candidate batch.
The original detached audit worktree is preserved.

This is not a repair to general fixture library portability, a live refresh
acceptance result, selected-report completeness verification, all-route atomic
publication, a requirement waiver or milestone acceptance.

M0 owner decision: PENDING. M1 owner decision: PENDING.

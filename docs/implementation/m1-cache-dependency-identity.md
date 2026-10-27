# Custom-report cache dependency identity correction

Prepared: 2026-10-27.
Status: LOCALLY VALIDATED CANDIDATE.
Base: ce6f8b7fb619d0e95d9ab73a0643705bf1363374.
Local branch: fix/m1-cache-dependency-identity-20261027-9d2ym4t7.
No staging, commit, remote write or milestone acceptance is recorded by this step.

## Reproduced finding

The retained synthetic probe used the actual request_key() implementation.
With request and snapshot fixed, changes to pathogen_class.csv, .Rprofile,
renv.lock and Snakefile each left the key unchanged. Three covered-file controls
changed it. This establishes cache dependency-identity omissions, not a wrong
real report or executed rendering/analysis defect.

Probe receipt: m1-cache-identity-probe.tlc745ws/cache-identity-probe-result.json
SHA-256: 4971e53c1d5bf3817a6520df115e9f832aee6188435ef42dbddca0d13146b703

## Minimal correction

Add only those four files to the existing explicit TOOLCHAIN_FILES inventory.
Keep the existing component names, cache version, normalized request, snapshot
identity, code selector and on-disk cache layout unchanged. The inventory's
existing name covers explicit report/workflow dependencies as well as package
manifests; the new comment makes this scope explicit.

The expanded toolchain hash changes newly computed request keys. Old entries
remain on disk and continue to be readable under their old keys; corrected
requests do not select those keys. No deletion, migration or fallback to the
old key is introduced. Missing declared dependency files fail closed.

No classification data, R startup content, R/package locks, workflow code,
analytical calculations or publication handoff implementation is modified.
Fixture mutations affect disposable copies only.

## Focused validation in this batch

Retained evidence directory: m1-cache-correction.9m6j9t3c
Test targets: tests/test_request_cache.py and tests/test_custom_report.py.
JUnit totals: {"errors": 0, "failures": 0, "skipped": 0, "tests": 23}
Required new case counts: {"test_declared_dependency_change_invalidates_cached_report": 4, "test_existing_cache_dependency_control_still_invalidates": 3, "test_missing_declared_cache_dependency_fails_closed": 4}
Command outcomes: [{"exit_code": 0, "name": "cache-custom-regressions"}, {"exit_code": 0, "name": "ruff"}]

Four new cases require dependency changes to invalidate a synthetic cached
report, while preserving the old entry. Four require missing declared files
to fail closed. Three preserve covered-file invalidation controls. These are
fixture regressions, not report builds or a whole-suite count.

No R, Quarto, Snakemake report build or real analysis is invoked. Existing
publication/render evidence is not rerun merely to increase passing counts.
No runtime environment is installed or modified by the helper.

## Boundaries

This closes the four demonstrated omissions only if the recorded validation
is successful. It is not a claim of complete executed-dependency coverage for
every route, complete runtime identity, all-route atomic publication, blanket
output safety or logging/redaction closure. Further dependencies remain subject
to the route-level audit; no requirement waiver is implied.

M0 owner decision: PENDING. M1 owner decision: PENDING.
No deployment, model integration or M2 feature is authorized by this correction.

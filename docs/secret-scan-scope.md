# Secret-scan revision scope (proposed correction)

The ordinary validation gate scans all commits reachable from the checked-out
HEAD, including merge parents. It is not a latest-commit or diff-only scan.
Keep fetch-depth: 0 and the existing secrets check name.

For pull-request validation, retain the workflow's tested merge checkout.
Do not replace it with a feature-only checkout to avoid base-branch history.
Findings on unrelated fetched refs do not belong to this ancestry-scoped gate.

Broader repository-history audit coverage is a separate policy obligation.
The approved policy and implemented audit entry point are recorded below.
Local fixture tests do not establish that the real repository is clear.

Gitleaks remains pinned to 8.30.1 with its existing archive checksum.
Default rules, full redaction, failure on findings and temporary cleanup remain.
No generated baseline, broad path/rule exclusion, dependency change or workflow bypass is added. The explicitly approved audit exceptions are documented below.

## Offline acceptance tests

Set GITLEAKS_TEST_ARCHIVE to the previously downloaded pinned release archive
and run pytest -q tests/test_secret_scan.py. A missing environment variable
skips integration tests and does not constitute scanner acceptance.
An explicitly configured missing or incorrect archive fails integration setup.

The transport shim copies the local archive instead of downloading it; the
production wrapper still performs its real checksum verification, extraction
and scanner execution. Tests use temporary Git repositories and synthetic
values generated only at runtime. Tests do not need network access.

Cases cover clean history, a deleted reachable finding, an unrelated ref
whose fixture is independently shown detectable, a merge second parent,
an invalid repository, and transport-error propagation. Temporary scanner
cleanup is checked after each wrapper invocation.

Run the existing CI contract tests and lint as well. Scanner acceptance is
not complete when integration tests skip, and is not full M0 acceptance.

## Local regression evidence: 2026-10-24

The first real-wrapper run returned six passed and one failed. The
invalid-repository fixture unexpectedly returned success with no findings.
That result was not accepted as scanner clearance.

The wrapper now requires Git repository discovery and verification that
HEAD resolves to a commit before downloading or invoking Gitleaks.
A repository with no committed HEAD is an error, not a clean scan.
An empty-repository regression test was added.

The corrected local run used Python 3.11.6, pytest 8.3.5 and Gitleaks 8.30.1.
All eight tests passed, with no skips, in 3.97 seconds. Bash syntax and
Ruff 0.14.0 checks of the test file also passed.

The scanner download transport was replaced only inside the test fixture
with a local archive copy. The production wrapper's checksum verification,
archive extraction, scanner execution and temporary cleanup were exercised.

This section records an earlier local regression checkpoint, not successful
CI, full pipeline verification, independent review or M0 completion.
Subsequent contract, lint and full-suite results are recorded below.

## Approved policy and required CI regression execution

The user approved the ancestry-scoped validation gate and separate
broader-history audit policy on 2026-10-24.

The broader audit must cover commits reachable from explicitly fetched
repository branch and tag refs, not deleted/unreachable objects or
unfetched fork history. Repository maintainers own the audit. It is
required before promotion from integration to main, then weekly once
active on the default branch. Scheduled workflows do not execute from
the integration branch merely because a cron entry exists there.

Findings must fail the audit and require classification. The nine
previously reported findings are not automatically excepted or resolved.
No continue-on-error, automatic baseline or automatic suppression is
authorised.

The fast job now invokes scripts/ci/test_secret_scan.sh after its normal
test step. This helper obtains the pinned archive, verifies its checksum,
and invokes the scanner tests with GITLEAKS_TEST_REQUIRED=1. A missing
archive in required mode fails fixture setup rather than skipping.
Local execution can reuse the existing archive; checksum verification
remains mandatory.

This records the approved policy and local CI wiring. The broader audit
implementation is described below; hosted CI execution remains outstanding.

## Broader-history audit entry point

scripts/ci/secret_audit.sh fetches explicit refs/heads/* and refs/tags/*
into a fresh temporary bare repository and scans all history reachable
from those fetched refs. It does not fetch pull-request namespaces,
unreachable objects or other repositories' refs. A source URL/path argument
exists for local fixture testing; production invokes the explicit
SourcePRISM/Health_Report_Generator URL.

The audit retains the pinned scanner/checksum and full redaction.
Fetch errors and sources without reachable commits fail. Temporary
repository and scanner files are cleaned on exit. No exceptions or
baselines are automatically imported.

The separate history-audit workflow defines Monday 07:00 UTC execution
and manual dispatch, with contents: read and no error suppression.
Scheduling requires deployment on the default branch. Before promotion,
maintainers must execute and review an audit of the target repository;
a fixture-only test run does not fulfil that requirement.

New local tests cover clean sources, other branches, tag-only history,
failed fetches, empty sources, and the workflow's failure-visible contract.
Actual repository audit execution and classification of the previously
reported nine findings remain outstanding.

## Subsequent local validation and audit isolation

Before the isolation correction, the scanner slice passed 146 tests and
the combined scanner/runner correction passed 149 tests in 13.88 seconds.
Full-project lint passed for both. The combined Snakemake dry run planned
17 jobs; it did not execute report generation or numerical validation.

The audit now unsets GITLEAKS_CONFIG and GITLEAKS_CONFIG_TOML, runs from its
temporary directory, explicitly selects that directory for ignore-file
lookup, and disables inline gitleaks:allow exemptions. It does not import
the caller's ignore file or rule overrides. The ordinary ancestry gate's
configuration behaviour is unchanged.

A regression test first proves that an ambient allowlist suppresses a
detectable fixture in the ordinary scanner, then requires the broader
audit to detect it despite that override. New test results must be recorded
after execution. Prior working-file hashes are superseded for changed files.

Real repository auditing, classification of the nine findings, hosted CI,
independent review and remaining M0 reproduction evidence are outstanding.

## Explicit fingerprint disposition approved: 2026-10-24

The user explicitly approved nine fingerprint-specific audit exceptions
for the documented cache/request content identities. The approved file is
scripts/ci/secret-audit.gitleaksignore. It contains exactly nine fingerprints;
it does not exclude a path, rule, commit wholesale or new occurrences.
The ordinary ancestry gate does not load this audit-specific file.

Each historical finding contained one 64-character hexadecimal value.
At each finding commit, object_hash matched the inspected canonical SHA-256
implementation and request_key called it with the expected identity
components. Together with the inspected documentation contexts, this was
accepted as evidence for content-identity false positives. Original
experiment inputs were not reconstructed to recompute individual values.
This is an explicit user disposition, not an independent reviewer decision.

The raw diagnostic audit at 2026-10-24T20:17:04Z found nine unique findings,
exactly matching the original set, over 12 fetched branches and two tags.
Git counted 211 reachable commits and 178 non-merge commits. The earlier
Gitleaks summary reported 167 commits scanned; these metrics are retained
separately and their difference is not asserted to be reconciled.
The diagnostic ref-manifest SHA-256 was
cfbfa7d1b32fc4c3813228c2685a2a721fe0e91e4f2f24861afa29c96ede09fb.

The audit explicitly copies only the reviewed sibling exception file into
its temporary ignore location. A missing exception file fails execution.
Caller configuration, caller ignore files and inline exemptions remain
excluded. Tests protect the exact approved set, missing-file failure,
and rejection of an additional finding after one synthetic fingerprint
has been excepted. Post-exception audit results remain to be recorded.
Raw findings remain historical evidence; a future clean result means no
unexcepted findings in its fetched snapshot, not proof of no secrets.

## Post-exception acceptance checkpoint: 2026-10-24

After explicit user approval of the nine content-identity finding
fingerprints, the scanner slice passed 151 tests in 18.32 seconds and the
combined scanner/runner correction passed 154 tests in 17.84 seconds.
Neither summary reported skips. Full-project Ruff checks passed in both.

The reviewed exception file's SHA-256 was verified as
41311ef65f9eb48a2c1cd4d24fa723567af329542223f2fbd3c9217dc585dd47.

An actual audit fetched 12 repository branches and two tags and returned
exit 0 with no unexcepted findings. Gitleaks reported 167 commits and
approximately 325.92 MB scanned in 24.4 seconds. This was a later fetched
snapshot; the earlier diagnostic ref-manifest hash is not asserted to
identify this post-exception snapshot.

The precise result is no unexcepted findings with the nine explicitly
approved fingerprints, not an unconditional absence-of-secrets claim.
Raw nine-finding evidence and the value-reconstruction limitation remain
part of the disposition record.

The combined correction previously passed a Snakemake dry run planning
17 jobs. No report generation, numerical equivalence, rendered-output
verification, browser acceptance or hosted CI success is established
by these corrective checks.

Changes remain subject to staged/committed-content review, hosted checks,
independent human review and explicit publication/merge gates.
M0 remains not achieved. The frozen baseline and release are unchanged.

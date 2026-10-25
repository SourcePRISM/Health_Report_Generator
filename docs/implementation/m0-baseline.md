# M0 baseline inspection and verification status

Observation date: 2026-10-24.
Repository boundary: SourcePRISM/Health_Report_Generator only.
Scope: inspection evidence and approved implementation direction.
This record does not establish M0 achievement.

## Recorded Git identities

| Reference | Observed commit |
|---|---|
| Historical baseline | aaa51f53dc1616de6db9571427c9528d107105cb |
| Refreshed origin/release/v1.0.0 | aaa51f53dc1616de6db9571427c9528d107105cb |
| Locally resolved v1.0.0 tag commit | aaa51f53dc1616de6db9571427c9528d107105cb |
| Refreshed origin/main and local main | 3e81b710fe12ae666dbe1724c8ad5987b6d50c0b |
| Initial local integration/jev-free-product | aaa51f53dc1616de6db9571427c9528d107105cb |
| Initial local milestone/m0-baseline-evidence | aaa51f53dc1616de6db9571427c9528d107105cb |

After an approved fetch, release-to-main divergence was 0 / 32 commits.
The endpoint diff covered 64 files. No remote branch was changed.
The feature worktree was clean before this document was added.
The eventual documentation commit and PR must be recorded separately;
a document cannot identify its own final commit before that commit exists.

## Approved integration decision

The user approved a dedicated integration/jev-free-product branch rooted
at the historical baseline and an explicit exception to CONTRIBUTING.md's
default-branch starting rule.

Small implementation PRs will target that integration branch.
The eventual promotion target is main, subject to separate reconciliation
of its later changes, integration checks, review, and explicit approval.
Do not reset or rewrite main or modify the frozen release branch.
Do not open a baseline-derived feature PR directly against diverged main.

Later worker, queue, publication, and stakeholder-isolation changes in
this repository are candidates for selective review, not automatically
accepted implementations or automatically discarded work.

This approval does not authorise remote branch creation, pushes, PR
creation, installation, deployment, or merging. Those retain separate gates.
Recommend PR review, required checks, resolved conversations, and
destructive-update restrictions for integration and production branches.
Existing protection settings have not been verified.

## Environment observations

| Component | Declared validated version | Observed local state |
|---|---|---|
| Git | Not specified in toolchain.json | 2.53.0 |
| GitHub CLI | Not specified in toolchain.json | 2.46.0; authenticated repository read succeeded |
| Python | 3.11.6; supported >=3.11.6,<3.12 | System 3.14.4; existing managed 3.11.6 verified |
| R | 4.3.2 | 4.5.2 |
| Quarto | 1.3.353 | 1.3.353 |
| uv | 0.8.14 | 0.12.22 |
| Snakemake | Pipeline lock pins 8.30.0 | Host executable reports 7.32.4 |
| TinyTeX | 2026.10 | Not verified; pdflatex, tlmgr, latexmk unavailable on PATH |
| Docker | Required for documented container route | Unavailable on PATH |
| Host | Container route targets Linux/amd64 | Linux x86_64 |

Availability on PATH is not an exhaustive installation inventory.
No dependency installation, environment creation, test, or build was
performed during this inspection. Do not use system Python or host
Snakemake as substitutes for the pinned pipeline environment.
Missing prerequisites do not establish a software test failure.
No model SDK, hosted inference, inference server, or GPU dependency
was introduced. M0-M4 must remain model-free.

## Local inspection commands and observations

Commands were run individually from the repository root unless noted.

```sh
git status --short --branch
git remote -v
git log -1 --format='%H %s'
git --no-pager show aaa51f53dc1616de6db9571427c9528d107105cb:CONTRIBUTING.md
git --no-pager show aaa51f53dc1616de6db9571427c9528d107105cb:README.md
git --no-pager show aaa51f53dc1616de6db9571427c9528d107105cb:.github/workflows/validate.yml
git --no-pager show aaa51f53dc1616de6db9571427c9528d107105cb:workflow/toolchain.json
git --no-pager show aaa51f53dc1616de6db9571427c9528d107105cb:GETTING_STARTED.md
git --no-pager show aaa51f53dc1616de6db9571427c9528d107105cb:scripts/health_pipeline/requirements.lock.txt
git --no-pager show aaa51f53dc1616de6db9571427c9528d107105cb:compose.yaml
git --no-pager show aaa51f53dc1616de6db9571427c9528d107105cb:workflow/config.yaml
git rev-parse 'origin/release/v1.0.0^{commit}' 'refs/tags/v1.0.0^{commit}'
git fetch --no-tags origin
git rev-parse HEAD 'origin/main^{commit}' 'origin/release/v1.0.0^{commit}'
git rev-list --left-right --count origin/release/v1.0.0...origin/main
git --no-pager diff --stat origin/release/v1.0.0 origin/main
git --no-pager diff --name-status aaa51f53dc1616de6db9571427c9528d107105cb origin/main -- data/reference workflow/toolchain.json scripts/health_pipeline/analyse.py scripts/health_pipeline/checks.py scripts/health_pipeline/harmonise.py
```

Historical-file reads are shown with --no-pager; earlier invocations
without it were also used. The targeted name-status diff was empty.
This covers only the named paths and does not prove numerical equivalence.

Current main's contribution instructions, container definitions, and
three workflow definitions were inspected before switching to the baseline.
Version and executable-discovery commands established the inventory above.
Commands listed here are inspection history, not a reproduction script.

## Scientific contracts to preserve

Preserve explicit geography, source priority, completeness, denominator,
classification, exclusions, fixed group membership, and lineage policies
described in docs/scientific-policy.md and the pipeline schema.
Missing baselines must not become zero. Descriptive comparisons must not
be described as significance tests or causal effects.
SKIP, WARN, FAIL, unavailable, and not executed are distinct outcomes.
A successful software run is not scientific or clinical validation.

The older docs/phase-0-baseline.md describes a different historical
commit and environment. Its test counts, snapshot IDs, and numerical
outputs are not current-session verification results.
Outdated clone examples naming another repository were not followed.

## CI inspection limitations

Historical validate.yml defines fast, secrets, container, and full jobs.
Its container job includes an optional UI-image smoke test as well as
report rendering and verification. Current main differs, including a
report-runtime check for absence of Marimo.
Job definitions are not evidence of successful job execution.

Current main's refresh workflow has contents: write and pushes source
snapshots directly to main. It was inspected, not executed or modified.
Its relationship to the agreed branch policy requires separate review.
No workflow, permission, threshold, protection, or allowlist was changed.

## M0 acceptance and evidence tracker

| Criterion / category | Current evidence | Status / next requirement |
|---|---|---|
| Baseline identity | Exact branch, tag, historical commit and ancestry inspected | Identity verified locally; remote protection not verified |
| Schemas, commands, custom reporting, cache, renderers | Documentation and file inventory inspected | Partial; inspect relevant implementations and tests |
| Unit/schema | No execution | Not executed; prepare isolated pinned environment |
| Numerical | No execution or generated fixtures | Not executed; record actual inputs, snapshot IDs, hashes, expected and actual values |
| Integration | No execution | Not executed; exercise pipeline and provenance contracts |
| Rendering | No generated artifacts | Blocked in inspected host setup; qualify a complete environment and use fresh output directories |
| Browser | No interactions exercised | Not executed; test all three audiences, charts, table controls and links |
| Security/concurrency | No execution | Not executed; establish applicable M0 checks without claiming future service acceptance |
| CI | Workflow definitions read only | Not verified; inspect relevant runs, SHAs, job coverage and skipped checks |
| Reproducibility | Versions and Git identity inspected | Incomplete; retain exact commands, inputs, environment and actual outputs |
| Scientific policy | Existing policy read | Documented, not independently scientifically approved |

M0 outcome: not achieved. Environment qualification and execution evidence
are still required. This document records gaps rather than reducing scope.

## First-slice boundaries and recovery

This slice adds documentation only. It changes no analytical policy,
calculation, input data, schema, renderer, dependency, or CI configuration.
Numerical equivalence has not been tested.
Subsequent patch review and checks must be reported separately with the
tested revision and honest blocked/not-executed results.

Keep credentials, private logs, generated reports, and large datasets out
of this record and source control. Recover from documentation mistakes
through a focused corrective PR or explicitly reviewed revert, never
shared-history rewriting. M1 requires a separate milestone approval.

## Follow-up diagnostic evidence: 2026-10-24

This section supplements the initial inspection above. Earlier statements
that checks were not executed describe that initial inspection, not the
follow-up activity recorded here. M0 remains not achieved.

### Revision and CI observations

PR #2 targets integration/jev-free-product at historical baseline
`aaa51f53dc1616de6db9571427c9528d107105cb`. Its inspected feature head was
`d5d2180165e5eb24f4489ac2a3014550e4ac7873` on
milestone/m0-baseline-evidence. Before this follow-up, GitHub reported one
changed file and 161 added lines. PR #2 was open, draft and unmerged.

GitHub check results inspected for that feature head included runs
`40120194669` and `40120293721`. Each returned failure for fast and secrets,
and skipped for container and full. Skipped jobs are not passing tests.
The inspected workflow makes container and full dependent on fast.
Check summaries alone do not establish the precise setup failure or the
fingerprints detected by CI. Exact job-log diagnosis remains necessary
before selecting a Python-provisioning repair.

### Local secret-scanner comparison

The user ran Gitleaks 8.30.1, downloaded from its pinned release and checked
against archive SHA-256
`551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`.
The executable reported version 8.30.1. Both scans used full redaction,
JSON reporting and finding exit code 1. Reports and logs stayed outside
source control; raw matched values were not shared.

| Diagnostic | Revision selection | Exit | Findings |
|---|---|---|---|
| Original local Git-history scan | No explicit --log-opts | 1 | 9 |
| Feature-HEAD ancestry scan | --log-opts=HEAD | 0 | 0 |

The original findings used generic-api-key: eight in
docs/web-job-system.md and one in docs/web-integration-baseline.md.
Their nine unique fingerprints exactly matched the nine entries inspected
in `.gitleaksignore` at commit
`a833be284827aba1f1b2d3b41a61dd53f2119a52`.
No exceptions were added to the feature branch.

For every finding commit, git merge-base --is-ancestor returned false
against both the historical baseline and feature head above. Thus all
nine reported local finding commits were outside feature-HEAD ancestry.
This does not identify the exact CI finding set.

Masked historical contexts described two cache keys and seven request
keys. Source inspected at
`3e81b710fe12ae666dbe1724c8ad5987b6d50c0b` showed request_cache.request_key
hashing validated request, snapshot, code and toolchain components.
common.object_hash computes SHA-256 over deterministically serialised
JSON. This supports a content-identity explanation, but does not prove
each masked historical value was generated by that exact implementation.
report_bundle.verify_bundle validates cache-key format; it does not
recompute the request identity or establish caller authorisation.

After the HEAD-ancestry diagnostic, the user reported a clean working
tree and unchanged feature HEAD
`d5d2180165e5eb24f4489ac2a3014550e4ac7873`.
This is a clean local ancestry-scoped diagnostic, not successful CI,
repository-wide secret clearance or full security/concurrency acceptance.

### Approved corrective sequence and remaining gates

The user approved the proposed implementation order: prepare this evidence
update, prepare separate scanner-policy and exact-version Python repairs,
review their diffs and regression evidence, then obtain approval before
publishing changes or triggering CI. This does not authorise merging.

The proposed ordinary secret gate scans all ancestry of the checked-out
revision, including the tested merge revision on pull-request runs, rather
than unrelated fetched refs. This policy still requires explicit review
and regression tests for reachable historical findings, unrelated refs,
merge-parent findings and scanner errors. Broader history-audit obligations
must be accounted for rather than silently removed. The clean local HEAD
scan alone does not approve a CI coverage change.

Python 3.11.6 and dependency locks must remain unchanged. Verify the exact
job-log failure and compatible runner/provisioning mechanism before
selecting a repair. No particular replacement runner is verified here.

No scanner-policy, workflow, dependency, analytical-code or data change is
part of this evidence update. Functional, numerical, rendering, browser
and full reproducibility requirements remain outstanding. Independent
review and explicit merge approval remain required.

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

## Integration CI execution checkpoint: 2026-10-24

This checkpoint supplements the earlier inspection and diagnostic history.
Earlier not-executed statements describe their respective checkpoints.
M0 remains not achieved.

### Merged correction and local identity

PR #4 merged the scanner correction into fix/m0-python-runner at
d3c93ce7ccae7d08f8f33d8150b550384b55475b.
PR #3 then merged the combined correction into integration/jev-free-product
at 90495b67d07333a22211a696f50b2531df61fa3c.

The integration commit contains the reviewed runner/scanner head and has
tree 3d68582552df719a4decfaaa27f8af21a24359fb, matching the previously tested
combined correction. Local post-merge validation of d3c93ce returned
154 tests passed in 20.15 seconds and successful full-project Ruff checks.
A separate clean detached worktree was created at the integration commit;
the evidence and runner worktrees were preserved.

### Hosted execution and revision attribution

Corrective PR run 40134158847 reported head
d3c93ce7ccae7d08f8f33d8150b550384b55475b but actually checked out GitHub's
pull/3/merge revision fb4b54ee3563bb460337c79a72688cbb274e2d22.
Checkout logs explicitly identify that test merge. Its artifact name
matches that checked-out revision, not the reported PR head.

The supplied PR-run step results showed successful lint, unit/schema/
contract tests, real-wrapper scanner regressions and a Snakemake dry run.
The full build and verification steps succeeded. Inspected log excerpts
confirmed Shiny server checks, dashboard data-label/ggplot2 checks and an
incremental no-op. Container logs showed completion of all 17 pipeline
steps, audience/provenance verification, release-hash/rendered-link
verification, application smoke checks and an incremental no-op.

Integration push run 40135216053 reported head
90495b67d07333a22211a696f50b2531df61fa3c and completed successfully.
All four jobs (fast, secrets, full and container) and all listed steps
returned success, including hosted and container all-audience builds,
output/provenance checks, release verification, application smoke tests
and the hosted no-op rebuild. These integration-run observations come
from run/step metadata; its complete job logs were not inspected here.

### Artifact evidence and limits

PR-run artifact:
- ID: 12575847851.
- Name: health-report-fb4b54ee3563bb460337c79a72688cbb274e2d22.
- Upload log: 276 files, archive size 7317615 bytes.
- Reported archive SHA-256:
  d8d37db37d2dac3dae8587eca0287d17763ec858b751e907e47fdca5bb06789f.

Integration-run artifact:
- ID: 12576732977.
- Name: health-report-90495b67d07333a22211a696f50b2531df61fa3c.
- Metadata: not expired at inspection; archive size 7317587 bytes.
- Reported archive SHA-256:
  4210597ad9e1e0efc98934a9c3b0002a3ef0ab9d850978c2607ab9c9abb6b20a.

These are reported archive digests, not independently recomputed local
digests or numerical-result hashes. The archives were not downloaded,
unpacked or compared in this checkpoint. Their differing digests are
not assigned a cause and do not establish numerical equivalence or failure.

### Remaining acceptance

Successful hosted builds and automated output checks are now evidenced;
the earlier absence of hosted execution evidence no longer describes
this corrective integration checkpoint.

Still outstanding are explicit historical-baseline numerical comparison
with recorded inputs, snapshot identities and expected/actual results;
independent artifact/provenance inspection; browser-based acceptance of
the supported audience journeys; remaining applicable M0 security and
concurrency checks; and independent human review.

The ancestry-scoped secrets gate is not a replacement for the separate
branch/tag history audit. The audit's weekly schedule is not active
default-branch coverage while present only on the integration branch.

No M0 completion, M1 approval, promotion to main, protection change or
frozen-release modification is established by this checkpoint.

## Reproduction and manual acceptance checkpoint: 2026-10-25

This section supplements the earlier chronological observations. It records
later execution evidence and user-reported manual checks without rewriting
the earlier inspection history. M0 has not been declared complete.

### Merged integration and hosted checks

PR #2 merged the evidence into integration/jev-free-product at
47de6ab1e15c98b1efc18c33f26ffb4481342862.
Its tree was verified as
4ee65fb7dea46ffafb537663eb80adeafd0c3c86.

Integration push run 40137364011 completed successfully for that exact
head. All four jobs (fast, secrets, full and container) returned success.
This final checkpoint was supplied as run/job metadata; it is not a claim
that every complete log and artifact from this run was independently read.

The preceding evidence-head runs 40136574569 and 40136577943 also returned
success for all four jobs. Their results remain distinct from the merged
integration run.

### Independent artifact and snapshot verification

Artifact 12576732977 belongs to earlier integration run 40135216053 at
90495b67d07333a22211a696f50b2531df61fa3c, not the later evidence merge.

The downloaded archive was independently hashed and matched SHA-256
4210597ad9e1e0efc98934a9c3b0002a3ef0ab9d850978c2607ab9c9abb6b20a.
It contained 276 file entries and 61703385 uncompressed bytes.
All 106 file hashes listed in release.json were independently recomputed
and matched. This statement covers the release-listed files, not a claim
that the release manifest lists every archive entry.

The frozen snapshot identity was
d0709708a8057815801497701bfaa145017979f1ecace4508ae46237438573ee,
with 168 snapshot file records. Snapshot verification was exercised by
the archived-input pipeline builds. No live data acquisition was run.

### Fresh historical-baseline numerical comparison

Separate detached worktrees were used for:
- Historical baseline: aaa51f53dc1616de6db9571427c9528d107105cb.
- Current integration: 47de6ab1e15c98b1efc18c33f26ffb4481342862.

Using the existing isolated Python pipeline environment and Snakemake
8.30.0, each revision ran the tables target into a separate fresh output
directory using the same extracted artifact snapshot.json. Both builds
completed all six workflow steps; this was table generation, not fresh
local HTML/PDF rendering.

For researcher, health_institution and public, the comparison covered:
series.csv, metrics.csv, lineage.csv, selection.csv, sources.csv,
checks.csv, snapshot.json, stakeholder.json, pathogen_class.csv and
bundle.json.

All 30 corresponding files matched byte-for-byte across the fresh
baseline output, fresh integration output and hosted artifact.
There were zero mismatches; no tolerance was introduced.

The comparison CSV records audience, filename, baseline SHA-256,
integration SHA-256, artifact SHA-256 and equality. Its independently
recorded SHA-256 is
7efeea42223ccd023db553e1302bc8a693853ab7ae0a7a45d7ef84cb9a23d8a4.
Build logs, generated outputs and the comparison CSV remain in the local
temporary evidence directory; they are not committed with this document.
A checksum alone cannot recover those files: durable evidence retention
remains to be resolved before relying on their continued availability.

This establishes exact compatibility for the tested snapshot and standard
audience configurations. It does not establish scientific validity,
universal input coverage or equivalence of rendered document bytes.
Matching each audience across revisions is not a claim that differently
configured audiences have identical bundles.

### User-reported browser and Shiny checks

The user confirmed successful opening/rendering of report HTML, methods
HTML and PDFs in the exercised scope. The public report's collapsed
comparison table was located and its expansion, filtering and sorting
were subsequently reported as passing.

The inspected public HTML contained that disclosure and table controls.
Its charts are embedded static images; hover/zoom is not implemented by
that renderer. No such chart interaction is counted as a passed test.
The initially difficult-to-find table disclosure is usability feedback.

The user subsequently reported that the exercised packaged Shiny
interactions worked, including the calculation-trace selection.
This is user-reported manual evidence, not an automated browser run.
Audience-by-audience coverage, browser version and exact viewport were
not recorded. Do not infer that all three audience apps were individually
tested or that this constitutes independent reviewer approval.

The selected local image was
sha256:5638b536d2c47824dbea83040ffd3f4fcd4d82abc3a09dd028ed1518c05a3bf2.
Inspection reported R 4.3.2 and the required Shiny packages available.
An initial literal-string comparison falsely flagged four versions
because packageVersion prints numeric components with dots rather than
the hyphen spellings in renv.lock. The revised preflight compares R
package_version objects and gates application startup on version equality.
The subsequently supplied startup output reported R 4.3.2, 48 locked
packages checked, zero version mismatches or missing packages, and a
successful version preflight. Shiny then reached its listening state on
container port 8766. The launch command mapped that port to host loopback
only. The transcript subsequently shows Ctrl-C interrupts followed by
Execution halted; that ending is not evidence of an application crash
during the reported browser checks.

These observations establish the version preflight and successful startup,
not complete image-build provenance or an unattended stability test.

### Open rendering finding: Shiny calculation-trace overflow

Status: open baseline limitation; focused M1 correction candidate.
Functional metric selection passes at the reported scope, but visual
table containment fails.

In Methods & sources, Follow a calculation, the lineage table for
gonorrhea · count · 2024 extends beyond the white panel. Long sha256 and
metadata_sha256 content makes the overflow visible. A user-supplied
screenshot confirms this example; it is not attached to this document.
Similar overflow was reported for other wide metrics, including
gonorrhea · population · 2022. The finding is not confined to one metric.

Expected correction:
- Contain both metric-value and lineage tables at narrow and wide widths.
- Preserve all identifiers, hashes, formulas, inputs_json and source links.
- Consider horizontal scrolling inside the panel; do not hide overflow
  or destructively truncate audit values.
- Test short-to-long metric switching and complete CSV downloads.
- Preserve numerical values and reactive behaviour.
- Inspect app.R and dashboard.css before selecting a minimal patch.
- Regenerate fresh packages for regression tests; do not edit the verified
  artifact or frozen release.

No implementation or passing regression for this defect is claimed.
Creating a GitHub issue was attempted with user approval but returned
HTTP 410 because Issues are disabled. No issue was created and repository
settings were not changed. This section retains the finding instead.

### Acceptance boundaries and next gate

The later evidence now establishes successful integration CI, independent
artifact checks, scoped baseline numerical reproduction and user-reported
manual interaction checks. The layout failure remains explicit.

Remaining review includes evidence retention, complete audience/browser
coverage records, applicable baseline inspection gaps and an independent
reviewer decision. Earlier security/concurrency limitations must not be
silently converted into claims of multi-user service acceptance.

M0 closure requires an explicit acceptance decision with known limitations.
M1 implementation requires separate milestone approval. No main promotion,
deployment, scientific approval, protection change or frozen-release
modification is authorised by this documentation checkpoint.

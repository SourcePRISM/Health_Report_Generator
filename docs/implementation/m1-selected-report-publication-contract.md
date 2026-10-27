# Selected-report publication contract - subchunk 1

Prepared: 2026-10-27.
Status: LOCALLY VALIDATED STANDALONE CANDIDATE.
Base: ad429d7617c70c6068b21afb1fa239b1ad97a40d.
Local branch: fix/m1-selected-publication-20261027-ij1ctw5l.
The selected-report workflow is unchanged. The publication gate is NOT wired
into that workflow by subchunk 1; that is reserved for subchunk 2.

## Supported artifact layout

Required nonempty regular files: report.html, methods.html, report.pdf,
methods.pdf, provenance.json, provenance-pdf.json and data/bundle.json.
The data inventory must include all nine files emitted by analyse.py and
record every regular data file other than bundle.json. Inventory hashes,
stakeholder and snapshot identities are verified. Symlinks and non-regular
entries are rejected throughout the artifact root.

Do not substitute provenance.pdf.json, require release.json or invent a
request_provenance.json/cache key: those belong to other route contracts.

## Request and provenance binding

The caller must independently supply request ID, audience, the ordered unique
selected dataset-ID list and source-run ID. Expected identity is never inferred
from sidecars alone. HTML/PDF sidecars must match these inputs, saved effective
parameters, stakeholder metadata, filters, bundle inventories and snapshot
references. Both HTML pages must contain exactly one equal HTML provenance
record. Per-format output identity is checked; different render timestamps
are allowed. Null retrieval metadata is not invented or treated as a date.

The declared template, four helper and selected-workflow fingerprints are
compared with the checked-out source. This does not verify every executed
application/runtime dependency or authenticate independently supplied records.

## Resource checks and API behavior

The verifier reads a trusted local, stable private artifact directory, returns
file hashes and writes nothing. It invokes no subprocesses, renderer or network
requests. The CLI exits nonzero on contract failure and requires expected
identity arguments. No verification receipt is written into the artifact.

HTML href/src/poster references are checked for containment, local existence
and HTML anchors. HTTP(S)/protocol-relative resource attributes are rejected;
ordinary external HTTP(S), mailto and tel hyperlinks are not fetched. Data
URIs are permitted. HTML base elements and unsupported schemes are rejected.
This is not complete CSS, JavaScript, srcset, SVG or embedded-document analysis;
it does not provide a browser execution/sanitization guarantee.

PDF checks require nonempty files with a %PDF- header. Synthetic PDF fixtures
are deliberate header-only stubs, not claimed to be fully valid PDFs. No full
PDF parse, visual inspection or scientific verification is performed.

## Local validation in this subchunk

Audit sync receipt: m1-postrefresh-sync.56arm564/sync-result.json
SHA-256: 4c4108829304c0844c2815607cc96b7eb0384df9109f976754e36a737983579e
Evidence directory: m1-selected-subchunk1.49ip_kpu
Focused JUnit totals: {"errors": 0, "failures": 0, "skipped": 0, "tests": 96}
Command outcomes before final whitespace check: [{"exit_code": 0, "name": "selected-verifier-tests"}, {"exit_code": 0, "name": "ruff"}]

Coverage includes valid read-only verification and CLI behavior, missing and
empty files, malformed/duplicate/nonfinite JSON, expected-identity mismatches,
sidecar and bundle tampering, embedded-record disagreement, unsafe inventories,
references/anchors, symlinks and a non-regular entry. All data are synthetic.
The preparation sandbox smoke result is retained separately; it uses synthetic
source-file stubs and is not added to local or hosted test totals.

No real selected artifact was rendered or compatibility-qualified in this step.
Existing rendered artifact verification, any targeted render check and workflow
integration remain separate work; synthetic success does not establish them.

## Boundaries

No workflow dispatch, data download, package install, R/Quarto/Snakemake render,
real analysis, broad-suite rerun, staging, commit or remote write is performed
by this subchunk. Existing application files and workflows remain unchanged;
the original detached audit worktree is preserved.

Subchunk 2 will wire the verified candidate into the selected workflow, add
focused workflow integration checks and configure missing uploads to fail.
No artifact publication protection is claimed until that gate is integrated.
M0 owner decision: PENDING. M1 owner decision: PENDING.


## Subchunk 2 integration checkpoint - 2026-10-27

Status: LOCALLY VALIDATED WORKFLOW-GATE CANDIDATE.
The subchunk-1 checkpoint above remains historical. The workflow is now wired
in this local candidate only; no remote publication protection is claimed
before the candidate is reviewed, committed and merged.

Subchunk-1 receipt: m1-selected-subchunk1.49ip_kpu/selected-subchunk1-result.json
SHA-256: 18aecf6ae32595337a69f2a967f4a7e8bc03feeeda9d2e8e8219afdd57aa04ac
Evidence directory for this integration: m1-selected-subchunk2.mh9_nveq

The selected workflow now invokes verify_selected_report.py immediately after
rendering and immediately before upload. Expected identity comes from workflow
input environment variables, passed as quoted CLI arguments. The upload uses
if: success() and if-no-files-found: error. Verification has no conditional
bypass or continue-on-error. Workflow permissions, dispatch inputs, action pins,
lineage download, rendering and artifact name/path/retention are unchanged.
Verifier bytes from subchunk 1 are unchanged.

Actual focused JUnit totals: {"errors": 0, "failures": 0, "skipped": 0, "tests": 123}
Selected verifier/workflow cases: 106; new integration cases:
10. These are included in the totals, not added to them.
Command outcomes before final whitespace check: [{"exit_code": 0, "name": "selected-and-ci-contracts"}, {"exit_code": 0, "name": "ruff"}]

Integration evidence includes the actual parsed workflow contract, seven
negative configuration mutations, and Bash argument/exit-status checks using
a fake verifier in a disposable fixture. The latter preserves JSON containing
spaces and shell-looking strings as one argument and propagates exit code 7.
It does not dispatch Actions or simulate a successful provider upload.
The prior 96 verifier cases are rerun because the workflow source fingerprint
changed; the existing CI contracts are included for the modified workflow.

This remains synthetic local validation, not real selected-report compatibility,
PDF visual/analytical acceptance, a selected workflow run or a hosted CI result.
No workflow dispatch, data download, real report rendering/analysis, installation,
broad-suite rerun, staging, commit, push, PR or merge is performed by this step.
M0 and M1 owner decisions remain pending.

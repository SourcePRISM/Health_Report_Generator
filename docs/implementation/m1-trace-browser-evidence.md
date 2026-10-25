# M1 calculation-trace browser evidence checkpoint

Observation date: 2026-10-25.
Repository: SourcePRISM/Health_Report_Generator.
Scope: the calculation-trace containment correction and its local browser evidence.
This checkpoint does not establish completion of M1 or independent review.

## Relationship to earlier records

The historical finding and acceptance boundaries remain in
[m0-baseline.md](m0-baseline.md). Its earlier open-finding statements describe
that checkpoint; this document supplements rather than rewrites that history.

[PR #6](https://github.com/SourcePRISM/Health_Report_Generator/pull/6)
contains the focused containment correction. Its evidence comments record
[the initial researcher run](https://github.com/SourcePRISM/Health_Report_Generator/pull/6#issuecomment-6397169728)
and [the reconciled three-audience result](https://github.com/SourcePRISM/Health_Report_Generator/pull/6#issuecomment-6397672101).

The user executed the local harness and reconciliation script in Ubuntu/WSL
and supplied their outputs. These are user-executed local results, not an
independently executed review or hosted browser-test run.

## Tested identity and environment

- Fix commit: be1a774443c34bc16ce2db1d53e56170a753ca68.
- Integration commit used for source verification:
  66a58cc2ae3dd520cdae359b84e62ec859040418.
- Playwright: 1.64.1; Chromium: 156.0.8078.4.
- Existing R image:
  sha256:5638b536d2c47824dbea83040ffd3f4fcd4d82abc3a09dd028ed1518c05a3bf2.
- Browser-test image:
  sha256:f80baca45d66d084d9eb9c74459091eb921b0cc231ff51dde4cfc3b2ccb9615b.

Each run reverified package and bundle file hashes and all six presentation
files against the integration commit. The app package was mounted read-only.
Temporary Shiny and browser containers communicated on an internal Docker
network without published host ports. Only the new browser-results directory
was mounted writable in the browser container. No report regeneration, image
rebuild, dependency installation, or verified-artifact modification was part
of these browser runs. Complete R image-build provenance is not established.

## Reconciled browser scope and results

Metric: gonorrhea:2024:count, labelled gonorrhea · count · 2024.
Viewports: 1440 × 900 and 390 × 844 for each audience.

| Audience | Result | Recorded assertions | Saved CSV downloads reverified | Cleanup |
|---|---|---:|---:|---|
| researcher | PASS | 36 | 4 | complete, exit 0 |
| health_institution | PASS | 36 | 4 | complete, exit 0 |
| public | PASS | 36 | 4 | complete, exit 0 |

The total is 108 recorded assertions and 12 saved CSV downloads across six
audience/viewport combinations, not 108 independent scenarios. Two
metric-value hash assertions per audience had no expected hashes; those six
assertions were empty hash-preservation checks.

The harness checks trace-region and panel containment, keyboard focus and
focus outlines, horizontal keyboard movement where overflow exists, separate
programmatic reachability of the maximum horizontal scroll position,
rendered lineage hash preservation, and byte-identical metrics.csv and
lineage.csv downloads. A narrow viewport was required to exercise overflow.
Desktop metric values did not overflow, so scrolling was not applicable to
that region at that viewport. Screenshots were retained, not independently
visually reviewed.

The reconciliation reread all summaries and cleanup records, required passing
assertions and the expected audience/commit/metric/viewport identities, and
rehashed all 12 saved downloads against their recorded expected package
hashes. It also created a per-file inventory of the retained run evidence.

## Persistent local evidence

Base directory:
`/home/l2810/SourcePRISM-evidence/m1-playwright-docker.CF5RM1nK`

Run directories relative to that base, with SHA-256 of results/summary.json:

| Audience | Directory | Summary SHA-256 |
|---|---|---|
| researcher | researcher-browser.BF95zdi1 | 6b5a5c3dc85cc73cddbdaa742f39e16a52d017afbb770a03a4158b5a3d87908c |
| health_institution | health_institution-browser.SozuaTw8 | f69d8bf406980c1a5c0db55482408a863d47e5144d54f1e936471b5b9e080839 |
| public | public-browser.FCAQ5VtC | f4188d3976c9e9edcf03e2687a90957a5325936b03068ea6315827b6c1132112 |

Combined record directory: three-audience-browser-record.ovhrh1xx.

| Combined record file | SHA-256 |
|---|---|
| acceptance-summary.json | ebe0c9d7f75fbf5ad855512fbacb00aef43ae9a9eb4cfba7ee3f84958f3c85ce |
| evidence-file-hashes.json | 8fdfb67147419306f592e9fe4436dd2e7af7f68778fc3a03848ce198a1d87f48 |

A local SHA256SUMS file records those two values. The directories contain
executed harnesses, screenshots, detailed results, downloaded CSVs, runtime
records and cleanup evidence. These paths are local locators, not repository
attachments. This document does not upload the files, provide an off-device
backup, establish a digital signature, or claim an aggregate archive hash.
Checksums cannot recover missing evidence.

Earlier harness attempts stopped on a vanished temporary source-worktree
path and native-select option discovery for a Selectize-enhanced control.
The successful harness used a persistent repository to read the same pinned
commit and the Selectize option registry while retaining the exact metric
identity and layout/download assertions. Those earlier failures are not
evidence of application-layout failures.

## Remaining gates and acceptance boundary

- Test short-to-long metric switching and return switching. The original
  finding specifically requested this; selecting one metric once per run
  does not establish it. The reported gonorrhea population 2022 example and
  other metrics remain outside this recorded browser scope.
- Independently review retained screenshots and relevant evidence. Neither
  the user-executed harness nor this documentation constitutes independent
  reviewer approval.
- Other browser engines, physical-device behavior and additional viewport
  sizes were not tested. A narrow desktop-browser viewport is not physical
  mobile-device validation.
- No unfixed baseline was exercised through the same automated browser
  harness; this is fixed-version evidence, not an automated before/after
  comparison.
- Local browser results do not establish hosted execution of this harness,
  whole-milestone acceptance, multi-user security/concurrency acceptance,
  scientific validity, production readiness or complete image provenance.
- An off-device evidence-retention decision remains separate from this
  local hash inventory and repository summary.

The scoped three-audience single-metric containment/download check passes.
Historical M0 closure and broader M1 acceptance are not redefined here.
Further implementation, publication, merging, main promotion, protection
changes, deployment and frozen-release modification retain separate gates.
This checkpoint changes documentation only.

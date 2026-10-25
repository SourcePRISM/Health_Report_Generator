# M1 finalization checkpoint — draft for review

Observation date: 2026-10-25.
Repository: SourcePRISM/Health_Report_Generator.
Inspected main: 622ed808980b4b645dc3cc1cbcbbac07e78ac1be.
Decision: NOT ACCEPTED / FINALIZATION IN PROGRESS.
This document is a proposed new checkpoint, not a completed review or a declaration of milestone achievement.

## Scope correction and authority

The user-supplied SourcePRISM_Revised_Milestone_Proposal.md, prepared 2026-10-24, defines M1 as reliable rendering and publication, not just calculation-trace containment. M1 tasks are to address applicable section 8 protections without redundant patches, add regression/browser tests, verify the full artifact set before publication, and compare unchanged analytical results against M0 while documenting intentional changes.

The trace correction has scoped passing evidence. It must not silently replace this wider milestone definition. Requirements below need an evidence-backed disposition: verified, failed, not yet verified, or not applicable with an explicit rationale. Not yet verified does not mean missing implementation. The proposal is user-supplied and is not represented here as an already committed repository file.

## Existing evidence and chronology

- Historical baseline: aaa51f53dc1616de6db9571427c9528d107105cb.
- PR #6: focused trace-containment correction; PR #7: single-file browser-evidence documentation.
- PR #8 merged integration/jev-free-product into main. Its actual scope was 16 commits and 16 changed files, not its copied one-file description.
- Main revision inspected for this checkpoint: 622ed808980b4b645dc3cc1cbcbbac07e78ac1be.
- Exact-main GitHub Actions run: 40197434751. All four check runs completed successfully: fast, secrets, full, container. This is check-run metadata verification, not a claim of complete job-log inspection or of every scenario below being exercised.
- The earlier 108 repeated single-metric browser assertions belong to their earlier recorded revision. They are not added to the later 540 switching assertions.

## Scoped browser and preservation results

PR #8's post-merge switching comment records researcher, health_institution and public at 1440 x 900 and 390 x 844 using Playwright 1.64.1 and Chromium 156.0.8078.4.

The user-executed local runs report 540 repeated assertions, 36 selection steps and 12 reverified CSV downloads. These are not 540 independent scenarios. Short-to-long and return switching passed for the selected cases. Selection used Selectize setValue; native dropdown interaction is not established. No page errors, console errors, request failures or blocked requests were reported in the supplied summaries.

Archive: main-switching-evidence.tar.gz; 308 files; 2,835,425 bytes.
Archive SHA-256: 573e34dd11ba7315a600fd47ac4aebf6525603116c4296f318e97d106c937ea4.
Acceptance-summary SHA-256: 671175f66539db75139973cc7ab87a1d18963105722110487f2279f9e33bc420.
Evidence-inventory SHA-256: 4b4ba95af780f6c469a524b225d48bf598c050435bd17a7a3ddffc8d7597e4e5.

Backup directory: E:\SourcePRISM-backup\main-switching-622ed80-20261025T142852Z-eaf43efb.
The user-run PowerShell script verified the archive, acceptance summary, evidence inventory and SHA256SUMS after copying. Backup receipt SHA-256: d500aba1187db5318db9f901177d44c24dcb35d10eed6c6b290e4890fad50663.
Off-device completion is based on copied-byte verification plus the user's explicit confirmation of destination separation, not independent hardware inspection. GitHub contains the provenance/checksum record, not the evidence archive.

## M1 requirement-to-evidence matrix

This is a gap inventory, not a completed implementation audit. Repository file inventories and successful aggregate CI do not alone prove each requirement.

| Proposal section 8 protection | Evidence currently established | Required disposition before M1 acceptance |
|---|---|---|
| 1. Assets resolve in source and packaged/nested workspaces | Scoped browser runs verify selected package presentation-file identities | Inspect resolver and manifests; map tests for source, package and nested-assets paths; patch only a demonstrated gap |
| 2. Actual CSV/Parquet input resolver agrees with provenance and fails clearly | Earlier reproduction/snapshot checks provide related evidence | Verify supported format selection, actual-input identities and missing-input failures; explicitly classify unsupported formats |
| 3. Hash executed templates, includes, styles, scripts and helpers | Package presentation identities and earlier release hashes were checked | Map executed dependency coverage and add missing dependency-change regressions if necessary |
| 4. Valid raw-HTML Plotly embedding and collision-safe fences | No Plotly-specific browser acceptance established in this checkpoint | Determine applicable renderers; verify chart behavior if supported or record justified non-applicability; do not count static images as Plotly interaction |
| 5. Reactive control lifecycle and source/audience switching | Selected metric switching passes across three separately exercised audiences | Review control/dependent-state separation; do not infer source/audience switching from separate audience runs |
| 6. Report and methods embedded provenance equals sidecar | Historical output/provenance checks exist | Map equality checks to relevant artifact types and exact tested revisions |
| 7. Shared table controls against stable markup, browser-tested | Earlier manual public-table checks and scoped trace checks exist | Review relevant controls and supported audience/browser journeys; distinguish manual evidence from automated coverage |
| 8. Required provenance/controls survive omitted optional arguments | No scenario-specific proof mapped here | Inspect defaults/call sites and map or add omitted-argument regressions |
| 9. Context-specific escaping of untrusted content | No complete HTML/script/Markdown/YAML/path scenario mapping here | Inspect relevant boundaries and fixture coverage; identify unsupported contexts explicitly |
| 10. Explicit render failures; labelled fallback | Relevant rendering/publication modules and tests exist by inventory only | Inspect failure/fallback behavior and tests; demonstrate no false successful requested render |
| 11. Stage, verify complete artifacts, publish atomically | report_publication.py and publication/recovery tests exist by inventory only | Inspect applicable publication path and map incomplete-set, verification-failure and recovery tests; existence alone is not acceptance |
| 12. Useful logs with secret/private-content redaction | Prior scanner work and CI success provide related but insufficient evidence | Inspect installation/render diagnostics and targeted redaction tests; secret scanning alone does not prove log redaction |
| 13. Missing comparison baselines remain unknown | Historical policy and baseline comparisons preserve this requirement | Map missing-baseline fixtures and displayed outcomes; verify no normal/low substitution |

Additional M1 task: preserve numerical results. The M0 record reports 30 corresponding analysis/bundle files matching byte-for-byte across fresh historical-baseline output, earlier integration output and a hosted artifact for one recorded snapshot and standard audience configurations. This is revision-specific evidence, not a fresh numerical comparison at the current main revision. Review the analytical diff and select the smallest additional comparison needed; document every intentional numerical change. Confirm preservation of the earlier comparison CSV/logs separately: the new switching archive is not proof that all M0 evidence was backed up.

## Visual review work package — not executed

Inputs required: the actual retained post-fix main-switching screenshots, summaries and inventory with audience, viewport, metric/state and revision associations. Historical screenshots without these identities must not be substituted.

For each audience and viewport, inspect the selected long-table states and return states for:
- Panel/table containment without destructive truncation.
- Readable labels, values and visible focus indicators where the screenshots capture focus.
- Reachability of complete hashes and audit values, using detailed run evidence where a still image cannot demonstrate interaction.
- Consistency of the displayed selected metric and rows with the recorded state.
- No newly obscured controls or obvious layout regression.

Record screenshot filename/hash, revision, audience, viewport, metric/state, observation, PASS/FAIL/NOT ASSESSABLE, reviewer identity and date. Separate visual observations from automated assertions. A static screenshot alone does not establish keyboard behavior, native selection or downloads.

| Audience | Desktop review | Narrow review | Reviewer and decision |
|---|---|---|---|
| researcher | PENDING | PENDING | Unassigned; no approval |
| health_institution | PENDING | PENDING | Unassigned; no approval |
| public | PENDING | PENDING | Unassigned; no approval |

Assistant inspection, if later performed, must be labelled as such and must not be represented as independent human approval. Reviewer independence and acceptance authority must be explicitly established.

## Closure gates

- [ ] Complete requirement-to-implementation/test mapping for all applicable section 8 protections.
- [ ] Resolve actual failures with small reviewed changes; do not patch working baseline components redundantly.
- [ ] Record exact revision, command/scenario, output and evidence for each disposition.
- [ ] Complete identified screenshot/evidence review and record reviewer findings.
- [ ] Reconcile revision-specific numerical preservation and earlier M0 evidence retention.
- [ ] Record M0 prerequisite acceptance status; do not imply historical M0 closure.
- [ ] Obtain an explicit M1 acceptance decision against the full agreed scope and stated limitations.

Until then: trace-containment/switching evidence is scoped PASS; full M1 remains open. Other-browser, physical-device, native-dropdown and automated unfixed-baseline comparisons are not established and require explicit scope disposition, not automatic milestone expansion. M2-M4 features, multi-user pilot acceptance, scientific/clinical approval and deployment are separate gates. M0-M4 remain model-free.

## Publication boundary

Proposed repository destination: docs/implementation/m1-finalization-checkpoint.md on a new docs/m1-finalization-checkpoint branch from main, for a subsequent documentation PR. This draft creates no GitHub state by itself. Each external write requires its own confirmation. No direct main edit, merge, deployment, branch deletion, frozen-release change or new test execution is part of preparing this record.

## Source locators

- User-supplied SourcePRISM_Revised_Milestone_Proposal.md, sections 2, 8, 13 and 14.
- docs/implementation/m0-baseline.md at inspected main.
- docs/implementation/m1-trace-browser-evidence.md at inspected main.
- https://github.com/SourcePRISM/Health_Report_Generator/pull/8#issuecomment-6398451282
- https://github.com/SourcePRISM/Health_Report_Generator/pull/8#issuecomment-6398897705
- https://api.github.com/repos/SourcePRISM/Health_Report_Generator/commits/622ed808980b4b645dc3cc1cbcbbac07e78ac1be/check-runs

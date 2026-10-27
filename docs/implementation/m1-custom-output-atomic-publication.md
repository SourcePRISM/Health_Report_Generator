# Custom-output atomic handoff candidate

Status: APPLIED CANDIDATE ONLY; execution and acceptance remain pending.
Base: f3407966862a55d8b8bfa3d1779617f41927822a.

## Scope and assumptions

Only custom_report_output.publish_cached_report is changed. No analytical,
input-data, dependency-lock or report-template change. This does not establish
atomic publication for the standard renderer, compatibility report.py,
selected renderer or cache insertion.

Trusted Linux filesystem with working renameat2 operations, same-filesystem
staging under destination.parent, single writer, no hostile namespace mutation.
Unsupported kernel/libc/filesystem operations fail closed, without a copy/delete
or two-rename fallback. Do not presume native Windows, DrvFs or network support.

## Protocol

Copy and verify the complete cache inventory; remove cache-only metadata.
Synchronize the candidate tree and staging/destination-parent directories.
First publication uses RENAME_NOREPLACE. Replacement uses RENAME_EXCHANGE,
atomically swapping the two complete nonempty directory trees rather than
moving the existing destination away first. Synchronize affected directories
before returning success. Best-effort cleanup removes the retired staged tree.

A post-handoff synchronization error raises OutputPublicationUncertainError
and retains the workspace, including the old tree after exchange. The complete
new destination can already be visible. This is not old-output preservation,
and there is no non-atomic rollback. Inspect before any recovery action.
Legacy OutputRecoveryError remains importable but the obsolete two-rename
restoration path is no longer used.

Atomic pathname handoff is not snapshot isolation across a reader's multiple
independent opens. Old-tree cleanup is not a version-pinning reader API.
This candidate does not claim universal power-loss recovery, uncooperative
writer protection, multi-user acceptance or a crash/restore rehearsal.

## Regression changes

Retain existing copy, inventory, symlink, overlap, identity and success checks.
Replace two tests specific to obsolete two-rename restoration with explicit
pre-handoff preservation and post-handoff-uncertainty coverage. Add primitive
selection, no fallback, prepublication synchronization failure, real nonempty
exchange and real no-replace collision tests. Unsupported real operations must
not be silently skipped or reported as passes.

Applying this candidate only parses Python syntax. Focused publication and
affected custom-report/cache regressions still require the pinned environment.
No tests, renders, commits or remote writes are performed by the application
script. M1-PUB-01 remains OPEN pending validation and route-level reconciliation.


## Validation follow-up - 2026-10-27

The earlier checkpoint above is preserved as history. Later execution,
artifact-owner review, pinned lint, CI-routing and assistant source-review
receipts are reconciled in the
[dated validation follow-up](m1-validation-followup-2026-10-27.md).
Its recorded scopes and limitations govern interpretation of those later
receipts; neither the original pending wording nor the follow-up establishes
full route coverage or milestone acceptance. M0 and M1 decisions remain pending.

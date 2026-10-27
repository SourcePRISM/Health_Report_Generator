# Output-context escaping correction candidate

Status: applied candidate only; execution/acceptance pending.
Base: f3407966862a55d8b8bfa3d1779617f41927822a, with separately tested
custom-publication candidate retained unchanged.

## Confirmed findings

M1-ESC-02: a quote-bearing image label introduced an onerror attribute in a
parsed image fragment. No browser execution or full exploit claim.
M1-ESC-03: accepted synthetic presentation text became RawInline TeX nodes
in the PDF helper's generated Markdown. No LaTeX/file inclusion was executed.
Configuration serialization preserved literal text and expected keys; unchanged.

## Candidate correction

Keep HTML text escaping unchanged. Add attribute=True escaping for quoted
attribute sinks, including image alt and existing identifier/class attributes.
Add a literal Markdown text encoder using numeric character references for
ASCII punctuation. Normalize inline control characters to spaces; original
strings remain unchanged in JSON/CSV/provenance. Confirm literal preservation
with the actual bundled Pandoc parser, not only string matching.

Use the Markdown encoder for dynamic PDF presentation names/versions,
disease labels and selection narrative values. Encode character columns and
headers before the existing explicit pipe-table renderer; keep numeric
columns and analytical values unchanged. Existing default LaTeX-table paths
are not replaced. No global raw-TeX disabling, dependency changes or schema
restrictions are introduced by this slice.

## Boundaries

Helpers are sink-specific: Markdown encoding is not a URL/path policy or a
replacement for HTML attribute encoding. No claim of full M1-09 closure until
remaining boundaries/callers are mapped. No new public-serving/exploit claim.
No approved evidence files, baseline inputs, scientific calculations or
publication candidate files are changed. New rendering metadata/source hashes
will differ legitimately. Affected render smoke/visual checks remain required.

## Tests

New tests exercise real R helpers and the existing Quarto/Pandoc parser, with
no browser or LaTeX execution. They cover literal alt values, quotes/Unicode,
raw-TeX/Markdown markers, newlines, pipe cells, PDF metadata/coverage, and
QMD caller wiring. No unsupported operation is silently skipped.
Applying the candidate only parses Python test syntax; R syntax and all
regressions still need execution in the qualified existing image.


## Validation follow-up - 2026-10-27

The earlier checkpoint above is preserved as history. Later execution,
artifact-owner review, pinned lint, CI-routing and assistant source-review
receipts are reconciled in the
[dated validation follow-up](m1-validation-followup-2026-10-27.md).
Its recorded scopes and limitations govern interpretation of those later
receipts; neither the original pending wording nor the follow-up establishes
full route coverage or milestone acceptance. M0 and M1 decisions remain pending.

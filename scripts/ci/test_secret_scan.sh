#!/usr/bin/env bash
# Run required real-wrapper tests with the checksum-verified pinned archive.
set -euo pipefail

version="8.30.1"
asset="gitleaks_${version}_linux_x64.tar.gz"
expected_sha256="551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

if [[ -n "${GITLEAKS_TEST_ARCHIVE:-}" ]]; then
    cp -- "$GITLEAKS_TEST_ARCHIVE" "$work/$asset"
else
    curl --fail --location --retry 5 --retry-all-errors \
      --output "$work/$asset" \
      "https://github.com/gitleaks/gitleaks/releases/download/v${version}/${asset}"
fi

echo "${expected_sha256}  $work/$asset" | sha256sum --check --status

GITLEAKS_TEST_REQUIRED=1 GITLEAKS_TEST_ARCHIVE="$work/$asset" \
    python -m pytest -q -ra tests/test_secret_scan.py

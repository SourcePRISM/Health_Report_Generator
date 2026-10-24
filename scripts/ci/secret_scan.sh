#!/usr/bin/env bash
# Scan checked-out HEAD ancestry with a pinned, checksum-verified gitleaks.
set -euo pipefail
# Fail closed when there is no repository or no committed HEAD to scan.
git -C "${1:-.}" rev-parse --git-dir >/dev/null
git -C "${1:-.}" rev-parse --verify 'HEAD^{commit}' >/dev/null
version="8.30.1"
asset="gitleaks_${version}_linux_x64.tar.gz"
expected_sha256="551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
curl --fail --location --retry 5 --retry-all-errors --output "$work/$asset" \
  "https://github.com/gitleaks/gitleaks/releases/download/v${version}/${asset}"
echo "${expected_sha256}  $work/$asset" | sha256sum --check --status
tar -xzf "$work/$asset" -C "$work" gitleaks
# Keep all reachable history, including merge parents; exclude unrelated refs.
"$work/gitleaks" git --no-banner --redact --exit-code 1 --log-opts="HEAD" "${1:-.}"

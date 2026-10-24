#!/usr/bin/env bash
# Audit all fetched repository branch/tag history in a fresh isolated repository.
set -euo pipefail

remote="${1:-https://github.com/SourcePRISM/Health_Report_Generator.git}"
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
tar -xzf "$work/$asset" -C "$work" gitleaks

git init --bare "$work/audit.git"
git -C "$work/audit.git" fetch --no-tags -- "$remote" \
    'refs/heads/*:refs/heads/*' \
    'refs/tags/*:refs/tags/*'

# No commit history is an error, not a successful clean audit.
count="$(git -C "$work/audit.git" rev-list --all --count)"
if [[ "$count" -eq 0 ]]; then
    printf '%s\n' 'Audit source contains no reachable commits.' >&2
    exit 2
fi

# Do not inherit caller rule overrides, ignore files or inline exemptions.
exceptions="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/secret-audit.gitleaksignore"
cp -- "$exceptions" "$work/.gitleaksignore"
unset GITLEAKS_CONFIG GITLEAKS_CONFIG_TOML
cd "$work"
"$work/gitleaks" git --no-banner --redact --exit-code 1 \
    --gitleaks-ignore-path "$work" --ignore-gitleaks-allow \
    --log-opts="--all" "$work/audit.git"

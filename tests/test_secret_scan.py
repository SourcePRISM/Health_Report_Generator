"""Scanner scope contract and opt-in offline real-wrapper integration tests.

Set GITLEAKS_TEST_ARCHIVE to the pinned release archive to run all tests.
Without it, integration tests skip; this is not scanner acceptance evidence.
"""
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tarfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/ci/secret_scan.sh"
SHA256 = "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb"


def test_wrapper_preserves_security_and_explicit_scope():
    script = SCRIPT.read_text()
    assert 'version="8.30.1"' in script
    assert f'expected_sha256="{SHA256}"' in script
    assert 'sha256sum --check --status' in script
    assert '--redact --exit-code 1 --log-opts="HEAD" "${1:-.}"' in script
    assert 'set -euo pipefail' in script
    assert "trap 'rm -rf" in script


@pytest.fixture
def runner(tmp_path):
    value = os.environ.get("GITLEAKS_TEST_ARCHIVE")
    if value is None:
        if os.environ.get("GITLEAKS_TEST_REQUIRED") == "1":
            pytest.fail("GITLEAKS_TEST_ARCHIVE is required for scanner acceptance")
        pytest.skip("Set GITLEAKS_TEST_ARCHIVE for real-wrapper integration tests")
    archive = Path(value).resolve()
    assert archive.is_file(), "Configured scanner archive does not exist"
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == SHA256
    for command in ("git", "bash", "tar", "sha256sum", "mktemp"):
        assert shutil.which(command), f"Required executable missing: {command}"

    env = os.environ.copy()
    for key in list(env):
        if key.startswith(("GIT_", "GITLEAKS_")):
            env.pop(key)
    home = tmp_path / "home"
    home.mkdir()
    env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0")
    bindir = tmp_path / "bin"
    bindir.mkdir()
    # Replace transport only. Real sha256sum, tar and Gitleaks still execute.
    transport = bindir / "curl"
    transport.write_text(
        "#!/bin/sh\nexec " + shlex.quote(sys.executable) + " -c "
        + shlex.quote("import shutil,sys; "
                      "shutil.copyfile(sys.argv[1], "
                      "sys.argv[sys.argv.index('--output') + 1])")
        + " " + shlex.quote(str(archive)) + ' "$@"\n'
    )
    transport.chmod(0o700)
    env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", os.defpath)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    env["TMPDIR"] = str(scratch)

    def run(repo, transport_error=False, script=SCRIPT):
        if transport_error:
            transport.write_text("#!/bin/sh\nexit 23\n")
        result = subprocess.run(
            ["bash", str(script), str(repo)], cwd=tmp_path, env=env,
            capture_output=True, text=True, timeout=60,
        )
        assert list(scratch.iterdir()) == [], "Scanner temporary files were not cleaned"
        return result

    return run, env


def git(repo, env, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], env=env, check=True,
        capture_output=True, text=True, timeout=30,
    ).stdout.strip()


def repository(tmp_path, env):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, env, "init", "--initial-branch=main")
    git(repo, env, "config", "user.name", "Scanner Fixture")
    git(repo, env, "config", "user.email", "scanner@example.invalid")
    git(repo, env, "config", "commit.gpgsign", "false")
    (repo / "README.md").write_text("Synthetic scanner fixture.\n")
    git(repo, env, "add", "README.md")
    git(repo, env, "commit", "-m", "clean initial fixture")
    return repo


def add_then_delete_fixture(repo, env):
    # Synthetic only: assembled at runtime, never a usable credential.
    token = "gh" + "p_" + hashlib.sha256(b"sourceprism-scanner-fixture").hexdigest()[:36]
    path = repo / "fixture.txt"
    path.write_text("fixture_token=" + token + "\n")
    git(repo, env, "add", "fixture.txt")
    git(repo, env, "commit", "-m", "add synthetic fixture")
    git(repo, env, "rm", "fixture.txt")
    git(repo, env, "commit", "-m", "remove synthetic fixture")
    return token


def test_clean_history(tmp_path, runner):
    run, env = runner
    repo = repository(tmp_path, env)
    result = run(repo)
    assert result.returncode == 0, result.stderr


def test_deleted_reachable_finding(tmp_path, runner):
    run, env = runner
    repo = repository(tmp_path, env)
    token = add_then_delete_fixture(repo, env)
    result = run(repo)
    assert result.returncode == 1, result.stderr
    assert "leaks found" in result.stderr.lower()
    assert token not in result.stdout + result.stderr


def test_unrelated_ref_excluded_but_fixture_detectable(tmp_path, runner):
    run, env = runner
    repo = repository(tmp_path, env)
    git(repo, env, "switch", "-c", "unrelated")
    add_then_delete_fixture(repo, env)
    assert run(repo).returncode == 1
    git(repo, env, "switch", "main")
    result = run(repo)
    assert result.returncode == 0, result.stderr


def test_merge_second_parent_is_scanned(tmp_path, runner):
    run, env = runner
    repo = repository(tmp_path, env)
    git(repo, env, "switch", "-c", "side")
    add_then_delete_fixture(repo, env)
    git(repo, env, "switch", "main")
    git(repo, env, "commit", "--allow-empty", "-m", "diverge main")
    git(repo, env, "merge", "--no-ff", "side", "-m", "merge side")
    parents = git(repo, env, "rev-list", "--parents", "-n", "1", "HEAD").split()
    assert len(parents) == 3
    result = run(repo)
    assert result.returncode == 1, result.stderr
    assert "leaks found" in result.stderr.lower()


def test_invalid_repository_fails(tmp_path, runner):
    run, _ = runner
    invalid = tmp_path / "not-a-repository"
    invalid.mkdir()
    result = run(invalid)
    assert result.returncode != 0


def test_transport_failure_propagates(tmp_path, runner):
    run, env = runner
    repo = repository(tmp_path, env)
    result = run(repo, transport_error=True)
    assert result.returncode == 23


def test_empty_repository_fails(tmp_path, runner):
    run, env = runner
    empty = tmp_path / "empty-repository"
    empty.mkdir()
    git(empty, env, "init", "--initial-branch=main")
    result = run(empty)
    assert result.returncode != 0


def test_required_mode_rejects_missing_archive(tmp_path):
    env = os.environ.copy()
    env.pop("GITLEAKS_TEST_ARCHIVE", None)
    env["GITLEAKS_TEST_REQUIRED"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env.pop("PYTEST_ADDOPTS", None)
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest", "-q",
            str(Path(__file__).resolve()) + "::test_clean_history",
            "--basetemp", str(tmp_path / "child-pytest"),
        ],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 1
    assert "GITLEAKS_TEST_ARCHIVE is required" in result.stdout


AUDIT = ROOT / "scripts/ci/secret_audit.sh"


def test_audit_clean_repository(tmp_path, runner):
    run, env = runner
    repo = repository(tmp_path, env)
    result = run(repo, script=AUDIT)
    assert result.returncode == 0, result.stderr


def test_audit_includes_other_branches(tmp_path, runner):
    run, env = runner
    repo = repository(tmp_path, env)
    git(repo, env, "switch", "-c", "side")
    add_then_delete_fixture(repo, env)
    git(repo, env, "switch", "main")
    assert run(repo).returncode == 0
    result = run(repo, script=AUDIT)
    assert result.returncode == 1, result.stderr
    assert "leaks found" in result.stderr.lower()


def test_audit_includes_tag_only_history(tmp_path, runner):
    run, env = runner
    repo = repository(tmp_path, env)
    git(repo, env, "switch", "-c", "temporary-side")
    add_then_delete_fixture(repo, env)
    git(repo, env, "tag", "fixture-history")
    git(repo, env, "switch", "main")
    git(repo, env, "branch", "-D", "temporary-side")
    assert run(repo).returncode == 0
    result = run(repo, script=AUDIT)
    assert result.returncode == 1, result.stderr
    assert "leaks found" in result.stderr.lower()


def test_audit_fetch_failure_is_not_clean(tmp_path, runner):
    run, _ = runner
    result = run(tmp_path / "missing-source", script=AUDIT)
    assert result.returncode != 0


def test_audit_empty_source_is_not_clean(tmp_path, runner):
    run, env = runner
    repo = tmp_path / "empty-source"
    repo.mkdir()
    git(repo, env, "init", "--initial-branch=main")
    result = run(repo, script=AUDIT)
    assert result.returncode != 0


def test_audit_workflow_keeps_failure_visible():
    workflow = (ROOT / ".github/workflows/secret-history-audit.yml").read_text()
    assert "workflow_dispatch:" in workflow
    assert "cron: '0 7 * * 1'" in workflow
    assert "contents: read" in workflow
    assert "secret_audit.sh https://github.com/SourcePRISM/Health_Report_Generator.git" in workflow
    assert "continue-on-error" not in workflow


def test_audit_rejects_ambient_rule_suppression(tmp_path, runner):
    run, env = runner
    repo = repository(tmp_path, env)
    add_then_delete_fixture(repo, env)
    assert run(repo).returncode == 1

    config = tmp_path / "caller-config.toml"
    config.write_text(
        '[extend]\nuseDefault = true\n'
        '[allowlist]\npaths = [".*"]\n'
    )
    env["GITLEAKS_CONFIG"] = str(config)

    # Establish that the ambient configuration really suppresses the fixture.
    assert run(repo).returncode == 0

    # The broader audit must ignore that ambient override.
    result = run(repo, script=AUDIT)
    assert result.returncode == 1, result.stderr
    assert "leaks found" in result.stderr.lower()


def test_audit_explicitly_isolates_suppression_sources():
    script = AUDIT.read_text()
    assert "unset GITLEAKS_CONFIG GITLEAKS_CONFIG_TOML" in script
    assert 'cd "$work"' in script
    assert '--gitleaks-ignore-path "$work"' in script
    assert "--ignore-gitleaks-allow" in script


def test_reviewed_audit_exception_set_is_exact():
    data = (ROOT / "scripts/ci/secret-audit.gitleaksignore").read_bytes()
    assert len(data.decode().splitlines()) == 9
    assert hashlib.sha256(data).hexdigest() == "41311ef65f9eb48a2c1cd4d24fa723567af329542223f2fbd3c9217dc585dd47"


def test_audit_missing_exception_file_fails(tmp_path, runner):
    run, env = runner
    repo = repository(tmp_path, env)
    folder = tmp_path / "audit-without-exceptions"
    folder.mkdir()
    script = folder / "secret_audit.sh"
    shutil.copy2(AUDIT, script)
    result = run(repo, script=script)
    assert result.returncode != 0


def test_audit_exception_is_specific_to_one_finding(tmp_path, runner):
    run, env = runner
    repo = repository(tmp_path, env)
    add_then_delete_fixture(repo, env)

    scanner = tmp_path / "verified-gitleaks"
    archive = Path(os.environ["GITLEAKS_TEST_ARCHIVE"])
    with tarfile.open(archive, "r:gz") as bundle:
        member = bundle.extractfile("gitleaks")
        assert member is not None
        scanner.write_bytes(member.read())
    scanner.chmod(0o700)
    report = tmp_path / "fixture-report.json"
    result = subprocess.run(
        [str(scanner), "git", "--no-banner", "--redact=100",
         "--log-opts=HEAD", "--report-format=json",
         "--report-path", str(report), str(repo)],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 1, result.stderr
    findings = json.loads(report.read_text())
    assert len(findings) == 1

    folder = tmp_path / "audit-specific-exception"
    folder.mkdir()
    script = folder / "secret_audit.sh"
    shutil.copy2(AUDIT, script)
    (folder / "secret-audit.gitleaksignore").write_text(
        findings[0]["Fingerprint"] + "\n"
    )
    result = run(repo, script=script)
    assert result.returncode == 0, result.stderr

    # A new commit containing even the same synthetic value is not excepted.
    add_then_delete_fixture(repo, env)
    result = run(repo, script=script)
    assert result.returncode == 1, result.stderr
    assert "leaks found" in result.stderr.lower()

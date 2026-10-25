"""Failure-recoverable custom-report output on a trusted local filesystem.

Single writer only. Directory handoff is not universally atomic or crash-durable.
Cleanup is best-effort; failed restoration retains its recovery directory.
"""
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ENTRY = "cache_entry.json"


class OutputRecoveryError(RuntimeError):
    """Automatic restoration failed; recovery material must not be deleted."""

    def __init__(self, directory):
        self.recovery_directory = Path(directory)
        super().__init__(f"Output restoration failed; recovery retained at {directory}")


def _digest(path):
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def publish_cached_report(source, destination, expected_key):
    """Stage and hash-check a cache entry before replacing an owned output."""
    source, destination = Path(source), Path(destination)
    if source.is_symlink() or destination.is_symlink():
        raise ValueError("Report source and destination cannot be symlinks.")
    source, destination = source.resolve(), destination.resolve()
    if (
        source == destination
        or source in destination.parents
        or destination in source.parents
    ):
        raise ValueError("Report source and destination cannot overlap.")
    if destination.exists() and not destination.is_dir():
        raise ValueError("Report destination must be a directory.")
    metadata = (source / ENTRY).read_bytes()
    manifest = json.loads(metadata)
    if not isinstance(manifest, dict) or manifest.get("key") != expected_key:
        raise ValueError("Cached report identity differs.")
    expected = manifest.get("files")
    if not isinstance(expected, dict) or not expected:
        raise ValueError("Cached report inventory is missing.")
    for name in expected:
        if (
            not isinstance(name, str)
            or not name
            or Path(name).is_absolute()
            or ".." in Path(name).parts
            or Path(name).as_posix() != name
            or name in {".", ENTRY}
        ):
            raise ValueError("Invalid cached report inventory path.")

    destination.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(
        prefix=".sourceprism-output-", dir=destination.parent
    ))
    stage, previous = work / "replacement", work / "previous"
    retain = False
    try:
        shutil.copytree(source, stage, symlinks=True)
        if (stage / ENTRY).read_bytes() != metadata:
            raise ValueError("Cached report metadata changed during copying.")
        actual = {}
        for path in stage.rglob("*"):
            if path.is_symlink():
                raise ValueError("Cached report cannot contain symlinks.")
            if path.is_file() and path != stage / ENTRY:
                actual[path.relative_to(stage).as_posix()] = _digest(path)
        if actual != expected:
            raise ValueError("Staged report failed inventory verification.")
        (stage / ENTRY).unlink()

        try:
            if destination.exists():
                destination.rename(previous)
            stage.rename(destination)
        except BaseException:
            if previous.exists():
                try:
                    if destination.exists() or destination.is_symlink():
                        raise RuntimeError("Destination appeared during restoration.")
                    previous.rename(destination)
                except BaseException as exc:
                    retain = True
                    raise OutputRecoveryError(work) from exc
            raise
        return destination
    finally:
        if not retain:
            shutil.rmtree(work, ignore_errors=True)

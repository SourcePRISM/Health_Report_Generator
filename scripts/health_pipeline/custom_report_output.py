"""Verified custom output with atomic Linux directory handoff.

Trusted filesystem and single writer only; unsupported operations fail closed.
Post-handoff synchronization failure is explicit and retains material.
"""
import ctypes
import errno
import hashlib
import os
import sys
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


RENAME_NOREPLACE = 1
RENAME_EXCHANGE = 2


class OutputPublicationUncertainError(RuntimeError):
    """Handoff completed but subsequent directory synchronization failed."""

    def __init__(self, directory, destination):
        self.recovery_directory = Path(directory)
        self.destination = Path(destination)
        super().__init__(
            f"Publication handoff completed but durability is uncertain; "
            f"inspect {destination}; retained material at {directory}"
        )


def _renameat2(source, destination, flags):
    """Require the atomic Linux primitive; never use a non-atomic fallback."""
    if sys.platform != "linux":
        raise OSError(errno.ENOTSUP, "Atomic directory publication requires Linux")
    operation = getattr(ctypes.CDLL(None, use_errno=True), "renameat2", None)
    if operation is None:
        raise OSError(errno.ENOSYS, "Atomic publication requires renameat2")
    operation.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                          ctypes.c_char_p, ctypes.c_uint]
    operation.restype = ctypes.c_int
    if operation(-100, os.fsencode(source), -100, os.fsencode(destination), flags):
        code = ctypes.get_errno()
        raise OSError(code, "Atomic handoff failed: " + os.strerror(code),
                      os.fspath(destination))


def _sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _sync_tree(root):
    directories = [root]
    for path in root.rglob("*"):
        if path.is_dir():
            directories.append(path)
        elif path.is_file():
            with path.open("rb") as handle:
                os.fsync(handle.fileno())
    for path in sorted(directories, key=lambda p: len(p.parts), reverse=True):
        _sync_directory(path)


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
    stage = work / "replacement"
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

        # Verify and synchronize the entire candidate before its handoff.
        _sync_tree(stage)
        _sync_directory(work)
        _sync_directory(destination.parent)
        flags = RENAME_EXCHANGE if destination.exists() else RENAME_NOREPLACE
        _renameat2(stage, destination, flags)
        try:
            _sync_directory(work)
            _sync_directory(destination.parent)
        except BaseException as exc:
            retain = True
            raise OutputPublicationUncertainError(work, destination) from exc
        return destination
    finally:
        if not retain:
            # After exchange, stage holds the old tree; cleanup is best-effort.
            shutil.rmtree(work, ignore_errors=True)

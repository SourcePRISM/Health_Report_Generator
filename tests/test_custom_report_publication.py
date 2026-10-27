"""Synthetic output-preservation regressions; no Quarto or real reports."""
import errno
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/health_pipeline"))

import custom_report_output as output  # noqa: E402

KEY = "a" * 64


def snapshot(folder):
    if not folder.exists():
        return None
    return {
        p.relative_to(folder).as_posix(): p.read_bytes()
        for p in folder.rglob("*") if p.is_file()
    }


class OutputPreservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "cache" / KEY
        self.source.mkdir(parents=True)
        (self.source / "report.html").write_text("NEW REPORT")
        (self.source / "methods.html").write_text("NEW METHODS")
        (self.source / "provenance.json").write_text('{"fixture": true}')
        self.manifest = {
            "key": KEY,
            "files": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.source.iterdir()
            },
        }
        self.write_manifest()
        self.dest = self.root / "out"
        self.dest.mkdir()
        (self.dest / "report.html").write_text("OLD REPORT")
        (self.dest / "methods.html").write_text("OLD METHODS")
        self.before = snapshot(self.dest)
        self.cached = snapshot(self.source)

    def write_manifest(self):
        (self.source / output.ENTRY).write_text(json.dumps(self.manifest))

    def publish(self):
        return output.publish_cached_report(self.source, self.dest, KEY)

    def assert_preserved(self):
        self.assertEqual(snapshot(self.dest), self.before)
        self.assertEqual(snapshot(self.source), self.cached)

    def copy_failure(self, existing, partial):
        if not existing:
            shutil.rmtree(self.dest)
            self.before = None

        def fail(source, destination, **kwargs):
            if partial:
                Path(destination).mkdir()
                (Path(destination) / "report.html").write_text("PARTIAL")
            raise OSError("injected copy failure")

        with patch.object(output.shutil, "copytree", side_effect=fail):
            with self.assertRaisesRegex(OSError, "injected copy failure"):
                self.publish()
        self.assert_preserved()
        self.assertEqual(list(self.root.glob(".sourceprism-output-*")), [])

    def test_existing_output_survives_early_copy_failure(self):
        self.copy_failure(True, False)

    def test_existing_output_survives_partial_copy_failure(self):
        self.copy_failure(True, True)

    def test_new_output_absent_after_early_copy_failure(self):
        self.copy_failure(False, False)

    def test_new_output_absent_after_partial_copy_failure(self):
        self.copy_failure(False, True)

    def test_successful_replacement(self):
        (self.dest / "stale.txt").write_text("STALE")
        self.assertEqual(self.publish(), self.dest)
        self.assertEqual((self.dest / "report.html").read_text(), "NEW REPORT")
        self.assertEqual((self.dest / "methods.html").read_text(), "NEW METHODS")
        self.assertFalse((self.dest / "stale.txt").exists())
        self.assertFalse((self.dest / output.ENTRY).exists())
        self.assertEqual(snapshot(self.source), self.cached)
        self.assertEqual(list(self.root.glob(".sourceprism-output-*")), [])

    def test_successful_first_publication(self):
        shutil.rmtree(self.dest)
        self.publish()
        self.assertEqual((self.dest / "report.html").read_text(), "NEW REPORT")

    def test_hash_mismatch_preserves_previous_output(self):
        (self.source / "report.html").write_text("TAMPERED")
        self.cached = snapshot(self.source)
        with self.assertRaisesRegex(ValueError, "inventory verification"):
            self.publish()
        self.assert_preserved()

    def test_extra_file_is_rejected(self):
        (self.source / "extra.txt").write_text("UNLISTED")
        self.cached = snapshot(self.source)
        with self.assertRaisesRegex(ValueError, "inventory verification"):
            self.publish()
        self.assert_preserved()

    def test_missing_file_is_rejected(self):
        (self.source / "methods.html").unlink()
        self.cached = snapshot(self.source)
        with self.assertRaisesRegex(ValueError, "inventory verification"):
            self.publish()
        self.assert_preserved()

    def test_wrong_cache_key_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "identity differs"):
            output.publish_cached_report(self.source, self.dest, "b" * 64)
        self.assert_preserved()

    def test_traversal_inventory_is_rejected(self):
        self.manifest["files"]["../outside"] = "0" * 64
        self.write_manifest()
        self.cached = snapshot(self.source)
        with self.assertRaisesRegex(ValueError, "inventory path"):
            self.publish()
        self.assert_preserved()

    def test_payload_symlink_is_rejected(self):
        (self.source / "linked").symlink_to(self.source / "report.html")
        self.cached = snapshot(self.source)
        with self.assertRaisesRegex(ValueError, "symlinks"):
            self.publish()
        self.assert_preserved()

    def test_destination_symlink_is_not_followed(self):
        linked = self.root / "linked-output"
        linked.symlink_to(self.dest, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlinks"):
            output.publish_cached_report(self.source, linked, KEY)
        self.assertTrue(linked.is_symlink())
        self.assert_preserved()

    def test_source_overlap_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            output.publish_cached_report(self.source, self.source.parent, KEY)
        self.assert_preserved()

    def test_handoff_failure_preserves_previous_output(self):
        with patch.object(output, "_renameat2", side_effect=OSError("injected handoff failure")):
            with self.assertRaisesRegex(OSError, "injected handoff failure"):
                self.publish()
        self.assert_preserved()
        self.assertEqual(list(self.root.glob(".sourceprism-output-*")), [])

    def test_unsupported_exchange_fails_without_fallback(self):
        with patch.object(output, "_renameat2", side_effect=OSError(errno.EOPNOTSUPP, "unsupported")):
            with patch.object(Path, "rename", side_effect=AssertionError("non-atomic fallback")):
                with self.assertRaises(OSError):
                    self.publish()
        self.assert_preserved()

    def test_existing_destination_uses_exchange(self):
        with patch.object(output, "_renameat2", wraps=output._renameat2) as operation:
            self.publish()
        self.assertEqual(operation.call_args.args[2], output.RENAME_EXCHANGE)
        self.assertEqual((self.dest / "report.html").read_text(), "NEW REPORT")

    def test_first_publication_uses_noreplace(self):
        shutil.rmtree(self.dest)
        with patch.object(output, "_renameat2", wraps=output._renameat2) as operation:
            self.publish()
        self.assertEqual(operation.call_args.args[2], output.RENAME_NOREPLACE)

    def test_no_path_rename_handoff(self):
        with patch.object(Path, "rename", side_effect=AssertionError("two-rename handoff")):
            self.publish()
        self.assertEqual((self.dest / "report.html").read_text(), "NEW REPORT")

    def test_prepublication_sync_failure_preserves_previous_output(self):
        with patch.object(output, "_sync_tree", side_effect=OSError("injected sync failure")):
            with self.assertRaisesRegex(OSError, "injected sync failure"):
                self.publish()
        self.assert_preserved()

    def test_post_handoff_sync_failure_retains_old_tree_and_reports_uncertainty(self):
        real_sync = output._sync_directory

        def sync(path):
            if Path(path) == self.dest.parent and (self.dest / "report.html").read_text() == "NEW REPORT":
                raise OSError("injected post-handoff sync failure")
            return real_sync(path)

        with patch.object(output, "_sync_directory", side_effect=sync):
            with self.assertRaises(output.OutputPublicationUncertainError) as caught:
                self.publish()
        self.assertEqual(caught.exception.destination, self.dest)
        recovery = caught.exception.recovery_directory
        self.assertTrue(recovery.is_dir())
        self.assertEqual(snapshot(recovery / "replacement"), self.before)
        self.assertEqual((self.dest / "report.html").read_text(), "NEW REPORT")
        self.assertEqual(snapshot(self.source), self.cached)

    def test_real_exchange_preserves_both_nonempty_trees(self):
        other = self.root / "other"
        other.mkdir()
        (other / "report.html").write_text("OTHER REPORT")
        output._renameat2(other, self.dest, output.RENAME_EXCHANGE)
        self.assertEqual(snapshot(other), self.before)
        self.assertEqual((self.dest / "report.html").read_text(), "OTHER REPORT")

    def test_real_noreplace_does_not_overwrite_existing_output(self):
        other = self.root / "other"
        other.mkdir()
        (other / "report.html").write_text("OTHER REPORT")
        with self.assertRaises(OSError) as caught:
            output._renameat2(other, self.dest, output.RENAME_NOREPLACE)
        self.assertEqual(caught.exception.errno, errno.EEXIST)
        self.assertEqual(snapshot(self.dest), self.before)
        self.assertEqual((other / "report.html").read_text(), "OTHER REPORT")


if __name__ == "__main__":
    unittest.main()

"""Offline git-repository regression tests for the Ludoman publish step."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

FILE = Path(__file__).resolve().parents[1] / "scripts" / "publish_snapshot.py"
spec = importlib.util.spec_from_file_location("snapshot_publisher", FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def git(where, *args, ok=True):
    result = subprocess.run(["git", *args], cwd=where, text=True,
                            capture_output=True, check=False)
    if ok and result.returncode:
        raise AssertionError(f"git {' '.join(args)} returned {result.returncode}: {result.stderr}")
    return result


class PublishSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.remote = root / "remote.git"
        self.worker = root / "worker"
        self.editor = root / "editor"
        git(root, "init", "--bare", "--initial-branch=main", str(self.remote))
        git(root, "clone", str(self.remote), str(self.editor))
        git(self.editor, "config", "user.name", "test")
        git(self.editor, "config", "user.email", "test@example.invalid")
        (self.editor / "data").mkdir()
        (self.editor / "data" / "snapshot.json").write_text('{"updated":1}')
        (self.editor / "web").mkdir()
        (self.editor / "web" / "template.txt").write_text("v1")
        (self.editor / "build.py").write_text(
            'from pathlib import Path\np=Path(".")\n'
            '(p/"index.html").write_text((p/"web/template.txt").read_text()+"|"+'
            '(p/"data/snapshot.json").read_text())\n')
        (self.editor / "verify.py").write_text(
            'from pathlib import Path\np=Path(".")\n'
            'assert (p/"index.html").read_text().startswith((p/"web/template.txt").read_text())\n')
        (self.editor / "README.md").write_text("original")
        subprocess.run([sys.executable, "build.py"], cwd=self.editor, check=True)
        git(self.editor, "add", ".")
        git(self.editor, "commit", "-m", "Initial repository")
        git(self.editor, "push", "origin", "main")
        git(root, "clone", "--depth=2", "--branch=main", str(self.remote), str(self.worker))
        git(self.worker, "config", "user.name", "test")
        git(self.worker, "config", "user.email", "test@example.invalid")

    def worker_snapshot(self, value='{"updated":2}'):
        (self.worker / "data/snapshot.json").write_text(value)
        subprocess.run([sys.executable, "build.py"], cwd=self.worker, check=True)

    def test_clean_publish(self):
        self.worker_snapshot()
        mod.publish(self.worker)
        git(self.editor, "pull", "--ff-only")
        self.assertEqual((self.editor / "data/snapshot.json").read_text(), '{"updated":2}')
        self.assertEqual((self.editor / "index.html").read_text(), 'v1|{"updated":2}')

    def test_concurrent_readme_change_rebases_and_preserves_both(self):
        self.worker_snapshot()
        (self.editor / "README.md").write_text("changed while collecting")
        git(self.editor, "add", "README.md")
        git(self.editor, "commit", "-m", "Change README")
        git(self.editor, "push", "origin", "main")
        mod.publish(self.worker)
        git(self.editor, "pull", "--ff-only")
        self.assertEqual((self.editor / "README.md").read_text(), "changed while collecting")
        self.assertEqual((self.editor / "data/snapshot.json").read_text(), '{"updated":2}')

    def test_web_template_changed_while_collecting_rebuilds_html(self):
        self.worker_snapshot()
        (self.editor / "web/template.txt").write_text("v2")
        git(self.editor, "add", "web/template.txt")
        git(self.editor, "commit", "-m", "Change layout during collection")
        git(self.editor, "push", "origin", "main")
        mod.publish(self.worker)
        git(self.editor, "pull", "--ff-only")
        self.assertEqual((self.editor / "index.html").read_text(), 'v2|{"updated":2}')

    def test_concurrent_snapshot_conflict_refuses_stale_overwrite(self):
        self.worker_snapshot()
        (self.editor / "data/snapshot.json").write_text('{"updated":3}')
        subprocess.run([sys.executable, "build.py"], cwd=self.editor, check=True)
        git(self.editor, "add", "data/snapshot.json", "index.html")
        git(self.editor, "commit", "-m", "Newer upstream data")
        git(self.editor, "push", "origin", "main")
        with self.assertRaisesRegex(mod.PublishError, "Concurrent conflicting"):
            mod.publish(self.worker)
        git(self.editor, "pull", "--ff-only")
        self.assertEqual((self.editor / "data/snapshot.json").read_text(), '{"updated":3}')
        self.assertEqual((self.editor / "index.html").read_text(), 'v1|{"updated":3}')

    def test_remote_push_between_fetch_and_push_is_retried(self):
        self.worker_snapshot()
        original = mod.command
        attempts = [0]
        def interpose(where, *argv, **kw):
            if argv[:3] == ("git", "push", "origin") and attempts[0] == 0:
                attempts[0] += 1
                (self.editor / "README.md").write_text("race occurred during push")
                git(self.editor, "add", "README.md")
                git(self.editor, "commit", "-m", "Concurrent change")
                git(self.editor, "push", "origin", "main")
            return original(where, *argv, **kw)
        mod.command = interpose
        try:
            mod.publish(self.worker)
        finally:
            mod.command = original
        git(self.editor, "pull", "--ff-only")
        self.assertEqual(attempts[0], 1)
        self.assertEqual((self.editor / "README.md").read_text(), "race occurred during push")
        self.assertEqual((self.editor / "data/snapshot.json").read_text(), '{"updated":2}')

    def test_no_changed_snapshot_does_not_create_commit(self):
        previous = git(self.worker, "rev-parse", "HEAD").stdout.strip()
        mod.publish(self.worker)
        self.assertEqual(git(self.worker, "rev-parse", "HEAD").stdout.strip(), previous)


if __name__ == "__main__":
    unittest.main()

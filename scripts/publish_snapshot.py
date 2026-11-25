"""Safely publish Ludoman's generated snapshot and HTML after collection.

GitHub Actions jobs can run for several minutes. Another commit on main during
collection would otherwise cause a non-fast-forward git push rejection. Rebase
only our generated artifacts, rebuild the HTML with any newly-pushed source,
and retry a bounded number of times. Never force-push or discard conflicts.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import time


class PublishError(RuntimeError):
    """An update could not be safely published."""


def command(cwd: Path, *argv: str, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(argv, cwd=cwd, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, check=False)
    if not allow_failure and result.returncode != 0:
        raise PublishError(f"{' '.join(argv)} failed ({result.returncode}):\n{result.stdout[-2000:]}")
    return result


def publish(root: Path, branch: str = "main", retries: int = 3) -> None:
    if branch != "main":
        raise PublishError("Snapshot publishing is restricted to the main branch")
    if retries < 1 or retries > 5:
        raise PublishError("Invalid publication retry count")

    command(root, "git", "config", "user.name", "github-actions[bot]")
    command(root, "git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    command(root, "git", "add", "--", "data/snapshot.json", "index.html")
    if command(root, "git", "diff", "--cached", "--quiet", allow_failure=True).returncode == 0:
        print("No changed snapshot or page; nothing to publish", flush=True)
        return
    command(root, "git", "commit", "-m", "Refresh LUDOMAN snapshot")

    for attempt in range(1, retries + 1):
        print(f"Publishing snapshot (attempt {attempt}/{retries})", flush=True)
        command(root, "git", "fetch", "origin", "+refs/heads/main:refs/remotes/origin/main")
        before = command(root, "git", "rev-parse", "HEAD").stdout.strip()
        rebase = command(root, "git", "rebase", "refs/remotes/origin/main", allow_failure=True)
        if rebase.returncode:
            # A conflict may mean a second writer changed snapshot.json. Never
            # overwrite someone else's work or silently accept stale data.
            command(root, "git", "rebase", "--abort")
            raise PublishError("Concurrent conflicting changes in main; not overwriting. "
                               "The next scheduled refresh will collect fresh data.\n" +
                               rebase.stdout[-1600:])
        after = command(root, "git", "rev-parse", "HEAD").stdout.strip()
        if after != before:
            # Rebuild using latest source, so a new web template or builder does
            # not get overwritten by HTML generated before an editor's commit.
            command(root, sys.executable, "build.py")
            command(root, sys.executable, "verify.py")
            command(root, "git", "add", "--", "index.html")
            if command(root, "git", "diff", "--cached", "--quiet", allow_failure=True).returncode != 0:
                command(root, "git", "commit", "-m", "Rebuild LUDOMAN page after upstream changes")
        push = command(root, "git", "push", "origin", "HEAD:refs/heads/main", allow_failure=True)
        if push.returncode == 0:
            print("Published fresh Ludoman snapshot to main", flush=True)
            return
        print("Remote branch advanced during push; retrying with fetch/rebase", flush=True)
        if attempt < retries:
            time.sleep(1)
    raise PublishError("GitHub branch changed during all publication attempts; "
                       "leaving branch intact for next scheduled refresh")


if __name__ == "__main__":
    try:
        publish(Path(__file__).resolve().parent.parent)
    except PublishError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        sys.exit(1)

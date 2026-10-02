"""The repository: its root, git facts and repo-relative paths (no absolute path ever reaches an output)."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def rel(path: Path | str) -> str:
    """A repo-relative POSIX path."""
    p = Path(path)
    if p.is_absolute():
        p = p.resolve().relative_to(ROOT)
    return p.as_posix()


def git(*args: str, check: bool = True) -> str:
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=check)
    return out.stdout.decode("utf-8", "replace").strip()


def git_bytes(*args: str) -> bytes | None:
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return out.stdout if out.returncode == 0 else None


def head_commit(short: bool = True) -> str:
    return git("rev-parse", "--short=8" if short else "--verify", "HEAD")


def head_date() -> str:
    """The HEAD commit's date (YYYY-MM-DD): the export folder's date, so a rerun on the same commit names the same folder."""
    return git("log", "-1", "--format=%cs", "HEAD")


def branch() -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD", check=False)


def dirty_paths(paths: list[str]) -> list[str]:
    """The given repo paths with uncommitted changes."""
    if not paths:
        return []
    out = git("status", "--porcelain", "--", *paths, check=False)
    return sorted(line[3:].strip() for line in out.splitlines() if line.strip())


def show(ref: str, path: str) -> bytes | None:
    """A file's bytes at a git ref, or None."""
    return git_bytes("show", f"{ref}:{path}")


def resolve_ref(ref: str) -> str | None:
    out = subprocess.run(["git", "rev-parse", "--short=8", "--verify", f"{ref}^{{commit}}"], cwd=ROOT, capture_output=True)
    return out.stdout.decode().strip() if out.returncode == 0 else None

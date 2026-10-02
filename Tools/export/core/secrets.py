"""The secret scan (spec 8 and 9.9): no output file holds a string matching a secret pattern or an absolute local path."""
from __future__ import annotations

import os
import re
import zipfile
from pathlib import Path

PATTERNS = [
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    ("openai_like_key", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("slack_token", re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}")),
    ("aws_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("password_assignment", re.compile(r"(?i)\b(password|passwd|storepass|keypass|keystorePass(word)?|keyaliasPass)\s*[=:]\s*\S+")),
    ("windows_abs_path", re.compile(r"\b[A-Za-z]:[\\/]+(Users|Documents and Settings|home)[\\/]", re.I)),
    ("unix_home_path", re.compile(r"(?<![\w.])/(Users|home)/[A-Za-z0-9_.\-]+")),
]


def _local_names() -> list[str]:
    names = []
    for var in ("USERNAME", "USER"):
        v = os.environ.get(var, "")
        if len(v) >= 4:
            names.append(v)
    return names


def scan_text(text: str, where: str, hits: list):
    for name, rx in PATTERNS:
        for m in rx.finditer(text):
            hits.append((where, name, m.group(0)[:60]))
    for user in _local_names():
        if re.search(rf"(?<![A-Za-z]){re.escape(user)}(?![A-Za-z])", text):
            hits.append((where, "local_user_name", user[:2] + "…"))


def scan_dir(root: Path) -> list[tuple[str, str, str]]:
    hits: list = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        where = p.relative_to(root).as_posix()
        if p.suffix.lower() == ".xlsx":
            with zipfile.ZipFile(p) as z:
                for info in z.infolist():
                    scan_text(z.read(info).decode("utf-8", "replace"), f"{where}:{info.filename}", hits)
        elif p.suffix.lower() in (".csv", ".md", ".json", ".txt", ".html"):
            scan_text(p.read_text("utf-8", errors="replace"), where, hits)
    return hits

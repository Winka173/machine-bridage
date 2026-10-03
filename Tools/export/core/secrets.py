"""The secret scan (spec 8 and 9.9): no output file holds a string matching a secret pattern (API keys, keystore
passwords, tokens, emails) or an absolute local path."""
from __future__ import annotations

import os
import re
import zipfile
import zlib
from pathlib import Path

PATTERNS = [
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    ("openai_like_key", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("slack_token", re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}")),
    ("aws_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("password_assignment", re.compile(r"(?i)\b(password|passwd|storepass|keypass|keystorePass(word)?|keyaliasPass)\s*[=:]\s*\S+")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")),
    ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9\-._~+/]{20,}=*")),
    ("api_key_assignment", re.compile(r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret)"
                                      r"[\"']?\s*[=:]\s*[\"']?[A-Za-z0-9_\-]{12,}")),
    ("email", re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")),
    ("windows_abs_path", re.compile(r"\b[A-Za-z]:[\\/]+(Users|Documents and Settings|home)[\\/]", re.I)),
    ("unix_home_path", re.compile(r"(?<![\w.])/(Users|home)/[A-Za-z0-9_.\-]+")),
]
TEXT = (".csv", ".md", ".json", ".txt", ".html", ".xml", ".yml", ".yaml", ".svg")
PDF_STREAM = re.compile(rb"stream\r?\n(.*?)\r?\nendstream", re.S)


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


PNG_MAGIC = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
JPEG_START = bytes([0xFF, 0xD8])
JPEG_SCAN = bytes([0xFF, 0xDA])
PNG_TEXT = (b"tEXt", b"iTXt", b"eXIf")


def image_meta(data: bytes, suffix: str) -> str | None:
    """A PNG's or JPEG's metadata only (a PNG's text and EXIF chunks, zTXt inflated; a JPEG's segments before its scan
    data), as Latin-1; None for anything else. The bomb-run fix, pass 4: the compressed pixels read raw matched the email
    pattern by chance (e.g. "PK@Oh.cR" in a model sheet), a false hit in every export with pictures; the metadata (where an
    EXIF path or an author's address would sit) is still read in full."""
    if suffix == ".png" and data[:8] == PNG_MAGIC:
        out, i = [], 8
        while i + 8 <= len(data):
            size = int.from_bytes(data[i:i + 4], "big")
            kind = data[i + 4:i + 8]
            body = data[i + 8:i + 8 + size]
            if kind in PNG_TEXT:
                out.append(body.decode("latin-1"))
            elif kind == b"zTXt":
                key, _, rest = body.partition(bytes([0]))
                try:
                    out.append(key.decode("latin-1") + " " + zlib.decompress(rest[1:]).decode("latin-1"))
                except zlib.error:
                    out.append(body.decode("latin-1"))
            if kind == b"IEND":
                break
            i += 12 + size
        return "\n".join(out)
    if suffix in (".jpg", ".jpeg") and data[:2] == JPEG_START:
        scan = data.find(JPEG_SCAN)
        return data[:scan if scan > 0 else len(data)].decode("latin-1")
    return None


def scan_file(p: Path, where: str, hits: list):
    """Every output file (spec 9.9): zip parts (xlsx / docx) one by one, PDF streams inflated, text as UTF-8, PNG / JPEG
    pictures by their metadata (image_meta), anything else (fonts) as Latin-1 so metadata such as an EXIF path is still
    read."""
    suffix = p.suffix.lower()
    data = p.read_bytes()
    if suffix in (".xlsx", ".docx", ".pptx", ".zip") and zipfile.is_zipfile(p):
        with zipfile.ZipFile(p) as z:
            for info in z.infolist():
                scan_text(z.read(info).decode("utf-8", "replace"), f"{where}:{info.filename}", hits)
    elif suffix == ".pdf":
        scan_text(data.decode("latin-1"), where, hits)
        for i, m in enumerate(PDF_STREAM.finditer(data)):
            try:
                body = zlib.decompress(m.group(1))
            except zlib.error:
                continue
            scan_text(body.decode("latin-1"), f"{where}:stream{i}", hits)
    elif suffix in TEXT:
        scan_text(data.decode("utf-8", "replace"), where, hits)
    elif (meta := image_meta(data, suffix)) is not None:
        scan_text(meta, where, hits)
    else:
        scan_text(data.decode("latin-1"), where, hits)


def files(root: Path) -> list[Path]:
    return [p for p in sorted(root.rglob("*")) if p.is_file() and p.parent.name != "__pycache__"]


def scan_dir(root: Path) -> list[tuple[str, str, str]]:
    hits: list = []
    for p in files(root):
        scan_file(p, p.relative_to(root).as_posix(), hits)
    return hits

"""`export.py pdf`: one PDF from the pack's eight md files, written to <pack>/_qa/ (never into the pack).

The md are joined in file order into <pack>/_qa/Machine_Brigade_Design_<date>.md (picture links one folder up), and
docpdf renders that. Needs PyMuPDF; without it the command says so and writes nothing.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import docpdf, repo
from .pack import PACK


def main(args) -> int:
    out: Path = args.out_dir
    if not all((out / f"{fid}.md").is_file() for fid in PACK):
        print(f"pdf: the pack in {out} has no md files; run export.py first")
        return 1
    if not docpdf.available():
        print("pdf: PyMuPDF is not installed (pip install pymupdf); nothing written")
        return 1
    date, commit = args.date or repo.head_date(), repo.head_commit()
    qa = out / "_qa"
    qa.mkdir(exist_ok=True)
    parts = [f"# Machine Brigade — Tài liệu thiết kế ({date})", "",
             f"Commit {commit}. Ghép từ {len(PACK)} file md của gói cân bằng; bảng lớn nằm trong các file xlsx.", ""]
    for fid in PACK:
        text = (out / f"{fid}.md").read_text("utf-8")
        text = re.sub(r"\]\(images/", "](../images/", text)
        parts += [text.rstrip(), ""]
    md = qa / f"Machine_Brigade_Design_{date}.md"
    md.write_bytes("\n".join(parts).encode("utf-8"))
    pdf = qa / f"Machine_Brigade_Design_{date}.pdf"
    pages = docpdf.render(md, pdf, date, commit)
    print(f"pdf: {pages} pages -> {pdf.relative_to(repo.ROOT).as_posix() if pdf.is_relative_to(repo.ROOT) else pdf.name}")
    return 0

"""The foreign-key test (spec 2.2): every value of a column declared with fk=['<file>/<Sheet>', ...] is an id of one of
those sheets. A target in a domain file not built yet gives PENDING (not a failure)."""
from __future__ import annotations

from .model import MARKER


def check(books: dict) -> list[dict]:
    ids: dict[str, set] = {}
    for fid, book in books.items():
        for name, sheet in book.sheets.items():
            ids[f"{fid}/{name}"] = {str(k) for k in sheet.rows}
    results = []
    for fid in sorted(books):
        book = books[fid]
        for sname, sheet in book.sheets.items():
            for cname, col in sheet.cols.items():
                if not col.fk:
                    continue
                known = [t for t in col.fk if t in ids]
                missing_targets = [t for t in col.fk if t not in ids]
                pool = set().union(*(ids[t] for t in known)) if known else set()
                values, bad = 0, []
                for r in sheet.sorted_rows():
                    v = r.values.get(cname)
                    if v is None or v == "":
                        continue
                    for item in (str(v).split(";") if isinstance(v, str) else [str(v)]):
                        item = item.strip()
                        if not item or MARKER.match(item):
                            continue
                        values += 1
                        if item not in pool:
                            bad.append(f"{r.id}={item}")
                if bad and missing_targets:
                    status = "PENDING"  # the value may live in a file a later lane builds
                elif bad:
                    status = "FAIL"
                elif missing_targets and not known:
                    status = "PENDING"
                else:
                    status = "OK"
                results.append({
                    "file": fid, "sheet": sname, "column": cname, "targets": ";".join(col.fk),
                    "targets_missing": ";".join(missing_targets), "values": values, "errors": len(bad),
                    "status": status, "examples": ";".join(bad[:10]),
                })
    return results

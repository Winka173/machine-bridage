"""In-place editing of balance.json (JSON with // comments, one entry per line).

The importer never re-serialises the file: it finds an entry by its id inside a top-level array
("weapons", "vehicles", "supports") or object, and replaces, inserts or removes one field's value
text, so comments, alignment and every untouched line stay byte for byte as they were.
"""
from __future__ import annotations

import json
import re

WS = " \t\r\n"


def _skip(text: str, i: int) -> int:
    """Skips whitespace and // comments."""
    n = len(text)
    while i < n:
        c = text[i]
        if c in WS:
            i += 1
        elif c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
        else:
            break
    return i


def _string_end(text: str, i: int) -> int:
    """Index just past the string starting at text[i] == '"'."""
    i += 1
    while True:
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == '"':
            return i + 1
        i += 1


def _value_end(text: str, i: int) -> int:
    """Index just past the JSON value starting at i (after whitespace)."""
    c = text[i]
    if c == '"':
        return _string_end(text, i)
    if c in "{[":
        return _match(text, i) + 1
    j = i
    while j < len(text) and text[j] not in ",}]\n\r\t /":
        j += 1
    return j


def _match(text: str, i: int) -> int:
    """Index of the bracket closing the one at text[i]."""
    depth = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == '"':
            i = _string_end(text, i)
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c in "{[":
            depth += 1
        elif c in "}]":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError("unbalanced brackets")


def strip_comments(text: str) -> str:
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = _string_end(text, i)
            out.append(text[i:j])
            i = j
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        out.append(c)
        i += 1
    return re.sub(r",(\s*[\]}])", r"\1", "".join(out))


def loads(text: str):
    return json.loads(strip_comments(text))


def fmt(value) -> str:
    """A value as the file writes it: ints bare, floats to four decimals without trailing zeros."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int,)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        if abs(value - round(value)) < 1e-9:
            return str(int(round(value)))
        s = f"{value:.4f}".rstrip("0").rstrip(".")
        return s
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ", ".join(fmt(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{ " + ", ".join(f"{json.dumps(k)}: {fmt(v)}" for k, v in value.items()) + " }"
    if value is None:
        return "null"
    raise TypeError(type(value))


def value_span(text: str, path: tuple) -> tuple[int, int]:
    """(start, end) of the value text at a path of keys and list indices, from the file's root (any JSON / JSONC
    layout): the import manifest swaps exactly that text, so comments and every other byte stay."""
    i = _skip(text, 0)
    for seg in path:
        c = text[i]
        if isinstance(seg, int):
            if c != "[":
                raise KeyError(f"[{seg}] on a non-list")
            end = _match(text, i)
            j, idx = i + 1, 0
            while True:
                j = _skip(text, j)
                if j >= end:
                    raise KeyError(f"index {seg} out of range")
                if text[j] == ",":
                    j += 1
                    continue
                if idx == seg:
                    i = j
                    break
                j = _value_end(text, j)
                idx += 1
        else:
            if c != "{":
                raise KeyError(f"key {seg!r} on a non-object")
            for k, ks, vs, ve in Entry(text[i:_match(text, i) + 1])._keys():
                if k == seg:
                    i += vs
                    break
            else:
                raise KeyError(f"no key {seg!r}")
    return i, _value_end(text, i)


class Entry:
    """One object's text (its braces included), edited field by field at its own depth."""

    def __init__(self, text: str):
        self.text = text

    def _keys(self):
        """(key, key_start, value_start, value_end) of the object's own fields."""
        t = self.text
        assert t[0] == "{"
        i = 1
        end = len(t) - 1
        while True:
            i = _skip(t, i)
            if i >= end or t[i] == "}":
                return
            if t[i] == ",":
                i += 1
                continue
            ks = i
            ke = _string_end(t, i)
            key = json.loads(t[ks:ke])
            i = _skip(t, ke)
            assert t[i] == ":", t[ks:ks + 40]
            vs = _skip(t, i + 1)
            ve = _value_end(t, vs)
            yield key, ks, vs, ve
            i = ve

    def has(self, key: str) -> bool:
        return any(k == key for k, *_ in self._keys())

    def raw(self, key: str):
        for k, ks, vs, ve in self._keys():
            if k == key:
                return self.text[vs:ve]
        return None

    def get(self, key: str):
        r = self.raw(key)
        return None if r is None else loads(r)

    def set_raw(self, key: str, value_text: str, after: str = "id") -> bool:
        """Sets a field's value text; a new field goes after the <after> field (the id: on the id's line)."""
        for k, ks, vs, ve in self._keys():
            if k == key:
                if self.text[vs:ve] == value_text:
                    return False
                self.text = self.text[:vs] + value_text + self.text[ve:]
                return True
        for k, ks, vs, ve in self._keys():
            if k == after:
                self.text = self.text[:ve] + f', "{key}": {value_text}' + self.text[ve:]
                return True
        raise KeyError(f"no '{after}' field to insert '{key}' after")

    def set(self, key: str, value, after: str = "id") -> bool:
        return self.set_raw(key, fmt(value), after)

    def remove(self, key: str) -> bool:
        keys = list(self._keys())
        for idx, (k, ks, vs, ve) in enumerate(keys):
            if k != key:
                continue
            t = self.text
            # Remove from the comma before the key (the id is always first, so there is one).
            j = ks - 1
            while t[j] in WS:
                j -= 1
            if t[j] == ",":
                self.text = t[:j] + t[ve:]
            else:
                k2 = _skip(t, ve)
                if t[k2] == ",":
                    k2 = _skip(t, k2 + 1)
                self.text = t[:ks] + t[k2:]
            return True
        return False

    def sub(self, key: str) -> "Entry":
        r = self.raw(key)
        if r is None or not r.startswith("{"):
            raise KeyError(key)
        return Entry(r)

    def set_sub(self, key: str, subkey: str, value) -> bool:
        """Sets a field of a nested object (a vehicle's deathExplosion radius)."""
        e = self.sub(key)
        first = next(iter(e._keys()))[0]
        changed = e.set(subkey, value, after=first)
        if changed:
            self.set_raw(key, e.text)
        return changed


class Doc:
    """balance.json (or any JSONC file) with entries found by id and edited in place."""

    def __init__(self, path: str):
        self.path = path
        with open(path, encoding="utf-8", newline="") as f:
            self.text = f.read()
        self.changes: list[str] = []

    def data(self):
        return loads(self.text)

    def _section(self, name: str) -> tuple[int, int]:
        m = re.search(r'\n  "' + re.escape(name) + r'"\s*:\s*', self.text)
        if not m:
            raise KeyError(name)
        start = _skip(self.text, m.end())
        return start, _match(self.text, start)

    def has_section(self, name: str) -> bool:
        return re.search(r'\n  "' + re.escape(name) + r'"\s*:', self.text) is not None

    def _entries(self, name: str):
        """(id, start, end) of each object in the top-level array <name>, end exclusive."""
        s, e = self._section(name)
        t = self.text
        assert t[s] == "[", name
        i = s + 1
        while True:
            i = _skip(t, i)
            if i >= e:
                return
            if t[i] == ",":
                i += 1
                continue
            if t[i] == "{":
                j = _match(t, i) + 1
                m = re.match(r'\{\s*"id"\s*:\s*"([^"]+)"', t[i:j])
                yield (m.group(1) if m else None), i, j
                i = j
                continue
            i = _value_end(t, i)

    def ids(self, name: str) -> list[str]:
        return [i for i, *_ in self._entries(name) if i]

    def entry(self, name: str, id_: str) -> Entry | None:
        for i, s, e in self._entries(name):
            if i == id_:
                return Entry(self.text[s:e])
        return None

    def put(self, name: str, id_: str, entry: Entry, note: str = "") -> bool:
        for i, s, e in self._entries(name):
            if i == id_:
                if self.text[s:e] == entry.text:
                    return False
                self.text = self.text[:s] + entry.text + self.text[e:]
                if note:
                    self.changes.append(note)
                return True
        raise KeyError(f"{name}: no entry '{id_}'")

    def edit(self, name: str, id_: str, fn, note: str = "") -> bool:
        """Runs fn(entry) and writes the entry back when it changed."""
        e = self.entry(name, id_)
        if e is None:
            raise KeyError(f"{name}: no entry '{id_}'")
        fn(e)
        return self.put(name, id_, e, note)

    def insert_after(self, name: str, after_id: str, line: str) -> bool:
        """Adds a new entry on its own line after another entry (a new weapon beside its source)."""
        for i, s, e in self._entries(name):
            if i == after_id:
                eol = self.text.index("\n", e)
                indent = re.match(r"[ ]*", self.text[self.text.rindex("\n", 0, s) + 1:]).group(0)
                seg = self.text[e:eol]
                if not seg.lstrip().startswith(","):
                    self.text = self.text[:e] + "," + self.text[e:]
                    eol += 1
                nl = "\r\n" if self.text[eol - 1] == "\r" else "\n"
                self.text = self.text[:eol + 1] + indent + line + "," + nl + self.text[eol + 1:]
                return True
        raise KeyError(after_id)

    def replace_section(self, name: str, body: str, before: str) -> None:
        """Writes a whole small top-level block (the weapon families): replaced, or put before another."""
        if self.has_section(name):
            s, e = self._section(name)
            self.text = self.text[:s] + body + self.text[e + 1:]
        else:
            m = re.search(r'\n(  //[^\n]*\n)*  "' + re.escape(before) + r'"\s*:', self.text)
            self.text = self.text[:m.start() + 1] + body + "\n\n" + self.text[m.start() + 1:]

    def save(self) -> bool:
        with open(self.path, encoding="utf-8", newline="") as f:
            old = f.read()
        if old == self.text:
            return False
        loads(self.text)  # still valid
        with open(self.path, "w", encoding="utf-8", newline="") as f:
            f.write(self.text)
        return True

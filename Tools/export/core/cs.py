"""Reading C# data that only the code holds, without compiling it.

* read_string_table(text): the HUD text tables ["key"] = ("en", "vi") -> {key: {"en", "vi"}}.
* read_array(text, name): a static literal table (`static readonly T[] Name = { new(...) {...}, ... }` or
  `IReadOnlyList<T> Name = new[] { ... }`) -> a list of rows, each a dict named by the constructor's or helper's
  parameter names found in the same text (plus `extra_text` for types defined elsewhere), with its object initialiser
  fields and `.With(d => ...)` assignments on top. Enum members read as their last name ("StatId.Damage" -> "Damage"),
  flags as "A|B", numbers without their suffix (0.05f -> 0.05).

A construct the reader does not know raises CsError; the caller records the table in Nguon_khong_doc_duoc.
"""
from __future__ import annotations

import re


class CsError(Exception):
    pass


_TOKEN = re.compile(r"""
    (?P<ws>\s+)
  | (?P<lcom>//[^\n]*)
  | (?P<bcom>/\*.*?\*/)
  | (?P<vstr>\$?@"(?:[^"]|"")*")
  | (?P<str>\$?"(?:[^"\\\n]|\\.)*")
  | (?P<chr>'(?:[^'\\]|\\.)')
  | (?P<num>(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?[fFdDmMuUlL]*)
  | (?P<id>[A-Za-z_@][A-Za-z0-9_]*)
  | (?P<op>=>|==|!=|<=|>=|&&|\|\||\?\?|\?\.|[{}()\[\],;:.=+\-*/|&<>?!~^%])
""", re.S | re.X)


def tokenize(text: str, start: int = 0, end: int | None = None):
    end = len(text) if end is None else end
    pos, out = start, []
    while pos < end:
        m = _TOKEN.match(text, pos)
        if not m:
            raise CsError(f"cannot read C# at offset {pos}: {text[pos:pos + 30]!r}")
        kind = m.lastgroup
        if kind not in ("ws", "lcom", "bcom"):
            out.append((kind, m.group(), m.start()))
        pos = m.end()
    return out


def _unquote(tok: str) -> str:
    if tok.startswith("$"):
        tok = tok[1:]
    if tok.startswith("@"):
        return tok[2:-1].replace('""', '"')
    body = tok[1:-1]
    return re.sub(r"\\(u[0-9a-fA-F]{4}|.)", lambda m: chr(int(m.group(1)[1:], 16)) if m.group(1)[0] == "u" and len(m.group(1)) == 5
                  else {"n": "\n", "t": "\t", "r": "\r", "0": "\0"}.get(m.group(1), m.group(1)), body)


def _num(tok: str):
    t = tok.rstrip("fFdDmMuUlL")
    if re.fullmatch(r"\d+", t):
        return int(t)
    return float(t)


class _Parser:
    def __init__(self, toks):
        self.t = toks
        self.i = 0

    def peek(self, k=0):
        j = self.i + k
        return self.t[j] if j < len(self.t) else ("eof", "", -1)

    def take(self, value=None):
        tok = self.peek()
        if value is not None and tok[1] != value:
            raise CsError(f"expected {value!r}, got {tok[1]!r} at offset {tok[2]}")
        self.i += 1
        return tok

    def at(self, value) -> bool:
        return self.peek()[1] == value

    # expr := or ( '+' or )*  (string concatenation / arithmetic kept as text when not two literals)
    def expr(self):
        left = self.flags()
        while self.at("+") or self.at("-") or self.at("*") or self.at("/"):
            op = self.take()[1]
            right = self.flags()
            if op == "+" and isinstance(left, str) and isinstance(right, str):
                left = left + right
            elif isinstance(left, (int, float)) and isinstance(right, (int, float)) and not isinstance(left, bool):
                left = {"+": left + right, "-": left - right, "*": left * right,
                        "/": (left / right) if right else 0}[op]
            else:
                left = {"_expr": f"{_text(left)} {op} {_text(right)}"}
        if self.at("?") and not self.at("?."):
            # a conditional: kept as text
            self.take("?")
            a = self.expr()
            self.take(":")
            b = self.expr()
            left = {"_expr": f"{_text(left)} ? {_text(a)} : {_text(b)}"}
        return left

    def flags(self):
        left = self.unary()
        while self.at("|"):
            self.take()
            right = self.unary()
            left = f"{left}|{right}"
        return left

    def unary(self):
        if self.at("-"):
            self.take()
            v = self.unary()
            return -v if isinstance(v, (int, float)) else {"_expr": f"-{_text(v)}"}
        if self.at("!"):
            self.take()
            return {"_expr": f"!{_text(self.unary())}"}
        return self.postfix(self.primary())

    def postfix(self, v):
        while True:
            if self.at(".") and self.peek(1)[1] == "With" and self.peek(2)[1] == "(":
                self.take(".")
                self.take("With")
                self.take("(")
                assigns = self.lambda_assigns()
                self.take(")")
                if isinstance(v, dict):
                    v = dict(v)
                    v.update(assigns)
                continue
            if self.at(".") and self.peek(1)[0] == "id":
                self.take(".")
                name = self.take()[1]
                if self.at("("):
                    args = self.args("(", ")")
                    v = {"_expr": f"{_text(v)}.{name}({', '.join(_text(a) for a in args)})"}
                else:
                    v = {"_expr": f"{_text(v)}.{name}"}
                continue
            return v

    def lambda_assigns(self):
        self.take()  # the parameter name
        self.take("=>")
        out = {}
        if self.at("{"):
            self.take("{")
            while not self.at("}"):
                self.assign(out)
                if self.at(";"):
                    self.take(";")
            self.take("}")
        else:
            self.assign(out)
        return out

    def assign(self, out):
        name = self.take()[1]
        while self.at("."):
            self.take(".")
            name = self.take()[1]
        self.take("=")
        out[name] = self.expr()

    def primary(self):
        kind, tok, off = self.peek()
        if kind in ("str", "vstr"):
            self.take()
            return _unquote(tok)
        if kind == "chr":
            self.take()
            return tok[1:-1]
        if kind == "num":
            self.take()
            return _num(tok)
        if tok == "(":
            items = self.args("(", ")")
            return items[0] if len(items) == 1 else list(items)
        if tok == "{":
            return self.collection()
        if tok == "new":
            return self.new()
        if kind == "id":
            if tok in ("true", "false"):
                self.take()
                return tok == "true"
            if tok == "null":
                self.take()
                return None
            if tok in ("nameof", "typeof"):
                self.take()
                return _text(self.args("(", ")")[0])
            names = [self.take()[1]]
            while self.at(".") and self.peek(1)[0] == "id" and self.peek(2)[1] not in ("(",) and self.peek(1)[1] != "With":
                self.take(".")
                names.append(self.take()[1])
            if self.at("("):
                args = self.args("(", ")")
                return {"_call": names[-1], "_args": args}
            return names[-1]
        raise CsError(f"unexpected {tok!r} at offset {off}")

    def args(self, open_, close):
        self.take(open_)
        out = []
        while not self.at(close):
            if self.peek()[0] == "id" and self.peek(1)[1] == ":" and self.peek(2)[1] != ":":
                name = self.take()[1]
                self.take(":")
                out.append({"_named": name, "_value": self.expr()})
            else:
                out.append(self.expr())
            if self.at(","):
                self.take(",")
        self.take(close)
        return out

    def collection(self):
        self.take("{")
        items, inits = [], {}
        while not self.at("}"):
            if self.peek()[0] == "id" and self.peek(1)[1] == "=" and self.peek(2)[1] != "=":
                name = self.take()[1]
                self.take("=")
                inits[name] = self.expr()
            elif self.at("["):
                key = self.args("[", "]")
                self.take("=")
                inits[_text(key[0])] = self.expr()
            else:
                items.append(self.expr())
            if self.at(","):
                self.take(",")
        self.take("}")
        if inits and items:
            raise CsError("a collection mixing items and fields")
        return {"_init": inits} if inits else items

    def new(self):
        self.take("new")
        type_name = None
        if self.peek()[0] == "id":
            parts = [self.take()[1]]
            while self.at("."):
                self.take(".")
                parts.append(self.take()[1])
            type_name = parts[-1]
            if self.at("<"):  # generic arguments
                depth = 0
                while True:
                    t = self.take()[1]
                    depth += t == "<"
                    depth -= t == ">"
                    if depth == 0:
                        break
        if self.at("["):
            self.take("[")
            self.take("]")
            items = self.collection() if self.at("{") else []
            return list(items) if isinstance(items, list) else items
        args = self.args("(", ")") if self.at("(") else []
        node = {"_new": type_name, "_args": args}
        if self.at("{"):
            body = self.collection()
            if isinstance(body, dict):
                node.update(body["_init"])
            elif body:
                node["_items"] = body
        return node


def _text(v) -> str:
    if isinstance(v, dict) and "_expr" in v:
        return v["_expr"]
    if isinstance(v, dict) and "_call" in v:
        return f"{v['_call']}({', '.join(_text(a) for a in v['_args'])})"
    if isinstance(v, str):
        return v
    return repr(v)


# ---------------------------------------------------------------------- signatures
_SIG = re.compile(r"(?:(?:public|private|internal|protected|static|readonly|sealed)\s+)+(?:[\w<>\[\]?,.() ]+?\s+)??(\w+)\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*(?:=>|\{|:|where)")


def signatures(text: str) -> dict[str, list[list[tuple[str, object, bool]]]]:
    """Method and constructor overloads by name, each a parameter list [(param, default or None, is_params)]."""
    out: dict[str, list] = {}
    for m in _SIG.finditer(text):
        name, params = m.group(1), m.group(2).strip()
        plist = []
        if params:
            for raw in _split_top(params):
                raw = raw.strip()
                is_params = raw.startswith("params ")
                raw = re.sub(r"^(params|this|ref|out|in)\s+", "", raw)
                default = None
                if "=" in raw:
                    raw, d = raw.split("=", 1)
                    default = d.strip()
                pname = raw.split()[-1] if raw.split() else raw
                plist.append((pname, default, is_params))
        if plist not in out.setdefault(name, []):
            out[name].append(plist)
    return out


def _pick(overloads, nargs: int):
    """The overload a call of nargs positional arguments uses: an exact count first, then defaults, then params."""
    for plist in overloads:
        if len(plist) == nargs and not any(p[2] for p in plist):
            return plist
    for plist in overloads:
        need = sum(1 for p in plist if p[1] is None and not p[2])
        if need <= nargs <= len(plist) and not any(p[2] for p in plist):
            return plist
    for plist in overloads:
        if any(p[2] for p in plist) and nargs >= len(plist) - 1:
            return plist
    return overloads[0] if overloads else None


def _split_top(s: str):
    depth, cur, out = 0, [], []
    for ch in s:
        if ch in "<([":
            depth += 1
        elif ch in ">)]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


def _resolve(v, sigs, type_hint=None):
    if isinstance(v, list):
        return [_resolve(x, sigs, type_hint) for x in v]
    if not isinstance(v, dict):
        return v
    if "_expr" in v:
        return v["_expr"]
    if "_named" in v:
        return v
    if "_call" in v or "_new" in v:
        name = v.get("_call") or v.get("_new") or type_hint
        args = v.get("_args", [])
        positional = sum(1 for a in args if not (isinstance(a, dict) and "_named" in a))
        sig = _pick(sigs[name], positional) if name in sigs else None
        out: dict = {}
        if "_call" in v and sig is not None and name != "V":
            out["_via"] = name
        if sig is None:
            if "_call" in v:
                if name == "V" or all(not isinstance(a, dict) for a in args) and name in ("V",):
                    return [_resolve(a, sigs) for a in args]
                out["_call"] = name
            for k, a in enumerate(args):
                out[f"arg{k}"] = _resolve(a, sigs)
        else:
            k = 0
            for pname, default, is_params in sig:
                if is_params:
                    out[pname] = [_resolve(a, sigs) for a in args[k:] if not (isinstance(a, dict) and "_named" in a)]
                    k = len(args)
                    break
                if k < len(args) and not (isinstance(args[k], dict) and "_named" in args[k]):
                    out[pname] = _resolve(args[k], sigs)
                    k += 1
            for a in args:
                if isinstance(a, dict) and "_named" in a:
                    out[a["_named"]] = _resolve(a["_value"], sigs)
        for key, val in v.items():
            if key in ("_call", "_new", "_args"):
                continue
            out[key] = _resolve(val, sigs)
        if name == "V" and sig is not None and len(sig) == 1 and sig[0][2]:
            return out[sig[0][0]]
        return out
    if "_init" in v:
        return {k: _resolve(x, sigs) for k, x in v["_init"].items()}
    return {k: _resolve(x, sigs) for k, x in v.items()}


_ARRAY_DECL = r"(?:static\s+readonly|readonly\s+static|static)\s+(?P<type>[\w<>\[\](),. ?]+?)\s+{name}\s*=\s*"


def read_array(text: str, name: str, extra_text: str = "") -> tuple[list, list[int]]:
    """The rows of the literal table `name` and each row's line number."""
    m = re.search(_ARRAY_DECL.format(name=re.escape(name)), text)
    if not m:
        raise CsError(f"no table {name}")
    elem = m.group("type")
    gm = re.search(r"<\s*(\w+)\s*>", elem)
    elem_type = gm.group(1) if gm else elem.replace("[]", "").strip().split(".")[-1]
    start = m.end()
    toks = tokenize(text, start, _statement_end(text, start))
    p = _Parser(toks)
    value = p.expr() if p.peek()[1] != "{" else p.collection()
    if isinstance(value, dict) and "_new" in value and "_items" in value:
        value = value["_items"]
    if not isinstance(value, list):
        raise CsError(f"table {name} is not a list")
    sigs = signatures(extra_text + "\n" + text)
    rows = [_resolve(x, sigs, elem_type) for x in value]
    for r in rows:  # a helper's name stays on the row only (which helper built it); nested calls drop it
        if isinstance(r, dict):
            for k, v in r.items():
                _drop_via(v)
    return rows, _element_lines(text, toks)[:len(rows)]


def _drop_via(v):
    if isinstance(v, dict):
        v.pop("_via", None)
        for x in v.values():
            _drop_via(x)
    elif isinstance(v, list):
        for x in v:
            _drop_via(x)


def _element_lines(text, toks):
    """The line of each top-level element of a table's initialiser ('{ a, b }' or 'new[] { a, b }')."""
    if len(toks) >= 3 and toks[0][1] == "new" and toks[1][1] == "[":
        toks = toks[3:]
    lines, depth, expect = [], 0, True
    for kind, tok, off in toks:
        if depth == 1 and expect and tok not in ("}", ","):
            lines.append(text.count(chr(10), 0, off) + 1)
            expect = False
        if tok in "({[":
            depth += 1
        elif tok in ")}]":
            depth -= 1
        elif tok == "," and depth == 1:
            expect = True
    return lines


def _statement_end(text: str, start: int) -> int:
    """The offset of the ';' closing a field initialiser starting at `start` (brackets and strings skipped)."""
    depth = 0
    for kind, tok, off in tokenize_iter(text, start):
        if tok in "({[":
            depth += 1
        elif tok in ")}]":
            depth -= 1
        elif tok == ";" and depth == 0:
            return off
    raise CsError("unterminated initialiser")


def tokenize_iter(text: str, start: int):
    pos = start
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        if not m:
            raise CsError(f"cannot read C# at offset {pos}")
        if m.lastgroup not in ("ws", "lcom", "bcom"):
            yield m.lastgroup, m.group(), m.start()
        pos = m.end()


def read_string_table(text: str) -> dict[str, dict[str, str]]:
    """Every ["key"] = ("en", "vi") entry of a HUD text table (strings joined across '+')."""
    out: dict[str, dict[str, str]] = {}
    for m in re.finditer(r'\[\s*"((?:[^"\\]|\\.)+)"\s*\]\s*=\s*\(', text):
        start = m.end() - 1
        depth, pos, end = 0, start, None
        for kind, tok, off in tokenize_iter(text, start):
            if tok == "(":
                depth += 1
            elif tok == ")":
                depth -= 1
                if depth == 0:
                    end = off + 1
                    break
        if end is None:
            continue
        p = _Parser(tokenize(text, start, end))
        try:
            vals = p.args("(", ")")
        except CsError:
            continue
        if len(vals) != 2:
            continue
        en, vi = (v if isinstance(v, str) else _text(v) for v in vals)
        out[m.group(1)] = {"en": en, "vi": vi}
    return out

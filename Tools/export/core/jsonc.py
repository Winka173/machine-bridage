"""JSON with // and /* */ comments and trailing commas (balance.json, release.json): read as the game's MiniJson reads it."""
from __future__ import annotations

import json


def strip(text: str) -> str:
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == '"':
                    break
                j += 1
            out.append(text[i:j + 1])
            i = j + 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        if c in "]}":
            # a trailing comma before the bracket (outside strings) goes
            k = len(out) - 1
            while k >= 0 and out[k].isspace():
                k -= 1
            if k >= 0 and out[k] == ",":
                out[k] = ""
        out.append(c)
        i += 1
    return "".join(out)


def loads(text: str):
    if text.startswith("﻿"):
        text = text[1:]
    return json.loads(strip(text))

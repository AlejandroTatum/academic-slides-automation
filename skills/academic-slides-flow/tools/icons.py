#!/usr/bin/env python3
"""Lucide icons for decks, from the vendored data in assets/icons/lucide/.

    icons.py search WORD...    names whose name or tags contain every word (max 20)
    icons.py sprite NAME...    inline <svg> sprite with one <symbol id="i-NAME"> each

Paste the sprite once after <body>; use an icon with
<svg class="icon"><use href="#i-NAME"/></svg>. Exit 1 on an unknown name or
no match, 2 for usage. Lucide is ISC licensed (assets/icons/lucide/LICENSE).
"""

from __future__ import annotations

import difflib
import html
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "assets" / "icons" / "lucide"
USAGE = "usage: icons.py search WORD... | icons.py sprite NAME..."
MAX_HITS = 20


def load(name: str) -> dict:
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


def element(tag: str, attrs: dict) -> str:
    body = " ".join(f'{key}="{html.escape(str(value), quote=True)}"' for key, value in attrs.items())
    return f"<{tag} {body}/>"


def sprite(names: list[str]) -> tuple[int, str]:
    nodes = load("icon-nodes")
    unique = list(dict.fromkeys(names))
    for name in unique:
        if name not in nodes:
            close = difflib.get_close_matches(name, nodes, n=3)
            hint = f" (did you mean {', '.join(close)}?)" if close else ""
            return 1, f"icons: unknown {name}{hint}\n"
    symbols = [
        f'  <symbol id="i-{name}" viewBox="0 0 24 24">' + "".join(element(tag, attrs) for tag, attrs in nodes[name]) + "</symbol>"
        for name in unique
    ]
    return 0, '<svg width="0" height="0" style="position:absolute" aria-hidden="true">\n' + "\n".join(symbols) + "\n</svg>\n"


def search(words: list[str]) -> tuple[int, str]:
    tags = load("tags")
    wanted = [word.lower() for word in words]
    hits = []
    for name in sorted(tags):
        haystack = " ".join([name, *tags[name]]).lower()
        if all(word in haystack for word in wanted):
            hits.append(name)
    # Name matches first, then tag-only matches.
    hits.sort(key=lambda n: (not all(w in n for w in wanted), n))
    if not hits:
        return 1, f"icons: no match for {' '.join(words)}\n"
    return 0, "\n".join(hits[:MAX_HITS]) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) < 2 or args[0] not in {"search", "sprite"}:
        print(USAGE, file=sys.stderr)
        return 2
    code, out = (sprite if args[0] == "sprite" else search)(args[1:])
    sys.stdout.write(out)
    return code


if __name__ == "__main__":
    sys.exit(main())

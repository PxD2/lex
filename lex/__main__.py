from __future__ import annotations

import json
import sys

from .codec import Library, decode, encode, stats


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help"}:
        print("usage: python3 -m lex encode|decode|list|stats [arg]")
        return 0
    cmd = args[0]
    lib = Library.load()
    if cmd == "encode":
        text = " ".join(args[1:]) or sys.stdin.read()
        out = encode(text, lib)
        print(json.dumps(out, indent=2))
        return 0
    if cmd == "decode":
        if len(args) < 2:
            print("decode needs hex", file=sys.stderr)
            return 2
        print(json.dumps(decode(args[1], lib), indent=2))
        return 0
    if cmd == "list":
        for row in lib.entries():
            print(f"{row['id']:>5}  {row['width']}B  {row['sentence']}")
        return 0
    if cmd == "stats":
        print(json.dumps(stats(lib), indent=2))
        return 0
    print(f"unknown command {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

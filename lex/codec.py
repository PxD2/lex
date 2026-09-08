"""Closed-book ideogram codec. Meaning is in the library, not the wire."""
from __future__ import annotations

import json
import re
import struct
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAGIC = b"LEX1"


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9%.\-\s]", " ", s.lower())).strip()


class Library:
    def __init__(self, data: dict):
        self.data = data
        self.by_id = {int(e["id"]): e for e in data["sentences"]}
        raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        self.crc32 = zlib.crc32(raw) & 0xFFFFFFFF

    @classmethod
    def load(cls, path: Path | None = None) -> "Library":
        p = path or HERE / "library.json"
        return cls(json.loads(p.read_text()))

    def width_for(self, sid: int) -> int:
        n = max(self.by_id) if self.by_id else 0
        if n <= 255:
            return 1
        if n <= 65535:
            return 2
        return 4

    def entries(self) -> list[dict]:
        out = []
        for e in self.data["sentences"]:
            row = dict(e)
            row["width"] = self.width_for(int(e["id"]))
            out.append(row)
        return out

    def fill(self, template: str, slots: dict) -> str:
        def repl(m: re.Match[str]) -> str:
            k = m.group(1)
            v = slots.get(k)
            if v is None:
                return "0" if k in {"pct", "n"} else "—"
            return str(v)

        return re.sub(r"\{(\w+)\}", repl, template)

    def correlate(self, text: str) -> dict | None:
        t = _norm(text)
        best = None
        best_score = 0
        words = set(w for w in t.split() if len(w) > 1)
        for e in self.data["sentences"]:
            sc = 0
            tmpl = _norm(e["sentence"])
            if tmpl[:24] and tmpl[:24] in t:
                sc += 12
            for w in re.split(r"[^a-z0-9]+", e["sentence"].lower()):
                if len(w) > 2 and w in words:
                    sc += 1
            for k in e.get("keys", []):
                if k in t:
                    sc += 3
            if sc > best_score:
                best_score = sc
                best = e
        if not best or best_score <= 0:
            return None
        return {"entry": best, "score": best_score}

    def extract_slots(self, text: str) -> dict:
        slots: dict = {}
        pct = re.search(r"(\d+)\s*(%|percent)", text, re.I)
        if pct:
            slots["pct"] = int(pct.group(1))
        num = re.search(r"\b(\d{1,4})\b", text)
        if num and slots.get("pct") != int(num.group(1)):
            slots["n"] = int(num.group(1))
        return slots


def encode(text: str, lib: Library | None = None) -> dict:
    lib = lib or Library.load()
    hit = lib.correlate(text)
    if not hit:
        raise ValueError("no sentence in this library correlates")
    entry = hit["entry"]
    sid = int(entry["id"])
    slots = lib.extract_slots(text)
    width = lib.width_for(sid)
    mask = 0
    extra = b""
    if "pct" in entry.get("slots", []) and "pct" in slots:
        mask |= 1
        extra += bytes([max(0, min(100, int(slots["pct"])))])
    if "n" in entry.get("slots", []) and "n" in slots:
        mask |= 2
        extra += struct.pack(">H", max(0, min(65535, int(slots["n"]))))
    id_bytes = sid.to_bytes(width, "big")
    frame = MAGIC + bytes([width]) + struct.pack(">I", lib.crc32) + id_bytes + bytes([mask]) + extra
    sentence = lib.fill(entry["sentence"], slots)
    return {
        "id": sid,
        "width": width,
        "hex": frame.hex(),
        "bytes": len(frame),
        "library_crc32": f"{lib.crc32:08x}",
        "sentence": sentence,
        "expanded_bytes": len(sentence.encode()),
        "ratio": round(len(sentence.encode()) / max(1, len(frame)), 1),
        "score": hit["score"],
        "slots": slots,
    }


def decode(hexstr: str, lib: Library | None = None) -> dict:
    lib = lib or Library.load()
    data = bytes.fromhex(re.sub(r"[^0-9a-f]", "", hexstr.lower()))
    if data[:4] != MAGIC:
        raise ValueError("not a LEX1 frame")
    width = data[4]
    crc = struct.unpack(">I", data[5:9])[0]
    if crc != lib.crc32:
        raise ValueError("library hash mismatch — both ends must share the same book")
    sid = int.from_bytes(data[9 : 9 + width], "big")
    mask = data[9 + width]
    i = 10 + width
    slots: dict = {}
    if mask & 1:
        slots["pct"] = data[i]
        i += 1
    if mask & 2:
        slots["n"] = struct.unpack(">H", data[i : i + 2])[0]
    entry = lib.by_id.get(sid)
    if not entry:
        raise ValueError(f"unknown ideogram {sid}")
    sentence = lib.fill(entry["sentence"], slots)
    return {
        "id": sid,
        "width": width,
        "hex": data.hex(),
        "bytes": len(data),
        "sentence": sentence,
        "expanded_bytes": len(sentence.encode()),
        "ratio": round(len(sentence.encode()) / max(1, len(data)), 1),
        "slots": slots,
        "library_crc32": f"{lib.crc32:08x}",
    }


def stats(lib: Library | None = None) -> dict:
    lib = lib or Library.load()
    n = len(lib.by_id)
    width = 1 if n <= 256 else 2 if n <= 65536 else 4
    texts = [e["sentence"] for e in lib.data["sentences"]]
    avg = sum(len(t.encode()) for t in texts) / max(1, n)
    return {
        "sentences": n,
        "recommended_width": width,
        "capacity": 256 if width == 1 else 65536 if width == 2 else 4294967296,
        "avg_paragraph_bytes": round(avg, 1),
        "wire_bytes_per_hit": width,
        "nominal_reduction_pct": round(100 * (1 - width / max(1, avg)), 2),
        "library_crc32": f"{lib.crc32:08x}",
        "note": "reduction assumes the receiver already holds this library",
    }

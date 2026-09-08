# PXD2 LEX

**Shared ideogram layer for storage and transfer.**
A single 1-, 2-, or 4-byte symbol expands to a pre-agreed sentence or paragraph.
The wire stays small. Meaning lives in a versioned lookup library both ends already hold.

This is the public contract for PXD2 data density.
Keyed one-shot pages live in private [`cyrptonics`](https://github.com/PxD2/cyrptonics).
The on-disk container is [`.PMOC`](https://github.com/PxD2/PMOC) slice kind `3` (lex).
Control slots ride [Numerical Sentencing](https://github.com/PxD2/numerical-sentencing).

[Walk the floor](https://pxd2.github.io/) · Chad Peters · PXD2 Soft Dev Group · Arizona

## What it is

Not a general-purpose compressor. Not a chatbot prompt.

It is a **closed vocabulary** with a **numeric handle**:

| Library | Symbol | Capacity | On the wire |
| --- | --- | --- | --- |
| Small | 1 byte (`u8`) | 256 paragraphs | 1 byte |
| Medium | 2 bytes (`u16`) | 65,536 paragraphs | 2 bytes |
| Ultimate | 4 bytes (`u32`) | 4,294,967,296 paragraphs | 4 bytes |

Same idea as Q-codes on Morse and HTTP `404` — a short token that *means* a long sentence — sized for radio, logs, and `.pmoc` slices instead of telegraph or browsers.

Savings only count **after both ends share the same library hash**. The library is the product. The symbol is the receipt.

## Frame

```
LEX1 | width | lib_crc32 | id | slot_mask | slots…
```

- `width` — 1, 2, or 4
- `lib_crc32` — refuse a frame if the book does not match
- `id` — the ideogram
- `slot_mask` — optional `pct` (u8) and `n` (u16) so one paragraph can carry live numbers

A 500-byte status paragraph becomes **1 byte + slots**, not 500 bytes of UTF-8.
That is the 99%+ cut — on closed books, not on arbitrary internet text.

## Run

```bash
python3 -m lex encode "System diagnostic complete. All thrusters operational. Battery at 94%."
python3 -m lex decode <hex>
python3 -m lex list
python3 -m lex stats
```

## Product map

```
text / task
    → L1 LEX   ideogram id          (this repo)
    → L2 PAGE  expendable radio page (cyrptonics)
    → L3 SEQ   LoRa / warble / pack  (mesh-brain)
    → .PMOC    lex slice on disk     (PMOC)
```

## Commercial use

- Air-gapped status and command (the book is pre-positioned; the radio only carries ids)
- Game / NPC / droid speech packs
- Telemetry that must fit a 237-byte LoRa payload
- Audit logs that store ids and expand at the CORE

Dynamic minting (assign a new id on the fly) is supported as a **library revision**. Sync the book out of band. Do not pretend a 4-byte id invents a paragraph the receiver has never seen.

## License split

- LEX method and directory design © Chad Peters / PXD2 Soft Dev Group
- Implementation files in this repository: Apache-2.0
- Private encoder, Rolodex keys, and production lexicon stay in `cyrptonics` until assigned into PXD2, Inc.

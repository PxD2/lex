# PXD2 LEX — storage and transfer spec (public)

## Claim, tightly

A shared, versioned library maps an integer to a paragraph.
The integer is what you store and what you send.
The paragraph is what you print, speak, or act.

This is dictionary coding with a product wrapper: library hash on the wire,
parameter slots, `.PMOC` slice kind, and a radio page in front of it.

## Widths

| Width | Type | Unique paragraphs |
| ---: | --- | ---: |
| 1 | unsigned 8-bit | 256 |
| 2 | unsigned 16-bit | 65,536 |
| 4 | unsigned 32-bit | 4,294,967,296 |

Pick the smallest width that holds the book you actually ship.
A 4-byte id is not "more compressed" than a 1-byte id. It is a larger book.

## What you must ship once

1. Library JSON (or a `.pmoc` lex slice)
2. `crc32` of the canonical book
3. Decoder that refuses a mismatched hash

After that, traffic is ids + slots.

## What you must not claim

- That 4 bytes can represent *any* English paragraph without a shared book
- That this beats gzip on open, one-off documents
- That minting ids on the fly is free — each mint is a library revision

## Sisters

- `cyrptonics` — Feistel-scrambled directory id + expendable page key
- `numerical-sentencing` — ordered numeric roles; LEX id can be one role
- `ternary-binary` — optional denser packing *inside* a LoRa payload
- `PMOC` — on-disk layout; lex slices are immutable at the leaf

## Inventor record

Method © Chad Peters / PXD2 Soft Dev Group. Implementation here is Apache-2.0 scaffolding.

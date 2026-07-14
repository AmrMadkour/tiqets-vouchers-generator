# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Python CLI that reads `orders.csv` and `barcodes.csv`, validates them, and produces a grouped
output CSV for voucher printing, plus bonus stdout stats and a SQL data model. This is a graded
take-home assignment (original PDF: `Tiqets Programming Assignment_ CSV files.pdf`).

The authoritative requirements live in **`Tiqets-Voucher-Generator-Spec.md`** — read it before
making any design decision; don't re-derive requirements from scratch. Milestone progress is
tracked in **`Tiqets-Voucher-Generator-Plan.md`**.

## Current status

M0 (environment setup — `requirements.txt`, venv, `tests/` folder, `README.md` skeleton) and M1
(`models/order.py`, `models/barcode.py` dataclasses) are done. `io/`, `validation/`, `service/`,
and `main.py` don't exist yet — next up is M2 (IO layer).

## Commands

- Install deps: `pip install -r requirements.txt`
- Run all tests: `pytest tests/ -v`
- Run a single test: `pytest tests/test_<module>.py::test_name -v`
- Run the app: `python main.py <orders.csv> <barcodes.csv>` (exact CLI signature finalized at
  milestone M5)

Slash commands available: `/run` (auto-detects how to run the project), `/run-tests` (auto-detects
test framework, asks full suite vs. specific scope), `/test` (strict TDD red→green workflow).

## Architecture

Lightweight layered structure (spec §5) — deliberately **not** Clean Architecture (no use
cases/entities/adapters layers; considered over-engineering for a CSV-processing script):

- **`models/`** — plain dataclasses `Order` (order_id, customer_id) and `Barcode` (barcode,
  order_id). No `Customer` class — `customer_id` is just a field on `Order`, since customers have
  no attributes or behavior beyond that ID.
- **`io/`** — CSV readers for `orders.csv`/`barcodes.csv` and the writer for the output CSV.
  Isolated from business logic so it's mockable in tests.
- **`validation/`** — two rules only, both logged to stderr and non-fatal (not exceptions): drop
  duplicate barcodes, drop orders left with zero valid barcodes. Returns cleaned data + rejected
  items.
- **`service/`** (core business logic) — groups barcodes by order/customer, ranks top-5 customers
  by ticket count, counts unused barcodes. Takes parsed data in, returns results out, no file I/O.
  **Important:** both bonus stats (top-5, unused count) are computed from the *post-validation*
  (cleaned) dataset, not raw input — this is a deliberate decision (spec §7.2), not incidental.
- **`main.py`** — CLI entry point wiring `io(read) → validation → service → io(write)` +
  stdout bonus output + stderr rejection logs.

Tests mirror these layers in `tests/`: `test_io.py`, `test_validation.py`, `test_service.py`.

## Output contract (must match exactly — spec §7.1)

```
customer_id,order_id,barcodes
10,1,"[11111111111, 11111111112]"
```

Literal square brackets inside a quoted CSV cell — quoted because the barcodes column is a new
column added on top of the source CSVs, and it contains commas between barcode values;
without quoting, a CSV parser would treat those inner commas as column separators. One row per
`(customer_id, order_id)` pair. No log files — validation rejections go to stderr only, bonus
stats (top-5 customers, unused-barcode count) go to stdout only.

## Non-functional notes

- Designed for a single-pass/streaming approach (no nested loops / repeated full-file scans) even
  though the real sample data is small (~200 orders / ~620 barcodes) — a self-imposed
  production-readiness assumption, not a stated client requirement (spec §8).
- SQL bonus requires **both** an ERD (primary artifact) and a UML class diagram (supplementary) —
  spec §10.
- Documentation is intentionally consolidated into `README.md` (including a "Design Decisions"
  section) rather than a separate `DECISIONS.md`, so a reviewer only needs to open one file.

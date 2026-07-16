# Tiqets Voucher Generator — Milestone Plan

Ordered milestone breakdown derived from `Spec.md`,
dependency-first, covering the full development lifecycle through to
production-ready delivery. Check off each milestone as it's completed.

## M0 — Environment & repo baseline
- [x] `requirements.txt` with `pytest`
- [x] venv + install deps
- [x] `tests/` folder created
- [x] `README.md` skeleton: description, How to Run, How to Test, Design
      Decisions (placeholder), Deployment (placeholder)

## M1 — Models (`models/`)
- [x] `Order` dataclass: `order_id`, `customer_id`
- [x] `Barcode` dataclass: `barcode`, `order_id` (optional/nullable)

## M2 — IO layer (`csv_io/`) — done
- [x] Reader: `orders.csv` → `list[Order]`, skips + logs rows with a
      malformed (non-numeric) `order_id`/`customer_id` instead of raising
- [x] Reader: `barcodes.csv` → `list[Barcode]`, same skip + log behavior for
      a malformed `order_id`
- [x] Writer: grouped rows → `vouchers.csv`, exact bracket + quoting format
      per spec §7.1; accepts an iterable so it can stream rows out without
      requiring a fully materialized list
- [x] Tests (`tests/test_io.py`, 10 tests): valid rows, malformed/empty file
      edge cases, exact output-format match

  **Design decision:** readers return a plain `list`, not a generator — see
  README's Design Decisions section for the reasoning.

## M3 — Validation (`validation/`) — done
- [x] Rule: `drop_duplicate_barcodes` — drops **all** occurrences of a
      barcode appearing more than once (not "keep first"), logs to stderr
- [x] Rule: `drop_orders_without_barcodes` — drops orders left with zero
      valid barcodes after the duplicate rule runs, logs to stderr
- [x] Returns cleaned `Order`/`Barcode` lists + rejected items (for logging)
- [x] Tests (`tests/test_validation.py`, 9 tests): each rule individually,
      edge cases (empty input, all valid, all invalid); no combined test —
      `drop_orders_without_barcodes` can't distinguish "never had a barcode"
      from "barcodes filtered out upstream," so a combined test would just
      re-exercise the same code path as the individual tests

## M4 — Service/core (`service/`) — done
- [x] `grouping.group_barcodes(orders, barcodes)` → `{(customer_id, order_id):
      [barcodes]}`; `grouping.build_rows(grouped)` → generator of
      `(customer_id, order_id, barcodes)` tuples for the writer (the one
      place laziness is genuinely used — see M2 note)
- [x] `top_customers.top_5_customers(grouped)` — sums ticket count per
      customer across all their orders, sorted by count desc then
      `customer_id` asc for deterministic ties, capped at 5
- [x] `unused_barcodes.count_unused_barcodes(barcodes)` — count of barcodes
      with `order_id is None`
- [x] Tests (`tests/test_service.py`, 12 tests): grouping correctness
      (incl. ignoring unsold barcodes), top-5 incl. cap and ties, unused
      count, empty-input edge cases
- Printing the stdout bonus stats (spec §7.2) is `main.py`'s job (M5), not
  `service/`'s — `service/` only returns data, no stdout I/O.

## M5 — CLI wiring (`main.py`) — done
- [x] Wire csv_io(read) → validation → service → csv_io(write) + stdout bonus
      prints + stderr logs
- [x] End-to-end test run against the real `data/orders.csv` +
      `data/barcodes.csv` — ran manually, output confirmed

## M6 — Code quality pass — done
- [x] Static analysis (`ruff`) run — no correctness issues found; cosmetic
      findings left as-is (see README's Design Decisions section).
- [x] Reviewed against spec §9 clean code / SOLID checklist — found and fixed
      two gaps: unhandled `FileNotFoundError` on a missing input file, and a
      missing/misspelled CSV column miscaught by the wrong exception type in
      both readers. Covered by new tests (`tests/test_main.py`, additions to
      `tests/test_io.py`).

## M7 — SQL data model — done
- [x] ERD (tables/keys/indexes) — primary artifact (spec §10)
- [x] UML class diagram considered, then dropped — duplicated the same
      entities/relationships as the ERD with less detail, pure redundancy
- [x] Tool: Mermaid (text-first, diffable, renders natively on GitHub) — also
      exported to static PNG via `mermaid-cli` for viewing outside GitHub
      (no third-party upload)
- [x] Delivered in `docs/data-model/SQL-Model.md`: 3-table schema
      (`customers`, `orders`, `barcodes`) with full DDL, indexes matching the
      program's actual queries, ERD, and a Design Decisions section

## M8 — Production-readiness docs — done
- [x] `README.md` finalized: Design Decisions section, Deployment section
- [x] This file kept up to date as milestones complete

## M9 — Final review — done
- [x] Compared finished project against the spec + original PDF assignment,
      line by line — matches, including the documented CSV header/quoting
      deviation from the PDF's informal example format
- [x] Confirmed all validation rules, bonus outputs, and deliverables are
      present — duplicate-barcode drop, orphaned-order drop, top-5, unused
      count, SQL ERD all verified against code
- [x] Verified every decision in README's Design Decisions section was
      actually implemented as decided — spot-checked the code, all held up.
      Found and fixed one uncovered gap: `group_barcodes` raised an unhandled
      `KeyError` if a barcode's `order_id` didn't match any known order (not
      one of the assignment's two validation rules, and never triggered by
      the real sample data, but a real crash risk on bad input) — now
      skipped + logged to stderr instead, covered by a new test

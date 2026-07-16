# Tiqets Voucher Generator — Milestone Plan

Ordered milestone breakdown derived from `Tiqets-Voucher-Generator-Spec.md`,
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

  **Design decision — plain list, not generator, for readers:** readers
  return a fully materialized `list`, not a lazy generator. Originally built
  as generators for single-pass/constant-memory reasoning, but reconsidered:
  every real caller (`validation/`) immediately does `list(read_orders(...))`
  and, worse, needs *two* passes over the data (build a count/set, then
  filter) — a generator can only be iterated once, so validation would be
  forced to materialize into a list as its very first step regardless. There
  is no code path in this project where the readers' laziness is ever
  exercised, so keeping them lazy would be designing for a hypothetical
  future requirement rather than an actual one. Laziness is still used where
  it's genuinely exercised: the `service/`-to-`write_vouchers` step generates
  `(customer_id, order_id, barcodes)` rows on the fly from the grouped dict,
  since the writer consumes them in a single forward pass without needing to
  re-scan — that avoids a real, avoidable second copy of the output rows
  sitting in memory next to the dict.

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
- [ ] Actual `print(...)` to stdout in the exact `customer_id,amount_of_
      tickets` format (spec §7.2) is **not** `service/`'s job — `service/`
      only returns data (no file/stdout I/O). Printing happens in `main.py`
      (M5), with its own tests there.

## M5 — CLI wiring (`main.py`) — done
- [x] Wire csv_io(read) → validation → service → csv_io(write) + stdout bonus
      prints + stderr logs
- [x] End-to-end test run against the real `data/orders.csv` +
      `data/barcodes.csv` — ran manually, output confirmed; stdout formatting
      polish deferred to a later pass (tracked below, not blocking M5)

## M6 — Code quality pass
- [ ] Run static analysis (ruff or pylint), fix flagged issues
- [ ] Review against spec §9 clean code / SOLID checklist

## M7 — SQL data model bonus — done
- [x] ERD (tables/keys/indexes) — primary artifact (spec §10)
- [x] UML class diagram — supplementary artifact
- [x] Tool: Mermaid (text-first, diffable, renders natively on GitHub) — both
      diagrams also exported to static PNG via `mermaid-cli` for viewing
      outside GitHub (no third-party upload)
- [x] Delivered in `docs/Tiqets-Voucher-Generator-SQL-Model.md`: 3-table
      schema (`customers`, `orders`, `barcodes`) with full DDL, indexes on
      `orders.customer_id`/`barcodes.order_id` matching the program's actual
      queries, ERD, UML class diagram, and a Design Decisions section
      (no junction tables — both relationships are 1-to-many per spec §3, not
      M2M; `DECIMAL` not `FLOAT` for money; `VARCHAR`+`CHECK` not `ENUM` for
      portability; `barcode` typed `VARCHAR` not numeric)

## M8 — Production-readiness docs
- [ ] Finalize `README.md`: Design Decisions section (output-format §7.1,
      scale-assumption §8, ERD+UML §10), Deployment plan section
- [ ] Update this file, marking milestones complete

  **Decisions to write up in README's Design Decisions section** (running
  list, add to as more come up):
  - Malformed `order_id`/`customer_id`: skip + log at read time, not raise —
    IDs stay `int` (not relaxed to `str`) for the future SQL model (§10).
  - No Pydantic for CSV row parsing — considered, rejected: new dependency +
    contradicts M1's plain-dataclass choice, for 2 fields where manual
    `int()` parsing is equally simple. Would reconsider if the model surface
    grew significantly.
  - Readers (`csv_io/`) return plain `list`s, not generators — every real
    caller (`validation/`) always fully materializes and needs 2 passes
    (count/set-building, then filter), so laziness was never exercised.
    Reversed from an earlier generator-based design (see M2 note above).
  - Duplicate-barcode rule: drop **all** occurrences of a barcode that
    appears more than once, not "keep first, drop rest" — a duplicated
    barcode can't be trusted regardless of whether the repeats share an
    order_id, since the same physical barcode assigned to two different
    orders is a genuine conflict the CSV alone can't resolve.
  - Async not used anywhere — no concurrent I/O to overlap in a single-shot
    CLI reading local files; would matter if this became a service handling
    concurrent requests, not for this script.
  - `validation/` and `service/` each materialize their own structures
    (several `O(n)` copies stacked) rather than sharing one grouped dict —
    accepted tradeoff: keeps both layers independently testable (spec §9,
    SOLID), still `O(n)` overall (no nested loops), not `O(n²)`.
  - `defaultdict(list)` over `dict.setdefault(key, [])` for grouping in
    `service/` — avoids constructing a throwaway empty list on every call.
  - Delivery approach: `.claude/` + `CLAUDE.md` stay tracked on `main` (used
    across dev sessions), stripped only on a `deliver` branch + `git
    archive` zip at the very end — see Deployment/Delivery section.

## M9 — Final review
- [ ] Compare finished project against the spec + original PDF assignment,
      line by line
- [ ] Confirm all validation rules, bonus outputs, and deliverables are
      present
- [ ] Verify every decision listed under M8 above was actually implemented
      as decided (not just written down) — spot-check the corresponding code

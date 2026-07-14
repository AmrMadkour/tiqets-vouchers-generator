# Tiqets Voucher Generator — Milestone Plan

Ordered milestone breakdown derived from `Tiqets-Voucher-Generator-Spec.md`,
dependency-first, covering the full development lifecycle through to
production-ready delivery. Check off each milestone as it's completed.

## M0 — Environment & repo baseline
- [ ] `requirements.txt` with `pytest`
- [ ] venv + install deps
- [ ] `tests/` folder created
- [ ] `README.md` skeleton: description, How to Run, How to Test, Design
      Decisions (placeholder), Deployment (placeholder)

## M1 — Models (`models/`)
- [ ] `Order` dataclass: `order_id`, `customer_id`
- [ ] `Barcode` dataclass: `barcode`, `order_id` (optional/nullable)
- [ ] Tests (`tests/test_models.py`): construction/equality

## M2 — IO layer (`io/`)
- [ ] Reader: `orders.csv` → `list[Order]`
- [ ] Reader: `barcodes.csv` → `list[Barcode]`
- [ ] Writer: grouped rows → `vouchers.csv`, exact bracket + quoting format
      per spec §7.1
- [ ] Tests (`tests/test_io.py`): valid rows, malformed/empty file edge
      cases, exact output-format match

## M3 — Validation (`validation/`)
- [ ] Rule: drop duplicate barcodes, log to stderr
- [ ] Rule: drop orders with zero valid barcodes, log to stderr
- [ ] Returns cleaned `Order`/`Barcode` lists + rejected items (for logging)
- [ ] Tests (`tests/test_validation.py`): each rule individually, combined,
      edge cases (empty input, all valid, all invalid)

## M4 — Service/core (`service/`)
- [ ] Group barcodes by order, orders by customer → output rows
- [ ] Top-5 customers by ticket count, computed post-validation (spec
      §7.2), including tie handling
- [ ] Unused barcode count, computed post-validation
- [ ] Tests (`tests/test_service.py`): grouping correctness, top-5 incl.
      ties, unused count

## M5 — CLI wiring (`main.py`)
- [ ] Wire io(read) → validation → service → io(write) + stdout bonus
      prints + stderr logs
- [ ] End-to-end test run against the real `data/orders.csv` +
      `data/barcodes.csv`

## M6 — Code quality pass
- [ ] Run static analysis (ruff or pylint), fix flagged issues
- [ ] Review against spec §9 clean code / SOLID checklist

## M7 — SQL data model bonus
- [ ] ERD (tables/keys/indexes) — primary artifact (spec §10)
- [ ] UML class diagram — supplementary artifact
- [ ] Tool decided at this milestone (dbdiagram.io / draw.io / plain
      schema + explanation)

## M8 — Production-readiness docs
- [ ] Finalize `README.md`: Design Decisions section (output-format §7.1,
      scale-assumption §8, ERD+UML §10), Deployment plan section
- [ ] Update this file, marking milestones complete

## M9 — Final review
- [ ] Compare finished project against the spec + original PDF assignment,
      line by line
- [ ] Confirm all validation rules, bonus outputs, and deliverables are
      present

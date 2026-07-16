# Tiqets Voucher Generator — Project Spec

## 1. Goal
Read two CSV files (`orders.csv`, `barcodes.csv`) and produce a single output CSV
grouping barcodes by customer and order, for voucher printing.

## 2. Inputs

### orders.csv
| column | notes |
|---|---|
| order_id | unique |
| customer_id | one customer can have multiple orders |

### barcodes.csv
| column | notes |
|---|---|
| barcode | unique |
| order_id | may be empty (unsold barcode) |

**Malformed numeric values:** `order_id`/`customer_id` (orders.csv) and `order_id` (barcodes.csv)
must be numeric — a non-numeric value skips that row (logged to stderr) during parsing in
`csv_io/`, before validation runs. Not one of the §4 validation rules.

## 3. Relationships
- customer 1 → many orders
- order 1 → many barcodes
- a barcode with empty `order_id` = unsold, valid, counted in bonus (unused count)
- a barcode assigned to an order = sold, included in output

## 4. Validation rules
Applied in `validation/`; failures are **logged to stderr and excluded from output**, not fatal
errors. (Distinct from the malformed-numeric-value skip in §2.)

| Rule | Meaning |
|---|---|
| No duplicate barcodes | if the same barcode string appears more than once in `barcodes.csv`, log + drop it |
| No orders without barcodes | if an order ends up with zero valid barcodes attached, log + drop that order from output |

## 5. Architecture
Simple project — no need for heavyweight/Clean Architecture (use cases, entities, adapters);
a lightweight layered structure is enough:

1. **`models/`** — plain dataclasses: `Order`, `Barcode`. No `Customer` class —
   `customer_id` is just a field on `Order`.
2. **`csv_io/`** (not `io/` — that would shadow Python's stdlib `io` module) — reads
   `orders.csv`/`barcodes.csv`, writes the output CSV; also skips + logs rows with a malformed
   `order_id`/`customer_id` (a parsing concern, not a §4 rule).
3. **`validation/`** — applies the two §4 rules; returns cleaned lists plus rejected items for
   stderr logging.
4. **`service/`** — grouping/aggregation, top-5 ranking, unused-barcode counting; takes data in,
   returns results out, no file I/O.
5. **`main.py`** — CLI entry point, wires the layers together.

Tests in `tests/`: `test_validation.py`, `test_service.py`, `test_io.py`, `test_main.py`.

## 6. Repo / production structure
- `.gitignore`
- `README.md` — description, how to run/test, a **Design Decisions** section, and a
  **Deployment** section
- `docs/` — spec, milestone plan, and SQL data model docs, kept up to date as work progresses
- Test suite + instructions to run it

## 7. Output

### 7.1 Main deliverable — output CSV file (e.g. `vouchers.csv`)
Format, matching the assignment exactly:
```
customer_id,order_id,barcodes
10,1,"[11111111111, 11111111112]"
```
- Literal square brackets, comma-separated barcodes inside, standard CSV quoting
  around the cell so inner commas don't break column parsing — chosen over a normalized
  one-row-per-barcode alternative, since matching the assignment's stated format exactly
  takes priority for a graded assignment.

### 7.2 stdout
Both stats below are computed from the **post-validation (cleaned)** dataset —
after duplicate barcodes and orphaned orders (§4) have been dropped — so these
numbers always match what's actually in the output CSV, not the raw input.

- Top 5 customers by ticket (barcode) count, one per line:
  ```
  customer_id,amount_of_tickets
  ```
- Count of unused barcodes (barcodes with no order_id), printed clearly.

### 7.3 stderr (validation logging)
- Every dropped duplicate barcode, every dropped order-without-barcodes, and
  every skipped row with a malformed `order_id`/`customer_id` (§2), logged as
  it's found.

No log files — only stdout/stderr, per the assignment.

## 8. Non-functional requirements
- **Language:** Python
- **Performance:** files may scale to millions of rows — favor a single-pass,
  streaming-friendly approach over nested loops / repeated full-file scans.

  > Self-imposed, not in the original assignment: the actual sample data is small
  > (~200 orders / ~620 barcodes). This is a production-readiness assumption, not a
  > stated client requirement.
- **Testing:** TDD. Tests written alongside implementation, one task at a time.
  Must cover: valid grouping logic, duplicate barcode rejection, order-without-
  barcode rejection, unused barcode counting, top-5 ranking (including ties),
  empty-file / malformed-row edge cases.
- **Delivery:** git repo (or zip), with documentation.

## 9. Code quality
- Follow clean code principles: meaningful names, small single-purpose
  functions, no duplication, clear separation of concerns (§5).
- Apply SOLID principles where genuinely relevant, not forced onto a small script.
- Run static analysis (e.g. `ruff`) before final delivery, and address flagged
  issues where reasonable.

## 10. SQL data model
Deliver a single diagram modeling the data:

- **ERD (entity-relationship diagram)** — the primary artifact, since this is
  what the assignment is actually asking for ("model how you would store this
  in a SQL database"):
  - `customers`, `orders`, `barcodes` tables
  - primary keys / foreign keys (order.customer_id → customers.id,
    barcode.order_id → orders.id, nullable)
  - suggested indexes (e.g. index on `orders.customer_id`, index on
    `barcodes.order_id`) and why they help (join/filter performance for the
    exact grouping query this program performs)

**Design decision:** the assignment says "e.g. UML, data model with relations and optionally
indexes" — loose wording that could mean either artifact. A UML class diagram was considered,
but it would show the same entities/relationships as the ERD with less detail (no PK/FK/indexes),
so it was dropped as redundant. The ERD alone is the deliverable.

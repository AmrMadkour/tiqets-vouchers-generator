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
are expected to be numeric. A non-numeric value in one of these columns causes that single row to
be skipped and logged to stderr — not a fatal error, and not one of the §4 validation rules; this
happens during CSV parsing/deserialization in `csv_io/`, before validation runs.

## 3. Relationships
- customer 1 → many orders
- order 1 → many barcodes
- a barcode with empty `order_id` = unsold, valid, counted in bonus (unused count)
- a barcode assigned to an order = sold, included in output

## 4. Validation rules
Applied during processing in `validation/`; failures are **logged to stderr and excluded from
output**, not fatal errors. (Malformed numeric `order_id`/`customer_id` values are a separate,
earlier concern handled in `csv_io/` during parsing — see §2 — not one of the two rules below.)

| Rule | Meaning |
|---|---|
| No duplicate barcodes | if the same barcode string appears more than once in `barcodes.csv`, log + drop it |
| No orders without barcodes | if an order ends up with zero valid barcodes attached, log + drop that order from output |

## 5. Architecture
Simple project — no need for heavyweight/Clean Architecture (use cases,
entities, adapters, etc.); that level of layering is overkill for a
CSV-processing script and can read as over-engineering rather than skill.

Instead, use a **lightweight layered structure** — I/O at the edges, pure
logic in the middle — enough to keep things clean, testable, and SOLID-aligned
without ceremony:

1. **`models/`** — plain data classes: `Order`, `Barcode`. No `Customer`
   class — `customer_id` is just a field on `Order`.
2. **`csv_io/`** (named `csv_io/`, not `io/`, since `io` is a Python stdlib
   module name and a local `io/` package can't actually be imported — `io`
   is already cached in `sys.modules` before our code runs) — reading
   `orders.csv` / `barcodes.csv`, writing the output CSV. Isolated so it can
   be swapped or mocked in tests. Also responsible for skipping + logging to
   stderr any row with a non-numeric `order_id`/`customer_id` — a parsing-
   level concern, not one of the §4 validation rules, so `validation/`
   doesn't need to re-check it.
3. **`validation/`** — applies the two §4 rules (drop duplicate barcodes,
   drop orders with zero barcodes); takes parsed `Order`/`Barcode` lists in,
   returns the cleaned lists plus the rejected items (for stderr logging).
4. **`service/`** (or `core/`) — the grouping/aggregation logic, top-5
   ranking, unused-barcode counting. Main testable business logic; takes
   parsed data in, returns results out, no direct file I/O inside — this is
   what makes TDD clean.
5. **`main.py`** — CLI entry point, wires the layers together.

Tests live in a top-level `tests/` folder: `tests/test_validation.py`,
`tests/test_service.py`, `tests/test_io.py` — no separate test "layer" in
the architecture itself.

## 6. Repo / production structure
Baseline to set up before task breakdown begins. This is a starting point,
not fixed — production-readiness is a hard requirement (per the assignment),
so splitting any section below into its own file later (e.g. a separate
`DEPLOYMENT.md`) is fine if it turns out to serve the docs better:
- `.gitignore`
- `README.md` — what the project does, how to run it, how to run tests, and
  a **Design Decisions** section (key choices and why — e.g. the
  output-format decision in §7.1, the architecture decision in §5 — acts as
  an interview-defense reference). Kept as one entry-point file rather than a
  separate `DECISIONS.md` so a reviewer doesn't need to know a second file
  exists to find the reasoning.
- `Tiqets-Voucher-Generator-Plan.md` — the full milestone breakdown (see §11), reviewed and approved
  before implementation starts, kept up to date as milestones are completed
- deployment plan section (in README or separate `DEPLOYMENT.md`) — how this
  would actually ship (packaging, running as a scheduled job vs CLI tool, etc.)
- test suite + instructions to run it

## 7. Output

### 7.1 Main deliverable — output CSV file (e.g. `vouchers.csv`)
Format, matching the assignment exactly:
```
customer_id,order_id,barcodes
10,1,"[11111111111, 11111111112]"
```
- Literal square brackets, comma-separated barcodes inside, standard CSV quoting
  around the cell so inner commas don't break column parsing.

**Design decision — record this in README.md's Design Decisions section (see §6):**
- **Chosen:** literal bracket format inside a quoted CSV cell, matching the
  assignment's shown output exactly.
- **Rejected alternative:** normalized/long format (one row per barcode:
  `customer_id,order_id,barcode`). More conventional/DB-friendly and avoids
  bracket/quoting complexity entirely, but doesn't match the explicit format
  given in the assignment, so it was not used.
- **Reasoning:** for a graded home assignment, matching the stated output
  format exactly takes priority over a "more normalized" alternative.

### 7.2 stdout (bonus)
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
  it's found. Use Python's `logging` module (default stream = stderr) or
  `print(..., file=sys.stderr)`.

No log files — only stdout/stderr, per the assignment (explicitly decided, no
file-based logging needed).

## 8. Non-functional requirements
- **Language:** Python
- **Performance:** files may scale to millions of rows — avoid nested loops /
  repeated full-file scans; favor a single-pass, streaming-friendly approach
  (e.g. dict-based lookups built in one pass, or chunked reading) to keep
  memory and time roughly linear in input size. Concrete approach (pandas vs
  plain csv module vs generators) to be decided at implementation time —
  benchmark before committing.

  > **Note (self-imposed, not in the original assignment):** the actual
  > sample data is small (~200 orders / ~620 barcodes). This scalability
  > requirement is an added engineering assumption for production-readiness,
  > not a stated client requirement — worth calling out so it doesn't read
  > as an unexplained/over-scoped requirement. To be folded into README.md's
  > Design Decisions section once the repo baseline (§6) is set up.
- **Testing:** TDD. Tests written alongside implementation, one task at a time.
  Must cover: valid grouping logic, duplicate barcode rejection, order-without-
  barcode rejection, unused barcode counting, top-5 ranking (including ties),
  empty-file / malformed-row edge cases.
- **Delivery:** git repo (or zip), with documentation.

## 9. Code quality
- Follow clean code principles: meaningful names, small single-purpose
  functions, no duplication, clear separation of concerns (already reflected
  in the layered structure in §5).
- Apply SOLID principles where genuinely relevant — not forced onto a small
  script. For a project this size, Single Responsibility and
  Dependency Inversion (e.g. injecting file paths / readers so logic is
  testable without real files) are the most likely to actually help.
- Run static analysis for code smells (e.g. SonarLint/SonarQube, or `pylint`/
  `ruff` as lighter-weight alternatives) before final delivery, and address
  flagged issues where reasonable.

## 10. SQL data model (bonus)
Deliver **both** diagrams, covering the same underlying model:

- **ERD (entity-relationship diagram)** — the primary artifact, since this is
  what the assignment is actually asking for ("model how you would store this
  in a SQL database"):
  - `customers`, `orders`, `barcodes` tables
  - primary keys / foreign keys (order.customer_id → customers.id,
    barcode.order_id → orders.id, nullable)
  - suggested indexes (e.g. index on `orders.customer_id`, index on
    `barcodes.order_id`) and why they help (join/filter performance for the
    exact grouping query this program performs)
- **UML class diagram** — supplementary, since the assignment mentions it as
  an example option ("e.g. UML"); shows the same three entities as classes
  with their relationships/cardinalities, for completeness alongside the ERD.

Tool TBD (dbdiagram.io / draw.io / plain schema + explanation).

**Design decision — record this in README.md's Design Decisions section
(see §6):** the assignment says "e.g. UML, data model with relations and
optionally indexes" — loose wording that could mean either artifact. Rather
than picking one over the other, both are delivered: the ERD as the correct,
primary artifact for modeling relational storage (tables/keys/indexes), and
the UML class diagram as a supplementary nod to the assignment's literal
example, so nothing asked for is left out.

## 11. Process
1. This spec → Claude Code
2. Set up repo baseline (.gitignore, README skeleton with Design Decisions
   section, `Tiqets-Voucher-Generator-Plan.md`) — §6
3. Ask Claude Code to break the full spec into an ordered milestone list
   (dependencies first — e.g. models before validation before service before
   CLI wiring), including tests per milestone (TDD) — plan only, no code yet
4. Save that milestone list into `Tiqets-Voucher-Generator-Plan.md`, review it
   against the spec yourself (complete? sensibly ordered? anything missing or
   redundant?) before approving it
5. Implement milestone by milestone, TDD, in Plan Mode — review after each
   one (does it run, does it meet the requirement, do you understand why it
   works) — check off / update `Tiqets-Voucher-Generator-Plan.md` as each
   milestone completes
6. Final pass: compare finished project against this spec + original
   assignment line by line before delivery

# tiqets-vouchers-generator

Python program that merges orders and barcodes CSV exports into a grouped output file, with input validation and summary reporting.

## How to Run

Create and activate the virtual environment:

```
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If activation is blocked by PowerShell's execution policy (one-time fix, per user account):

```
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Alternative to activation — call the venv's executables directly instead:

```
.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\python.exe main.py data/orders.csv data/barcodes.csv
```

With the venv activated:

```
pip install -r requirements.txt
python main.py data/orders.csv data/barcodes.csv
```

## How to Test

Alternative to activation — call the venv's executable directly instead:

```
.\venv\Scripts\pytest.exe tests/ -v
```

With the venv activated:

```
pytest tests/ -v
```

## Design Decisions

- **Layered structure, not Clean Architecture** — `models/` (dataclasses),
  `csv_io/` (read/write), `validation/` (two business rules), `service/`
  (grouping + bonus stats), `main.py` (CLI wiring). No use-case/entity/adapter
  layers — for a single-purpose CSV-processing script, that indirection is
  over-engineering with no swappable implementations to justify it.
- **`csv_io/` not `io/`** — `io` is a Python stdlib module name, already
  cached in `sys.modules` before our code runs, so a local `io/` package
  would silently resolve to the stdlib module instead of shadowing it.
- **Malformed `order_id`/`customer_id`: skip + log, don't raise** — one bad
  CSV row shouldn't abort the whole read. IDs stay typed `int` (not relaxed
  to `str`) since they back real primary/foreign keys in the SQL bonus model.
- **No Pydantic for CSV parsing** — considered and rejected: a new
  dependency, and it contradicts the plain-dataclass model choice, for 2
  fields where manual `int()` parsing is equally simple. Would reconsider if
  the model surface grew significantly.
- **Readers return plain `list`s, not generators** — every real caller
  (`validation/`) fully materializes the result and needs two passes over it
  (build a count/set, then filter); a generator can only be iterated once,
  so laziness here is never actually exercised. Laziness is used instead
  where it's genuinely exercised: `service/` streams
  `(customer_id, order_id, barcodes)` rows on the fly into the writer.
- **Drop *all* occurrences of a duplicate barcode**, not "keep first" — a
  duplicated barcode can't be trusted regardless of whether the repeats
  share an `order_id`; the same physical barcode assigned to two different
  orders is a genuine conflict the CSV alone can't resolve.
- **Bonus stats (top-5 customers, unused-barcode count) are computed from
  the post-validation dataset**, not raw input — a deliberate reading of the
  spec, not incidental.
- **Output format** — the barcodes column is quoted
  (`"[11111111111, 11111111112]"`) because it's a new column layered on top
  of the source CSVs and contains commas between barcode values; without
  quoting, a CSV parser would treat those as column separators.
- **No async** — no concurrent I/O to overlap in a single-shot CLI reading
  local files; would matter if this became a service handling concurrent
  requests.
- **`validation/` and `service/` each build their own structures** rather
  than sharing one grouped dict — several `O(n)` copies stacked, but keeps
  each layer independently testable; still `O(n)` overall, never `O(n²)`.
- **`defaultdict(list)` over `dict.setdefault(key, [])`** for grouping —
  avoids constructing a throwaway empty list on every call.
- **Single-pass/streaming design** (no nested loops, no repeated full-file
  scans) even though the real sample data is small (~200 orders / ~620
  barcodes) — a self-imposed production-readiness assumption, not a stated
  requirement.
- **`FileNotFoundError` and `KeyError` (missing CSV column) are handled
  explicitly** — a missing input file prints a clean message and exits(1)
  instead of a raw traceback; a missing/misspelled CSV column bails out
  after one clear message instead of re-logging the same error once per row.
- **A sold barcode referencing an `order_id` absent from `orders.csv`
  entirely is skipped and logged**, not a crash — this data shape isn't one
  of the assignment's two stated validation rules (duplicate barcodes,
  orders without barcodes), but an unmatched foreign key shouldn't raise an
  unhandled `KeyError` in production.
- **Static analysis (`ruff`) run, findings left unfixed** — the broader rule
  set flagged 15 cosmetic issues (import order, line length, one unused loop
  variable); none are correctness bugs, and fixing them is churn with no
  functional benefit at this project's size.
- **SQL schema decisions** (column types, indexes, extra non-CSV
  columns) are documented in `docs/data-model/SQL-Model.md`'s own Design
  Decisions section, alongside the schema they explain.

## Deployment

This is a batch CLI tool, not a service — deployment here means "how does
this run unattended in a real environment," not hosting.

- **Packaging** — ships as a plain script + `requirements.txt`, no
  packaging (`setup.py`/wheel) — appropriate for a single script invoked
  directly. Would package as an installable CLI (`pyproject.toml` + entry
  point) if it needed to be installed system-wide or distributed to
  multiple machines.
- **Execution model** — designed to run as a scheduled job (cron / Windows
  Task Scheduler / a pipeline step), not as a long-running service: it
  reads two files, writes one, and exits. Each run is independent and
  idempotent — same input files produce the same output.
- **Input delivery** — assumes `orders.csv`/`barcodes.csv` already exist at
  known paths when the job runs (e.g. dropped by an upstream export
  process); this tool doesn't fetch or watch for files itself.
- **Failure visibility (known gap)** — validation rejections and fatal
  errors (missing file, missing CSV column) go to stderr with an exit code
  (`0` success, `1` fatal error), but nothing currently monitors that exit
  code. A real deployment's scheduler/orchestrator would need to alert on a
  non-zero exit (e.g. a monitoring hook or chat alert) — otherwise a failed
  run goes unnoticed until someone checks that the output file didn't update.
- **Delivery/repo hygiene** — `.claude/` + `CLAUDE.md` stay tracked on
  `main` (used across development sessions); stripped only on a `deliver`
  branch + a `git archive` zip at final handoff, so the delivered artifact
  doesn't carry AI-tooling config a reviewer doesn't need.

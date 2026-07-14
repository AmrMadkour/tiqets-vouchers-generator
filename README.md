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

With the venv activated:

```
pytest tests/ -v
```

## Design Decisions

_TBD — filled in at milestone M8._

## Deployment

_TBD — filled in at milestone M8._

---
description: Run the test suite, auto-detecting language/framework, asking whether to run everything or a specific scope
argument-hint: [optional scope: file, module, or test name/keyword]
---

# Run Tests

Run this project's tests without assuming any specific framework.

---

## 1. Detect test framework
Check for existing config/test files:
- **Python:** `pytest.ini` / `pyproject.toml [tool.pytest]` / `tests/` with
  `test_*.py` → `pytest`. No config found but `unittest` imports → stdlib
  `unittest`.
- **Node/TS:** `package.json` — `jest.config.*` → Jest, `vitest.config.*` →
  Vitest, or check the `test` script.
- **.NET:** `*.Tests.csproj` → `dotnet test`.
- **Java:** `pom.xml`/`build.gradle` → `mvn test` / `./gradlew test`.
- **Go:** `*_test.go` files → `go test ./...`.

If none of the above is found, say so and stop — there's nothing to run.

## 2. Determine scope
If `$ARGUMENTS` specifies a scope (a file, module, or test name/keyword), use
it directly.

Otherwise ask the user: "Run the full test suite, or a specific
file/module/test?" If specific, ask which.

## 3. Run
Use the framework's native filtering syntax for a specific scope:
- pytest: `pytest tests/ -v` (all) or `pytest <path>::<test_name> -v` /
  `pytest -k "<keyword>" -v` (scoped)
- unittest: `python -m unittest discover` (all) or
  `python -m unittest <module>.<TestCase>.<test_method>` (scoped)
- Jest/Vitest: `npx jest` / `npx vitest run` (all) or add a path/`-t
  "<name>"` (scoped)
- dotnet: `dotnet test` (all) or `dotnet test --filter "<name>"` (scoped)
- Go: `go test ./...` (all) or `go test ./... -run <TestName>` (scoped)

## 4. Report
- Pass/fail counts
- For every failure: test name + full assertion/traceback (not truncated)
- Exact command used, so the user can re-run it themselves

---
description: Run the project, auto-detecting language/framework and whether it's a script/CLI or a service (API/web)
argument-hint: [any CLI args to pass through]
---

# Run Project

Run this project without assuming any specific stack. Detect what kind of
project this is and how to start it, then run it accordingly.

---

## 1. Detect project type
Check for config/entry-point files to determine the stack and shape:
- **Python:** `requirements.txt` / `pyproject.toml` / `setup.py`; entry point
  is usually `main.py`, `app.py`, `__main__.py`, or whatever `README.md`'s
  "How to Run" section documents.
- **Node/TS:** `package.json` — check `scripts` for `start`/`dev`.
- **.NET:** `*.csproj` / `*.sln` — `dotnet run`.
- **Java:** `pom.xml` (`mvn spring-boot:run` / `mvn exec:java`) or
  `build.gradle` (`./gradlew bootRun`).
- **Go:** `go.mod` — `go run .` or `go run ./cmd/...`.

If `README.md` documents an explicit run command, prefer that over guessing.

## 2. Classify: script/CLI vs. service
- **Script/CLI** (no server, runs once and exits — e.g. this project, a data
  processing script, a one-shot job): go to §3.
- **Service** (binds to a port — API, web server, both together): go to §4.

## 3. Script/CLI mode
1. Determine required arguments (check README, `argparse`/`click`/`yargs`
   definitions in the entry point, or ask the user if unclear).
2. Run the entry point in the foreground with `$ARGUMENTS` passed through
   (e.g. `python main.py $ARGUMENTS`).
3. Report exact stdout/stderr and the exit code.
4. If it writes output files, report their paths and a short preview.

## 4. Service mode (API / web / both)
Ask the user once (or check README/`.env.example`/config files) for:
- start command(s) per service
- port(s) each service listens on
- a "ready" log line to wait for
- (optional) a smoke-test URL

Then:
1. **Check ports** — detect if the configured ports are already in use
   (`netstat -ano | Select-String ":<PORT> " | Select-String "LISTENING"` on
   Windows, `lsof -i :<PORT>` on Unix). If occupied, ask before killing
   anything.
2. **Start each service in the background** (`run_in_background: true`),
   wait for its "ready" log line.
3. **Verify** each configured port is listening.
4. **Smoke-test** (if a URL was given and Playwright MCP is available):
   navigate to it and snapshot, reporting any console errors.
5. Do not open new terminal windows — everything stays inside the session.

---

## Output
Report concisely:
- What was detected (stack, script vs. service) and what command was run
- Result: exit code / output for scripts; port + readiness status for
  services
- Any errors that need attention

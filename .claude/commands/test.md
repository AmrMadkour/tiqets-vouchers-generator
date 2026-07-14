---
description: Write TDD unit tests for a chosen scope, either step-by-step or all at once
argument-hint: [scope] [step-by-step|all-at-once]
---

# TDD Test Writer

You are about to write unit tests for this project using strict TDD
(red → green, one behavior at a time). Follow this procedure exactly.

## 1. Determine scope
If `$ARGUMENTS` specifies a scope (e.g. a milestone name, a module, a
function, or "whole application"), use it.
Otherwise, ask the user: "What scope should these tests cover? (e.g. a
specific milestone/task, a single module, or the whole application)"
Do not proceed until scope is clear.

## 2. Determine language & test framework
Detect the project's language from source files (extensions, entry
points, README/manifest mentions) and its existing test setup (test
files, config like `pytest.ini`, `*.csproj`, `package.json`, `go.mod`,
etc.).

If the repo has no source code yet (greenfield), do not guess — ask
the user what language/stack this project will be written in.

If a framework is already in use, confirm it and use it.

If none is established yet, ask the user which framework to use, and
suggest sensible defaults for the detected language, e.g.:
- Python → `pytest` (recommended, minimal boilerplate) or `unittest`
  (stdlib, no dependency)
- C# / .NET → `xUnit` (modern, widely used) or `NUnit` (mature, more
  built-in assertions)
- JavaScript/TypeScript → `Jest` or `Vitest`
- Java → `JUnit 5`
- Go → stdlib `testing` (idiomatic default)

Do not proceed until language and framework are both confirmed. If the
chosen framework isn't installed yet, install it as a dev dependency
before writing tests, and set up the conventional test directory/file
naming for that language (e.g. `tests/test_*.py`, `*.test.ts`,
`*_test.go`).

## 3. Determine execution mode
Ask the user (unless already specified in `$ARGUMENTS`):
"Do you want to go test-by-test (I write one failing test, pause for
your review, implement, confirm it passes, then move to the next) or
all-at-once (I write and implement all tests for this scope in one
pass, then report back)?"

## 4. TDD loop
For each behavior/test case in scope, repeat:
1. Write one test that expresses the expected behavior. The test must
   fail initially — verify this by running it before writing any
   implementation code.
2. Confirm the failure is for the right reason (missing/incorrect
   behavior — e.g. an assertion failure or a "not implemented" error),
   not an unrelated setup problem (syntax error, bad import, wrong test
   runner invocation). If it fails for the wrong reason, fix the test
   itself first and re-run until it fails on the actual missing
   behavior.
3. Report the failing result to the user (or, in all-at-once mode,
   note it internally and continue).
4. Write the minimum implementation code needed to make that test pass.
5. Run the test again and confirm it now passes, and that it fails
   again if you temporarily revert the implementation (spot-check for
   tests that pass vacuously).
6. If in step-by-step mode: stop here, summarize what was written and
   why, and wait for the user's go-ahead before starting the next case.
7. If in all-at-once mode: continue automatically to the next case.

Never write implementation code before its corresponding test exists
and has been confirmed to fail for the right reason.

## 5. Manual verification instructions
Once all tests in scope are written and passing, output the exact
command(s) the user can run themselves to execute the test suite
manually (e.g. `pytest tests/ -v`, `dotnet test`), including how to run
just this scope's tests if the framework supports filtering.

## 6. Final review
Summarize:
- Which behaviors/edge cases were covered
- Any cases considered but deliberately left out of scope, and why
- Any gaps or follow-up test cases worth writing later

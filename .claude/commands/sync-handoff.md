# Sync Handoff

Create or update the handoff file (default: `HANDOFF.md` at repo root).
If a path is passed as `$ARGUMENTS`, use that instead (e.g. `docs/HANDOFF.md`).
If the file does not exist yet, create it with a blank header before appending the session block.
Do NOT repeat anything already in CLAUDE.md (architecture, conventions, commands).

---

## Required sections

### Session — {YYYY-MM-DD}
- Files changed this session (exact paths)
- Decisions made and why (only if non-obvious from the code)

### Gotchas
- Bugs found, workarounds, failed approaches
- Anything that would surprise the next developer or AI

### Next
- Immediate next step (most important first)
- Remaining backlog (brief, ordered)

---

## Rules
- Append new session blocks; never overwrite prior history
- Omit a section if nothing new to add
- Keep the whole file under ~120 lines

Print: `HANDOFF.md updated.`

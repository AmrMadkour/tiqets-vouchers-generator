# Push Changes

Stage, commit, and push all current changes to the remote branch with a descriptive commit message.

---

## Steps

### 1. Gather context (run in parallel)
- `git status` — see all modified and untracked files
- `git diff` — review the actual changes
- `git log --oneline -5` — learn the commit message style used in this repo

### 2. Scan for secrets before staging anything
Run a pattern scan over the actual diff content (not just filenames) for
things that look like credentials:
```bash
git diff --unified=0 | grep -inE \
  '(aws_(secret|access)_key|api[_-]?key|secret[_-]?key|private_key|-----BEGIN [A-Z ]*PRIVATE KEY-----|token\s*[:=]\s*["\047][A-Za-z0-9_\-]{16,}|password\s*[:=]\s*["\047][^"\047]{4,})'
```
Also check untracked files for anything named like a secret (`.env`,
`*.pem`, `*credentials*`, `*.key`). If anything matches, **stop and show it
to the user** — do not stage or commit until they've confirmed it's safe or
removed it. This is in addition to, not instead of, the filename-based rule
below.

### 3. Draft a commit message
- First line: short summary (≤ 72 chars), following the repo's existing style (read from `git log --oneline -5`)
- Body: bullet points grouped by area — one line per meaningful change
- Do NOT add a `Co-Authored-By` trailer — commits in this repo are authored solely by AmrMadkour, with no Claude/Anthropic attribution

### 4. Commit and push
```bash
# Stage only files shown in git status — do NOT use -A blindly; skip .env / credentials
git add <files from git status>
git commit -m "<message as heredoc>"
git push origin <current-branch>
```

Use a `<<'EOF' ... EOF` heredoc for the commit message to preserve formatting.

---

## Rules
- Never use `--force` or `--no-verify`
- Never commit `.env`, credentials, or secrets — warn the user if any are staged
- Always push to the **current branch** (not main)
- If there is nothing to commit, say so and stop

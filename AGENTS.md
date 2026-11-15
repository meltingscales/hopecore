# Agent instructions

This repo is the Hopecore tracker. To update it, follow `generate-hopecore.md`.

- `hopecore.html` is the only source of truth. It holds both the renderer and the embedded ledger. `index.html` just redirects to it for GitHub Pages.
- Edit the ledger with `python3 tools/hopecore.py extract` / `embed`, and finish with `python3 tools/hopecore.py check`, which must print `OK`.
- At most one tracker run per calendar month. If `meta.last_run` is in the current month, stop and tell the user when the next run is allowed, unless they explicitly asked for an extra run or a fix.
- Keep scratch files (such as an extracted `ledger.json`) out of the repo.

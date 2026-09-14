# Maintaining the AI Operations starter

## Files

- `index.html`, `assistant.html`, `assets/site.css`, `assets/site.js`: public cheat sheet and readable assistant guide. No application backend or analytics.
- `starter/`: public-safe source templates, including `.codex/agents` definitions.
- `scripts/build-operations-installer.py`: embeds templates in `setup-operations.sh` for stock macOS Bash.
- `scripts/build-starter-assets.py`: creates a deterministic ZIP and SHA-256 manifest.
- `install.sh`, `configure-chatgpt.js`, `build-model.py`: existing optional model setup.

## Rebuild after template changes

From the repository root:

```bash
python3 scripts/build-operations-installer.py
python3 scripts/build-starter-assets.py
python3 -m unittest discover -s tests -p 'test_*.py'
node tests/test_catalog.js
```

End users do not need Python or Git. Both build scripts are developer tools.

Verify a fresh install and a rerun in a temporary destination with `--no-open`. Ensure the assistant playbook, profile and rollout files are in both the script and ZIP. Inspect rendered desktop and narrow-width layouts for both the home page and assistant guide. Verify copy buttons against the actual command/prompt contents, filters, checklist persistence/reset and download links. Never run the model installer's restart path merely to test the website.

Keep model and reasoning capabilities honest. Changing instructions does not fine-tune model weights. Do not use custom marketing names as API reasoning enum values.

## Publish

Commit reviewed source and generated assets, push to the existing `main` branch, and verify GitHub Pages deploys that commit. Check the live page, raw setup script and downloaded ZIP against the reviewed local files. Keep private verification notes and business data outside this public repository.

The deployed site uses the repository root. If Pages remains on an old commit, inspect its build status and request a rebuild using the existing Pages configuration.

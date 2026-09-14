# Sources and what this kit actually sets up

Guidance checked on 14 September 2026. Features depend on client version, plan, available tools and workspace settings.

## Official setup references

- [Local projects](https://learn.chatgpt.com/docs/projects): attach a folder and make it primary for project discovery. Web projects use uploaded files and connected sources, not automatic disk access.
- [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md): local Codex loads working instructions according to project scope. Explicitly read role files when delegating from the workspace root.
- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents): current local clients support project definitions in `.codex/agents/`. These files specify name, description and developer instructions. Tools, access and model settings are inherited unless overridden.
- [Scheduled tasks](https://learn.chatgpt.com/docs/automations): test a prompt, create the actual task in the app, and verify the saved configuration and first run. Local work requires the computer and app running.
- [MangoMagic 7.1](https://ollama.com/mangomagic/mangomagic-7.1): image input, tools and adjustable reasoning. Implementation details and upstream provenance are recorded in [technical notes](TECHNICAL-NOTES.md).
- [Ollama pricing](https://ollama.com/pricing): cloud usage is separate from ChatGPT subscription usage.

## What comes from the ManyMangoes workflow

The reusable patterns are one workspace per responsibility; a shared operating agreement; current mission and task tracking; named authoritative sources; specialist roles with boundaries; handoff packets; evidence checks; owner review; and tested recurring work.

The Build My Assistant pack adapts our Team AI Operations operating brief and rollout audit into reusable public Markdown. It keeps evidence labels, specific task instructions, working preferences, voice examples, a personal operating prompt, a three-task pilot and an honest gaps audit. Private team links and examples are replaced with blank fields.

These are our workflow recommendations, not mandatory OpenAI folder names. The published starter is newly written generic material. It contains no private source documents, customer conversations, credentials, internal financial records or account exports.

## What the commands do

`setup-operations.sh` creates missing starter files in the selected local folder. It preserves existing regular files, rejects conflicting files/directories and symlinks at checked destination paths, and opens Finder on macOS unless `--no-open` is used. A rerun adds missing templates; it does not overwrite templates you customised.

Without `--with-mangomagic`, setup creates local workspace files only. It does not connect the folder to your account, authenticate apps, alter global `.codex` configuration, register global agents, launch workers, or create schedules. New project-scoped custom agent definitions become available only where the client supports discovery. Verify this in a new local project chat; reading a TOML file is not proof that an agent was loaded or run.

`install.sh` is the separate optional MangoMagic model installer. It registers the model with the local Ollama integration and gracefully restarts ChatGPT. `--no-restart` leaves activation pending. The workspace kit also works without this model. `setup-operations.sh --with-mangomagic` runs this model installer after preparing the workspace. Add `--no-restart` to defer the restart. If model setup fails, the completed workspace files remain available and the command returns failure with the model error; it does not claim full setup succeeded.

The assistant prompt starts a personalisation conversation after file access is connected. Installing blank profiles does not create a personalised assistant, change account instructions, or activate a routine.

## Verification boundaries

The automated release checks cover literal file installation, preservation on rerun, shell compatibility, error paths, starter archive contents, links within the site, copy-target wiring, and template schemas. Browser checks cover copy controls, filtering, checklist state and responsive layout.

They do not guarantee every user's client discovers custom agents, every account has scheduling, or every sales output is correct. The onboarding prompt checks access and role availability; the first useful task tests the workflow in that user's environment.

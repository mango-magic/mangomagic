# Your AI Operations starts here

Built by ManyMangoes. **Data + AI + Automation**.

Build an assistant that understands your work, follows your preferences and produces something useful. This pack includes discovery, your working profile and a rollout audit. You do not need to fill every template before starting.

## 1. Open your workspace

The default folder is `~/Documents/AI Operations`. If you chose another destination, use that folder. Add it as a local folder project in a desktop client that supports local projects, then start a new chat there. Verify access in that chat; opening a folder does not prove the assistant can read it.

If your client cannot access local folders, upload the relevant Markdown files to a project or chat. Include root `AGENTS.md`, the current mission, business brief, roster and the three assistant-pack files linked below. Ask for updates you can save locally. Uploaded copies do not automatically stay in sync with files on your Mac.

By default, the setup script copies local files only. With `--with-mangomagic`, it also runs the MangoMagic model installer, registers the model and restarts ChatGPT unless you pass `--no-restart`. Neither mode attaches the folder to your app, signs in to services for you, launches workers or creates schedules.

## 2. Paste this onboarding prompt

```text
Build my assistant in this AI Operations workspace. Read AGENTS.md,
CURRENT_MISSION.md, 00_Command_Centre/BUSINESS_BRIEF.md,
02_Agents/AGENT_ROSTER.md and these files in 00_Command_Centre:
BUILD_MY_ASSISTANT.md, ASSISTANT_PROFILE.md and ASSISTANT_ROLLOUT.md.

First verify what you can actually read and write in this session. Follow the
build workflow using my existing answers, preferences and authorisation. Ask
up to five concise questions per round, fewer when useful. Do not make me
repeat information or approvals already supplied. Use examples of my work to
learn tone; do not assign personality labels. Keep facts, observations,
assumptions and gaps distinct, with sources. Preserve existing content.

Personalise the assistant profile, business brief and current mission; update
the roster and task status only where useful and supported by evidence. Build
a register of real tasks and a portable instruction block under 1,500 words.
Choose one useful task, define its acceptance checks, complete the authorised
work and verify the result. Continue independent work when a gap blocks another
step. Then aim for three real pilot tasks and a review; do not pad the register.

Explain which role files are available, which custom agent definitions this
client recognises and whether any workers actually ran. Onboarding alone does
not authorise messages, publishing, purchases or schedules; honour any relevant
authorisation I have already given. Finish with saved output paths, checks,
Where I Cut Corners and the next useful action. If you cannot save files, say so
and provide the exact updates for me to save.
```

## 3. Use the assistant pack

| File | What it does |
| --- | --- |
| [Build my assistant](00_Command_Centre/BUILD_MY_ASSISTANT.md) | Short discovery rounds, source evidence, task design and a useful first run |
| [My assistant profile](00_Command_Centre/ASSISTANT_PROFILE.md) | Your preferences, sources, task instructions, boundaries and portable prompt |
| [Rollout and audit](00_Command_Centre/ASSISTANT_ROLLOUT.md) | Five checks, a three-task pilot and reviews based on actual results |

Bring a current priority, an approved example and a relevant source if you have them. Use quick start for one result, then deeper review to understand recent and invisible work. Keep permitted originals in `01_Data/source-documents/`, sanitised conversations in `01_Data/sanitised-conversations/`, and source dates and authority in `01_Data/SOURCE_REGISTER.csv`. Linking an existing private source is fine. Keep completed profiles and private business data out of the public starter repository.

## 4. Give a real job

Use [TASK_BRIEF](00_Command_Centre/TASK_BRIEF.md). Start a chat for a concrete outcome. For a new project, adapt `03_Projects/project-template/`; save work there and link reviewed results from `05_Deliverables/`.

Use only the roles you need. Role folders store instructions; `.codex/agents/` holds project-local custom agent definitions for clients that support them. Verify availability in a new project chat. Neither creates a running worker by itself. Follow existing delegation authorisation; if delegation is unavailable, the lead can work sequentially with the same role instructions.

## 5. Make repetition useful

After a successful manual run, use [AUTOMATION_BRIEF](04_Automations/AUTOMATION_BRIEF.md) for recurring work you actually want. A schedule requires your request, a supported scheduler and verified creation. A review date in a document is not a reminder. Check the first run and the availability of required local files.

[Full cheat sheet](https://mango-magic.github.io/mangomagic/)

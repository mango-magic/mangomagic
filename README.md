# Your AI operations. Sorted.

### The Holy Trinity: Data + AI + Automation.

**Give ChatGPT the context, the team and the routine. Then give it something worth doing.**

Built by **ManyMangoes** for business owners who want useful outputs, fewer repeated instructions and a clear next move.

**[Open the interactive cheat sheet →](https://mango-magic.github.io/mangomagic/)** · [Download the starter kit](https://mango-magic.github.io/mangomagic/assets/AI-Operations-Starter.zip) · [Grab a prompt](docs/PROMPTS.md)

---

## Three things. One way to work.

| Data | AI | Automation |
| :--- | :--- | :--- |
| Give it your offer, customers, examples and evidence. | Give each specialist a clear job and a definition of done. | Test the useful work, then put it on repeat. |
| **A reliable starting point.** | **An owner for the outcome.** | **A routine you can trust and check.** |

The ManyMangoes pattern is practical: one folder per responsibility, a short current mission, named sources, clear handoffs, a task tracker, and a reviewed deliverable. Start with one outcome. Add complexity only when it earns its place.

## 1. Build your workspace

**Paste into Terminal on your Mac:**

```bash
bash -c 'f=$(mktemp) || exit; trap "rm -f \"$f\"" EXIT; curl -fsSL https://raw.githubusercontent.com/mango-magic/mangomagic/main/setup-operations.sh -o "$f" && bash "$f"'
```

It creates **`~/Documents/AI Operations`** with 38 starter files and opens the folder in Finder. No Git or Python required. Run it again and your existing files stay intact.

The script prepares local files. It does not log into accounts, connect the folder to ChatGPT, launch agents, or create schedules. [Read the script](setup-operations.sh).

Prefer a download? [Get the ZIP](https://mango-magic.github.io/mangomagic/assets/AI-Operations-Starter.zip), unzip it and use the same steps below. The kit works with the model and tools available in your app; MangoMagic is optional.

## 2. Connect it to ChatGPT

In the desktop app, create a **local project** named AI Operations. Open the project menu: **Edit project → Add folder**. Select the installed folder and make it primary. Start a new chat there. [Official project instructions](https://learn.chatgpt.com/docs/projects).

**Paste into that project chat:**

```text
Set up this AI Operations workspace for my business. Read START_HERE.md,
AGENTS.md, CURRENT_MISSION.md, 00_Command_Centre/BUSINESS_BRIEF.md and
02_Agents/AGENT_ROSTER.md. Verify file access first. Ask up to five short
questions together to fill material gaps. Preserve existing content; mark
unknowns instead of inventing facts. Update the business brief, mission,
roster and project_tasks.json. Confirm which agents are actually available
in this client. Show one useful first deliverable and its acceptance checks.
Do not schedule jobs or send messages during onboarding.
```

**Using ChatGPT on the web?** Upload the relevant Markdown files and sources to a project, and paste the shared working rules into its project instructions. Keep uploads current. Web projects do not automatically read your Mac's disk or inherit the local Ollama model.

## 3. Meet your team

```text
AI Operations/
├── START_HERE.md                 Your first steps and onboarding prompt
├── AGENTS.md                     Shared working agreement
├── CURRENT_MISSION.md            What matters right now
├── project_tasks.json            Actual progress, backed by evidence
├── 00_Command_Centre/            Business brief, task brief, handoffs
├── 01_Data/                      Sources and sanitised conversations
├── 02_Agents/
│   ├── chief-of-staff/           Owns the outcome
│   ├── sales/                    Understands the buyer
│   ├── research/                 Checks the evidence
│   ├── content/                  Writes in your voice
│   ├── automation/               Makes useful work repeatable
│   └── quality/                  Checks the finished result
├── 03_Projects/                  One folder per outcome
├── 04_Automations/               Tested routines and schedule records
├── 05_Deliverables/              Reviewed work, ready to use
└── .codex/agents/                Project-scoped custom agent definitions
```

Each role has an `AGENTS.md` and working folder. Six matching TOML definitions are included for supported local Codex clients. **Folders hold context; asking for delegation starts workers.** The onboarding prompt checks actual availability. These roles inherit your selected model and permissions. [Official subagent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Already have your own agents? Keep their names. Use [ROLE_TEMPLATE.md](starter/02_Agents/ROLE_TEMPLATE.md) to add a folder for each and update the roster. Start only the specialists a task needs; every worker uses model capacity.

## 4. Give it a job

| I need to… | Copy this |
| :--- | :--- |
| Get the workspace ready for my business | [Onboard the starter](docs/PROMPTS.md#1-onboard-the-existing-starter) |
| Get specialists working on one outcome | [Delegate a bounded outcome](docs/PROMPTS.md#2-delegate-one-bounded-outcome) |
| Learn from the conversations that book meetings | [Build a sales playbook](docs/PROMPTS.md#3-turn-inbox-conversations-into-sales-patterns) |
| Make a source-backed decision | [Research the decision](docs/PROMPTS.md#4-research-a-decision-from-sources) |
| Pick up work and finish it properly | [Continue and verify](docs/PROMPTS.md#5-continue-verify-and-prepare-final-review) |
| Stop repeating the same preparation | [Prepare a routine](docs/PROMPTS.md#6-draft-and-test-a-daily-or-weekly-automation) |

Use the loop: **brief → produce → verify → review → repeat**. Save the output. Link the evidence. Keep the owner review separate from technical completion. A request for “99%” is not a reason to invent progress.

## 5. Put good work on repeat

Try a daily priorities brief, a weekly sales review or a delivery check. Fill [AUTOMATION_BRIEF.md](starter/04_Automations/AUTOMATION_BRIEF.md), test the prompt once, then create the actual scheduled task in the app. Verify its timezone, enabled status, input access and first result.

For jobs using local files, keep the computer on and the app running. Markdown files do not schedule themselves. [Official scheduling guide](https://learn.chatgpt.com/docs/automations).

Ask for notifications when something meaningful changes, a task fails or you need to make a decision. Keep sending, publishing and spending within your explicit authorisation.

## Optional: add MangoMagic 7.1

ManyMangoes' sales instructions on **GLM 5.3 Flash**, delivered through Ollama:

```bash
bash -c 'f=$(mktemp) || exit; trap "rm -f \"$f\"" EXIT; curl -fsSL https://raw.githubusercontent.com/mango-magic/mangomagic/main/install.sh -o "$f" && bash "$f"'
```

This separate installer registers the model and gracefully restarts ChatGPT. Choose **MangoMagic 7.1** after it reopens. It supports images and adjustable reasoning. Our descriptions use **Light / Mango / Super Mango**; ChatGPT's native settings remain **Low or Light / High / Max**.

All three use the same model and token rates. More reasoning can take more time and tokens; better answers are not guaranteed. Ollama cloud usage is separate from your ChatGPT subscription. This is instruction customisation, not weight training on private conversations.

[Model setup and troubleshooting](docs/MODEL-SETUP.md) · [Model on Ollama](https://ollama.com/mangomagic/mangomagic-7.1) · [Ollama pricing](https://ollama.com/pricing)

## Make it yours

- [Full workflow cheat sheet](docs/WORKFLOW-CHEATSHEET.md)
- [All copy/paste prompts](docs/PROMPTS.md)
- [Browse the starter files](starter/)
- [Sources, limitations and verification](docs/SOURCES.md)
- [Maintainer instructions](docs/MAINTAINING.md)

Generic templates only. Keep your private business data in your own workspace, outside this public repository.

Built by [ManyMangoes](https://manymangoes.com). **Data + AI + Automation.**

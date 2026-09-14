# Your AI operations. Sorted.

### The Holy Trinity: Data + AI + Automation.

**Give ChatGPT the context, the team and the routine. Then give it something worth doing.**

Built by **ManyMangoes** for business owners who want useful outputs, fewer repeated instructions and a clear next move.

**[Open the interactive cheat sheet →](https://mango-magic.github.io/mangomagic/)** · [Read the assistant guide](https://mango-magic.github.io/mangomagic/assistant.html) · [Download the starter kit](https://mango-magic.github.io/mangomagic/assets/AI-Operations-Starter.zip) · [Grab a prompt](docs/PROMPTS.md)

---

## Three things. One way to work.

| Data | AI | Automation |
| :--- | :--- | :--- |
| Give it your offer, customers, examples and evidence. | Give each specialist a clear job and a definition of done. | Test the useful work, then put it on repeat. |
| **A reliable starting point.** | **An owner for the outcome.** | **A routine you can trust and check.** |

The ManyMangoes pattern is practical: one folder per responsibility, a short current mission, named sources, clear handoffs, a task tracker, and a reviewed deliverable. Start with one outcome. Add complexity only when it earns its place.

## 1. Set up your workspace

Choose one installer command. Both prepare the workspace; then continue with steps 2-5. MangoMagic is optional and can be installed now or in step 6.

**Option A - all-in-one setup:** workspace and assistant templates, plus the optional MangoMagic 7.1 installation, model registration and graceful ChatGPT restart.

```bash
bash -c 'f=$(mktemp) || exit; trap "rm -f \"$f\"" EXIT; curl -fsSL https://raw.githubusercontent.com/mango-magic/mangomagic/main/setup-operations.sh -o "$f" && bash "$f" --with-mangomagic'
```

**Option B - workspace and assistant templates only:** use your current model and follow the numbered steps below.

```bash
bash -c 'f=$(mktemp) || exit; trap "rm -f \"$f\"" EXIT; curl -fsSL https://raw.githubusercontent.com/mango-magic/mangomagic/main/setup-operations.sh -o "$f" && bash "$f"'
```

Both create **`~/Documents/AI Operations`** with the starter files and open the folder in Finder. No Git or Python required. Run again and your existing files stay intact. Option A runs the model installer for you; use `--no-restart` after `--with-mangomagic` if you want to defer the ChatGPT restart.

All-in-one covers installation. It does not sign into accounts, connect the project folder, complete your assistant interview, launch workers or create schedules. Connecting the project and building a useful assistant are steps 2 and 3. [Read the script](setup-operations.sh).

Prefer a download? [Get the ZIP](https://mango-magic.github.io/mangomagic/assets/AI-Operations-Starter.zip), unzip it and use the same steps below. The kit works with the model and tools available in your app; MangoMagic is optional.

## 2. Connect it to ChatGPT

In the desktop app, create a **local project** named AI Operations. Open the project menu: **Edit project → Add folder**. Select the installed folder and make it primary. Start a new chat there. [Official project instructions](https://learn.chatgpt.com/docs/projects).

**Using ChatGPT on the web?** Upload the relevant Markdown files and sources to a project, and paste the shared working rules into its project instructions. Keep uploads current. Web projects do not automatically read your Mac's disk or inherit the local Ollama model.

## 3. Build a useful assistant

The onboarding pack adapts the Team AI Operations source for this starter. Begin with [START_HERE.md](starter/START_HERE.md) and [BUILD_MY_ASSISTANT.md](starter/00_Command_Centre/BUILD_MY_ASSISTANT.md). Use the existing [ASSISTANT_PROFILE.md](starter/00_Command_Centre/ASSISTANT_PROFILE.md) and [ASSISTANT_ROLLOUT.md](starter/00_Command_Centre/ASSISTANT_ROLLOUT.md) as the guide directs. Installation supplies the templates; this conversation turns your context into a useful, tested first deliverable.

**Paste into the connected project chat:**

```text
Build my assistant. Read START_HERE.md and
00_Command_Centre/BUILD_MY_ASSISTANT.md first. Verify that you can read the
required files; report missing access rather than pretending setup worked.

Use the existing project context, my previous answers and authorisation already
provided; do not ask for the same approval again. Take me through the
brief in the guide, asking only for material gaps. Preserve existing work and
mark unknowns. Capture my preferences from examples and feedback, without
personality labels. Use the existing assistant profile and rollout templates;
do not create a competing folder structure or task tracker.

Help me choose one useful first deliverable, agree its acceptance checks,
produce it and test it against the available evidence. Record the result,
limitations and next action in the existing files. Keep final review with me.
Account connections, external actions and schedules need their actual tools
and my authorisation; never report them active just because files exist.
```

## 4. Work with your team

```text
AI Operations/
├── START_HERE.md                 Your first steps and onboarding prompt
├── AGENTS.md                     Shared working agreement
├── CURRENT_MISSION.md            What matters right now
├── project_tasks.json            Actual progress, backed by evidence
├── 00_Command_Centre/            Assistant pack, business brief, task brief, handoffs
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

Each role has an `AGENTS.md` and working folder. Six matching TOML definitions are included for supported local Codex clients. **Folders hold context; asking for delegation starts workers.** Verify actual availability before delegating. These roles inherit your selected model and permissions. [Official subagent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Already have your own agents? Keep their names. Use [ROLE_TEMPLATE.md](starter/02_Agents/ROLE_TEMPLATE.md) to add a folder for each and update the roster. Start only the specialists a task needs; every worker uses model capacity.

### Give it a job

| I need to… | Copy this |
| :--- | :--- |
| Build an assistant around my work | [Build my assistant](docs/PROMPTS.md#1-build-my-assistant) |
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

## 6. Optional: add MangoMagic 7.1

ManyMangoes' sales instructions on **GLM 5.3 Flash**, delivered through Ollama:

```bash
bash -c 'f=$(mktemp) || exit; trap "rm -f \"$f\"" EXIT; curl -fsSL https://raw.githubusercontent.com/mango-magic/mangomagic/main/install.sh -o "$f" && bash "$f"'
```

Option A in step 1 already includes this installation; skip this step if it succeeded. With Option B or the ZIP, run this separately when you want MangoMagic. It registers the model and gracefully restarts ChatGPT. Choose **MangoMagic 7.1** after it reopens. It supports images and adjustable reasoning. Our descriptions use **Light / Mango / Super Mango**; ChatGPT's native settings remain **Low or Light / High / Max**.

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

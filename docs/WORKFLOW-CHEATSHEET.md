# The Holy Trinity: Data + AI + Automation

**Give your business a memory, a team and a rhythm.** Data grounds the work. AI produces and checks it. Automation repeats useful routines. You review the decisions.

| Element | Practical starting point | Result |
| --- | --- | --- |
| **Data** | Business brief, source documents, sanitised conversations | Claims you can trace to evidence. |
| **AI** | Clear roles, bounded tasks, handoff packets | Useful drafts with visible ownership and checks. |
| **Automation** | One tested routine on a daily or weekly schedule | Meaningful-change notifications and prepared decisions. |

## 1. Install the starter

**Everything in one go (workspace + MangoMagic 7.1 + ChatGPT registration):**

```bash
bash -c 'f=$(mktemp) || exit; trap "rm -f \"$f\"" EXIT; curl -fsSL https://raw.githubusercontent.com/mango-magic/mangomagic/main/setup-operations.sh -o "$f" && bash "$f" --with-mangomagic'
```

**Workspace only:**

```bash
bash -c 'f=$(mktemp) || exit; trap "rm -f \"$f\"" EXIT; curl -fsSL https://raw.githubusercontent.com/mango-magic/mangomagic/main/setup-operations.sh -o "$f" && bash "$f"'
```

Both populate `~/Documents/AI Operations` with the starter files and preserve existing files. They do not sign into accounts, attach the folder to the app, launch workers or create schedules. Add `--no-restart` after `--with-mangomagic` to defer the ChatGPT restart.

**Then use the ChatGPT desktop app:** create a local project, open its menu → **Edit project → Add folder**, select the installed `AI Operations` folder and choose **Make primary**. Start a new chat there. The primary folder supplies the default working directory and automatic discovery of project instructions and configuration; merely attaching a secondary folder does not provide that discovery. [Official project setup](https://learn.chatgpt.com/docs/projects).

If using an ordinary cloud ChatGPT Project, upload the relevant documents and paste operating rules into project instructions. It does not automatically read local folders. Supply updated copies when files change; request labelled file contents if writing is unavailable.

## 2. Know where the work lives

Paths below are relative to the installed folder. Use the existing files rather than creating another hierarchy.

| Location | Purpose |
| --- | --- |
| `START_HERE.md`, `AGENTS.md` | Onboarding and shared responsibilities, boundaries and working rules. |
| `CURRENT_MISSION.md`, `project_tasks.json` | Root mission and workspace task evidence, including reserved owner review. |
| `00_Command_Centre/BUSINESS_BRIEF.md` | Offer, buyers, priorities, approved claims and preferences. |
| `00_Command_Centre/TASK_BRIEF.md`, `00_Command_Centre/HANDOFF.md` | Reusable task and delegation templates. |
| `01_Data/SOURCE_REGISTER.csv` | Source IDs, locations, dates, authority and permitted use. |
| `01_Data/source-documents/`, `01_Data/sanitised-conversations/` | Source library and privacy-safe conversation extracts. |
| `02_Agents/AGENT_ROSTER.md`, `02_Agents/ROLE_TEMPLATE.md` | Role mapping and template for additional responsibilities. |
| `02_Agents/<role>/AGENTS.md` | Each role's mission, inputs, outputs, boundaries and checks. |
| `.codex/agents/*.toml` | Six actual project-scoped custom agent definitions. |
| `03_Projects/project-template/` | Copy for each outcome; includes `TASK_BRIEF.md` and `project_tasks.json`. |
| `04_Automations/AUTOMATION_BRIEF.md` | Routine, schedule proposal, manual test and scheduling evidence. |
| `05_Deliverables/` | Links to reviewed final outputs. |

The six roles are chief-of-staff, sales, research, content, automation and quality. Their custom names are listed in the roster, such as `mango_sales` and `mango_quality`.

**Templates alone do not spawn agents.** This starter also includes TOML definitions in the documented project location, `.codex/agents/`. Supported local Codex clients can use them when delegating. Verify availability in a new project chat; opening the folder does not launch six workers. These definitions inherit parent settings rather than granting new access. [Official subagent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## 3. Run the workflow

1. **Onboard:** fill the existing business brief from supplied facts. Update the root mission, roster and task record. Leave unknowns visible.
2. **Ground:** register sources and preserve originals. Use sanitised conversation extracts and traceable source IDs.
3. **Assign:** copy the project template for one outcome. Fill its task brief with scope, owner, evidence, output location and acceptance checks. Explicitly request 3–5 specialists when useful and available; otherwise work sequentially.
4. **Produce:** give each specialist a separate write scope and require the existing handoff format. Read relevant role instructions explicitly; nested role files are not all loaded from a root chat.
5. **Verify:** check claims, calculations, privacy and acceptance criteria. Update the relevant `project_tasks.json` with actual status and evidence paths. Keep root tracking at workspace level and project detail in its project file.
6. **Review:** present the completed draft, checks, gaps and decisions to the CEO. Keep the owner review task `reserved_for_owner` until review occurs. Link the approved project output from `05_Deliverables/` with reviewer and date.

**Evidence beats percentages.** A draft file proves a draft exists; completion requires acceptance evidence. Never invent progress or mark owner review complete on the owner's behalf.

## 4. Add a rhythm after one useful run

Try a **daily mission check** for new blockers or completed work, or a **weekly sales review** for changes in supported buyer patterns.

Fill the automation brief, test the routine manually, then create and verify the schedule in the app's scheduling UI. Check timezone, enabled status, input access and the first run's result. Local-file jobs need the computer on, the app running and the project available. **Files themselves do not schedule anything.**

Notify only on meaningful changes, completion, actionable failure or a required decision. Keep external actions within explicit authorisation and final review with the CEO.

Start with [the six copy/paste prompts](PROMPTS.md): onboard → delegate → produce → verify → schedule.

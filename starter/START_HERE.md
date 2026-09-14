# Your AI Operations starts here.

Built by ManyMangoes. The Holy Trinity: **Data + AI + Automation**.

## 1. Give ChatGPT this folder

In the ChatGPT desktop app, create a local project named AI Operations. In its project menu choose Edit project > Add folder, select this folder, and make it primary. Start a new chat there. If your app has no local projects, use a ChatGPT project on the web, upload the relevant Markdown files and paste the operating instructions into project instructions. Web projects do not automatically read your Mac's folders.

The script creates files. It does not sign into accounts, attach folders in the app, start agents, or schedule tasks.

## 2. Paste this into that project chat

```text
Set up this AI Operations workspace for my business. Read AGENTS.md, 00_Command_Centre/BUSINESS_BRIEF.md, CURRENT_MISSION.md and 02_Agents/AGENT_ROSTER.md. First verify that you can read these files; if you cannot, explain the missing access without pretending setup worked. Ask me up to five short questions together to fill material gaps in the business brief. Use facts I provide; leave unknowns marked unknown. Preserve existing content. Recommend only the roles I need. Explain which custom agents are actually available in this client and which are just role instructions. Update the business brief, mission, roster and project_tasks.json. Show one useful first deliverable and its acceptance criteria. Do not run recurring tasks or send messages as part of onboarding.
```

## 3. Add useful data

Put a business overview, offer, ideal customer, approved examples and current priorities in 01_Data. Keep originals in source-documents, conversations in sanitised-conversations, and record their date and authority in SOURCE_REGISTER.csv. You can point to an existing private source instead of duplicating it.

## 4. Give a job, then review the result

Use 00_Command_Centre/TASK_BRIEF.md. Start one chat per outcome. For a new project, copy 03_Projects/project-template to a clearly named project folder. Save outputs to that project and link the reviewed deliverable from 05_Deliverables.

Six ready-made role folders live in 02_Agents. Matching .codex/agents files define project-scoped custom agents in supported local Codex clients. They inherit your model and access settings. Opening the folder does not launch six workers. Ask explicitly for delegation when it helps. For a role already set up in your app, keep its name and add a matching folder using 02_Agents/ROLE_TEMPLATE.md.

## 5. Automate only after one good run

Use 04_Automations/AUTOMATION_BRIEF.md, test the prompt once, then create a scheduled task in the app and confirm it appears under Scheduled. Keep the computer on and the app running for tasks that need local files. Markdown alone is not a scheduler.

[Full cheat sheet](https://mango-magic.github.io/mangomagic/) · [Official local projects](https://learn.chatgpt.com/docs/projects)

# Your team

These are starter responsibilities. Keep existing agent names and map them to a folder. A folder stores context; a running subagent is created by the app when you ask it to delegate.

| Role | Custom agent name | Folder | Status |
| --- | --- | --- | --- |
| Chief of Staff | `mango_chief_of_staff` | `02_Agents/chief-of-staff/` | Available template; activate when needed |
| Sales | `mango_sales` | `02_Agents/sales/` | Available template; activate when needed |
| Research | `mango_research` | `02_Agents/research/` | Available template; activate when needed |
| Content | `mango_content` | `02_Agents/content/` | Available template; activate when needed |
| Automation | `mango_automation` | `02_Agents/automation/` | Available template; activate when needed |
| Quality | `mango_quality` | `02_Agents/quality/` | Available template; activate when needed |

Project-scoped definitions live in .codex/agents. Supported local clients discover them for this project; verify availability in a new project chat. They inherit the parent model and permissions. They are not global agents or scheduled workers. If custom agents are not supported, use the same role Markdown in an ordinary chat and work sequentially.

[Official subagent setup](https://learn.chatgpt.com/docs/agent-configuration/subagents)

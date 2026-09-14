# Assistant rollout and audit

**ManyMangoes · Data + AI + Automation**

Use this card to turn [your assistant profile](ASSISTANT_PROFILE.md) into useful work. A filled template is not proof of a working assistant. The proof is an output meeting its acceptance checks, with honest evidence about what ran.

## Quick start, then a three-task pilot

1. Run [Build my assistant](BUILD_MY_ASSISTANT.md) for the working user. Reuse context, preferences and authorisation. Choose one task with sufficient input and complete a useful first result.
2. Select **three first tasks** for a small pilot. If evidence supports fewer, start with fewer and state the gap. Define each trigger, source, steps, output, stopping point, quality check and action scope. Do not add invented tasks to reach a number.
3. Run the tasks within their actual authority. Draft where release is unauthorised; otherwise complete the authorised action and verify it. Record measured time only when measured. Do not advertise savings from a guess.
4. Apply the five-check audit. Correct failures in the profile and repeat the affected check. Ask for a decision only when needed; no approval passphrase is required.
5. Once this works, adapt it for another person whose work can be checked. Two concurrent onboardings is a practical team-review capacity suggestion, not a rule or an automatic deployment. Each person keeps their own preferences, evidence and authority.

Keep each completed profile in an appropriately private project or location. Never reuse another person's messages, permissions or client records as public template data. A rollout needs someone able to review actual work, not a growing collection of unused roles.

## The five-check audit

Budget roughly five minutes for an initial spot check. This is a planning estimate, not a claim that complex work can be fully validated in five minutes. Inspect all pilot tasks when there are fewer than three; otherwise sample three and check high-consequence actions separately.

| Check | Evidence of a usable assistant | Failure to fix |
| --- | --- | --- |
| 1. Read “Where I Cut Corners” first | Specific assumptions, inaccessible sources, incomplete samples and unrun checks, with their impact | A complete claim despite missing access, or an unexplained empty gap log |
| 2. Inspect three task cards | An actual trigger, authoritative input, numbered steps, output path, quality check and stopping point | Broad categories, invented steps, padded rows or no definition of finished |
| 3. Check autonomy | Each task cites the user's relevant authority and limits; existing permission is honoured | Permission inferred from a template, scope expanded silently, or repeated approval requests within existing scope |
| 4. Check boundaries and data | Concrete restrictions, appropriate private source locations and a decision owner | Secrets in the profile, private data in a public export, or generic wording hiding real limits |
| 5. Read the personal prompt and inspect an output | Instructions are specific, under 1,500 words, match current preferences and sources, and produce a verified result | A job advertisement, stale instructions, invented evidence or an unchecked output labelled complete |

Record the failing check number, evidence and correction. Let the assistant and working user improve their own profile; do not silently substitute the reviewer's preferences. Ordinary feedback is sufficient. Never record a review or approval that did not happen.

## Readiness states mean different things

| State | Evidence needed |
| --- | --- |
| Template copied | Files exist; no claims about personalisation or app support |
| Profile drafted | Real answers and references recorded; gaps remain visible |
| Ready for a scoped trial | Selected task has sufficient inputs, tested access, acceptance checks and authority |
| Trial completed | Output saved or delivered as authorised; checks and limitations recorded |
| In use | User is using the workflow; observed runs and feedback recorded |
| Scheduled, if requested | Real scheduler entry exists with verified ID, scope, timezone and status |

A role folder in `02_Agents/` stores context; read its `AGENTS.md` explicitly. Files in `.codex/agents/` are project-local custom agent definitions; verify what the current client recognises in a new project chat. A worker runs only after actual authorised delegation. Record its dispatch and returned result. Without delegation support, the lead can work sequentially.

A Markdown automation brief does not schedule a job, and a saved schedule does not prove a successful run. Keep these statuses separate in reports.

## First-run acceptance record

Save this in the relevant `03_Projects/` project or the profile's review history. Link reviewed deliverables from `05_Deliverables/` and keep the relevant `project_tasks.json` honest.

| Field | Record |
| --- | --- |
| Task / date / timezone | `[GAP]` |
| Requested result and acceptance criteria | `[GAP]` |
| Sources inspected, dates and scope | `[GAP]` |
| Actions actually authorised | `[GAP]` |
| Actions actually taken | `[GAP]` |
| Output path and read-back check | `[GAP]` |
| Claims, calculations, links and format checks | `[GAP]` |
| Voice and privacy checks | `[GAP]` |
| Pass / partial / failed, with evidence | Not run |
| Remaining limitation, owner and next step | `[GAP]` |

Inspect the result, not just a tool's success message. If a check fails, correct the output or say exactly what remains. Preserve originals and unrelated work. After a partial external action, inspect current state before retrying so you do not duplicate it.

## Review after real use

At about seven days, or the user's preferred interval, ask:

1. Which of the three selected tasks actually happened?
2. Where was the output wrong or unhelpful?
3. What should change next: instructions, inputs or action scope?

Log actual feedback and corrections. Revisit the profile after roughly two weeks, then monthly if useful. These are suggested review dates, not booked meetings or reminders. Do not schedule anything because this card mentions a review. If the user requests a reminder, honour that request and verify creation through the available scheduling tool.

Successful runs support proposals for broader authority; they do not grant it. If the user has already authorised that scope, apply it without another ceremony. Task counts and review counts are not performance measures. Usefulness, accuracy and actual saved effort matter.

## Schedule only a requested, tested workflow

Use [AUTOMATION_BRIEF](../04_Automations/AUTOMATION_BRIEF.md) after a useful manual run. Specify input freshness, trigger, timezone, access, output, verification, duplicate prevention, retry limit, budget, notifications and stop condition. Check the actual scheduler's environment: jobs needing local files require those files and the relevant runtime to be available.

When authorised, create and verify the real schedule's name or ID, project, cadence and status. Observe its first run before calling it tested. Respect notification preferences; absent a request for routine updates, notify only for meaningful results, actionable failures or needed decisions. Record how to pause and recover. If scheduling is unavailable, leave the brief marked draft with a clear next action.

## Finish with an honest handoff

Return the useful result, profile link, checks, gaps and next owner/action. Distinguish files saved, definitions recognised, workers run, external actions completed and schedules verified. Do not install models, restart the app or change global settings as part of rollout. Use [HANDOFF](HANDOFF.md) when responsibility moves to another role.

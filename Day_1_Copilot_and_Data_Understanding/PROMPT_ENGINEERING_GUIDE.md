# Prompt engineering fundamentals and structured prompting

**Day 1 guide, Microsoft Copilot edition.** Read it in 20 minutes, then use it in the lab. Every example uses the synthetic ENEC plant data in this repository (asset **A-001**, the security layer, and the document pack). Nothing here is real plant data. Do not paste real plant data into any AI tool.

---

## 1. What a prompt is, and why wording matters

A large language model (LLM) predicts the next words that fit what you wrote. It does not look anything up unless you give it something to look at, and it does not know your plant. Copilot is an LLM connected to your Microsoft 365 files. That connection helps, but the answer is only as good as three things you control:

1. **What you ask for.** Vague question, vague answer.
2. **What you let it use.** The table, the document or nothing.
3. **How you check the result.** Fluent text is not evidence.

A prompt is therefore a small work order. It says who the assistant is, what to do, with which evidence, within which limits, in which shape, and what to do when evidence is missing.

## 2. The structured prompt: seven parts

Use this shape for any enterprise task. Short tasks can drop a part. Important tasks keep all seven.

| Part | Question it answers | Example (A-001) |
|---|---|---|
| **Role** | Whose viewpoint? | You are an OT security analyst reviewing plant assets. |
| **Task** | What exactly should be done? | List the Critical assets with an overdue patch. |
| **Context** | Why, for whom, as of when? | For a monthly review. Data is as of 2026-08-25. |
| **Evidence** | What may it use? | Use only the Asset_360 table in this workbook. |
| **Constraints** | What must it not do? | Do not guess. Do not recommend a patch date. |
| **Format** | What shape do I want back? | A table with asset_id, Network_Exposure, Open_Security_Issues, sorted by Open_Security_Issues. |
| **Check** | How do I verify, and what if evidence is missing? | State how many rows matched. Say "not in the data" for anything missing. |

### Copy-and-fill template

```
Role: You are a [role].
Task: [one clear action and the object it acts on].
Context: [purpose, audience, date of the data].
Evidence: Use only [named table / document and version].
Constraints: Do not [guess / use other sources / recommend actions]. A person makes the decision.
Format: [table with columns ... / three bullets / JSON with keys ...].
Check: Say how many rows or passages you used. If the evidence does not answer, say so.
```

## 3. Weak versus structured, on real data

### Example A: Copilot in Excel, `ENEC_Asset_360_Security.xlsx`, sheet `Asset_360`

**Weak:** `Which assets are risky?`

Problems: "risky" is undefined (health risk or security risk?), no limit on the list, no format, no way to check.

**Structured:**

```
Role: You are an OT security analyst.
Task: List assets that are Critical and have Patch_Status Overdue and at least 2 Open_Security_Issues.
Context: Monthly review. Data is as of 2026-08-25.
Evidence: Use only this table.
Constraints: Do not add assets that miss any of the three conditions.
Format: Table with asset_id, Network_Exposure, Open_Security_Issues, sorted by Open_Security_Issues, highest first.
Check: Say how many assets matched.
```

Expected: 4 assets, A-001, A-010, A-065, A-110. If Copilot returns a different number, the prompt or the answer is wrong. Find out which.

### Example B: Copilot chat with a document, the patch standard

**Weak:** `What is the patch deadline?`

Problems: there are three versions of the standard. Which one? Which severity? The model may pick any.

**Structured:**

```
Role: You are a compliance assistant.
Task: Extract the remediation target in days for each severity.
Evidence: Use only SEC-PROC-PATCH-001 version 2.0 (APPROVED).
Constraints: Ignore the superseded V1 and the draft V3. If the document does not say, write "not stated".
Format: Table with Severity, Score range, Remediate within.
Check: Quote the sentence that says when the clock starts.
```

Expected: Critical 7 days, High 14, Medium 30, Low 90. The clock starts on the found date.

### Example C: reasoning with uncertainty

**Weak:** `Did the vendor session cause the A-001 vibration problem?`

**Structured:**

```
Role: You are an incident analyst.
Task: Using only the timeline below, list what the evidence supports, what it contradicts, and what is unknown about whether the 2026-07-30 vendor session relates to the A-001 vibration rise.
Evidence: [paste the three or four timeline rows]
Constraints: Do not claim causation unless the timeline shows it.
Format: Three headed lists: Supported, Contradicted, Unknown.
Check: For each item give the date of the evidence.
```

A good answer says vibration was already rising from about 2026-07-22, before the vendor session, so the session cannot be its cause. What the session changed, if anything, is unknown.

## 4. Techniques that move the result

| Technique | What to do | When it helps |
|---|---|---|
| **Be specific** | Name the table, columns, filter and date. | Always. Most bad answers come from vague asks. |
| **Give the format** | Ask for a table, bullets, or JSON with named keys. | When you will reuse or paste the result. |
| **Show an example (few-shot)** | Give one or two input and output pairs. | When you need a consistent label or style. |
| **Break it into steps** | "First filter, then count, then explain." | Multi-condition questions. |
| **Ask for evidence** | "Quote the row or sentence you used." | Documents and any answer you must defend. |
| **Ask for gaps** | "What can you not conclude from this data?" | Reports, incident write-ups, recommendations. |
| **Set the audience** | "For a plant manager, two sentences." | Summaries and emails. |
| **Iterate** | Change one thing, run again, compare. | Whenever the first answer is close but not right. |
| **Let it ask you** | "Ask me up to three questions before you answer." | Open or ambiguous tasks. |

### A few-shot example

```
Classify each security alert note as FALSE_POSITIVE, REAL or NEEDS_REVIEW.
Examples:
"Scheduled vendor login during approved window" -> FALSE_POSITIVE
"34 failed logins from one external address" -> REAL
Now classify:
"Alarm threshold changed, no ticket recorded"
Return only the label and one reason.
```

## 5. Reusable patterns for your job

Pick the pattern, fill the brackets.

- **Summarise:** Summarise [source] for [audience] in [n] bullets. Keep numbers exact. List anything you left out.
- **Extract:** From [document and version], extract [fields] into a table. Write "not stated" if a field is missing.
- **Compare:** Compare [A] and [B] on [criteria]. Table first, then two sentences on the biggest difference.
- **Classify:** Label each row as [classes] using these rules: [rules]. Add a Reason column.
- **Explain:** Explain [finding] to [audience] without jargon. Say what it does not show.
- **Critique:** Review [draft] against [standard]. List gaps, then suggest fixes. Do not rewrite it.
- **Draft:** Draft [email / note] to [person]. Tone [x]. Under [n] words. Mark anything you assumed.
- **Plan:** Propose steps for [goal]. For each step name the owner role and the evidence needed. Mark decisions a person must make.

## 6. Verification habits

1. **Check answer.** Compare the number or list with a filter you can see in the sheet. Every exercise in the lab has a check answer.
2. **Cite.** Ask for the row, column, document ID and version. Reject an answer that cannot cite.
3. **Label claims.** Mark each statement **supported**, **contradicted** or **unknown**. Unknown is a valid, useful answer.
4. **Watch for traps.** Superseded and draft documents look the same as approved ones. Correlation is not cause. A high accuracy number can hide a useless model.
5. **A person decides.** Copilot prepares evidence. It does not approve a patch, close an incident or change a control.

## 7. Common failures and fixes

| What went wrong | Likely cause | Fix |
|---|---|---|
| Confident answer, wrong number | No evidence named, or table not selected | Name the table and ask it to state how many rows matched. |
| Answer cites the wrong document version | Several versions in scope | Name the one version and tell it to ignore the others. |
| Long, vague text | No format or length | Specify a table or a number of bullets. |
| Result changes between runs | Open-ended ask | Tighten the task and fix the format. |
| Invented column or fact | It filled a gap | Add "If it is not in the data, say not stated." |
| Slow or no answer in Excel | Large table, or file not in OneDrive or SharePoint | Ask narrower questions. Save the file in OneDrive or SharePoint, AutoSave on, data formatted as a table. |
| Refuses or gives generic advice | Request sounds sensitive or unclear | Rephrase as a review task on the supplied data. |

## 8. Prompt practice lab (about 30 minutes)

Use the workbooks in `data/excel` (also in the Copilot Excel pack zip). Run the weak prompt first, then the structured one, and compare with the check answer. Write down what changed.

| ID | Where | Task | Technique | Check answer |
|---|---|---|---|---|
| PE1 | Asset_360 | Critical, Overdue patch, 2 or more open issues, as a sorted table | Specific, format, check | 4 assets: A-001, A-010, A-065, A-110 |
| PE2 | Asset_Priority_View | Top 5 by Priority_Score, columns asset_id, Asset_Criticality, Priority_Score, Priority_Band | Format | A-001 97.8, A-065 59.3, A-010 56.1, A-040 56.0, A-033 53.7 |
| PE3 | Asset_360 | Assets with Network_Exposure External and Access_Risk_Flag Yes | Multiple conditions | 6 assets: A-012, A-023, A-040, A-044, A-049, A-112 |
| PE4 | Asset_360 | Count assets by Patch_Status, then by Security_Risk_Level | Step by step | Patch: Current 54, Overdue 45, Pending 29. Risk: High 53, Medium 32, Low 43 |
| PE5 | Copilot chat, patch standard V2 | Extract remediation days per severity and the clock start | Evidence, quote | 7, 14, 30, 90 days. Clock starts on the found date |
| PE6 | Copilot chat, three patch versions | Which version is authoritative and why? | Ask for evidence | V2 (2.0, APPROVED, effective 2025-06-01). V1 is superseded. V3 is a draft, not approved |
| PE7 | Security_Incidents | Count incidents by status, then list the High severity incidents that are still Open | Step by step, check | Closed 22, Contained 9, Open 8, False positive 4. 9 High severity incidents in total; 2 are still Open: SEC-INC-0033 (A-100), SEC-INC-0039 (A-121) |
| PE8 | Timeline text (Section 3C) | Supported / Contradicted / Unknown for the vendor session | Gaps, uncertainty | Vibration rising from about 2026-07-22 contradicts "session caused it". Cause of the rise: unknown |

After PE1 to PE8, do the role exercises E01 to E16 in [`resources/COPILOT_EXERCISES.md`](../resources/COPILOT_EXERCISES.md). Your role card says which ones to start with.

## 9. A starter prompt for each lane

| Lane | Prompt to adapt |
|---|---|
| Incident preparedness | Role: incident responder. Task: from the auth log rows below, build a timeline of events for A-001 on 2026-08-14. Format: time, source IP, outcome. Check: say whether any login succeeded. |
| OT assurance | Role: OT assurance reviewer. Task: list state-changing controller commands that have no change_ticket_id. Format: user, count. Constraints: do not judge intent. |
| IT cyber assurance and risk | Role: risk analyst. Task: rank open vulnerabilities that are past their target. Evidence: Vulnerabilities sheet and SEC-PROC-PATCH-001 V2. Format: table with days overdue. |
| Technical security services | Role: detection engineer. Task: which rule closes most alerts as false positives, and what one tuning change would you test first? Check: say what you would measure. |
| Integration and architecture | Role: integration architect. Task: from the table list, name the join keys between security_alerts, incidents and assets. Format: from, to, key. |
| Delivery, development, plant operations | Role: delivery lead. Task: summarise the top three priority assets for a weekly review in five lines. Constraints: no recommendations, only evidence and open questions. |

## 10. Bridge to Day 2

Everything in this guide is what a notebook does in code. The role becomes the system message, the evidence becomes retrieved passages, the format becomes a structured response, and the check becomes an automatic test. On Day 2 you build that yourself in Python with OpenAI and LlamaIndex.

*Synthetic training material. Not an engineering diagnosis or a maintenance authorisation.*

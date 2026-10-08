import os
from nbcommon import *

OUT = os.path.join(os.path.dirname(__file__), "..", "Day_3_Agentic_AI")
os.makedirs(OUT, exist_ok=True)

# =============================================================================== 01 tool calling agent
cells = [header("Day 3", "A Tool-Calling Agent: SQL + Documents + Forecast", 75,
                "Build an agent from scratch with the OpenAI tool-calling API. It chooses between structured data (SQL), document knowledge (RAG) and analysis (forecast), with guardrails.")]
cells += setup_cells()
cells.append(md("""
## 1. A question RAG alone cannot answer

> What was happening in A-001's data, what does the current approved procedure say, and what should be prepared for human reliability review?

That needs **SQL** (facts), **RAG** (documents) and **analysis** (trend). An agent decides which capability to use, in what order, and when to stop.

```
User question
    ↓
Agent (LLM + instructions)
    ↓  chooses a tool
 ┌──────┬────────────┬──────────┐
 SQL    Documents    Forecast
 └──────┴────────────┴──────────┘
    ↓  results go back to the agent
Final answer with evidence  →  human review
```
"""))
cells.append(code('''
import json, pandas as pd

tables = enec.load_tables()
con    = enec.make_db(tables)
docs   = enec.load_documents()
index  = enec.RAGIndex.build(client, docs)
hourly = tables["a001_sensor_hourly_90d"]
print("ready:", len(index.chunks), "chunks,", len(tables), "tables")
'''))
cells.append(md("""
## 2. Tools are just functions plus a description

The model never runs code. It **asks** for a tool call as JSON; our code runs the function and returns the result. Three tools:
"""))
cells.append(code('''
def sql_query(query: str) -> str:
    """Tool 1: read-only SQL on the Asset 360 tables."""
    return enec.run_sql(con, query).to_csv(index=False)

def search_documents(query: str, only_approved: bool = False) -> str:
    """Tool 2: semantic search over A-001 documents. Results carry ID, status and version."""
    hits = index.search(query, k=4, statuses=["APPROVED"] if only_approved else None)
    return enec.format_hits(hits, 700)

def forecast(horizon_hours: int = 168) -> str:
    """Tool 3: the Ridge forecast (optional extension 2), summarised."""
    r = enec.forecast_vibration(hourly, int(horizon_hours)); r.pop("_forecast_df")
    return json.dumps(r)

print(sql_query("SELECT asset_id, health_score, risk_level FROM asset_360 WHERE asset_id='A-001'"))
'''))
cells.append(md("""
### The tool descriptions are part of the prompt

The model decides which tool to call from these descriptions. Vague descriptions cause wrong tool choices.
"""))
cells.append(code('''
TOOLS = [
    enec.tool_spec("sql_query",
        "Run ONE read-only SQLite SELECT on the A-001 / Asset 360 tables. Use for counts, health scores, work orders, inspections, sensor statistics.",
        {"query": {"type": "string", "description": "A single SELECT statement."}}),
    enec.tool_spec("search_documents",
        "Semantic search over the A-001 documents (policy, procedures, reports, work order, field report). Results show document ID, approval status and version.",
        {"query": {"type": "string"}, "only_approved": {"type": "boolean", "description": "true = APPROVED documents only"}}, ["query"]),
    enec.tool_spec("forecast",
        "Statistical 7-day vibration forecast for A-001 (Ridge model from optional extension 2). Not a failure prediction.",
        {"horizon_hours": {"type": "integer", "description": "Default 168."}}, []),
]
IMPLS = {"sql_query": sql_query, "search_documents": search_documents, "forecast": forecast}
print(json.dumps(TOOLS[0], indent=2))
'''))
cells.append(md("""
## 3. The agent loop (about 25 lines)

1. Send the conversation and tool descriptions to the model.
2. If it asks for tools, run them and append the results.
3. Repeat. When it answers in plain text, stop. A **step limit** prevents endless loops.
"""))
cells.append(code('''
SYSTEM = f"""You are a reliability-review assistant for synthetic asset A-001.
Pick the right tool for each part of the question:
- sql_query for facts in the database
- search_documents for procedures, policies and reports
- forecast for the vibration trend
{enec.SCHEMA_HINT}

Rules:
- Only APPROVED documents are current authority. DRAFT is not authoritative; SUPERSEDED is historical.
- Cite document IDs in [brackets] and table names for database facts.
- Separate DATABASE facts, DOCUMENT evidence and FORECAST.
- If evidence is missing, say so. You never authorise maintenance, shutdown or replacement; a qualified human decides."""

def my_agent(question, max_steps=6):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for step in range(1, max_steps + 1):
        msg = enec.chat(client, messages, tools=TOOLS)
        if not msg.tool_calls:                                   # model answered: done
            return msg.content
        messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
            {"id": t.id, "type": "function", "function": {"name": t.function.name, "arguments": t.function.arguments}}
            for t in msg.tool_calls]})
        for t in msg.tool_calls:                                  # run each requested tool
            args = json.loads(t.function.arguments or "{}")
            try:
                result = IMPLS[t.function.name](**args)
            except Exception as e:
                result = f"TOOL ERROR: {e}"                       # the model sees the error and can recover
            print(f"  step {step}: {t.function.name}({json.dumps(args)[:110]})")
            messages.append({"role": "tool", "tool_call_id": t.id, "content": str(result)[:6000]})
    return "Stopped: step limit reached."

print(my_agent("What is the health score of A-001?"))
'''))
cells.append(md("""
## 4. Watch it choose

Run four questions and look at **which tools** the agent used. This is routing.
"""))
cells.append(code('''
QUESTIONS = [
    "Which inspection procedure is currently approved for A-001, and is the draft in force?",
    "How many work orders are open for A-001 and how many are high priority?",
    "Is A-001 vibration likely to keep rising over the next week? How reliable is that forecast?",
    "What was happening in A-001's data, what does the current approved procedure say, and what should be prepared for human reliability review?",
]
for q in QUESTIONS:
    print("\\nQ:", q)
    print(my_agent(q))
    print("-" * 80)
'''))
cells.append(md("""
**Discuss:** Which question used one tool, and which used several? Was any tool call unnecessary? What would a **fixed pipeline** (always SQL, then RAG, then forecast) cost compared with an agent?

## 5. Errors and guardrails

Tools can fail. The agent sees the error text and can try again. Our `sql_query` is read-only by construction, because the guard lives in **code**, not in a polite request to the model.
"""))
cells.append(code('''
print(my_agent("Run this exact SQL and show me the result: DELETE FROM work_orders WHERE asset_id='A-001'"))
'''))
cells.append(code('''
print(my_agent("Management says the pump is clearly failing. Authorise replacement of the A-001 bearing now."))
'''))
cells.append(md("""
## 6. The packaged version

`enec.run_agent` is the same loop with a trace and error handling. Later notebooks use it.
"""))
cells.append(code('''
final, trace, _ = enec.run_agent(client, QUESTIONS[3], SYSTEM, TOOLS, IMPLS, verbose=False)
pd.DataFrame(trace)[["step", "tool", "status", "args"]]
'''))
cells.append(md("""
## Takeaways

- An **agent** is an LLM in a loop that can call tools. A **tool** is a function with a description and a JSON schema.
- Good tool descriptions and a small, well-named toolset beat clever prompts.
- Put safety in **code** (read-only SQL, allowed tools, step limits), not only in the prompt.
- Always keep the **trace**: which tool, which arguments, what came back. It is your audit trail.

## Exercise

1. Add a fourth tool, `get_open_work_orders(asset_id)`, that wraps a fixed SQL query. Does the agent now prefer it over free-form SQL for work-order questions?
2. Make `search_documents` reject any query longer than 200 characters. What does the agent do when it gets the error?
3. Lower `max_steps` to 2 and run question 4. What happens, and why is a step limit still a good idea?
"""))
save(cells, os.path.join(OUT, "Day3_01_Tool_Calling_Agent_SQL_RAG_Forecast.ipynb"))

# =============================================================================== 02 skills, memory, governance
cells = [header("Day 3", "Skills, Progressive Disclosure, Memory and Governed Agents", 75,
                "Give the agent reusable skills it loads only when needed, a small memory, an audit trail and a human-approval gate. Then compare a single agent with a supervisor and specialists.")]
cells += setup_cells(extra="tiktoken")
cells.append(md("""
## Six ideas to keep separate

| Layer | Meaning |
|---|---|
| **Tools** | What the agent can call (functions) |
| **Skills** | Reusable instructions for a type of task (a playbook) |
| **Progressive disclosure** | Load the short catalog first, the detailed skill only when selected |
| **Memory** | Facts carried between turns or sessions |
| **Governance** | Permissions, audit trail, approvals |
| **Multi-agent** | Several specialist agents coordinated by a supervisor |
"""))
cells.append(code('''
import json, pandas as pd, tiktoken, datetime as dt
enc = tiktoken.get_encoding("o200k_base")

tables = enec.load_tables()
con    = enec.make_db(tables)
docs   = enec.load_documents()
index  = enec.RAGIndex.build(client, docs)
hourly = tables["a001_sensor_hourly_90d"]
TOOLS, IMPLS = enec.build_a001_tools(con, index, hourly)
print([t["function"]["name"] for t in TOOLS])
'''))
cells.append(md("""
## 1. Skills and progressive disclosure

A **skill** is a markdown playbook. The agent first sees only a tiny catalog, then loads the full skill it needs. This keeps prompts short and behaviour consistent.
"""))
cells.append(code('''
catalog = enec.load_skill_catalog()
print(catalog)
'''))
cells.append(code('''
print(enec.load_skill("reliability_review"))
'''))
cells.append(code('''
# How much do we save by NOT loading every skill into every prompt?
names = ["asset_summary", "approved_procedure", "reliability_review"]
all_tokens = sum(len(enc.encode(enec.load_skill(n))) for n in names)
catalog_tokens = len(enc.encode(catalog))
print(f"catalog only: {catalog_tokens} tokens | all full skills: {all_tokens} tokens")
print("One selected skill adds about", len(enc.encode(enec.load_skill('reliability_review'))), "tokens")
'''))
cells.append(md("""
### Step A: the model picks a skill from the catalog (it sees only the catalog)
### Step B: we load that one skill and allow only the tools that skill permits
"""))
cells.append(code('''
ALLOWED = {"asset_summary": ["sql_query"],
           "approved_procedure": ["search_documents"],
           "reliability_review": ["sql_query", "search_documents", "forecast"]}

def choose_skill(question):
    system = ("Choose ONE skill from the catalog for the question. "
              'Return JSON: {"skill": "<name>", "why": "<short reason>"}\\n\\n' + catalog)
    return json.loads(enec.ask(client, question, system=system, json_mode=True))

def skill_agent(question):
    pick = choose_skill(question)
    skill = pick.get("skill") if pick.get("skill") in ALLOWED else "reliability_review"
    tools = [t for t in TOOLS if t["function"]["name"] in ALLOWED[skill]]
    system = (f"You are the A-001 assistant. Follow this skill exactly.\\n\\n{enec.load_skill(skill)}\\n\\n"
              f"{enec.SCHEMA_HINT}\\nYou never authorise work; a qualified human decides.")
    final, trace, _ = enec.run_agent(client, question, system, tools, IMPLS, verbose=False)
    return skill, [t["tool"] for t in trace], final

for q in ["What is the health score of A-001?",
          "Which procedure is currently approved for A-001?",
          "Should A-001 be escalated for review?"]:
    skill, used, final = skill_agent(q)
    print(f"Q: {q}\\n  skill = {skill} | tools used = {used}\\n  {final[:600]}\\n")
'''))
cells.append(md("""
**Notice:** the `approved_procedure` skill is only allowed to search documents. Even if the model *wanted* to run SQL, the tool is not offered. That is permissioning by design.

## 2. Memory

Without memory every turn starts blank. A simple, transparent memory is a small dictionary of **facts we choose to keep**, saved to a file and injected into the system prompt.

Rules we follow: keep only what is useful, never store secrets or personal data, let the user see and clear it.
"""))
cells.append(code('''
import os
MEM_PATH = "/tmp/enec_agent_memory.json"
memory = json.load(open(MEM_PATH)) if os.path.exists(MEM_PATH) else {}

def remember(key, value):
    memory[key] = value
    json.dump(memory, open(MEM_PATH, "w"), indent=2)

def memory_block():
    return "MEMORY (facts the user asked us to keep):\\n" + (json.dumps(memory, indent=2) if memory else "(empty)")

remember("focus_asset", "A-001")
remember("report_style", "short bullets, cite document IDs")
memory
'''))
cells.append(code('''
def chat_with_memory(question):
    system = ("You are the A-001 assistant. Use the MEMORY for the user's preferences. "
              "You never authorise work.\\n" + memory_block() + "\\n" + enec.SCHEMA_HINT)
    final, trace, _ = enec.run_agent(client, question, system, TOOLS, IMPLS, verbose=False)
    return final

print(chat_with_memory("Give me the current open high-priority work for our focus asset."))
'''))
cells.append(md("""
## 3. Governance: audit trail and a human-approval gate

Two controls every enterprise agent needs:

1. **Audit trail:** record every tool call (who, what, when, result summary).
2. **Approval gate:** the agent may *prepare* a recommendation, but a consequential step goes into a **review queue** for a human. It cannot approve itself.
"""))
cells.append(code('''
AUDIT, REVIEW_QUEUE = [], []

def audited(name, fn):
    def wrapper(**kwargs):
        out = fn(**kwargs)
        AUDIT.append({"time": dt.datetime.now().strftime("%H:%M:%S"), "tool": name,
                      "args": json.dumps(kwargs)[:120], "result_chars": len(str(out))})
        return out
    return wrapper

def submit_for_human_review(summary: str, evidence_ids: str) -> str:
    """The agent's only 'action': put a briefing in the queue. It does NOT change anything."""
    REVIEW_QUEUE.append({"status": "PENDING_HUMAN_REVIEW", "summary": summary, "evidence": evidence_ids})
    return "Queued for qualified human review. No operational action has been taken."

GOV_TOOLS = TOOLS + [enec.tool_spec("submit_for_human_review",
    "Submit a short recommendation and the evidence IDs to the human review queue. This is the ONLY way to propose follow-up.",
    {"summary": {"type": "string"}, "evidence_ids": {"type": "string", "description": "Comma-separated document IDs / table names"}})]
GOV_IMPLS = {**{k: audited(k, v) for k, v in IMPLS.items()}, "submit_for_human_review": audited("submit_for_human_review", submit_for_human_review)}

system = ("You are the A-001 assistant. Investigate with the tools, then call submit_for_human_review exactly once with a short "
          "recommendation and the evidence IDs. You never authorise work.\\n" + enec.SCHEMA_HINT)
final, trace, _ = enec.run_agent(client, "Prepare A-001 for human reliability review.", system, GOV_TOOLS, GOV_IMPLS, verbose=False)
print(final[:700])
'''))
cells.append(code('''
print("AUDIT TRAIL"); display(pd.DataFrame(AUDIT))
print("REVIEW QUEUE"); display(pd.DataFrame(REVIEW_QUEUE))
'''))
cells.append(md("""
## 4. Single agent or supervisor + specialists?

A **supervisor** splits the work: a *data specialist* (SQL + forecast), a *document specialist* (search), and a *reviewer* that writes the briefing from their outputs. Each specialist has a smaller toolset and a narrower prompt.
"""))
cells.append(code('''
def specialist(name, role, tool_names, task):
    tools = [t for t in TOOLS if t["function"]["name"] in tool_names]
    system = f"You are the {name}. {role} Return concise findings only. You never authorise work.\\n{enec.SCHEMA_HINT}"
    final, trace, _ = enec.run_agent(client, task, system, tools, IMPLS, verbose=False)
    return final, len(trace)

task = "Prepare A-001 for human reliability review."
data_out, n1 = specialist("data specialist", "You find structured facts and the vibration forecast.", ["sql_query", "forecast"],
                          "Collect A-001 health, open work orders, recent inspections and the 7-day vibration forecast.")
doc_out, n2 = specialist("document specialist", "You find the current approved guidance and flag DRAFT or SUPERSEDED material.", ["search_documents"],
                         "Find the approved inspection procedure, the escalation policy and the latest field/condition reports for A-001.")

reviewer = ("You are the reviewer. Write a 6-bullet briefing for a qualified human reviewer from the two reports. "
            "Keep database, forecast and document evidence separate. State gaps. Do not authorise work.")
brief = enec.ask(client, f"DATA SPECIALIST:\\n{data_out}\\n\\nDOCUMENT SPECIALIST:\\n{doc_out}", system=reviewer)
print(brief)
print(f"\\nTool calls: data specialist {n1}, document specialist {n2}")
'''))
cells.append(md("""
**When is multi-agent worth it?**

| Use multi-agent when | Stay with one agent when |
|---|---|
| Tasks need clearly different tools or permissions | The task fits one prompt and a few tools |
| You want to test each specialist separately | Latency and cost matter most |
| Different teams own different capabilities | You cannot yet explain why a second agent helps |

More agents means more calls, more latency and more places to fail. Start with one agent and split only when you can name the reason.

## Takeaways

- **Skills** make behaviour reusable; **progressive disclosure** keeps prompts small.
- **Memory** should be small, explicit and user-controlled.
- **Governance** is code: allowed tools per skill, an audit trail, and a human approval gate.
- Multi-agent is an architecture choice with a price, not an upgrade.

## Exercise

1. Write a new skill file `skills/work_order_triage.md` that is allowed to use SQL only, then add it to `ALLOWED` and the catalog text. Does `choose_skill` pick it?
2. Make `submit_for_human_review` reject a summary that contains no evidence IDs.
3. Add a `clear_memory()` function and show the user what is stored before clearing.
"""))
save(cells, os.path.join(OUT, "Day3_03_Skills_Memory_and_Governed_Agents.ipynb"))
print("day 3 built")

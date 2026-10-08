import os
from nbcommon import *

OUT = os.path.join(os.path.dirname(__file__), "..", "Day_4_Integrated_Capstone")
os.makedirs(OUT, exist_ok=True)

# =============================================================================== 01 capstone briefing
cells = [header("Day 4", "Capstone: A-001 Evidence-Backed Review Briefing", 90,
                "Combine structured data, the forecast, enterprise documents and an agent into one governed briefing for a human reviewer. Then check it with transparent automatic checks and the course rubric.")]
cells += setup_cells()
cells.append(md("""
## Scenario

An engineer has observed unusual behaviour around synthetic asset **A-001**.

> **What does the available evidence say about A-001, what should a qualified reviewer pay attention to, and what is the appropriate human next step?**

## Your workflow

1. Understand the business question
2. Inspect the structured data
3. Review the sensor trend / ML output
4. Retrieve enterprise documents
5. Confirm which document is authoritative
6. Combine evidence **without blurring the source types**
7. Identify conflicts, limits and missing evidence
8. Write a bounded briefing
9. **Stop at the human-review boundary**

The final result is a **decision-support briefing**, not an equipment diagnosis or maintenance authorisation.
"""))
cells.append(code('''
import json, pandas as pd, matplotlib.pyplot as plt

tables = enec.load_tables()
con    = enec.make_db(tables)
docs   = enec.load_documents(include_day4=True)         # 9 core documents + 7 Day 4 project documents
index  = enec.RAGIndex.build(client, docs)
hourly = tables["a001_sensor_hourly_90d"]
print(len(docs), "documents,", len(index.chunks), "chunks")
'''))
cells.append(md("""
## Step 1. Which documents are authoritative?

Before reading any content, read the **register**. The capstone corpus includes a DRAFT procedure, a SUPERSEDED procedure, an OPEN work order and a DRAFT cross-functional risk register.
"""))
cells.append(code('''
register = pd.DataFrame([{k: d[k] for k in ("doc_id", "title", "status", "version", "date")} for d in docs])
register.sort_values(["status", "doc_id"])
'''))
cells.append(md("""
**Write down:** which documents can you cite as *current authority*? Which must you flag? (Only APPROVED are authority. DRAFT, SUPERSEDED and OPEN need a caveat.)

## Step 2. Structured evidence (deterministic code, no LLM)
"""))
cells.append(code('''
enec.run_sql(con, "SELECT * FROM asset_360 WHERE asset_id='A-001'").T
'''))
cells.append(code('''
enec.run_sql(con, """SELECT work_order_id, work_type, priority, status, created_date, due_date, problem_description
FROM work_orders WHERE asset_id='A-001' AND status IN ('OPEN','IN_PROGRESS','DEFERRED')
ORDER BY created_date DESC""")
'''))
cells.append(code('''
enec.run_sql(con, """SELECT inspection_id, inspection_date, inspection_type, severity, finding, recommendation, follow_up_required
FROM inspections WHERE asset_id='A-001' ORDER BY inspection_date DESC LIMIT 5""")
'''))
cells.append(code('''
enec.run_sql(con, """SELECT project_id, risk_id, risk_category, exposure_score, risk_status, evidence_basis
FROM a001_project_risk_360 ORDER BY exposure_score DESC LIMIT 6""")
'''))
cells.append(md("## Step 3. Predictive evidence: sensor trend and forecast"))
cells.append(code('''
by_month = enec.run_sql(con, """SELECT substr(hour_timestamp,1,7) AS month, ROUND(AVG(avg_vibration_mm_s),2) AS avg_vibration,
       ROUND(MAX(max_vibration_mm_s),2) AS max_vibration, ROUND(AVG(avg_temperature_c),1) AS avg_temp_c,
       SUM(anomaly_minutes) AS anomaly_minutes FROM a001_sensor_hourly_90d GROUP BY 1 ORDER BY 1""")
display(by_month)

fc = enec.forecast_vibration(hourly); future = fc.pop("_forecast_df")
print(json.dumps(fc, indent=2))

plt.figure(figsize=(13, 4))
tail = hourly.tail(24 * 14)
plt.plot(tail.hour_timestamp, tail.avg_vibration_mm_s, label="Last 14 days")
plt.plot(future.hour_timestamp, future.avg_vibration_mm_s, label="Forecast", color="#f5a623")
plt.legend(); plt.grid(alpha=.25); plt.title("A-001 vibration (mm/s)"); plt.show()
'''))
cells.append(md("""
**What the forecast does not prove:** It extrapolates a pattern in a synthetic series. It does not identify a cause, a failure mode or a time to failure.

## Step 4. Document evidence

Retrieve from several angles so the briefing does not depend on one lucky search.
"""))
cells.append(code('''
seen, hits = set(), []
for q in enec.DOC_QUERIES:
    for h in index.search(q, k=3):
        key = (h["doc_id"], h["chunk_no"])
        if key not in seen:
            seen.add(key); hits.append(h)
pd.DataFrame([{"doc_id": h["doc_id"], "status": h["status"], "version": h["version"], "score": round(h["score"], 3),
               "excerpt": h["text"][:90].replace("\\n", " ")} for h in hits]).sort_values("doc_id")
'''))
cells.append(md("""
## Step 5. Assemble the evidence packet

The packet keeps the three evidence types **separate**. Keeping them separate is how you avoid blurring a database fact, a model output and a document claim into one confident sentence.
"""))
cells.append(code('''
packet = enec.build_evidence_packet(con, index, hourly, docs)
print({k: (len(v) if hasattr(v, "__len__") else v) for k, v in packet.items()})
text = enec.packet_to_text(packet)
print("packet size:", len(text), "characters")
print(text[:1500])
'''))
cells.append(md("""
## Step 6. Generate the briefing

The model writes only from the packet, in the eight required sections.
"""))
cells.append(code('''
briefing = enec.generate_briefing(client, packet)
from IPython.display import Markdown
Markdown(briefing)
'''))
cells.append(md("""
## Step 7. Check the briefing (transparent, rule-based)

These checks are deliberately simple so you can read and extend them. They support the human reviewer. They do not replace review.
"""))
cells.append(code('''
checks = enec.check_briefing(briefing, docs)
checks
'''))
cells.append(md("""
### Optional: second opinion from an LLM judge using the course rubric (1-5 per dimension, max 25)
"""))
cells.append(code('''
verdict = enec.judge_briefing(client, briefing)
print(json.dumps(verdict, indent=2))
scores = verdict.get("scores", {})
if scores:
    print("Total:", sum(int(v) for v in scores.values()), "/ 25   (21-25 strong, 16-20 good, 11-15 partial, 5-10 needs remediation)")
'''))
cells.append(md("""
## Step 8. Your review (the human part)

Read your briefing as the qualified reviewer would. Fill in this table by hand. **The score you give matters more than the judge's.**

| Dimension | What to look for | Your score (1-5) |
|---|---|---|
| Problem understanding | Is the business question framed, not just answered technically? | |
| Data use | Are observations separated from interpretation? | |
| AI / RAG use | Right documents retrieved? Status and version respected? | |
| Evidence & explainability | Can you trace each claim to a table or document ID? | |
| Governance & human oversight | Is uncertainty kept? Is the final decision left to a human? | |
"""))
cells.append(code('''
# Save the briefing so you can attach it to your capstone submission
path = "/content/A001_review_briefing.md" if enec.os.path.isdir("/content") else "A001_review_briefing.md"
open(path, "w").write(briefing)
print("saved:", path)
try:
    from google.colab import files
    files.download(path)
except Exception:
    pass
'''))
cells.append(md("""
## Capstone tasks

1. **Break it on purpose.** Re-run Step 6 after removing the `Authority rules` line from `enec.BRIEFING_SYSTEM`. Which checks fail?
2. **Find an evidence gap.** Which question can the packet not answer (for example: cost of downtime, spare-parts lead time)? Add a retrieval query or table that might close the gap, or state it explicitly in section 6.
3. **Conflict hunt.** Compare the DRAFT cross-functional risk register with an APPROVED document. Do they disagree? Does your briefing say which one governs?
4. **Present** your briefing in 3 minutes: the question, the evidence, the limits, and the human next step.
"""))
save(cells, os.path.join(OUT, "Day4_01_Capstone_A001_Review_Briefing.ipynb"))

# =============================================================================== 02 app in colab
cells = [header("Day 4", "The A-001 Review App, Running Inside Colab", 45,
                "Wrap the capstone into a small web app (Gradio) that runs inside this Colab session. No separate hosting or deployment platform is needed.")]
cells += setup_cells(extra="gradio")
cells.append(md("""
## What you are building

A three-tab app on top of everything from Days 1-4:

| Tab | What it does |
|---|---|
| **Ask A-001** | The tool-calling agent from Day 3 (SQL + documents + forecast) with a visible tool trace |
| **Review briefing** | The Day 4 capstone: evidence packet, 8-section briefing and automatic checks |
| **Document register** | Which documents are APPROVED, DRAFT or SUPERSEDED |

A banner on every tab states the boundary: *decision support only, a qualified human decides.*

**Where it runs:** inside this Colab session. It stops when the session stops.
"""))
cells.append(code('''
import json, pandas as pd, gradio as gr

tables = enec.load_tables()
con    = enec.make_db(tables)
docs   = enec.load_documents(include_day4=True)
index  = enec.RAGIndex.build(client, docs)
hourly = tables["a001_sensor_hourly_90d"]
TOOLS, IMPLS = enec.build_a001_tools(con, index, hourly)

SYSTEM = f"""You are a reliability-review assistant for synthetic asset A-001.
Use sql_query for database facts, search_documents for procedures, policies and reports, forecast for the vibration trend.
{enec.SCHEMA_HINT}
Rules: only APPROVED documents are current authority; DRAFT is not authoritative; SUPERSEDED is historical only.
Cite document IDs in [brackets] and table names for database facts. Separate DATABASE, DOCUMENT and FORECAST evidence.
If evidence is missing, say so. You never authorise maintenance, shutdown or replacement; a qualified human decides."""
BANNER = "**Decision support only.** Synthetic training data. A qualified human reviewer owns every decision."
print("ready")
'''))
cells.append(md("## The three functions behind the tabs"))
cells.append(code('''
def ask_agent(question):
    if not question or not question.strip():
        return "Please type a question.", pd.DataFrame()
    final, trace, _ = enec.run_agent(client, question, SYSTEM, TOOLS, IMPLS, verbose=False)
    t = pd.DataFrame(trace)[["step", "tool", "status", "args"]] if trace else pd.DataFrame(columns=["step", "tool", "status", "args"])
    t["args"] = t["args"].astype(str).str.slice(0, 160)
    return final, t

def make_briefing():
    packet = enec.build_evidence_packet(con, index, hourly, docs)
    text = enec.generate_briefing(client, packet)
    return text, enec.check_briefing(text, docs)

def register():
    return pd.DataFrame([{k: d[k] for k in ("doc_id", "title", "status", "version", "date")} for d in docs]).sort_values(["status", "doc_id"])

# Test them here first, then wrap them in a UI
ans, trace = ask_agent("How many high-priority work orders are open for A-001?")
print(ans); trace
'''))
cells.append(md("""
## The user interface

`gr.Blocks` lays out components; each button calls one of the functions above.
"""))
cells.append(code('''
EXAMPLES = ["Which procedure is currently approved for A-001, and is the draft in force?",
            "How many work orders are open for A-001 and how many are high priority?",
            "Is A-001 vibration likely to keep rising over the next week? How reliable is that forecast?",
            "Prepare A-001 for human reliability review."]

with gr.Blocks(title="A-001 Review Assistant") as demo:
    gr.Markdown("# A-001 Review Assistant\\n" + BANNER)
    with gr.Tab("Ask A-001"):
        q = gr.Textbox(label="Your question", lines=2)
        gr.Examples(EXAMPLES, inputs=q)
        go = gr.Button("Ask", variant="primary")
        out = gr.Markdown()
        trace_df = gr.Dataframe(label="Tool trace (what the agent actually did)", wrap=True)
        go.click(ask_agent, q, [out, trace_df])
    with gr.Tab("Review briefing"):
        gr.Markdown("Builds the evidence packet, writes the 8-section briefing and runs the automatic checks (about 20-40 seconds).")
        b = gr.Button("Generate briefing", variant="primary")
        brief = gr.Markdown()
        checks = gr.Dataframe(label="Automatic checks", wrap=True)
        b.click(make_briefing, None, [brief, checks])
    with gr.Tab("Document register"):
        gr.Markdown("Only **APPROVED** documents are current authority.")
        reg = gr.Dataframe(value=register(), wrap=True)
print("UI built")
'''))
cells.append(md("""
## Launch

- `SHARE = False` (default): the app opens inside the notebook output. Safest.
- `SHARE = True`: Gradio creates a temporary public link so a room can open it on their own devices. **Anyone with the link can use your OpenAI key through the app.** Use it only for a live demo, then stop the cell.
"""))
cells.append(code('''
SHARE = False
demo.launch(share=SHARE, debug=False)
'''))
cells.append(md("""
## Before you show it to anyone

- [ ] Run each example question once and read the **tool trace**
- [ ] Generate the briefing once and read the checks
- [ ] Check your OpenAI usage dashboard for cost
- [ ] If you used `SHARE = True`, stop the cell when finished (Runtime menu, then Interrupt)

## Stop the app

Run `demo.close()` or stop the cell.
"""))
cells.append(code('''
# demo.close()
'''))
save(cells, os.path.join(OUT, "Day4_02_A001_Review_App_in_Colab.ipynb"))
print("day 4 built")

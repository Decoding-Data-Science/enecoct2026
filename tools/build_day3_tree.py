import os
from nbcommon import *

OUT = os.path.join(os.path.dirname(__file__), "..", "Day_3_Agentic_AI")

cells = [header("Day 3", "Machine Learning as an Agent Tool: a Decision Tree on Log Windows", 75,
    "Build a small decision tree that flags suspicious 15-minute log windows, judge it honestly, then give it to an agent as a read-only tool next to SQL, with a human review step.",
    needs_ai=False)]
cells[0].source = cells[0].source.replace("**Needs:** No API key needed for this notebook",
    "**Needs:** no key for Parts 1 to 5. An OpenAI key in Colab Secrets (`OPENAI_API_KEY`) for Part 6")
cells += setup_cells(extra="llama-index-core", need_ai=False)

cells.append(md("""
## Why a model, and why a tool

An LLM is good with language. It is a poor way to score 23,000 numeric rows. A small machine-learning model is the opposite: fast, repeatable and checkable on numbers, and unable to explain itself in words.

So we combine them. The **tree** scores log windows. The **agent** decides when to ask it, joins the result to asset priority and documents, and hands the finding to a person.

```
Question  ->  Agent  ->  tools: SQL | decision tree | human review queue  ->  evidence  ->  person decides
```

**Part 1** looks at the data. **Parts 2 to 4** build and judge the tree. **Part 5** turns it into a tool. **Part 6** lets an agent use it.
"""))

cells.append(md("## 1. The data: one row per asset per 15-minute window"))
cells.append(code("""
import pandas as pd, numpy as np, matplotlib.pyplot as plt, json
pd.set_option("display.width", 200); pd.set_option("display.max_columns", 30)
w = pd.read_csv(enec.ROOT / "data" / "security" / "security_log_windows.csv", parse_dates=["window_start"])
print(len(w), "windows |", w.window_start.min(), "to", w.window_start.max())
w.head(5)
"""))
cells.append(md("""
Each row counts what was logged for one asset's gateway in 15 minutes: failed logins, new-country logins, denied firewall flows, bytes sent out, commands without a change ticket, and so on. `is_attack` is the simulation's ground truth. In real life you would not have it, you would have analyst decisions.

**The accuracy trap first.** How many windows are attacks, and what would a model that always says *normal* score?
"""))
cells.append(code("""
share = w.is_attack.mean()
print(w.attack_type.value_counts().to_string())
print(f"\\nAttack share: {share:.1%}   |   accuracy of 'always normal': {1 - share:.1%}")
"""))
cells.append(md("""
That model scores about 98% and catches nothing. So we judge by **recall** (of the real attacks, how many did we catch) and **precision** (of the alarms, how many were real), never accuracy alone.
"""))

cells.append(md("""
## 2. Features and a fair split

**Features** are the input columns. **Label** is what we predict. We split by **time**: train on the first 21 days, test on the last 9. A random split would put neighbouring windows of the same attack on both sides and flatter the model.
"""))
cells.append(code("""
FEATURES = ["auth_failures","auth_successes","distinct_users","distinct_src_ips","new_country_logins","logins_without_mfa",
            "flows_total","flows_denied","distinct_dst_ports","distinct_flow_sources","external_flows","bytes_out_kb",
            "commands_total","write_commands","unapproved_commands","off_hours"]
CUT = pd.Timestamp("2026-08-17")
train, test = w[w.window_start < CUT], w[w.window_start >= CUT]
print("train:", len(train), "windows,", int(train.is_attack.sum()), "attacks")
print("test: ", len(test), "windows,", int(test.is_attack.sum()), "attacks")
"""))

cells.append(md("""
## 3. Train a decision tree and read it

A decision tree is a set of yes/no questions on the features. It learns the questions and thresholds. `max_depth` limits how many questions in a row. `class_weight="balanced"` tells it that missing a rare attack costs more than a false alarm.
"""))
cells.append(code("""
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, recall_score, precision_score

tree = DecisionTreeClassifier(max_depth=5, class_weight="balanced", random_state=42).fit(train[FEATURES], train.is_attack)
print(export_text(tree, feature_names=FEATURES, max_depth=3))
"""))
cells.append(code("""
plt.figure(figsize=(16, 7))
plot_tree(tree, feature_names=FEATURES, class_names=["normal", "attack"], filled=True, max_depth=3, fontsize=8, impurity=False, proportion=True)
plt.title("The first three levels of the tree"); plt.show()
"""))
cells.append(md("""
Read the top of the tree like rules. A security lead can challenge every one of them. That is why a tree is a good first model, and why it is a good tool for an agent: the reason for a flag can be shown.
"""))

cells.append(md("## 4. Judge it on days it has not seen"))
cells.append(code("""
pred = tree.predict(test[FEATURES])
print(classification_report(test.is_attack, pred, target_names=["normal", "attack"]))
ConfusionMatrixDisplay(confusion_matrix(test.is_attack, pred), display_labels=["normal", "attack"]).plot(cmap="Blues")
plt.title("Test set: last 9 days"); plt.show()
"""))
cells.append(md("""
Look at the **attack** row. *Recall* is the share of real attacks caught. *Precision* is the share of alarms that were real. The confusion matrix shows the counts: top-right are false alarms, bottom-left are missed attacks.

**Choose the depth on unseen data.** Compare a few depths:
"""))
cells.append(code("""
rows = []
for d in [2, 3, 4, 5, 6, 8, None]:
    m = DecisionTreeClassifier(max_depth=d, class_weight="balanced", random_state=42).fit(train[FEATURES], train.is_attack)
    p = m.predict(test[FEATURES])
    rows.append({"max_depth": d, "recall": round(recall_score(test.is_attack, p), 2), "precision": round(precision_score(test.is_attack, p, zero_division=0), 2),
                 "alarms": int(p.sum()), "leaves": m.get_n_leaves()})
pd.DataFrame(rows)
"""))
cells.append(md("Pick the simplest depth that holds up. Deeper trees can memorise the training days: recall may rise while precision falls. Then see which attack types the tree misses and which features it relied on."))
cells.append(code("""
t2 = test.assign(pred=pred)
by_type = (t2[t2.is_attack == 1].groupby("attack_type").agg(windows=("pred", "size"), caught=("pred", "sum"))
           .assign(recall=lambda d: (d.caught / d.windows).round(2)))
display(by_type)
imp = pd.Series(tree.feature_importances_, index=FEATURES).sort_values().tail(8)
imp.plot.barh(title="What the tree relied on", color="#2a9d8f"); plt.show()
"""))
cells.append(md("""
Quiet attacks, such as a single off-hours vendor session, are the ones a threshold-style model misses. Note the answer: **the tree is a triage aid, not a verdict.** It prepares a list for an analyst.

### Features, predictions and outputs, in one line each
- **Features:** the 16 numbers counted from logs for each window.
- **Prediction:** `tree.predict(X)` gives 0 or 1.
- **Score:** `tree.predict_proba(X)[:, 1]` gives a number between 0 and 1 that we can threshold or rank.
- **Explanation:** the path of yes/no questions that led to the score.
"""))

cells.append(md("""
## 5. Turn the model into a tool

An agent can only use what we give it as a **function with a description**. We write two read-only tools and one that only records a request for human review:

| Tool | What it does | Can it change anything? |
|---|---|---|
| `list_flagged_assets` | Which assets had flagged windows in the last N days, joined to the combined priority list | No, read-only |
| `score_asset_windows` | The flagged windows for one asset, with the rule path that fired | No, read-only |
| `request_human_review` | Adds a line to a review queue for a person | Writes to a list only. No action on any system |

First, score every window with the model and prepare the join to asset priority.
"""))
cells.append(code("""
w["p_attack"] = tree.predict_proba(w[FEATURES])[:, 1]
w["flag"] = (w.p_attack >= 0.5).astype(int)
prio = pd.read_csv(enec.ROOT / "data" / "security" / "asset_priority_view.csv")[
    ["asset_id", "Asset_Criticality", "Priority_Rank", "Priority_Band", "Open_Security_Issues", "Ops_Attention_Flag"]]
AS_OF = w.window_start.max()
print("Scored", len(w), "windows. Flagged:", int(w.flag.sum()), "| data as of", AS_OF)

def rule_path(row_values, last=3):
    \"\"\"The yes/no questions the tree asked for one window (the last few are the most specific).\"\"\"
    t = tree.tree_; node = 0; steps = []
    while t.children_left[node] != -1:
        f, thr = t.feature[node], t.threshold[node]
        if row_values[f] <= thr: steps.append(f"{FEATURES[f]} <= {thr:.1f}"); node = t.children_left[node]
        else: steps.append(f"{FEATURES[f]} > {thr:.1f}"); node = t.children_right[node]
    return steps[-last:]

def list_flagged_assets(days: int = 7, top: int = 10) -> str:
    \"\"\"Assets with windows flagged by the decision tree in the last N days, joined to the combined priority list.\"\"\"
    days, top = max(1, min(int(days), 30)), max(1, min(int(top), 25))
    recent = w[(w.window_start > AS_OF - pd.Timedelta(days=days)) & (w.flag == 1)]
    g = (recent.groupby("asset_id").agg(flagged_windows=("flag", "sum"), max_score=("p_attack", "max"), last_flag=("window_start", "max"))
         .reset_index().merge(prio, on="asset_id", how="left").sort_values(["flagged_windows", "max_score"], ascending=False).head(top))
    g["max_score"] = g.max_score.round(2); g["last_flag"] = g.last_flag.astype(str)
    return json.dumps({"as_of": str(AS_OF), "days": days, "rows": g.to_dict("records"),
                       "note": "Model flags are triage evidence, not confirmed attacks. Precision is limited. A person decides."}, default=str)

def score_asset_windows(asset_id: str, days: int = 7) -> str:
    \"\"\"Flagged 15-minute windows for one asset in the last N days, with the rule path behind each flag.\"\"\"
    days = max(1, min(int(days), 30))
    a = w[(w.asset_id == asset_id) & (w.window_start > AS_OF - pd.Timedelta(days=days))]
    fl = a[a.flag == 1].sort_values("p_attack", ascending=False).head(5)
    out = [{"window_start": str(r.window_start), "score": round(float(r.p_attack), 2), "why": rule_path(r[FEATURES].to_numpy(dtype=float))} for _, r in fl.iterrows()]
    return json.dumps({"asset_id": asset_id, "days": days, "windows_scored": int(len(a)), "flagged": int(a.flag.sum()), "top_flags": out,
                       "note": "Triage evidence from a simulated data set. Not an incident finding."}, default=str)

REVIEW_QUEUE = []
def request_human_review(asset_id: str, reason: str) -> str:
    \"\"\"Record a request for a person to review an asset. This does not change any system.\"\"\"
    REVIEW_QUEUE.append({"asset_id": asset_id, "reason": reason[:300], "status": "waiting for a person"})
    return json.dumps({"queued": True, "position": len(REVIEW_QUEUE), "note": "A person will review. No action has been taken on any system."})

print(json.dumps(json.loads(list_flagged_assets(7, 5)), indent=1)[:1800])
"""))
cells.append(md("""
**Check the tool yourself before any agent uses it.** Does the top asset have more flagged windows than the next one? Does the rule path look sensible? An agent will trust this output, so you must.
"""))
cells.append(code("""
top = json.loads(list_flagged_assets(7, 5))["rows"]
first = top[0]["asset_id"]
print("Top flagged asset:", first)
print(json.dumps(json.loads(score_asset_windows(first, 7)), indent=1)[:1500])
"""))

cells.append(md("""
## The same function as a LlamaIndex tool

The plan for this course uses **LlamaIndex** for agent work. In LlamaIndex a tool is a Python function plus a name and description, the same idea as above. `FunctionTool` reads the parameters from the function's type hints.
"""))
cells.append(code("""
from llama_index.core.tools import FunctionTool

li_tools = [FunctionTool.from_defaults(fn=list_flagged_assets, name="list_flagged_assets",
                description="Assets with decision-tree flagged log windows in the last N days, with criticality and priority. Read-only."),
            FunctionTool.from_defaults(fn=score_asset_windows, name="score_asset_windows",
                description="Flagged 15-minute windows for one asset with the rule path behind each flag. Read-only."),
            FunctionTool.from_defaults(fn=request_human_review, name="request_human_review",
                description="Queue an asset for human review. Does not change any system.")]
for t in li_tools:
    print(t.metadata.name, "->", list(t.metadata.get_parameters_dict()["properties"]))
out = li_tools[0].call(days=7, top=3)
print(str(out.content)[:400])
"""))

cells.append(md("""
## 6. An agent that uses the tree, SQL and a human gate

Now the agent. It gets four tools: SQL on the asset tables, the two model tools and the review queue. The instructions state the rules: only use tool results, say what is uncertain, never claim an attack is confirmed, and never act on a system.
"""))
cells.append(code("""
client = enec.get_client()
MODEL = enec.pick_model(client)
tables = enec.load_tables(); con = enec.make_db(tables)

def sql_query(query: str) -> str:
    return enec.df_to_text(enec.run_sql(con, query))

specs = [
    enec.tool_spec("sql_query", "Run ONE read-only SELECT on the Asset 360 and security tables (asset_360, asset_priority_view, asset_security, security_alerts, security_incidents ...).",
                   {"query": {"type": "string", "description": "A single SQLite SELECT statement."}}),
    enec.tool_spec("list_flagged_assets", "Assets with decision-tree flagged log windows in the last N days, joined to criticality and the combined priority list. Read-only.",
                   {"days": {"type": "integer", "description": "1 to 30, default 7"}, "top": {"type": "integer", "description": "1 to 25, default 10"}}, []),
    enec.tool_spec("score_asset_windows", "Flagged 15-minute windows for ONE asset with the rule path behind each flag. Read-only.",
                   {"asset_id": {"type": "string"}, "days": {"type": "integer"}}, ["asset_id"]),
    enec.tool_spec("request_human_review", "Queue an asset for a person to review. Records a request only. Cannot change any system.",
                   {"asset_id": {"type": "string"}, "reason": {"type": "string"}}),
]
IMPLS = {"sql_query": sql_query, "list_flagged_assets": list_flagged_assets, "score_asset_windows": score_asset_windows, "request_human_review": request_human_review}

SYSTEM = (
    "You support a plant security reviewer. Use the tools; never answer from memory about this plant. "
    "Decision-tree flags are triage evidence from a simulated data set, not confirmed attacks. "
    "Report what the tools returned, name what is uncertain, and use request_human_review for anything that needs a person. "
    "You cannot block, isolate, patch, close or approve anything. If asked to, say you have no such tool and a person must decide.")

QUESTION = ("Which Critical or High assets had flagged windows in the last 7 days, how do they rank on the combined priority list, "
            "and what should a person review first? Queue the top one for review.")
answer, trace, _ = enec.run_agent(client, QUESTION, SYSTEM, specs, IMPLS, model=MODEL, max_steps=8)
print("\\n" + answer)
print("\\nReview queue:", REVIEW_QUEUE)
"""))
cells.append(md("""
**Read the trace.** Which tools did the agent call, in which order? Did it use the tree's output or only SQL? Did it say the flags are not confirmed attacks? Compare with `list_flagged_assets` run by hand above. If they disagree, the agent is wrong, not the tool.

### The boundary test
Ask the agent for something it must not do. It has no tool for it, so a good run refuses and hands the decision to a person.
"""))
cells.append(code("""
answer2, trace2, _ = enec.run_agent(client, "Isolate asset A-001 from the network now and close its open incident.", SYSTEM, specs, IMPLS, model=MODEL, max_steps=4)
print(answer2)
print("Tools called:", [t["tool"] for t in trace2])
print("Expected: no isolating or closing happens. At most a review request is queued.")
"""))
cells.append(md("""
### The same agent in LlamaIndex (optional, needs your key)

Same tools, different framework. This cell is wrapped so that a version or network problem prints a message instead of stopping the notebook. If it works, compare the two traces.
"""))
cells.append(code("""
try:
    # LlamaIndex agent, using the tools from the previous section
    %pip install -q llama-index-llms-openai
    from llama_index.core.agent.workflow import FunctionAgent
    from llama_index.llms.openai import OpenAI as LIOpenAI
    li_agent = FunctionAgent(tools=li_tools + [FunctionTool.from_defaults(fn=sql_query, name="sql_query", description="ONE read-only SELECT on the Asset 360 and security tables.")],
                             llm=LIOpenAI(model=MODEL, api_key=client.api_key), system_prompt=SYSTEM)
    resp = await li_agent.run(QUESTION)
    print(str(resp)[:1500])
except Exception as e:
    print("LlamaIndex agent cell did not run:", type(e).__name__, str(e)[:300])
    print("The loop above already showed the same idea. Carry on.")
"""))

cells.append(md("""
## Guardrails summary

- The model and the tools are **read-only** except the review queue, which only records a request.
- Every tool **clips its inputs** (days 1 to 30, top 1 to 25).
- Every output carries a **note** that flags are triage evidence.
- The agent has a **step limit** and a **system prompt** that forbids claiming confirmation or acting.
- The decision stays with a **person**.

## Exercise

1. Change `max_depth` to 3 and to 8. Re-run Parts 4 and 5. How do recall, precision and the flagged assets change? Which depth would you give an analyst, and why?
2. Raise the score threshold in `w["flag"]` from 0.5 to 0.8. How many flags remain? Which attack types now go missing?
3. Add a fourth model-based tool, `explain_window(window_id)`, that returns the rule path for one window. Does the agent use it when asked "why was this flagged?"
4. Role task: write one paragraph for your job. Which decision would you give the tree's flags to, who reviews them, and what would make you stop trusting it?
"""))

save(cells, os.path.join(OUT, "Day3_02_Decision_Tree_as_an_Agent_Tool.ipynb"))
print("ok")

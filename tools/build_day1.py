import os
from nbcommon import *

OUT = os.path.join(os.path.dirname(__file__), "..", "Day_2_GenAI_and_RAG")
EXT = os.path.join(os.path.dirname(__file__), "..", "Optional_Colab_Extensions")
os.makedirs(OUT, exist_ok=True); os.makedirs(EXT, exist_ok=True)

# =============================================================================== 00 setup + first prompts
cells = [header("Day 2", "Colab Setup and Your First Prompts in Code", 40,
                "Set up Colab and OpenAI once. Then re-run, in Python, the structured prompts you practised in Copilot on Day 1: grounding, structure, examples and boundaries.")]
cells.append(md("""
## Where this fits

**Day 1** you used Microsoft Copilot and a structured prompt (role, task, context, evidence, constraints, format, check) on the asset workbooks. **Today** the same ideas run in code, so an application can use them:

| Day 1 in Copilot | Day 2 in Python |
|---|---|
| Role and constraints | the **system** message |
| Evidence (a table or a document) | text you put in the prompt, later **retrieved** by RAG |
| Format | a **structured response** (JSON) your code can read |
| Check | tests your code can run |

This first notebook takes about 40 minutes: set up once, then six short experiments on one asset record.
"""))
cells.append(md("""
## Step 1. Put your OpenAI key in Colab Secrets (do this once)

1. Click the **key icon** in the left sidebar of Colab.
2. Click **Add new secret**. Name: `OPENAI_API_KEY`. Value: your key.
3. Switch **Notebook access** ON for this notebook.
4. Never paste the key into a code cell. Never share a notebook with the key typed into it.
"""))
cells += setup_cells()
cells.append(code('''
# First call. If this prints a sentence, your setup works.
print(enec.ask(client, "In one sentence, say hello to the ENEC training group."))
'''))
cells.append(md("""
## The same prompting ideas, now in code

A prompt is an interface contract between your code and the model. We will test five ideas on the **same asset record** (compare with the Day 1 guide, `Day_1_Copilot_and_Data_Understanding/PROMPT_ENGINEERING_GUIDE.md`):

1. No context vs grounded context
2. Prompt anatomy (role, task, context, format, constraints)
3. Structured output (JSON your code can use)
4. Few-shot examples
5. Boundaries (what the model must not do)
"""))
cells.append(code('''
import pandas as pd, json
tables = enec.load_tables()
a360 = tables["asset_360"]
row = a360[a360.asset_id == "A-001"].iloc[0].to_dict()
row
'''))
cells.append(md("""
## Experiment 1. Ask without context

The model has never seen this synthetic asset. Watch what it does.
"""))
cells.append(code('''
q = "What is the current health score and recommended action for asset A-001?"
print(enec.ask(client, q))
'''))
cells.append(md("""
**Discuss:** Did it admit it does not know, or did it invent something plausible? An invented but confident answer is a *hallucination*.

## Experiment 2. Same question, grounded in the record
"""))
cells.append(code('''
grounded = f"""Use ONLY this record to answer.

RECORD (from table asset_360):
{json.dumps(row, default=str, indent=2)}

QUESTION: {q}"""
print(enec.ask(client, grounded))
'''))
cells.append(md("""
## Experiment 3. Prompt anatomy

A reliable prompt has five parts. Name them in your prompt and the output becomes predictable.
"""))
cells.append(code('''
ROLE        = "You are a reliability engineering analyst supporting a qualified human reviewer."
TASK        = "Summarise the current condition of asset A-001 for a morning stand-up."
CONTEXT     = json.dumps(row, default=str)
FORMAT      = "Exactly three bullet points: Status, Why it matters, Suggested human next step. Max 25 words each."
CONSTRAINTS = "Use only the CONTEXT. If something is not in the CONTEXT, write 'not in the data'. Do not authorise any work."

prompt = f"""ROLE: {ROLE}
TASK: {TASK}
CONTEXT: {CONTEXT}
FORMAT: {FORMAT}
CONSTRAINTS: {CONSTRAINTS}"""
print(enec.ask(client, prompt))
'''))
cells.append(md("""
**Try it:** change `FORMAT` to a table, then to one sentence. Change `CONSTRAINTS` and see what breaks.

## Experiment 4. Structured output (JSON your code can use)

Free text is for people. Code needs structure. Ask for JSON and parse it.
"""))
cells.append(code('''
wo = tables["work_orders"]
open_wo = wo[(wo.asset_id == "A-001") & (wo.status.isin(["OPEN", "IN_PROGRESS", "DEFERRED"]))]
wo_text = open_wo[["work_order_id", "work_type", "priority", "created_date", "problem_description"]].to_csv(index=False)

system = "You convert work-order tables into JSON. Return a JSON object: {\\"items\\": [{\\"work_order_id\\": str, \\"priority\\": str, \\"issue_type\\": one of [VIBRATION, TEMPERATURE, NOISE, LEAKAGE, CALIBRATION, PREVENTIVE, OTHER], \\"needs_urgent_attention\\": bool}]}"
raw = enec.ask(client, wo_text, system=system, json_mode=True)
items = json.loads(raw).get("items", [])
pd.DataFrame(items)
'''))
cells.append(md("""
## Experiment 5. Few-shot examples

Show the model 3 labelled examples, then let it label the rest. We label every distinct problem description in the full work-order table (1,500 rows).
"""))
cells.append(code('''
descs = sorted(wo.problem_description.dropna().unique().tolist())
print(len(descs), "distinct descriptions")

LABELS = ["VIBRATION", "TEMPERATURE", "NOISE", "LEAKAGE", "CALIBRATION", "PREVENTIVE", "OTHER"]
examples = """Examples:
"Abnormal vibration observed during routine monitoring." -> VIBRATION
"Temperature trend exceeded expected operating band." -> TEMPERATURE
"Preventive maintenance interval reached." -> PREVENTIVE"""

system = (f"Label each description with one of {LABELS}. {examples}\\n"
          "Return JSON: {\\"labels\\": {\\"0\\": LABEL, \\"1\\": LABEL, ...}} using the numbers given.")
numbered = "\\n".join(f"{i}: {d}" for i, d in enumerate(descs))
out = json.loads(enec.ask(client, numbered, system=system, json_mode=True)).get("labels", {})
labelled = pd.DataFrame({"description": descs, "label": [out.get(str(i), "UNKNOWN") for i in range(len(descs))]})
labelled
'''))
cells.append(code('''
# Use the labels: how many work orders per label, and how many are still open?
lab_map = dict(zip(labelled.description, labelled.label))
wo2 = wo.assign(label=wo.problem_description.map(lab_map))
wo2.groupby("label").agg(work_orders=("work_order_id", "count"),
                         open_items=("status", lambda s: s.isin(["OPEN", "IN_PROGRESS", "DEFERRED"]).sum()))
'''))
cells.append(md("""
## Experiment 6. Boundaries

The most important prompt is the one that says what the model must **not** do.
"""))
cells.append(code('''
BOUNDARY = ("You support a qualified human reviewer. You never authorise maintenance, shutdown or replacement. "
            "When asked to decide, explain what evidence exists, what is missing, and who should decide.")
risky = f"""RECORD: {json.dumps(row, default=str)}
A manager says: 'Just tell us. Should we shut down A-001 right now and replace the pump?'"""

print("--- without boundary ---")
print(enec.ask(client, risky))
print("\\n--- with boundary ---")
print(enec.ask(client, risky, system=BOUNDARY))
'''))
cells.append(md("""
## Takeaways

- **Ground it:** put the facts in the prompt, or the model will fill gaps with guesses.
- **Name the parts:** role, task, context, format, constraints.
- **Ask for JSON** when code consumes the answer, and handle missing keys.
- **Show examples** when labels must be consistent.
- **Set boundaries** and keep a human in charge of consequential decisions.

## Exercise

Write a prompt that produces a 2-line shift-handover note for the **three lowest-health assets** in `asset_360`. Use `a360.sort_values("health_score").head(3)` as context, force JSON output, and add one constraint you think the night shift would want.
"""))
save(cells, os.path.join(OUT, "Day2_00_Colab_Setup_and_First_Prompts.ipynb"))

# =============================================================================== 01 asset 360 explore
cells = [header("Optional extension 1", "Asset 360: Explore the Data with SQL", 50,
                "Optional homework or early-finisher work. Load the Asset 360 tables, query them with SQL, check data quality and chart what matters.")]
cells += setup_cells(pip=True)
cells.append(md("""
## 1. Load the tables

Each CSV is one table. Each file is read with pandas and also load them into an in-memory **SQLite** database so we can use real SQL.
"""))
cells.append(code('''
import pandas as pd, matplotlib.pyplot as plt
tables = enec.load_tables()
con = enec.make_db(tables)

inventory = pd.DataFrame({"table": list(tables), "rows": [len(t) for t in tables.values()],
                          "columns": [len(t.columns) for t in tables.values()]})
inventory
'''))
cells.append(md("## 2. First SQL queries\n\n`enec.run_sql` runs one read-only `SELECT` and returns a DataFrame."))
cells.append(code('''
# The focus asset
enec.run_sql(con, "SELECT * FROM assets WHERE asset_id = 'A-001'")
'''))
cells.append(code('''
# Current 360-degree view of A-001
enec.run_sql(con, "SELECT * FROM asset_360 WHERE asset_id = 'A-001'").T
'''))
cells.append(code('''
# Which assets look weakest right now?
enec.run_sql(con, """
SELECT asset_id, asset_name, criticality, system_name, health_score, risk_level,
       open_work_orders, high_priority_open_work
FROM asset_360
ORDER BY health_score ASC
LIMIT 10""")
'''))
cells.append(md("## 3. GROUP BY and JOIN"))
cells.append(code('''
# Health and workload by plant system
enec.run_sql(con, """
SELECT system_name,
       COUNT(*)                        AS assets,
       ROUND(AVG(health_score), 1)     AS avg_health,
       SUM(open_work_orders)           AS open_work_orders,
       SUM(high_priority_open_work)    AS high_priority_open
FROM asset_360
GROUP BY system_name
ORDER BY avg_health ASC""")
'''))
cells.append(code('''
# JOIN: A-001 work orders with the asset and its system
enec.run_sql(con, """
SELECT w.work_order_id, w.work_type, w.priority, w.status, w.created_date,
       a.asset_name, s.system_name
FROM work_orders w
JOIN assets  a ON a.asset_id  = w.asset_id
JOIN systems s ON s.system_id = a.system_id
WHERE w.asset_id = 'A-001' AND w.status IN ('OPEN','IN_PROGRESS','DEFERRED')
ORDER BY CASE w.priority WHEN 'URGENT' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END, w.created_date""")
'''))
cells.append(code('''
# Inspections that need follow-up
enec.run_sql(con, """
SELECT inspection_id, inspection_date, inspection_type, severity, finding, recommendation
FROM inspections
WHERE asset_id = 'A-001'
ORDER BY inspection_date DESC""")
'''))
cells.append(code('''
# The A-001 story in time order (last 12 events)
enec.run_sql(con, "SELECT event_date, event_type, event_id, event_title FROM a001_event_timeline ORDER BY event_date DESC LIMIT 12")
'''))
cells.append(md("## 4. Charts"))
cells.append(code('''
a360 = tables["asset_360"]
fig, ax = plt.subplots(1, 2, figsize=(13, 4))
a360.groupby("risk_level").size().reindex(["LOW", "MEDIUM", "HIGH"]).fillna(0).plot.bar(ax=ax[0], color="#22d3ee")
ax[0].set_title("Assets by risk level"); ax[0].set_xlabel(""); ax[0].set_ylabel("assets")
a360.groupby("system_name").open_work_orders.sum().sort_values().plot.barh(ax=ax[1], color="#8b5cf6")
ax[1].set_title("Open work orders by system"); ax[1].set_ylabel("")
plt.tight_layout(); plt.show()
'''))
cells.append(md("## 5. Data quality checks before you trust any model"))
cells.append(code('''
checks = []
for name, df in tables.items():
    checks.append({"table": name, "rows": len(df), "duplicate_rows": int(df.duplicated().sum()),
                   "columns_with_nulls": int((df.isna().sum() > 0).sum())})
pd.DataFrame(checks)
'''))
cells.append(code('''
# Domain checks: are the values what we expect?
print("Priorities:", sorted(tables["work_orders"].priority.unique()))
print("Statuses  :", sorted(tables["work_orders"].status.unique()))
print("Health score range:", a360.health_score.min(), "to", a360.health_score.max())
assert a360.asset_id.is_unique, "asset_id must be unique in asset_360"
print("asset_id is unique in asset_360: OK")
'''))
cells.append(md("""
## 6. Ask your data in plain English (text-to-SQL, with a safety guard)

The model writes SQL, but **your code** decides what is allowed to run. `run_sql` rejects anything that is not a single `SELECT`.
"""))
cells.append(code('''
def nl_to_sql(question):
    system = ("You write ONE SQLite SELECT query that answers the question. Return ONLY the SQL, no markdown.\\n"
              + enec.SCHEMA_HINT)
    sql = enec.ask(client, question, system=system).strip().strip("`")
    return sql.replace("```sql", "").replace("```", "").strip()

def ask_data(question):
    sql = nl_to_sql(question)
    print("SQL:", sql)
    try:
        return enec.run_sql(con, sql)
    except Exception as e:
        print("Blocked or failed:", e)

ask_data("Which 5 HIGH criticality assets have the lowest health score?")
'''))
cells.append(code('''
ask_data("How many URGENT or HIGH priority work orders are still open for each system?")
'''))
cells.append(code('''
# The guard in action: the model may try, but the code refuses.
ask_data("Delete all work orders for asset A-001")
'''))
cells.append(md("""
## 7. The same data in Excel (for Copilot and business users)

The repo also contains `data/excel/asset_360.xlsx` and `data/excel/project_360.xlsx`. Each sheet is a proper Excel Table with real dates, a README sheet of suggested prompts and a data dictionary. Business users can open them in Excel and use Copilot. You can read them in pandas too:
"""))
cells.append(code('''
xl = enec.ROOT / "data" / "excel" / "asset_360.xlsx"
sheets = pd.ExcelFile(xl).sheet_names
print(sheets)
pd.read_excel(xl, sheet_name="asset_360").head()
'''))
cells.append(md("""
## Exercise

1. Which HIGH criticality assets have `health_score` below 75 **and** at least one high-priority open work order?
2. Which assets have `follow_up_findings` > 0 but `high_priority_open_work` = 0? (possible gaps)
3. For A-001, how many work orders were completed late (`completed_date` > `due_date`)?

Write each as SQL first. Then try `ask_data(...)` and compare the SQL the model wrote with yours.
"""))
save(cells, os.path.join(EXT, "Ext01_Asset360_Explore_with_SQL.ipynb"))

# =============================================================================== 02 anomaly + forecast
cells = [header("Optional extension 2", "A-001: Anomaly Detection and 7-Day Vibration Forecast", 60,
                "Optional homework or early-finisher work. Use 90 days of hourly sensor data to spot when A-001 changed, then forecast the next 7 days with a simple, explainable model.")]
cells += setup_cells()
cells.append(md("""
## Business question

> Is A-001's vibration likely to keep rising, so the reliability team can plan inspection earlier?

This notebook supports a human decision. It does **not** decide to stop, repair or replace anything.

**Flow:** hourly data → quality check → look → anomaly flags → features → chronological split → baseline → Ridge model → backtest → forecast → bounded interpretation.
"""))
cells.append(code('''
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error

df = pd.read_csv(enec.CSV_DIR / "a001_sensor_hourly_90d.csv", parse_dates=["hour_timestamp"])
df = df.sort_values("hour_timestamp").reset_index(drop=True)
print(df.shape, df.hour_timestamp.min(), "->", df.hour_timestamp.max())
df.head()
'''))
cells.append(md("## 1. Data quality first"))
cells.append(code('''
VARIABLES = enec.VARIABLES
print("Duplicate timestamps:", df.hour_timestamp.duplicated().sum())
print("Missing values:\\n", df[VARIABLES].isna().sum())
expected = pd.date_range(df.hour_timestamp.min(), df.hour_timestamp.max(), freq="h")
print("Missing hours:", len(expected.difference(df.hour_timestamp)))
print("Hours with sensor quality issues:", int((df.quality_issue_minutes > 0).sum()))
'''))
cells.append(md("## 2. Look at the pattern, not just the latest value"))
cells.append(code('''
first_anom = df.loc[df.anomaly_minutes > 0, "hour_timestamp"].min()
fig, ax = plt.subplots(2, 1, figsize=(14, 7), sharex=True)
ax[0].plot(df.hour_timestamp, df.avg_vibration_mm_s, color="#22d3ee"); ax[0].set_ylabel("Vibration (mm/s)")
ax[1].plot(df.hour_timestamp, df.avg_temperature_c, color="#f5a623"); ax[1].set_ylabel("Temperature (C)")
for a in ax:
    a.grid(alpha=.25)
    if pd.notna(first_anom):
        a.axvline(first_anom, color="red", ls="--", alpha=.6)
ax[0].set_title("A-001 hourly averages (red line = first hour with anomaly minutes)")
plt.tight_layout(); plt.show()
print("First hour with anomaly minutes:", first_anom)
'''))
cells.append(code('''
df[VARIABLES].corr().round(2)   # correlation is not causation: it only shows what moves together
'''))
cells.append(md("""
## 3. Simple anomaly detection

Two beginner-friendly ideas:

1. **Baseline z-score:** how far is each hour from the first 45 days (a "normal" window)?
2. **Isolation Forest:** an unsupervised model that isolates unusual combinations of sensors.
"""))
cells.append(code('''
base = df.iloc[: 24 * 45]
mu, sd = base.avg_vibration_mm_s.mean(), base.avg_vibration_mm_s.std()
df["vib_z"] = (df.avg_vibration_mm_s - mu) / sd
df["z_flag"] = df.vib_z.abs() > 4

from sklearn.ensemble import IsolationForest
iso = IsolationForest(contamination=0.05, random_state=42)
df["iso_flag"] = iso.fit_predict(df[VARIABLES]) == -1

print("z-score flags  :", int(df.z_flag.sum()), "hours")
print("IsolationForest:", int(df.iso_flag.sum()), "hours")
print("First z-flag   :", df.loc[df.z_flag, "hour_timestamp"].min())

plt.figure(figsize=(14, 4))
plt.plot(df.hour_timestamp, df.avg_vibration_mm_s, color="#8b5cf6", lw=1)
plt.scatter(df.loc[df.z_flag, "hour_timestamp"], df.loc[df.z_flag, "avg_vibration_mm_s"], s=8, color="red", label="z-score flag")
plt.title("Vibration with baseline z-score flags"); plt.legend(); plt.grid(alpha=.25); plt.show()
'''))
cells.append(md("""
**Discuss:** A flag is a *question*, not an answer. What would you check before deciding the pump has a problem? (Sensor quality, recent maintenance, operating state, other sensors.)

## 4. Time-series features

A normal regression model does not understand time. We give it a little memory: the value 1 hour ago, 24 hours ago, the 24-hour rolling mean, and the hour of day / day of week as sine and cosine.
"""))
cells.append(code('''
import inspect
print(inspect.getsource(enec.make_features))
'''))
cells.append(code('''
model_df, FEATURES = enec.make_features(df)
print(len(model_df), "rows,", len(FEATURES), "features")
'''))
cells.append(md("""
## 5. Chronological split (never shuffle a time series)

We keep the **last 7 days (168 hours)** completely unseen for the test.
"""))
cells.append(code('''
H = 24 * 7
train, test = model_df.iloc[:-H], model_df.iloc[-H:]
print("train rows:", len(train), "| test rows:", len(test))
print("test period:", test.hour_timestamp.min(), "->", test.hour_timestamp.max())
'''))
cells.append(md("## 6. A baseline to beat: \"next week looks like yesterday\""))
cells.append(code('''
y_true = test.avg_vibration_mm_s.to_numpy()
baseline = np.tile(train.avg_vibration_mm_s.iloc[-24:].to_numpy(), 7)
base_mae = mean_absolute_error(y_true, baseline)
base_rmse = np.sqrt(mean_squared_error(y_true, baseline))
print(f"Baseline  MAE {base_mae:.3f}  RMSE {base_rmse:.3f}")
'''))
cells.append(md("## 7. Multivariate Ridge model, backtested on the unseen week"))
cells.append(code('''
model = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(train[FEATURES], train[VARIABLES])
history = df[df.hour_timestamp < test.hour_timestamp.min()]
back = enec.recursive_forecast(model, history, H)

mae = mean_absolute_error(y_true, back.avg_vibration_mm_s)
rmse = np.sqrt(mean_squared_error(y_true, back.avg_vibration_mm_s))
print(f"Ridge     MAE {mae:.3f}  RMSE {rmse:.3f}   (baseline MAE {base_mae:.3f})")

plt.figure(figsize=(14, 4.5))
plt.plot(test.hour_timestamp, y_true, label="Actual")
plt.plot(back.hour_timestamp, back.avg_vibration_mm_s, label="Ridge backtest")
plt.plot(test.hour_timestamp, baseline, label="Repeat-yesterday baseline", alpha=.6)
plt.title("A-001 vibration: 7-day backtest"); plt.legend(); plt.grid(alpha=.25); plt.show()
'''))
cells.append(md("""
**Read the metrics honestly.** MAE is the average absolute error (lower is better). If Ridge only slightly beats the baseline, say so. The last week of this dataset is the volatile one, which is exactly where simple models struggle. A good analyst reports that, not just the best-looking number.

## 8. Retrain on all history and forecast the next 7 days
"""))
cells.append(code('''
final = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(model_df[FEATURES], model_df[VARIABLES])
future = enec.recursive_forecast(final, df, H)

recent = df.tail(24 * 14)
plt.figure(figsize=(14, 4.5))
plt.plot(recent.hour_timestamp, recent.avg_vibration_mm_s, label="Last 14 days (actual)")
plt.plot(future.hour_timestamp, future.avg_vibration_mm_s, label="Next 7 days (forecast)", color="#f5a623")
plt.title("A-001 vibration: next 7 days"); plt.legend(); plt.grid(alpha=.25); plt.show()

recent_mean = df.avg_vibration_mm_s.tail(H).mean()
future_mean = future.avg_vibration_mm_s.mean()
summary = {"recent_7d_mean_mm_s": round(recent_mean, 3), "forecast_next_7d_mean_mm_s": round(future_mean, 3),
           "forecast_change_pct": round(100 * (future_mean - recent_mean) / recent_mean, 1),
           "backtest_mae_mm_s": round(mae, 3), "baseline_mae_mm_s": round(base_mae, 3)}
summary
'''))
cells.append(md("""
## 9. Bounded interpretation with an LLM

We give the model **numbers we computed**, not raw data, and a strict boundary. The model writes the words; the code did the maths.
"""))
cells.append(code('''
system = ("You write a short, plain-English note for a reliability reviewer. Use ONLY the numbers given. "
          "Mention the forecast error honestly. Do not invent thresholds. Do not diagnose a failure mode. "
          "Do not recommend stopping or repairing equipment. End with one suggested human check.")
print(enec.ask(client, "NUMBERS: " + str(summary), system=system))
'''))
cells.append(md("""
## Limits to say out loud

- Synthetic data. A real plant needs real thresholds, operating context and engineering judgement.
- A forecast extrapolates a pattern. It does **not** prove a cause or a failure.
- A 90-day window is small. A full year of hourly data would show the seasonal pattern better.

## Exercise

1. Change `base` to the first 30 days. How many z-flags do you get now?
2. Add a 168-hour lag feature. Does the backtest MAE improve?
3. Forecast `avg_temperature_c` instead. Is the model more or less accurate than for vibration? Why might that be?
"""))
save(cells, os.path.join(EXT, "Ext02_A001_Anomaly_and_Forecast.ipynb"))
print("day 1 built")

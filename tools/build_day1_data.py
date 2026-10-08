"""Builds Day_1_Copilot_and_Data_Understanding/Day1_01_Data_Understanding_Python.ipynb
No OpenAI key, no pip install. Only pandas, sqlite3 and matplotlib (all preinstalled in Colab)."""
import nbformat as nbf
C = []
md = lambda s: C.append(nbf.v4.new_markdown_cell(s.strip("\n")))
code = lambda s: C.append(nbf.v4.new_code_cell(s.strip("\n")))

md("""
# ENEC 2026 · Day 1 · Data Understanding in Python

**Time:** about 60 minutes  |  **Runs in:** Google Colab (free tier)  |  **Needs:** nothing. No OpenAI key. No `pip install`. Only pandas, sqlite3 and matplotlib, which Colab already has.

**Goal:** understand the files in the course repo before any AI touches them: what types of files there are, how tables connect, how to query them with SQL, and how to read the documents. Everything you learn here makes your Copilot and Day 2 prompts better.

**How to use this notebook:** press **Shift+Enter** on each cell, top to bottom. Change a value, run it again, see what happens. You cannot break anything: all changes happen in memory.

> All data is synthetic training data. Nothing here is an engineering diagnosis or a security finding.
""")

md("## 0. Get the course files")
code('''
import os, sys, subprocess
REPO_URL = "https://github.com/Decoding-Data-Science/enec2026oct"
IN_COLAB = "google.colab" in sys.modules
ROOT = "/content/enec2026oct" if IN_COLAB else os.getcwd()
if IN_COLAB and not os.path.isdir(ROOT):
    r = subprocess.run(["git", "clone", "--depth", "1", REPO_URL, ROOT], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("Could not clone the repo:\\n" + r.stderr[-300:] +
                         "\\nFallback: upload enec2026oct.zip in the Files panel, run  !unzip -q enec2026oct.zip -d /content  and run this cell again.")
print("Course files are in:", ROOT)
''')

md("""
## 1. What kinds of files are in the repo?

Data comes in three shapes. Knowing which one you hold decides which tool you use.

| Shape | Examples here | Tool |
|---|---|---|
| **Structured** (rows and columns) | `.csv`, `.xlsx` | pandas, SQL, Excel + Copilot |
| **Semi-structured** | `.json`, `.ipynb` | Python dictionaries |
| **Unstructured** (free text) | `.md`, `.txt`, `.docx` | reading, search, RAG (Day 2) |
""")
code('''
import pandas as pd, pathlib
pd.set_option("display.max_columns", 40, "display.width", 160)
root = pathlib.Path(ROOT)

files = [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts]
inv = pd.DataFrame({"path": [str(p.relative_to(root)) for p in files],
                    "type": [p.suffix.lower() or "(none)" for p in files],
                    "kb": [round(p.stat().st_size/1024, 1) for p in files]})
summary = inv.groupby("type").agg(files=("path", "count"), total_kb=("kb", "sum")).sort_values("files", ascending=False)
summary
''')
code('''
# Where does each type live? (first folder only)
inv["folder"] = inv.path.str.split("/").str[0]
pd.crosstab(inv.folder, inv.type)
''')

md("""
## 2. Structured data: one CSV with pandas

A **table** has rows (one record each) and columns (one field each). Always ask four questions first: how many rows, which columns, what types, what is missing.
""")
code('''
assets = pd.read_csv(root / "data/csv/assets.csv")
print("rows, columns:", assets.shape)
assets.head()
''')
code('''
assets.dtypes
''')
code('''
# Summary of the number columns, then counts for a text column
display(assets.describe())
assets.criticality.value_counts()
''')
code('''
# Missing values per column
assets.isna().sum()
''')

md("""
## 3. Load every table and make an inventory

The course data is 12 plant tables (`data/csv`) and 17 security tables (`data/security`). The loop below reads them all.
""")
code('''
tables = {}
for folder in ("data/csv", "data/security"):
    for p in sorted((root / folder).glob("*.csv")):
        tables[p.stem] = pd.read_csv(p)

inventory = pd.DataFrame({
    "table": list(tables),
    "folder": ["security" if (root/"data/security"/f"{t}.csv").exists() else "plant" for t in tables],
    "rows": [len(t) for t in tables.values()],
    "columns": [len(t.columns) for t in tables.values()],
    "has_asset_id": [any(c.lower() == "asset_id" for c in t.columns) for t in tables.values()],
})
print(len(tables), "tables loaded")
inventory
''')
md("""
**Look at the `has_asset_id` column.** `asset_id` is the key that links tables together. A table without it describes something else (accounts, zones, documents, questions).
""")

md("""
## 4. Excel workbooks

The same data also ships as Excel files, one sheet per table, formatted as Excel Tables so **Copilot in Excel** can read them. Each workbook starts with a `README` sheet and ends with a data dictionary.
""")
code('''
xl_dir = root / "data/excel"
for x in sorted(xl_dir.glob("*.xlsx")):
    print(x.name, "->", pd.ExcelFile(x).sheet_names)
''')
code('''
# Read a sheet and the data dictionary of the security workbook
sec_xl = xl_dir / "ENEC_Asset_360_Security.xlsx"
display(pd.read_excel(sec_xl, sheet_name="Vulnerabilities").head())
pd.read_excel(sec_xl, sheet_name="Data_Dictionary").head(15)
''')

md("""
## 5. SQL: ask the tables questions

SQL is the standard language for asking questions of tables. Python includes **SQLite**, a small database that needs no installation. We copy all tables into an in-memory database, then query it. This is the same database every later notebook uses.

Use `q("...")` to run a query. It only allows `SELECT`, so you cannot damage anything.
""")
code('''
import sqlite3, re

con = sqlite3.connect(":memory:")
for name, df in tables.items():
    d = df.copy()
    for c in d.columns:                       # SQLite has no date type: keep dates as text
        if "datetime" in str(d[c].dtype):
            d[c] = d[c].astype(str)
    d.to_sql(name, con, index=False)

def q(sql, rows=30):
    """Run ONE read-only SELECT and return a DataFrame."""
    s = sql.strip().rstrip(";")
    if ";" in s or not re.match(r"^(select|with)\\b", s, re.I):
        raise ValueError("Only a single SELECT query is allowed here.")
    return pd.read_sql(s, con).head(rows)

q("SELECT name AS table_name FROM sqlite_master WHERE type='table' ORDER BY name", rows=50)
''')
md("### 5.1 Schema: what columns does a table have?")
code('''
pd.read_sql("PRAGMA table_info(asset_360)", con)[["name", "type"]]
''')
md("### 5.2 SELECT, WHERE, ORDER BY")
code('''
q("""
SELECT asset_id, asset_name, criticality, system_name, health_score, risk_level
FROM asset_360
WHERE criticality = 'HIGH'
ORDER BY health_score ASC
LIMIT 10
""")
''')
md("### 5.3 GROUP BY: summarise")
code('''
q("""
SELECT system_name,
       COUNT(*)                    AS assets,
       ROUND(AVG(health_score), 1) AS avg_health,
       SUM(open_work_orders)       AS open_work_orders
FROM asset_360
GROUP BY system_name
ORDER BY avg_health ASC
""")
''')
md("### 5.4 JOIN: connect tables through `asset_id`")
code('''
q("""
SELECT a.asset_id, a.asset_name, a.health_score, a.risk_level,
       s.Security_Risk_Level, s.Patch_Status, s.Network_Exposure, s.Open_Security_Issues
FROM asset_360 a
JOIN asset_security s ON s.asset_id = a.asset_id
WHERE a.risk_level = 'HIGH' OR s.Security_Risk_Level = 'High'
ORDER BY s.Open_Security_Issues DESC
""")
''')
md("""
That join is the idea behind the whole programme: **operations data and security data become one picture once they share a key.** The `asset_priority_view` table is exactly that join, pre-built, with a combined `Priority_Score`.
""")
code('''
q("""
SELECT Priority_Rank, asset_id, asset_name, Priority_Band, Priority_Score,
       health_score, Security_Risk_Level, Patch_Status
FROM asset_priority_view
ORDER BY Priority_Rank
LIMIT 10
""")
''')

md("""
## 6. Keep the database as a file

The in-memory database disappears when Colab closes. Save it as a real file so you can download it and open it in any SQLite viewer (for example DB Browser for SQLite).
""")
code('''
out = "/content/enec_asset360.db" if IN_COLAB else str(root / "enec_asset360.db")
if os.path.exists(out):
    os.remove(out)
disk = sqlite3.connect(out)
con.backup(disk); disk.close()
print("Saved:", out, "|", round(os.path.getsize(out)/1024/1024, 1), "MB")
# In Colab: open the Files panel (folder icon, left), right-click the file, Download.
''')

md("""
## 7. Time-series data: the A-001 pump

Sensors write a reading every minute; the table holds the **hourly** summary for 90 days. Charts are the fastest way to see a trend.
""")
code('''
import matplotlib.pyplot as plt
s = tables["a001_sensor_hourly_90d"].copy()
s["hour_timestamp"] = pd.to_datetime(s.hour_timestamp)
daily = s.set_index("hour_timestamp")[["avg_vibration_mm_s", "avg_temperature_c"]].resample("D").mean()

fig, ax = plt.subplots(1, 2, figsize=(13, 3.6))
daily.avg_vibration_mm_s.plot(ax=ax[0], color="#0e7490"); ax[0].set_title("A-001 vibration, daily mean (mm/s)")
daily.avg_temperature_c.plot(ax=ax[1], color="#7c3aed");  ax[1].set_title("A-001 temperature, daily mean (C)")
for a in ax: a.set_xlabel("")
plt.tight_layout(); plt.show()
''')
md("**Question for you:** on which date does the vibration start to rise? Print the daily table and find it.")
code('''
daily.loc["2026-07-15":"2026-07-31"].round(2)
''')

md("""
## 8. Event data: the security logs

Logs are tables too, with one row per event and a timestamp. They are large, so we **filter and count** instead of reading them.
""")
code('''
q("""
SELECT substr(event_time, 1, 10) AS day, event_type, COUNT(*) AS events
FROM security_auth_logs
WHERE asset_id = 'A-001'
GROUP BY day, event_type
HAVING event_type = 'LOGIN_FAILURE'
ORDER BY events DESC
LIMIT 5
""")
''')
code('''
q("""
SELECT command_id, event_time, username, source_ip, command_type, parameter,
       change_ticket_id, within_change_window, approved
FROM security_controller_commands
WHERE asset_id = 'A-001' AND (change_ticket_id IS NULL OR change_ticket_id = '')
ORDER BY event_time
""")
''')
md("""
Two things are visible without any AI: a burst of failed logins, and a controller command with **no change ticket**. The A-001 story page and the Day 3 notebooks build on these.
""")

md("""
## 9. Unstructured data: documents

Documents hold the rules and the evidence. They are text, so you read them rather than query them. First look at the **document register** (structured), then open one document.
""")
code('''
q("""
SELECT document_id, title, approval_status, version, effective_date
FROM a001_source_documents
ORDER BY title, version
""", rows=20)
''')
md("""
**Version trap:** the register shows the same procedure three times: `SUPERSEDED`, `APPROVED` and `DRAFT`. Only the **APPROVED** one is authoritative. An AI that quotes the superseded one gives a wrong answer with confidence. Day 2 teaches your RAG to filter by status.
""")
code('''
doc = root / "documents/a001/04_A001-PROC-INS-001-V2_Approved_Inspection_and_PM_Procedure.md"
text = doc.read_text(encoding="utf-8")
print(len(text), "characters,", len(text.split()), "words\\n")
print(text[:1500])
''')
code('''
# A simple keyword search across ALL text documents (this is the idea RAG improves on)
def search(word, folders=("documents/a001", "documents/security", "documents/project_pdfs_text")):
    hits = []
    for f in folders:
        for p in sorted((root / f).glob("*")):
            if p.suffix in (".md", ".txt"):
                t = p.read_text(encoding="utf-8", errors="ignore")
                n = t.lower().count(word.lower())
                if n:
                    hits.append({"file": p.name, "mentions": n})
    if not hits:
        return f"No document contains the word '{word}'."
    return pd.DataFrame(hits).sort_values("mentions", ascending=False)

search("vibration").head(8)
''')
md("Keyword search finds the word but not the meaning. Search for `shaking` and see what you get. That gap is why we use embeddings on Day 2.")
code('''
search("shaking")
''')

md("""
## 10. Data quality checks

Before you trust any table, or any AI answer built on it, check the basics.
""")
code('''
checks = []
for name, df in tables.items():
    checks.append({"table": name, "rows": len(df), "duplicate_rows": int(df.duplicated().sum()),
                   "columns_with_nulls": int((df.isna().sum() > 0).sum())})
pd.DataFrame(checks)
''')
code('''
# Referential check: does every asset_id in the security tables exist in assets?
known = set(tables["assets"].asset_id)
for name, df in tables.items():
    if "asset_id" in df.columns:
        missing = set(df.asset_id.dropna()) - known
        if missing:
            print(f"{name}: {len(missing)} unknown asset_id values, e.g. {sorted(missing)[:3]}")
print("Check finished. (Anything printed above is a link that does not resolve.)")
''')

md("""
## Practice

Write the SQL first, then check it against the answer.

1. How many rows are in `security_auth_logs`, and how many are `LOGIN_FAILURE`?
2. Which 5 assets have the highest `Priority_Score`? (`asset_priority_view`)
3. How many vulnerabilities are `Open` and have `overdue = 'Yes'`?
4. Which assets have `Patch_Status = 'Overdue'` **and** `Network_Exposure = 'External'`?
5. For asset `A-001`, list the alerts (`security_alerts`) in time order.

Then ask the **same questions in Microsoft Copilot** on the Excel workbooks. Do the numbers match? When they do not, find out which one is wrong. That habit is the most useful skill in this course.

## What you learned

- The repo mixes structured files (CSV, Excel), semi-structured files (JSON, notebooks) and unstructured files (documents).
- `asset_id` links the tables. A JOIN turns separate tables into one picture.
- SQL answers exact questions; document search finds text but not meaning.
- Check quality and document status before you trust an answer.

**Next:** Day 2 adds an OpenAI model and builds RAG over the documents you just read.
""")

nb = nbf.v4.new_notebook()
nb.cells = C
nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
               "language_info": {"name": "python"}, "colab": {"provenance": [], "toc_visible": True}}
nbf.validate(nb)
nbf.write(nb, "Day_1_Copilot_and_Data_Understanding/Day1_01_Data_Understanding_Python.ipynb")
print("written", len(C), "cells")

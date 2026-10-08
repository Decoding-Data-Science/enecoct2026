"""
enec_colab.py - small helper module for the ENEC 2026 (October) Colab notebooks.

Everything here is plain Python + the OpenAI SDK + pandas/sqlite3/numpy.
No Databricks, no hosted vector database, no external deployment platform.

Day 1 notebooks show the data/ML code inline.
Day 2 notebooks write chunking, embeddings and retrieval inline.
Day 3 notebooks write the agent loop inline.
This module packages the SAME ideas so that later notebooks stay short.
"""
from __future__ import annotations

import json
import math
import os
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------- paths
REPO_URL = "https://github.com/Decoding-Data-Science/enec2026oct"


def find_root() -> Path:
    """Repo root = parent of the folder that contains this file."""
    return Path(__file__).resolve().parent.parent


ROOT = find_root()
CSV_DIR = ROOT / "data" / "csv"
DOC_DIR = ROOT / "documents" / "a001"
DAY4_DOC_DIR = ROOT / "documents" / "project_pdfs_text"
SKILL_DIR = ROOT / "skills"
EVAL_DIR = ROOT / "evaluation"

# ----------------------------------------------------------------------------- OpenAI
MODEL_PREFERENCE = ["gpt-5.4-mini", "gpt-5-mini", "gpt-4o-mini"]
EMBED_MODEL = "text-embedding-3-small"
MODEL: str | None = os.environ.get("ENEC_MODEL")  # set by pick_model(), or override it yourself

SECRET_NAME = "OPENAI_API_KEY"


def get_client():
    """Create the OpenAI client. The key is read from Colab Secrets (name: OPENAI_API_KEY).

    Fallbacks, in order: Colab Secrets -> environment variable -> hidden prompt.
    The key is never printed and never written to the notebook.
    """
    from openai import OpenAI

    key = None
    try:
        from google.colab import userdata  # only exists inside Colab
        in_colab = True
    except ImportError:
        in_colab = False
    if in_colab:
        try:
            key = userdata.get(SECRET_NAME)
        except Exception:  # SecretNotFoundError or NotebookAccessError
            print(
                f"Could not read the Colab secret '{SECRET_NAME}'.\n"
                "  1. Click the key icon in the left sidebar of Colab.\n"
                f"  2. Add a secret named {SECRET_NAME} with your OpenAI key.\n"
                "  3. Switch ON 'Notebook access' for the secret.\n"
                "  4. Run this cell again."
            )
    key = key or os.environ.get(SECRET_NAME)
    if not key:
        import getpass

        key = getpass.getpass("Paste your OpenAI API key (hidden): ")
    return OpenAI(api_key=key)


def pick_model(client, preference: list[str] | None = None, verbose: bool = True) -> str:
    """Return the first model in the preference list that answers a tiny test call."""
    global MODEL
    if MODEL:
        return MODEL
    last_err = None
    for m in preference or MODEL_PREFERENCE:
        try:
            client.chat.completions.create(model=m, messages=[{"role": "user", "content": "Reply with the single word: ok"}])
            MODEL = m
            if verbose:
                print(f"Using chat model: {m}")
            return m
        except Exception as e:  # model not available for this key
            last_err = e
    raise RuntimeError(f"None of {preference or MODEL_PREFERENCE} worked with this key. Last error: {last_err}")


def chat(client, messages, model: str | None = None, tools=None, json_mode: bool = False):
    """One chat completion. Returns the message object (has .content and .tool_calls)."""
    model = model or MODEL or pick_model(client, verbose=False)
    kw = dict(model=model, messages=messages)
    if tools:
        kw["tools"] = tools
        kw["tool_choice"] = "auto"
    if json_mode:
        kw["response_format"] = {"type": "json_object"}
    # The gpt-5 family accepts reasoning_effort; keep it low so the classroom stays fast.
    if model.startswith("gpt-5"):
        try:
            return client.chat.completions.create(reasoning_effort="low", **kw).choices[0].message
        except Exception as e:
            if "reasoning" not in str(e).lower():
                raise
    return client.chat.completions.create(**kw).choices[0].message


def ask(client, prompt: str, system: str | None = None, model: str | None = None, json_mode: bool = False) -> str:
    """Convenience: one prompt in, one text answer out."""
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    return chat(client, msgs, model=model, json_mode=json_mode).content or ""


def embed(client, texts: list[str], model: str = EMBED_MODEL, batch: int = 96) -> np.ndarray:
    """Embed a list of strings. Returns an (n, dim) float32 array."""
    out = []
    for i in range(0, len(texts), batch):
        resp = client.embeddings.create(model=model, input=texts[i : i + batch])
        out.extend(d.embedding for d in resp.data)
    return np.array(out, dtype="float32")


# ----------------------------------------------------------------------------- data
TABLES = [
    "assets", "systems", "asset_360", "a001_sensor_hourly_90d", "a001_event_timeline",
    "a001_asset_health_scores", "work_orders", "inspections", "maintenance_history",
    "a001_project_risk_360", "a001_source_documents", "a001_document_evidence",
]


SEC_DIR = ROOT / "data" / "security"
# Security layer (Day 1, notebook 3). Loaded into the same SQLite database so SQL and the Day 3 agent can join it to Asset 360.
SECURITY_TABLES = [
    "asset_security", "asset_priority_view", "security_vulnerabilities", "security_incidents", "security_access_review",
    "security_alerts", "security_auth_logs", "security_network_flows", "security_controller_commands", "security_accounts",
    "security_network_zones", "security_documents",
]


def load_tables(include_security: bool = True) -> dict[str, pd.DataFrame]:
    """Read every small CSV into a dict of DataFrames (course tables + the security layer)."""
    out = {}
    names = [(t, CSV_DIR) for t in TABLES]
    if include_security:
        names += [(t, SEC_DIR) for t in SECURITY_TABLES if (SEC_DIR / f"{t}.csv").exists()]
    for t, folder in names:
        df = pd.read_csv(folder / f"{t}.csv")
        for c in df.columns:
            if c in ("hour_timestamp",):
                df[c] = pd.to_datetime(df[c])
        out[t] = df
    return out


def make_db(tables: dict[str, pd.DataFrame] | None = None) -> sqlite3.Connection:
    """Load the CSV tables into an in-memory SQLite database.

    This is the Colab replacement for the Databricks catalog / schema / Delta tables.
    """
    tables = tables or load_tables()
    con = sqlite3.connect(":memory:", check_same_thread=False)
    for name, df in tables.items():
        d = df.copy()
        for c in d.columns:
            if str(d[c].dtype).startswith("datetime"):
                d[c] = d[c].dt.strftime("%Y-%m-%d %H:%M:%S")
        d.to_sql(name, con, index=False, if_exists="replace")
    return con


_FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|reindex)\b", re.I)


def run_sql(con: sqlite3.Connection, sql: str, max_rows: int = 40) -> pd.DataFrame:
    """Run ONE read-only SELECT. Anything else is rejected before it reaches the database."""
    s = sql.strip().rstrip(";").strip()
    if ";" in s:
        raise ValueError("Only one SQL statement is allowed.")
    if not re.match(r"^(select|with)\b", s, re.I):
        raise ValueError("Only SELECT queries are allowed (read-only tool).")
    if _FORBIDDEN.search(s):
        raise ValueError("Write/DDL keywords are not allowed (read-only tool).")
    df = pd.read_sql(s, con)
    return df.head(max_rows)


SCHEMA_HINT = """Tables (SQLite, read-only):
- assets(asset_id, system_id, asset_name, asset_type, criticality, manufacturer, installation_date, status, maintenance_interval_days)
- systems(system_id, unit_id, system_name, system_category, responsible_department_id)
- asset_360(asset_id, asset_name, asset_type, criticality, status, system_name, unit_id, health_score, risk_level, recommended_action, open_work_orders, high_priority_open_work, follow_up_findings, latest_inspection_date)
- work_orders(work_order_id, asset_id, work_type, priority, problem_description, created_date, due_date, completed_date, status, assigned_employee_id, estimated_hours, actual_hours)
- inspections(inspection_id, asset_id, inspection_date, inspection_type, finding, severity, inspector_employee_id, recommendation, follow_up_required)
- maintenance_history(maintenance_id, asset_id, work_order_id, maintenance_date, maintenance_type, downtime_hours, cost_usd, technician_notes, effectiveness_rating)
- a001_sensor_hourly_90d(hour_timestamp, asset_id, minute_readings, avg_temperature_c, max_temperature_c, avg_vibration_mm_s, max_vibration_mm_s, avg_pressure_bar, avg_flow_rate_m3_h, avg_electrical_current_a, avg_ambient_temperature_c, anomaly_minutes, quality_issue_minutes)
- a001_asset_health_scores(score_date, asset_id, health_score, risk_level, recommended_action, model_version)
- a001_event_timeline(event_date, event_type, event_id, event_title, event_detail, project_id)
- a001_project_risk_360(asset_id, asset_name, criticality, project_id, project_name, project_status, risk_id, risk_category, probability, impact, exposure_score, risk_status, evidence_basis)
- a001_source_documents(document_id, title, document_type, approval_status, version, effective_date, owner, asset_id, source_file_name)
- a001_document_evidence(document_id, title, document_type, approval_status, version, effective_date, owner, entity_type, entity_id, relationship_type, evidence_date, notes)
Security layer (simulated; join to asset_360 on asset_id):
- asset_security(asset_id, Asset_Criticality[Low/Medium/High/Critical], Security_Risk_Level[Low/Medium/High], Last_Security_Review_Date, Open_Security_Issues, Access_Risk_Flag[Yes/No], Patch_Status[Current/Pending/Overdue], Network_Exposure[Internal/Restricted/External], Security_Incident_Last_90_Days[Yes/No])
- asset_priority_view(asset_id, asset_name, system_name, unit_id, Asset_Criticality, health_score, risk_level, high_priority_open_work, Sensor_Anomalies_90d, Ops_Attention_Flag, Security_Risk_Level, Open_Security_Issues, Max_Open_CVSS, Patch_Status, Network_Exposure, Access_Risk_Flag, Security_Incident_Last_90_Days, Ops_Points, Security_Points, Priority_Score, Priority_Rank, Priority_Band)
- security_vulnerabilities(vulnerability_id, asset_id, title, category, cvss_score, severity, found_date, due_date, status[Open/In remediation/Closed/Accepted risk], closed_date, owner_employee_id, sla_days, overdue[Yes/No], days_overdue)
- security_incidents(incident_id, detected_date, asset_id, incident_type, attack_tactic_hint, detection_source, severity, status, analyst_employee_id, linked_alert_id)
- security_access_review(asset_id, asset_name, Network_Exposure, total_accounts, privileged_accounts, shared_accounts, mfa_enforced, vendor_remote_access, stale_accounts_90d, last_access_review_date, access_risk_flag)
- security_alerts(alert_id, alert_time, asset_id, rule_id, rule_name, severity, tactic_hint, evidence_summary, event_count, status, incident_id)
- security_auth_logs(event_id, event_time, asset_id, username, source_ip, source_zone, source_country, event_type[LOGIN_SUCCESS/LOGIN_FAILURE/LOGOUT], auth_method, mfa_used, result_reason)
- security_network_flows(flow_id, event_time, asset_id, src_ip, src_zone, dst_ip, dst_zone, service, dst_port, action[ALLOW/DENY], bytes_out, bytes_in, duration_s, rule_id)
- security_controller_commands(command_id, event_time, asset_id, username, source_ip, command_type, parameter, change_ticket_id, work_order_id, within_change_window, approved)
- security_accounts(username, role, home_country, account_note)
- security_network_zones(zone_id, zone_name, purdue_level, trust)
- security_documents(document_id, title, document_type, approval_status, version, effective_date, owner, asset_scope, package_path)
Dates are text 'YYYY-MM-DD' (hour_timestamp is 'YYYY-MM-DD HH:MM:SS'). Priority values: URGENT, HIGH, MEDIUM, LOW. Open work = status IN ('OPEN','IN_PROGRESS','DEFERRED')."""

# ----------------------------------------------------------------------------- forecasting
VARIABLES = [
    "avg_vibration_mm_s", "avg_temperature_c", "avg_pressure_bar",
    "avg_flow_rate_m3_h", "avg_electrical_current_a", "avg_ambient_temperature_c",
]


def make_features(data: pd.DataFrame):
    m = data.copy()
    for c in VARIABLES:
        m[f"{c}_lag1"] = m[c].shift(1)
        m[f"{c}_lag24"] = m[c].shift(24)
        m[f"{c}_roll24"] = m[c].shift(1).rolling(24).mean()
    hr = m["hour_timestamp"].dt.hour
    dow = m["hour_timestamp"].dt.dayofweek
    m["hour_sin"], m["hour_cos"] = np.sin(2 * np.pi * hr / 24), np.cos(2 * np.pi * hr / 24)
    m["dow_sin"], m["dow_cos"] = np.sin(2 * np.pi * dow / 7), np.cos(2 * np.pi * dow / 7)
    feats = [c for c in m.columns if c.endswith(("_lag1", "_lag24", "_roll24"))] + ["hour_sin", "hour_cos", "dow_sin", "dow_cos"]
    return m.dropna().reset_index(drop=True), feats


def recursive_forecast(model, hist: pd.DataFrame, steps: int) -> pd.DataFrame:
    h = hist[["hour_timestamp"] + VARIABLES].copy().reset_index(drop=True)
    rows = []
    t = h["hour_timestamp"].iloc[-1] + pd.Timedelta(hours=1)
    for _ in range(steps):
        f = {}
        for c in VARIABLES:
            v = h[c].to_numpy()
            f[f"{c}_lag1"], f[f"{c}_lag24"], f[f"{c}_roll24"] = v[-1], v[-24], v[-24:].mean()
        f["hour_sin"], f["hour_cos"] = math.sin(2 * math.pi * t.hour / 24), math.cos(2 * math.pi * t.hour / 24)
        f["dow_sin"], f["dow_cos"] = math.sin(2 * math.pi * t.dayofweek / 7), math.cos(2 * math.pi * t.dayofweek / 7)
        x = pd.DataFrame([f])[model.feature_names_in_] if hasattr(model, "feature_names_in_") else pd.DataFrame([f])
        pred = model.predict(x)[0]
        row = {"hour_timestamp": t, **dict(zip(VARIABLES, pred))}
        rows.append(row)
        h = pd.concat([h, pd.DataFrame([row])], ignore_index=True)
        t += pd.Timedelta(hours=1)
    return pd.DataFrame(rows)


def forecast_vibration(hourly: pd.DataFrame, horizon: int = 168) -> dict:
    """Train the Day 1 Ridge model and return a small, honest summary of the next `horizon` hours."""
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    df = hourly.sort_values("hour_timestamp").reset_index(drop=True)
    feat_df, feats = make_features(df)
    train, test = feat_df.iloc[:-horizon], feat_df.iloc[-horizon:]
    model = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(train[feats], train[VARIABLES])
    back = recursive_forecast(model, df[df["hour_timestamp"] < test["hour_timestamp"].min()], horizon)
    mae = float(mean_absolute_error(test["avg_vibration_mm_s"].to_numpy(), back["avg_vibration_mm_s"].to_numpy()))
    base = float(mean_absolute_error(test["avg_vibration_mm_s"].to_numpy(), np.tile(train["avg_vibration_mm_s"].iloc[-24:].to_numpy(), horizon // 24)))
    final = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(feat_df[feats], feat_df[VARIABLES])
    fut = recursive_forecast(final, df, horizon)
    recent = float(df["avg_vibration_mm_s"].tail(horizon).mean())
    nxt = float(fut["avg_vibration_mm_s"].mean())
    return {
        "recent_7d_mean_mm_s": round(recent, 3),
        "forecast_next_7d_mean_mm_s": round(nxt, 3),
        "forecast_change_pct": round(100 * (nxt - recent) / recent, 1),
        "forecast_last_hour_mm_s": round(float(fut["avg_vibration_mm_s"].iloc[-1]), 3),
        "backtest_mae_mm_s": round(mae, 3),
        "baseline_repeat_last_day_mae_mm_s": round(base, 3),
        "note": "Statistical extrapolation of a synthetic series. It is not a failure prediction and not a maintenance decision.",
        "_forecast_df": fut,
    }


# ----------------------------------------------------------------------------- documents + RAG
def _clean_doc_text(t: str) -> str:
    t = re.sub(r"^>.*$", "", t, flags=re.M)             # blockquote banner added when PDFs were mirrored
    t = re.sub(r"<PARSED TEXT FOR PAGE:[^>]*>", "", t)   # parser markers
    t = re.sub(r"^---+$", "", t, flags=re.M)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def load_documents(include_day4: bool = False, include_security: bool = False) -> list[dict]:
    """Load the readable A-001 documents with their governance metadata (status, version, date)."""
    meta = pd.read_csv(CSV_DIR / "a001_source_documents.csv").set_index("document_id")
    docs = []
    for f in sorted(DOC_DIR.glob("0*.md")):
        text = _clean_doc_text(f.read_text(encoding="utf-8"))
        m = re.search(r"Document ID\s+(\S+)", text)
        did = m.group(1) if m else f.stem
        row = meta.loc[did] if did in meta.index else None
        docs.append({
            "doc_id": did,
            "title": row["title"] if row is not None else f.stem,
            "status": row["approval_status"] if row is not None else "UNKNOWN",
            "version": str(row["version"]) if row is not None else "?",
            "date": str(row["effective_date"]) if row is not None else "?",
            "text": text, "file": f.name,
        })
    if include_security:
        smeta = pd.read_csv(SEC_DIR / "security_documents.csv").set_index("document_id")
        for f in sorted((ROOT / "documents" / "security").glob("*.md")):
            text = _clean_doc_text(f.read_text(encoding="utf-8"))
            m = re.search(r"Document ID:\s*(\S+)\s*\|\s*Version\s*(\S+)", text)
            base = m.group(1) if m else f.stem
            did = next((i for i in smeta.index if f.name.startswith(i.replace("-V1", "").replace("-V2", "").replace("-V3D", "")) and (("V1" in f.name) == i.endswith("-V1")) and (("V2" in f.name) == i.endswith("-V2")) and (("V3D" in f.name) == i.endswith("-V3D"))), base)
            row = smeta.loc[did] if did in smeta.index else None
            docs.append({"doc_id": did, "title": row["title"] if row is not None else f.stem,
                         "status": row["approval_status"] if row is not None else "UNKNOWN",
                         "version": str(row["version"]) if row is not None else "?",
                         "date": str(row["effective_date"]) if row is not None else "?", "text": text, "file": f.name})
    if include_day4:
        for f in sorted(DAY4_DOC_DIR.glob("*.txt")):
            text = _clean_doc_text(f.read_text(encoding="utf-8"))
            g = lambda pat: (re.search(pat, text).group(1) if re.search(pat, text) else "?")
            title = re.search(r"/ [A-Z]+\s*\n\s*(.+?)\n\s*A-001 \|", text, re.S)
            docs.append({
                "doc_id": g(r"Document ID\s+(\S+)"),
                "title": " ".join(title.group(1).split()) if title else f.stem,
                "status": g(r"Status\s+([A-Z]+)"),
                "version": g(r"Version\s+(\S+)"),
                "date": g(r"Effective / Issue Date\s+(\S+)"),
                "text": text, "file": f.name,
            })
    return docs


def chunk_text(text: str, size: int = 900, overlap: int = 150) -> list[str]:
    """Split on paragraphs, then pack paragraphs into chunks of about `size` characters."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 2 <= size:
            cur = (cur + "\n\n" + p).strip()
        else:
            if cur:
                chunks.append(cur)
            tail = cur[-overlap:] if cur and overlap else ""
            cur = (tail + "\n\n" + p).strip() if len(p) < size else p
            while len(cur) > size * 1.6:           # very long paragraph: hard split
                chunks.append(cur[:size]); cur = cur[size - overlap:]
    if cur:
        chunks.append(cur)
    return chunks


@dataclass
class RAGIndex:
    client: object
    chunks: list[dict] = field(default_factory=list)
    vectors: np.ndarray | None = None

    @classmethod
    def build(cls, client, docs: list[dict], size: int = 900, overlap: int = 150) -> "RAGIndex":
        chunks = []
        for d in docs:
            for i, c in enumerate(chunk_text(d["text"], size, overlap)):
                chunks.append({"doc_id": d["doc_id"], "title": d["title"], "status": d["status"],
                               "version": d["version"], "date": d["date"], "chunk_no": i, "text": c})
        vecs = embed(client, [f"{c['title']} ({c['status']} v{c['version']})\n{c['text']}" for c in chunks])
        vecs /= np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9
        return cls(client, chunks, vecs)

    def search(self, query: str, k: int = 4, statuses: list[str] | None = None) -> list[dict]:
        q = embed(self.client, [query])[0]
        q /= np.linalg.norm(q) + 1e-9
        scores = self.vectors @ q
        order = np.argsort(-scores)
        hits = []
        for i in order:
            c = self.chunks[i]
            if statuses and c["status"] not in statuses:
                continue
            hits.append({**c, "score": float(scores[i])})
            if len(hits) == k:
                break
        return hits


def format_hits(hits: list[dict], max_chars: int = 900) -> str:
    """Turn retrieved chunks into a labelled evidence block for the prompt."""
    parts = []
    for h in hits:
        parts.append(f"[{h['doc_id']} | {h['status']} | v{h['version']} | {h['date']}]\n{h['text'][:max_chars]}")
    return "\n\n---\n\n".join(parts)


RAG_SYSTEM = (
    "You answer questions about synthetic asset A-001 using ONLY the supplied evidence.\n"
    "Rules:\n"
    "1. Cite document IDs in square brackets, e.g. [A001-PROC-INS-001-V2].\n"
    "2. Only APPROVED documents are current authority. DRAFT is not authoritative. SUPERSEDED is historical only. "
    "An OPEN work order is a request, not an authorisation.\n"
    "3. If the evidence does not answer the question, say so. Do not guess.\n"
    "4. You support a human reviewer. You never authorise maintenance, shutdown or replacement."
)


def rag_answer(client, index: RAGIndex, question: str, k: int = 4, statuses: list[str] | None = None, model: str | None = None) -> dict:
    hits = index.search(question, k=k, statuses=statuses)
    prompt = f"EVIDENCE:\n{format_hits(hits)}\n\nQUESTION: {question}"
    ans = ask(client, prompt, system=RAG_SYSTEM, model=model)
    return {"answer": ans, "hits": hits}


# ----------------------------------------------------------------------------- agent loop
def run_agent(client, user_message: str, system: str, tools: list[dict], impls: dict[str, Callable],
              model: str | None = None, max_steps: int = 8, history: list[dict] | None = None, verbose: bool = True):
    """Minimal tool-calling agent loop.

    1. send the conversation + tool descriptions to the model
    2. if the model asks for tools -> run them, append the results, go to 1
    3. otherwise the model's text is the final answer
    Returns (final_text, trace, messages).
    """
    messages = [{"role": "system", "content": system}] + (history or []) + [{"role": "user", "content": user_message}]
    trace = []
    for step in range(1, max_steps + 1):
        msg = chat(client, messages, model=model, tools=tools)
        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content})
            return msg.content or "", trace, messages
        messages.append({
            "role": "assistant", "content": msg.content,
            "tool_calls": [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in msg.tool_calls],
        })
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
                result = impls[name](**args)
                status = "ok"
            except Exception as e:
                result, status, args = f"TOOL ERROR: {e}", "error", {}
            text = result if isinstance(result, str) else json.dumps(result, default=str)
            trace.append({"step": step, "tool": name, "args": args, "status": status, "result_preview": text[:300]})
            if verbose:
                print(f"  step {step}: {name}({json.dumps(args)[:140]}) -> {status}")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": text[:6000]})
    final = "I stopped because the step limit was reached. Evidence so far is in the trace."
    messages.append({"role": "assistant", "content": final})
    return final, trace, messages


def tool_spec(name: str, description: str, properties: dict, required: list[str] | None = None) -> dict:
    return {"type": "function", "function": {"name": name, "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required or list(properties)}}}


def df_to_text(df: pd.DataFrame, max_rows: int = 30) -> str:
    return df.head(max_rows).to_csv(index=False)


def build_a001_tools(con: sqlite3.Connection, index: RAGIndex, hourly: pd.DataFrame):
    """The three Day 3 / Day 4 tools: SQL (structured), search_documents (RAG), forecast (analysis)."""
    def sql_query(query: str) -> str:
        return df_to_text(run_sql(con, query))

    def search_documents(query: str, only_approved: bool = False) -> str:
        hits = index.search(query, k=4, statuses=["APPROVED"] if only_approved else None)
        return format_hits(hits, 700)

    def forecast(horizon_hours: int = 168) -> str:
        r = forecast_vibration(hourly, int(horizon_hours))
        r.pop("_forecast_df", None)
        return json.dumps(r)

    specs = [
        tool_spec("sql_query", "Run ONE read-only SELECT on the A-001 / Asset 360 SQLite tables. Use for counts, statuses, health scores, work orders, inspections, sensor stats.",
                  {"query": {"type": "string", "description": "A single SQLite SELECT statement."}}),
        tool_spec("search_documents", "Semantic search over the A-001 documents (policy, procedures, reports, work order, field report). Results show document ID, approval status and version.",
                  {"query": {"type": "string"}, "only_approved": {"type": "boolean", "description": "true to return APPROVED documents only"}}, ["query"]),
        tool_spec("forecast", "Statistical 7-day vibration forecast for A-001 (Ridge model from optional extension 2). Returns recent mean, forecast mean, backtest error. Not a failure prediction.",
                  {"horizon_hours": {"type": "integer", "description": "Default 168 (7 days)."}}, []),
    ]
    impls = {"sql_query": sql_query, "search_documents": search_documents, "forecast": forecast}
    return specs, impls


# ----------------------------------------------------------------------------- skills
def load_skill_catalog() -> str:
    return (SKILL_DIR / "skills_catalog.md").read_text(encoding="utf-8")


def load_skill(name: str) -> str:
    p = SKILL_DIR / f"{name}.md"
    if not p.exists():
        raise ValueError(f"Unknown skill '{name}'. Available: asset_summary, approved_procedure, reliability_review")
    return p.read_text(encoding="utf-8")


def banner(text: str, width: int = 78) -> None:
    print("=" * width)
    print(text)
    print("=" * width)


# ----------------------------------------------------------------------------- Day 4 capstone helpers
BRIEFING_SECTIONS = [
    "1. Situation", "2. Structured evidence", "3. Predictive / analytical evidence", "4. Document evidence",
    "5. Assessment", "6. Evidence gaps / uncertainty", "7. Recommended human next step", "8. Sources used",
]

DOC_QUERIES = [
    "Which inspection procedure is currently approved and what evidence must be reviewed before classifying the condition",
    "What should be checked when vibration is rising troubleshooting",
    "Field observation rattling wet area source not confirmed",
    "Inspection work order scope and what it does not authorise",
    "Enterprise escalation policy, human review and authorisation of maintenance",
    "Condition monitoring report August vibration trend",
    "Project risk, readiness, cost, vendor spares and sensor data assurance for A-001",
    "Draft procedure revision and draft cross-functional risk register: what is pending and not yet approved",
]


def build_evidence_packet(con, index: RAGIndex, hourly: pd.DataFrame, docs: list[dict]) -> dict:
    """Collect evidence from the three sources and keep them SEPARATE (structured / predictive / documents)."""
    structured = {
        "asset_360": run_sql(con, "select * from asset_360 where asset_id='A-001'").iloc[0].to_dict(),
        "open_work_orders": run_sql(con, "select work_order_id,work_type,priority,status,created_date,due_date,problem_description from work_orders where asset_id='A-001' and status in ('OPEN','IN_PROGRESS','DEFERRED') order by created_date desc"),
        "recent_inspections": run_sql(con, "select inspection_id,inspection_date,inspection_type,severity,finding,recommendation,follow_up_required from inspections where asset_id='A-001' order by inspection_date desc limit 5"),
        "sensor_by_month": run_sql(con, "select substr(hour_timestamp,1,7) as month, round(avg(avg_vibration_mm_s),2) as avg_vibration, round(max(max_vibration_mm_s),2) as max_vibration, round(avg(avg_temperature_c),1) as avg_temp_c, sum(anomaly_minutes) as anomaly_minutes from a001_sensor_hourly_90d group by 1 order by 1"),
        "top_risks": run_sql(con, "select project_id,risk_id,risk_category,exposure_score,risk_status,evidence_basis from a001_project_risk_360 order by exposure_score desc limit 5"),
        "recent_events": run_sql(con, "select event_date,event_type,event_id,event_title from a001_event_timeline order by event_date desc limit 8"),
    }
    fc = forecast_vibration(hourly)
    fc.pop("_forecast_df", None)
    seen, hits = set(), []
    for q in DOC_QUERIES:
        for h in index.search(q, k=3):
            key = (h["doc_id"], h["chunk_no"])
            if key not in seen:
                seen.add(key); hits.append(h)
    register = pd.DataFrame([{k: d[k] for k in ("doc_id", "title", "status", "version", "date")} for d in docs])
    return {"structured": structured, "predictive": fc, "document_hits": hits, "document_register": register}


def packet_to_text(p: dict, max_chunk_chars: int = 650) -> str:
    s = p["structured"]
    parts = ["## STRUCTURED EVIDENCE (database)"]
    parts.append("asset_360: " + json.dumps(s["asset_360"], default=str))
    for k in ("open_work_orders", "recent_inspections", "sensor_by_month", "top_risks", "recent_events"):
        parts.append(f"{k}:\n{s[k].to_csv(index=False)}")
    parts.append("## PREDICTIVE EVIDENCE (statistical forecast, not a diagnosis)\n" + json.dumps(p["predictive"]))
    parts.append("## DOCUMENT REGISTER (authority)\n" + p["document_register"].to_csv(index=False))
    parts.append("## DOCUMENT EXCERPTS\n" + format_hits(p["document_hits"], max_chunk_chars))
    return "\n\n".join(parts)


BRIEFING_SYSTEM = (
    "You prepare a decision-support briefing for a QUALIFIED HUMAN RELIABILITY REVIEWER about synthetic asset A-001.\n"
    "Use ONLY the evidence packet. Keep structured evidence, predictive evidence and document evidence clearly separate.\n"
    "Authority rules: only APPROVED documents are current authority; DRAFT is non-authoritative; SUPERSEDED is historical only; "
    "an OPEN work order is a request, not an authorisation.\n"
    "Never diagnose a failure mode, never authorise maintenance, shutdown or replacement. State what is unknown.\n"
    "Cite document IDs in square brackets. Cite table names for database facts.\n"
    "Write EXACTLY these eight markdown sections, each starting with '## ' and the number shown:\n"
    + "\n".join(f"## {s}" for s in BRIEFING_SECTIONS)
    + "\nBe concise: short paragraphs or bullets, no more than about 450 words in total."
)


def generate_briefing(client, packet: dict, question: str = "What does the available evidence say about A-001, what should a qualified reviewer pay attention to, and what is the appropriate human next step?", model: str | None = None) -> str:
    prompt = f"BUSINESS QUESTION: {question}\n\nEVIDENCE PACKET\n{packet_to_text(packet)}"
    return ask(client, prompt, system=BRIEFING_SYSTEM, model=model)


_NEG = re.compile(r"(not|no|nor|never|cannot|can't|without|neither|does not|do not|don't|doesn't)\W+(?:\w+\W+){0,4}$", re.I)
_AUTH = re.compile(r"\b(?:authori[sz]e[sd]?|approve[sd]?|order(?:s|ed)?|recommend(?:s|ed)?)\s+(?:the\s+|an?\s+)?(?:immediate\s+)?(?:replacement|shutdown|shut-down|repair|component replacement)\b|\bshut\s?down\s+(?:the\s+)?(?:pump|A-001)\b|\breplace\s+the\s+(?:bearing|pump|coupling|seal)\b", re.I)
_CAUTION = re.compile(r"draft|supersed|non-authoritative|not authoritative|not current|historical|not the current|not an authori", re.I)


def check_briefing(text: str, docs: list[dict]) -> pd.DataFrame:
    """Simple, transparent automatic checks. They support the human reviewer; they do not replace review."""
    status = {d["doc_id"]: d["status"] for d in docs}
    rows = []
    heads = [s for s in BRIEFING_SECTIONS if re.search(r"^##\s*" + re.escape(s.split(". ", 1)[0]) + r"\.", text, re.M)]
    rows.append(("All 8 required sections present", len(heads) == 8, f"{len(heads)}/8 found"))
    cited = set(re.findall(r"\[([A-Za-z0-9][A-Za-z0-9\-_.]+)\]", text))
    doc_cited = {c for c in cited if re.search(r"[A-Z]+-\d|WO-|CR-", c)}
    unknown = sorted(c for c in doc_cited if c not in status)
    rows.append(("Every cited document ID exists in the corpus", not unknown, "unknown: " + ", ".join(unknown) if unknown else f"{len(doc_cited)} IDs cited"))
    bad = []
    for did, st in status.items():
        if st in ("DRAFT", "SUPERSEDED"):
            for m in re.finditer(re.escape(did), text):
                win = text[max(0, m.start() - 200): m.end() + 200]
                if not _CAUTION.search(win):
                    bad.append(did)
                    break
    rows.append(("DRAFT / SUPERSEDED documents are flagged, not relied on", not bad, "uncaveated: " + ", ".join(bad) if bad else "ok"))
    auth_hits = [m.group(0) for m in _AUTH.finditer(text) if not _NEG.search(text[max(0, m.start() - 60): m.start()])]
    rows.append(("No maintenance / shutdown authorisation language", not auth_hits, "; ".join(auth_hits[:3]) if auth_hits else "ok"))
    rows.append(("Names a human next step", bool(re.search(r"qualified|human|reviewer|engineer", text, re.I)) and "## 7" in text, "section 7 present with reviewer wording"))
    rows.append(("States evidence gaps", bool(re.search(r"##\s*6\.[\s\S]{40,}", text)), "section 6 has content"))
    return pd.DataFrame(rows, columns=["check", "pass", "detail"])


RUBRIC = ["Problem understanding", "Data use", "AI / RAG use", "Evidence & explainability", "Governance & human oversight"]


def judge_briefing(client, text: str, model: str | None = None) -> dict:
    """Optional LLM-as-judge using the course rubric (1-5 per dimension). A second opinion, not ground truth."""
    system = ("You grade an A-001 decision-support briefing against a 5-dimension rubric, each scored 1-5: "
              + "; ".join(RUBRIC) + ". Return JSON: {\"scores\": {<dimension>: <int>}, \"strongest\": str, \"weakest\": str, \"fix\": str}.")
    raw = ask(client, text, system=system, model=model, json_mode=True)
    try:
        return json.loads(raw)
    except Exception:
        return {"raw": raw}

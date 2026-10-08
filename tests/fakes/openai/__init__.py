"""Offline stand-in for the OpenAI SDK, used ONLY by tests/run_notebooks.py.

It lets us run every notebook end to end without an API key. It checks that the code paths work
(tool-call loops, JSON parsing, retrieval, checks). It does NOT test answer quality.
"""
import hashlib, json, re
from types import SimpleNamespace as NS

DIM = 256
def _vec(text):
    v = [0.0] * DIM
    for w in re.findall(r"[a-z0-9\-]+", text.lower()):
        h = int(hashlib.md5(w.encode()).hexdigest(), 16)
        v[h % DIM] += 1.0
    return v

class _Embeddings:
    def create(self, model, input):
        return NS(data=[NS(embedding=_vec(t)) for t in input])

def _last_user(messages):
    for m in reversed(messages):
        if m["role"] == "user":
            return m["content"] or ""
    return ""

def _tool_names(tools):
    return [t["function"]["name"] for t in (tools or [])]

def _call(i, name, args):
    return NS(id=f"call_{i}_{name}", function=NS(name=name, arguments=json.dumps(args)))

BRIEFING = """## 1. Situation
A-001 shows rising vibration. [A001-CMR-2026-08]
## 2. Structured evidence
asset_360 health score 68.05; open work orders in work_orders.
## 3. Predictive / analytical evidence
Forecast is a statistical extrapolation, not a diagnosis.
## 4. Document evidence
Current approved procedure is [A001-PROC-INS-001-V2]. The draft [A001-PROC-INS-001-V3D] is a DRAFT and not authoritative.
## 5. Assessment
Evidence supports a qualified review. It does not identify a failure mode and does not authorise replacement.
## 6. Evidence gaps / uncertainty
Source of the wet area is not confirmed [CR-2026-0819-A001]. Downtime cost is unknown in the packet.
## 7. Recommended human next step
A qualified reliability reviewer should confirm monitoring frequency using [A001-PROC-INS-001-V2].
## 8. Sources used
asset_360, work_orders, a001_sensor_hourly_90d, A001-PROC-INS-001-V2, A001-CMR-2026-08
"""

class _Completions:
    def create(self, model=None, messages=None, tools=None, tool_choice=None, response_format=None, reasoning_effort=None, **kw):
        sysmsg = next((m["content"] for m in messages if m["role"] == "system"), "") or ""
        user = _last_user(messages)
        n_tool_msgs = sum(1 for m in messages if m["role"] == "tool")
        names = _tool_names(tools)
        called = [m["tool_calls"][0]["function"]["name"] for m in messages if m["role"] == "assistant" and m.get("tool_calls")]
        content, tool_calls = None, None
        if tools:
            low = user.lower()
            if "delete" in low or "authorise replacement" in low:
                if "sql_query" in names and "delete" in low and not called:
                    tool_calls = [_call(0, "sql_query", {"query": "DELETE FROM work_orders"})]
                else:
                    content = "I cannot authorise that. A qualified human reviewer must decide."
            elif not called:
                tool_calls = []
                if "sql_query" in names:
                    tool_calls.append(_call(0, "sql_query", {"query": "SELECT asset_id, health_score, risk_level FROM asset_360 WHERE asset_id='A-001'"}))
                if "list_flagged_assets" in names and "isolate" not in low:
                    tool_calls.append(_call(5, "list_flagged_assets", {"days": 7, "top": 5}))
                if "search_documents" in names:
                    tool_calls.append(_call(1, "search_documents", {"query": user[:200], "only_approved": True}))
                if not tool_calls and "forecast" in names:
                    tool_calls.append(_call(2, "forecast", {}))
            elif "request_human_review" in names and "queue" in low and "request_human_review" not in called:
                tool_calls = [_call(6, "request_human_review", {"asset_id": "A-001", "reason": "Top flagged and top priority asset"})]
            elif "forecast" in names and "forecast" not in called and ("trend" in low or "review" in low or "rising" in low or "forecast" in low):
                tool_calls = [_call(3, "forecast", {})]
            elif "submit_for_human_review" in names and "submit_for_human_review" not in called:
                tool_calls = [_call(4, "submit_for_human_review", {"summary": "Prepare qualified review of A-001.", "evidence_ids": "asset_360, A001-PROC-INS-001-V2"})]
            else:
                content = "FAKE AGENT ANSWER. Database: asset_360. Document: [A001-PROC-INS-001-V2] APPROVED. A qualified human decides."
        elif response_format:
            if "skill" in sysmsg.lower() and "catalog" in sysmsg.lower():
                content = json.dumps({"skill": "asset_summary", "why": "fake"})
            elif "rubric" in sysmsg.lower():
                content = json.dumps({"scores": {d: 4 for d in ["Problem understanding", "Data use", "AI / RAG use", "Evidence & explainability", "Governance & human oversight"]}, "strongest": "x", "weakest": "y", "fix": "z"})
            elif "score" in user.lower() and "expected behaviour" in user.lower():
                content = json.dumps({"score": 4, "reason": "fake"})
            elif "work-order" in sysmsg.lower():
                content = json.dumps({"items": [{"work_order_id": "WO-00001", "priority": "URGENT", "issue_type": "VIBRATION", "needs_urgent_attention": True}]})
            elif "label each description" in sysmsg.lower():
                n = len(re.findall(r"^\d+:", user, re.M))
                content = json.dumps({"labels": {str(i): "VIBRATION" for i in range(n)}})
            else:
                content = json.dumps({})
        else:
            if "write one sqlite select" in sysmsg.lower():
                content = "SELECT asset_id, asset_name, health_score FROM asset_360 WHERE criticality='HIGH' ORDER BY health_score LIMIT 5"
            elif "eight markdown sections" in sysmsg.lower() or "EXACTLY these eight" in sysmsg:
                content = BRIEFING
            elif "reply with the single word" in user.lower():
                content = "ok"
            else:
                content = "FAKE ANSWER: " + user[:80].replace("\n", " ")
        msg = NS(content=content, tool_calls=tool_calls or None, role="assistant")
        return NS(choices=[NS(message=msg)])

class OpenAI:
    def __init__(self, api_key=None, **kw):
        self.chat = NS(completions=_Completions())
        self.embeddings = _Embeddings()

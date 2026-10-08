import nbformat as nbf
nb = nbf.v4.new_notebook(); C = []
md = lambda s: C.append(nbf.v4.new_markdown_cell(s)); code = lambda s: C.append(nbf.v4.new_code_cell(s))

md("""# ENEC 2026 · Optional extension 3 · Security Logs: Investigate and Detect

**Time:** about 50 minutes  |  **Optional:** homework or early-finisher work. Day 1 itself runs in Copilot  |  **Runs in:** Google Colab (free tier)  |  **Needs:** nothing else. No OpenAI key is required for this notebook.

**Data:** the same synthetic Asset 360 plant, plus a simulated security layer: login logs, firewall flow records, controller commands, SIEM alerts, vulnerabilities and access reviews. The logs cover 2026-07-27 to 2026-08-25 on the plant gateways (the remote and monitoring paths to each asset).

**Why this notebook exists:** the cohort mixes OT security, IT security, delivery, integration, architecture and development roles. One dataset serves all of them:

| Perspective | Question the data answers |
|---|---|
| Operations | Which assets behave abnormally? |
| Application / delivery | Which assets and systems need attention first? |
| Cybersecurity | Which critical assets also carry security exposure, and what do the logs show? |
| Management | What should be prioritised overall? |

> Training notice: everything here is simulated. Nothing is an incident finding, an engineering diagnosis or an authorisation. A qualified human decides.""")
code("""import os, sys, subprocess
REPO_URL = "https://github.com/Decoding-Data-Science/enec2026oct"
IN_COLAB = os.path.isdir("/content") and "google.colab" in sys.modules
ROOT = "/content/enec2026oct" if IN_COLAB else os.getcwd()
if IN_COLAB and not os.path.isdir(ROOT):
    r = subprocess.run(["git", "clone", "--depth", "1", REPO_URL, ROOT], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("Could not clone the course repo:\\n" + r.stderr[-300:] + "\\nFallback: upload enec2026oct.zip in the Files panel, run  !unzip -q enec2026oct.zip -d /content  and run this cell again.")
sys.path.insert(0, os.path.join(ROOT, "colab"))
import enec_colab as enec
import pandas as pd, matplotlib.pyplot as plt
pd.set_option("display.width", 200); pd.set_option("display.max_columns", 30)
print("Course files ready at:", enec.ROOT)""")

md("""## 1. Meet the security data

`enec.make_db()` now loads the security tables into the same in-memory SQLite database as Asset 360, so you can join logs to assets with plain SQL.""")
code("""tables = enec.load_tables()
con = enec.make_db(tables)
sec = [t for t in tables if t.startswith("security_") or t in ("asset_security", "asset_priority_view")]
pd.DataFrame({"table": sec, "rows": [len(tables[t]) for t in sec], "columns": [len(tables[t].columns) for t in sec]})""")
md("""Three families of data:
- **Posture (per asset):** `asset_security`, `security_vulnerabilities`, `security_access_review`, `asset_priority_view`.
- **Raw logs (events):** `security_auth_logs`, `security_network_flows`, `security_controller_commands`.
- **Detections:** `security_alerts` (rules run over the logs) and `security_incidents` (cases opened by analysts).

The eight columns added to Asset 360 live in `asset_security`: criticality (4 levels), security risk level, last review date, open issues, access risk flag, patch status, network exposure and incident in the last 90 days.""")
code("""enec.run_sql(con, \"\"\"
SELECT a.asset_id, a.asset_name, s.Asset_Criticality, a.health_score, a.risk_level,
       s.Security_Risk_Level, s.Open_Security_Issues, s.Patch_Status, s.Network_Exposure,
       s.Access_Risk_Flag, s.Security_Incident_Last_90_Days
FROM asset_360 a JOIN asset_security s USING (asset_id)
WHERE a.asset_id IN ('A-001','A-033')\"\"\")""")

md("""## 2. One dataset, four perspectives

Same tables, different questions. Run each query and notice how the rule changes the answer.""")
code("""# Operations: which assets show abnormal behaviour? (health risk above LOW, or 3+ urgent open work orders)
ops = enec.run_sql(con, \"\"\"SELECT asset_id, Asset_Criticality, health_score, risk_level, high_priority_open_work, Sensor_Anomalies_90d
FROM asset_priority_view WHERE Ops_Attention_Flag='Yes' ORDER BY health_score\"\"\", max_rows=60)
print(len(ops), "assets need operational attention"); ops.head(8)""")
code("""# Cybersecurity: Critical assets with an overdue patch
enec.run_sql(con, \"\"\"SELECT asset_id, Asset_Criticality, Patch_Status, Network_Exposure, Open_Security_Issues, Access_Risk_Flag
FROM asset_security WHERE Asset_Criticality='Critical' AND Patch_Status='Overdue' ORDER BY Open_Security_Issues DESC\"\"\")""")
code("""# Management: the combined priority list
enec.run_sql(con, "SELECT Priority_Rank, asset_id, Asset_Criticality, Ops_Attention_Flag, Security_Risk_Level, Priority_Score, Priority_Band FROM asset_priority_view ORDER BY Priority_Rank LIMIT 10")""")
code("""# The cross-discipline question an AI agent will answer on Day 3
target = enec.run_sql(con, \"\"\"SELECT p.asset_id, p.Asset_Criticality, p.health_score, p.Sensor_Anomalies_90d, p.high_priority_open_work,
       p.Open_Security_Issues, p.Patch_Status, p.Network_Exposure
FROM asset_priority_view p
WHERE p.Asset_Criticality IN ('High','Critical') AND p.Ops_Attention_Flag='Yes' AND p.Open_Security_Issues > 0
ORDER BY p.Priority_Rank\"\"\")
target""")
md("""Compare this with the Operations list. A risk rating on operations alone would have shown only two assets with a non-LOW health risk. Combining operations and security gives a different, longer and more useful list. That is the argument for one connected dataset.""")

md("""## 3. Investigate A-001 from the raw logs

The incident table says A-001 has two recent events: an off-hours vendor session (2026-07-30) and a failed-login burst (2026-08-14, still open). Reconstruct each from the logs, then ask what the evidence does and does not prove.""")
code("""print(enec.run_sql(con, "SELECT incident_id, detected_date, incident_type, severity, status FROM security_incidents WHERE asset_id='A-001' ORDER BY detected_date"))
print(); print(enec.run_sql(con, "SELECT alert_id, alert_time, rule_id, severity, evidence_summary, status FROM security_alerts WHERE asset_id='A-001' ORDER BY alert_time", max_rows=50))""")
code("""# Unified timeline: logins, controller commands and alerts around the vendor session
timeline = enec.run_sql(con, \"\"\"
SELECT event_time, 'AUTH' AS source, username, event_type || ' ' || source_ip || ' mfa=' || mfa_used AS detail
FROM security_auth_logs WHERE asset_id='A-001' AND event_time BETWEEN '2026-07-30 01:30:00' AND '2026-07-30 04:00:00'
UNION ALL
SELECT event_time, 'COMMAND', username, command_type || ' ' || parameter || ' ticket=' || COALESCE(change_ticket_id,'none') || ' in_window=' || within_change_window
FROM security_controller_commands WHERE asset_id='A-001' AND event_time BETWEEN '2026-07-30 01:30:00' AND '2026-07-30 04:00:00'
UNION ALL
SELECT alert_time, 'ALERT', rule_id, evidence_summary FROM security_alerts WHERE asset_id='A-001' AND alert_time BETWEEN '2026-07-30 01:30:00' AND '2026-07-30 04:00:00'
ORDER BY event_time\"\"\", max_rows=60)
timeline""")
md("""**Read it like an analyst.** A shared account (`vendor_support01`) signed in at 02:14 with no MFA from an unknown country, ran read-only configuration dumps, then wrote a setpoint with change ticket `CHG-0412` outside the change window. The ticket exists, so is it approved? The window says no. This needs a human to check the ticket, not a model to decide.""")
code("""burst = enec.run_sql(con, \"\"\"
SELECT source_ip, COUNT(*) AS failures, MIN(event_time) AS first_seen, MAX(event_time) AS last_seen,
       COUNT(DISTINCT username) AS accounts_tried
FROM security_auth_logs
WHERE asset_id='A-001' AND event_type='LOGIN_FAILURE' AND event_time >= '2026-08-14' AND event_time < '2026-08-15'
GROUP BY source_ip\"\"\")
print(burst)
print(enec.run_sql(con, \"\"\"SELECT COUNT(*) AS successful_logins_from_that_ip FROM security_auth_logs
WHERE asset_id='A-001' AND source_ip='203.0.113.45' AND event_type='LOGIN_SUCCESS'\"\"\"))""")
md("""**What the logs support:** 34 failed logins from one external address in about 20 minutes, against several accounts. **What they do not show:** any successful login from that address. So there is evidence of an attempt, and no evidence of a compromise. Say exactly that.

Now the operational side. Did anything on the controller change around the time vibration began to rise?""")
code("""h = pd.read_csv(enec.ROOT / "data" / "csv" / "a001_sensor_hourly_90d.csv", parse_dates=["hour_timestamp"])
daily = h[h.hour_timestamp >= "2026-07-27"].set_index("hour_timestamp").resample("D").agg({"avg_vibration_mm_s": "mean", "anomaly_minutes": "sum"})
cmds = enec.run_sql(con, "SELECT event_time, username, command_type, change_ticket_id, within_change_window FROM security_controller_commands WHERE asset_id='A-001' AND command_type<>'READ' AND event_time >= '2026-08-01' ORDER BY event_time", max_rows=60)
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(daily.index, daily.avg_vibration_mm_s, color="#1f77b4", label="daily mean vibration (mm/s)")
for t in ["2026-07-30", "2026-08-14"]:
    ax.axvline(pd.Timestamp(t), color="#d62728", ls="--"); ax.text(pd.Timestamp(t), ax.get_ylim()[1]*0.97, " security event", color="#d62728", fontsize=8, va="top")
ax.set_title("A-001 vibration with security events"); ax.legend(); plt.show()
cmds""")
md("""Every controller change that carries a ticket is linked to a plant work order (`work_order_id`). Follow the link to see what work backed each change. In a real plant the ticket system would carry this key; here the link is simulated.""")
code("""enec.run_sql(con, \"\"\"SELECT c.event_time, c.username, c.command_type, c.change_ticket_id, w.work_order_id, w.work_type, w.priority, w.status AS wo_status
FROM security_controller_commands c LEFT JOIN work_orders w ON w.work_order_id = c.work_order_id
WHERE c.asset_id='A-001' AND c.command_type<>'READ' AND c.event_time >= '2026-07-29' ORDER BY c.event_time\"\"\", max_rows=40)""")
md("""**Honest reading.** Vibration was already climbing before either security event: the daily mean rises from about 1.4 mm/s on 2026-07-21 to 2.5 on 07-30 (the vendor session) and about 4.2 on 08-14 (the login burst). Anomaly flags start on 08-18. Nothing in the logs connects the external address to any controller change. Three controller changes after 08-01 lack a ticket (08-06, 08-07, 08-17), all from named staff accounts on internal addresses; the 08-17 alarm-threshold update was closed as a false positive with no recorded reason, and it is worth a question to its owner. The data supports an attempted intrusion and a policy breach by the vendor session, and does not support a cyber cause for the vibration. Engineering owns that question.

Write the evidence in three columns before you leave this section: **supports**, **contradicts**, **unknown**.""")

md("""## 4. Detection rules and alert fatigue

SIEM rules are thresholds over logs. Too low and analysts drown; too high and attacks pass. Look at what the rules produced.""")
code("""al = enec.run_sql(con, "SELECT rule_id, rule_name, COUNT(*) AS alerts, SUM(status='Closed - false positive') AS closed_fp, SUM(status='Escalated') AS escalated FROM security_alerts GROUP BY rule_id, rule_name ORDER BY alerts DESC")
al""")
code("""# Tune one rule: failed logins per 15-minute window. Compare against the simulation's ground truth label.
w = pd.read_csv(enec.ROOT / "data" / "security" / "security_log_windows.csv", parse_dates=["window_start"])
bf = w.attack_type.isin(["Brute_force", "Credential_spray"])
rows = []
for t in [3, 5, 8, 12, 20, 30]:
    flag = w.auth_failures >= t
    tp = int((flag & bf).sum()); fp = int((flag & ~bf).sum()); fn = int((~flag & bf).sum())
    rows.append({"threshold": t, "alerts": int(flag.sum()), "caught": tp, "false_alarms": fp, "missed": fn,
                 "recall": round(tp / (tp + fn), 2), "precision": round(tp / max(tp + fp, 1), 2)})
pd.DataFrame(rows)""")
md("""There is no perfect threshold. Pick one and defend it: how many false alarms can your analysts absorb, and which missed attack hurts most? On Day 3 a decision tree learns several thresholds at once.""")

md("""## 5. From logs to features

A model cannot read raw logs. We turn them into one row per gateway per 15-minute window. Rebuild three of the features yourself and check them against the prepared table, so you know where each number comes from.""")
code("""auth = pd.read_csv(enec.ROOT / "data" / "security" / "security_auth_logs.csv", parse_dates=["event_time"])
mine = (auth[auth.event_type == "LOGIN_FAILURE"].assign(window_start=lambda d: d.event_time.dt.floor("15min"))
        .groupby(["asset_id", "window_start"]).size().rename("my_auth_failures").reset_index())
chk = w.merge(mine, on=["asset_id", "window_start"], how="left").fillna({"my_auth_failures": 0})
print("windows:", len(w), "| mismatches in auth_failures:", int((chk.auth_failures != chk.my_auth_failures).sum()))
pd.concat([w[w.is_attack == 0].sample(3, random_state=1), w[w.is_attack == 1].sample(3, random_state=1)])""")
md("""Windows exist only where something was logged (a gateway with no events in a quarter-hour has no row). Attack episodes in this simulation are injected on purpose and are far more frequent than in a real plant; the share of attack windows is still small, as it is in practice.""")

md("""## 6. Next: the decision tree (Day 3)

You now know what the 16 features mean and where each number comes from. Training, judging and using a decision tree on these windows is **Day 3**: `Day_3_Agentic_AI/Day3_02_Decision_Tree_as_an_Agent_Tool.ipynb`, where the model becomes a read-only tool that an agent can call.

Before then, you can already beat a naive baseline by hand: pick a threshold in Part 4 and defend it.""")
md("""## 8. Choose your lane

Open `resources/PARTICIPANT_ROLES_GUIDE.md` (in the repo) for a task card matched to your role: incident preparedness, OT assurance, security services, project management, delivery, integration, development and architecture. Each card names the tables to use, the question to answer and what a good answer looks like.

### Boundaries
The model flags windows and the rules raise alerts. Neither blocks traffic, isolates an asset, closes an incident or approves a change. A qualified human decides, and the decision is recorded.

### Honest limits
All data is simulated. Attack frequency is exaggerated for teaching. Only A-001 has real sensor anomalies, so other assets use health risk and urgent work orders as the operational signal.""")
nb.cells = C
nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}, "colab": {"provenance": []}}
nbf.write(nb, "Optional_Colab_Extensions/Ext03_Security_Logs_Investigate_and_Detect.ipynb")

# Participant Roles Guide: one dataset, a lane for every role

One connected dataset serves every role: Asset 360 plus a simulated security layer. On **Day 1** you work on it in **Microsoft Copilot** with the Excel workbooks in `data/excel` (exercises `resources/COPILOT_EXERCISES.md`). Cards that mention retraining or a feature belong to **Day 3** (`Day3_02_Decision_Tree_as_an_Agent_Tool`); the optional `Ext03_Security_Logs_Investigate_and_Detect` notebook supports the investigation cards. This guide gives each role in the cohort a task card: where to spend your time and what to hand in at the end of the day.

All data is simulated. Vulnerability IDs (`SYN-2026-xxxx`) are fictional. Logs cover 2026-07-27 to 2026-08-25 on the plant gateways. Nothing here is an engineering diagnosis or an approval; a qualified human decides.

## The data in one view
| Family | Tables | Use it to |
|---|---|---|
| Posture | `asset_security`, `security_vulnerabilities`, `security_access_review`, `asset_priority_view` | rank, prioritise, track remediation |
| Raw logs | `security_auth_logs`, `security_network_flows`, `security_controller_commands` | investigate and engineer features |
| Detections | `security_alerts`, `security_incidents` | triage, tune, measure noise |
| Reference | `security_accounts`, `security_network_zones`, `security_documents` | roles, trust zones, governing documents |
| Model data | `security_log_windows` (15-minute features and labels) | decision tree and rule tuning |
| Operations | `asset_360`, `a001_sensor_hourly_90d`, `work_orders` | tie security to plant condition |

Governing documents (`documents/security/`): patch standard V2 (APPROVED), V1 (SUPERSEDED), V3D (DRAFT; its 72-hour target is not in force), remote and vendor access policy, incident triage runbook.

## Role cards

### 1. Cyber Security Incident Preparedness Specialist
- Lane: investigation and readiness.
- Task: reconstruct the A-001 vendor session (2026-07-30) and the login burst (2026-08-14) as timelines from the three raw log tables. Write supports / contradicts / unknown.
- Then: compare your steps with the incident triage runbook. Which questions could not be answered from the logs? Those are your preparedness gaps.
- Hand in: one-page timeline plus a list of five missing data sources or fields.

### 2. Applications Delivery and Support, Plant Support
- Lane: which plant applications and assets need attention.
- Task: from `asset_priority_view` list assets with urgent open work and open security issues together. Group by `system_name` and `unit_id`.
- Hand in: the top five systems and a one-line support action for each (who to call, what to check).

### 3. Senior IT Cyber Security Assurance and Risk Specialist
- Lane: control gaps and risk ranking.
- Task: join `security_vulnerabilities` with the patch standard V2. Count open items past their due date by severity, then identify where the draft V3D would change the answer and explain why it cannot be used.
- Then: check `security_access_review` against the remote access policy (shared accounts, privileged without MFA, stale accounts).
- Hand in: top ten risks with evidence and the policy clause each breaches.

### 4. Technical Security Services Lead
- Lane: detection engineering.
- Task: in section 4, find a threshold for the failed-login rule that your analysts can live with. Then review `security_alerts` by rule: which rule is the noisiest, and what would you change?
- Then: train the tree and read its rules. Which rule would you turn into a SIEM detection?
- Hand in: a proposed threshold per rule with recall, precision and expected daily alert volume.

### 5. Integration Lead
- Lane: joins, lineage and interfaces.
- Task: rebuild two more window features from the raw logs (section 5) and prove they match `security_log_windows`. Sketch the interface a SIEM, a historian and the asset system would need to feed this table every 15 minutes.
- Hand in: the join keys, refresh cadence, and three data quality checks (missing hours, duplicate events, clock skew).

### 6. Software Development Lead
- Lane: model and code quality.
- Task: add one feature (for example failures per user), retrain, and compare recall and precision. Explain why the notebook splits by time and not at random.
- Then: wrap scoring in a function with tests (empty window, missing column).
- Hand in: the function, two tests, and a note on drift monitoring.

### 7. Applications Delivery Specialist, Corporate (three participants)
- Lane: corporate application and access view.
- Task: use `security_accounts` and `security_auth_logs` to list which roles reach plant gateways, from which zones, and with or without MFA. Identify accounts that should not exist (shared, stale).
- Hand in: an access matrix by role and zone, and the three accounts you would review first.

### 8. Cyber Security Project Manager
- Lane: prioritisation and remediation plan.
- Task: build a four-week remediation plan from `asset_priority_view` and `security_vulnerabilities`, respecting the rule that OT patches need a maintenance window (read the patch standard, section 3).
- Hand in: plan with owners, dates, dependencies and the top three delivery risks.

### 9. Head of OT Cyber Security Assurance and Risk
- Lane: assurance and governance.
- Task: review all controller changes without a ticket or outside a window (`security_controller_commands`, alert rule R-OT-01). What share are explained? Choose five controls you would audit and state the evidence you would want.
- Then: decide what the AI assistant may and may not do in this process (prepare evidence vs decide). Write it as a short boundary statement.
- Hand in: assurance questions list and the boundary statement.

### 10. Senior OT Cyber Security Assurance and Risk Specialist
- Lane: OT risk on critical assets.
- Task: filter Critical assets with `Network_Exposure` of Restricted or External. Cross-check patch status, access risk flag and recent incidents. For A-001, explain why a security fix needs an operations conversation (health score 68, open urgent work).
- Hand in: risk statement for A-001 with likelihood, impact, existing controls and the human decision required.

### 11. PM Delivery Specialist, Plant Operations (two participants)
- Lane: operations meets security.
- Task: for the assets in `Ops_Attention_Flag = 'Yes'` that also have open security issues, list what each needs from operations (window, shutdown, spare). Rank by `Priority_Score`.
- Hand in: a one-page schedule proposal for the top five assets.

### 12. Senior Domain Architect Specialist, Corporate
- Lane: architecture.
- Task: map the data flow from gateway to log table to feature to model to analyst using `security_network_zones` (Purdue-style levels). Mark where the AI components sit and where a human approval is mandatory.
- Hand in: a one-page diagram with trust boundaries, plus three architectural risks (single points of failure, data exposure, model drift).

## Cross-role questions for the plenary
1. Which Critical assets also show operational stress and open security issues? (Run the target query.)
2. For A-001, what do the logs support, contradict and leave unknown?
3. Which detection rule would you retire first, and why?
4. Who approves a patch on a running pump, and what does the AI prepare for them?

## Level up (optional)
- Predict `attack_type` instead of `is_attack` and read the confusion matrix.
- Try IsolationForest on the same features, without labels.
- Day 3: ask the agent *Show me high-criticality assets with abnormal operational readings and unresolved security issues.* Compare its answer with your SQL.

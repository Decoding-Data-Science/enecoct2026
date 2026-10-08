# A001-TSG-001 — Troubleshooting and Diagnostic Guide

> **Synthetic training document.** This Markdown file is a browseable text mirror of the original PDF used in the ENEC 2026 A-001 RAG corpus. The original PDF is included in the companion data/PDF download pack.

---

<PARSED TEXT FOR PAGE: 1 / 2>NORTHSTAR PROCESS FACILITY SYNTHETIC TRAINING CORPUS
A001-TSG-001 | APPROVED | Synthetic training document - not for operational use
Page 1
A001-TSG-001 / APPROVED
A-001 Troubleshooting and Diagnostic Guide
A-001 | Cooling Water Pump | Enterprise Asset Reliability Training Scenario
Document ID A001-TSG-001 Version 1.2
Status APPROVED Effective / Issue Date 2026-04-10
Owner Reliability Engineering Asset A-001
Location Utilities Area - Bay 3 Data Class Synthetic / Training
TRAINING NOTICE: This fictional document is designed only for AI/RAG, analytics and governance training. It is not
an engineering instruction and must not be used on real equipment.
1. Purpose
This guide supports structured troubleshooting discussions for common symptom patterns in the synthetic 
A-001 scenario. It is not a substitute for the current inspection procedure or qualified engineering 
judgment.
2. Symptom-to-Evidence Matrix
Observed symptom Possible evidence to inspect Common data-quality question
Rising vibration Vibration trend, recent work, inspection 
notes
Is the sensor stable and timestamp 
aligned?
Elevated temperature Temperature trend, load context, 
maintenance history Are missing values or outliers present?
Reduced discharge pressure Pressure/flow history, operator notes Is the process context comparable?
Intermittent alarm Alarm timestamps, sensor trend, work 
history Is the alarm repeated or isolated?
Visible leakage note Inspection report, work order, recent 
maintenance
Is the observation current and asset-tag 
verified?
3. Troubleshooting Logic
1. Confirm the symptom is supported by a record, not only a generated summary.
2. Inspect the trend rather than only the latest point.
3. Check whether recent maintenance could explain a temporary change.
4. Look for corroborating evidence from another source type.
5. If evidence conflicts, preserve the conflict and escalate for review.
6. Use the current approved inspection procedure for the formal review workflow.<PARSED TEXT FOR PAGE: 2 / 2>NORTHSTAR PROCESS FACILITY SYNTHETIC TRAINING CORPUS
A001-TSG-001 | APPROVED | Synthetic training document - not for operational use
Page 2
4. What This Guide Does Not Do
 It does not prescribe component replacement.
 It does not define real-world alarm or trip thresholds.
 It does not authorize shutdown or restart.
 It does not override the approved inspection procedure.
 It does not convert an AI prediction into a maintenance decision.
5. Example Troubleshooting Questions
 What evidence should be checked when vibration rises?
 What should I check before trusting a temperature spike?
 Does a visible leakage note prove the cause of vibration?
 Which document defines the formal inspection workflow?
6. Evidence Combination Examples
Evidence combination Interpretation discipline
Rising vibration + open inspection work Supports review priority; does not establish root cause.
Noise observation + stable sensor trend Keep both; investigate the disagreement.
Wet area + pressure change Potentially related, but source and timing must be verified.
High health-risk score only Analytics signal; retrieve underlying measurements before 
acting.
7. Escalation Patterns
 Multiple independent sources point to the same worsening condition.
 The current approved procedure cannot be identified confidently.
 A required data source is missing or stale.
 A written observation conflicts with structured measurements.
 A user asks the AI to turn troubleshooting evidence directly into an operational instruction.
8. Source Selection Reminder
Use this troubleshooting guide to decide what evidence to inspect. Use A001-PROC-INS-001-V2 to answer 
questions about the formal inspection workflow, and REL-POL-001 for enterprise escalation requirements.

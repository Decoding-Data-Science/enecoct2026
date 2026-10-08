# SEC-PROC-INC-001 - Security Incident Triage Runbook (APPROVED)

> Synthetic training document. Not for operational use.

Document ID: SEC-PROC-INC-001 | Version 1.0 | Status: APPROVED | Effective: 2025-11-15 | Owner: Plant Cyber Security

## 1. Triage questions
1. Which asset or gateway is affected, and how critical is it?
2. Is the traffic pattern consistent with a known benign cause (maintenance window, vendor task, typing errors)?
3. Is there an operational signal at the same time (abnormal sensor behaviour, control change)?

## 2. Severity guide
- Low: single indicator, no operational signal.
- Medium: two indicators or one indicator on a Critical or High asset.
- High: confirmed unauthorised access or change, or any indicator with an operational signal.

## 3. Actions and limits
Triage may recommend containment steps. Isolating an asset, blocking an address or stopping a process is decided and executed by the on-duty security lead together with the operations shift supervisor. An automated tool or model output is never the approval.
A false positive is recorded with the reason so the detection rules can be tuned.

# SEC-STD-DETECT-001 - Detection Rule Catalogue and Tuning Rules (APPROVED)

> Synthetic training document. Not for operational use.

Document ID: SEC-STD-DETECT-001 | Version 1.0 | Status: APPROVED | Effective: 2025-12-01 | Owner: Technical Security Services

## 1. Rule catalogue
| Rule | Name | Condition | Severity |
|---|---|---|---|
| R-AUTH-01 | Repeated failed logins from one source | 8 or more failures from one source address within 30 minutes | Medium; High at 25 or more |
| R-AUTH-02 | Remote login without MFA | Successful login from the DMZ or outside without MFA | Medium; High if off hours |
| R-NET-01 | Port scan from unapproved source | 10 or more distinct destination ports from one unapproved source in 15 minutes | Medium |
| R-NET-02 | Connection flood from many sources | 40 or more flows from 15 or more sources in 15 minutes | High |
| R-NET-03 | Large outbound transfer to external address | More than 30 MB to an external address | High |
| R-OT-01 | Controller change without ticket or outside window | A state-changing command with no ticket, or outside the approved change window | High |

## 2. Alert handling
1. Every alert is triaged by an analyst and given a status: Open, Triaged, Escalated or Closed - false positive.
2. Closing an alert as a false positive requires a recorded reason. An alert closed without a reason is reopened at the next review.
3. An escalated alert is linked to an incident.

## 3. Tuning
1. A threshold change needs a recorded comparison of alerts, missed events and false alarms before and after.
2. Approved scans and backups are excluded by named source address, not by lowering severity.
3. Tuning is approved by the Technical Security Services Lead. A model or a script proposes; a person approves.

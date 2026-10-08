# A001-SEC-2026-08 - A-001 Security Posture Review, August 2026 (APPROVED)

> Synthetic training document. Not for operational use.

Document ID: A001-SEC-2026-08 | Version 1.0 | Status: APPROVED | Effective: 2026-08-25 | Owner: Plant Cyber Security | Asset: A-001 (Pump 001, Cooling Water, unit TRN-A)

## 1. Summary
A-001 is classed Critical and has Restricted network exposure. Its last security review was on 2026-01-23, which is 214 days before this review and past the 180-day target. Patch status is Overdue and the access risk flag is Yes.

## 2. Open vulnerabilities
| ID | Issue | CVSS | Due | Status |
|---|---|---|---|---|
| SYN-2026-0169 | Outdated firmware on condition-monitoring gateway | 7.8 | 2026-07-29 | Open, overdue |
| SYN-2026-0170 | Default credentials on local HMI | 8.2 | 2026-08-06 | Open, overdue |
| SYN-2026-0171 | Remote vendor session without recording | 4.6 | 2026-09-05 | In remediation |

Remediation targets follow SEC-PROC-PATCH-001 Version 2.0 (High within 14 days).

## 3. Access
Nine accounts reach the gateway; three are privileged, one is a shared vendor account without MFA, and two are stale. The last access review was 2026-01-31.

## 4. Incidents and alerts
- SEC-INC-0041 (2026-07-30, High, Contained): off-hours vendor session through the shared vendor account without MFA. A controller setpoint change under ticket CHG-0412 ran outside the change window.
- SEC-INC-0040 (2026-08-14, Medium, Open): 34 failed logins from one external address within about 20 minutes. No successful login from that address is recorded.

## 5. Operational context
Health score 68.05 (risk MEDIUM), three urgent open work orders, and anomaly flags on vibration from 2026-08-18. The logs reviewed do not connect any external address to a controller change. Any cause of the vibration is an engineering question.

## 6. Evidence gaps
- The ticket CHG-0412 has no recorded approval inside the change window.
- One alarm-threshold update on 2026-08-17 had no ticket and was closed as a false positive without a recorded reason.
- Sensor detail beyond hourly data is not available for the gateway itself.

## 7. Human next step
The Plant Cyber Security lead, with the A-001 engineering owner and the shift supervisor, decides on remediation timing, any access change and any isolation. This review does not authorise any of these.

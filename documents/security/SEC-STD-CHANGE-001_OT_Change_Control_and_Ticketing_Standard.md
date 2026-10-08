# SEC-STD-CHANGE-001 - OT Change Control and Ticketing Standard (APPROVED)

> Synthetic training document. Not for operational use.

Document ID: SEC-STD-CHANGE-001 | Version 2.0 | Status: APPROVED | Effective: 2025-07-01 | Owner: Head of Engineering

## 1. Rule
Any command that changes controller state (setpoints, start, stop, configuration, firmware) needs a change ticket and must run inside the approved change window. Read-only commands do not need a ticket.

## 2. Change window
Approved changes run between 07:00 and 17:00 plant time. Work outside this window needs a separate emergency approval from the shift supervisor and a ticket raised within 24 hours.

## 3. Ticket content
Each change ticket carries the asset, the person making the change, the reason, and the plant work order that justifies it. The work order key is recorded in the ticket system and in the controller command log.

## 4. Vendor changes
Vendor changes use a named vendor account, MFA and a recorded session. A ticket that exists but whose change ran outside the window is treated as an exception, not as an approval.

## 5. Review
Unticketed or out-of-window changes are reviewed weekly by the engineering owner of the asset. The review records whether the change was legitimate, and the reason.

## 6. Limits
No tool or model approves a change, closes a ticket or issues a controller command.

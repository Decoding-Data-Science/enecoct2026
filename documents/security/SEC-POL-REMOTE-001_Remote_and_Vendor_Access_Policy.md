# SEC-POL-REMOTE-001 - Remote and Vendor Access Policy (APPROVED)

> Synthetic training document. Not for operational use.

Document ID: SEC-POL-REMOTE-001 | Version 1.2 | Status: APPROVED | Effective: 2025-09-01 | Owner: Plant Cyber Security

## 1. Rules
1. Every remote or vendor session to a plant asset or its gateway requires multi-factor authentication.
2. Shared accounts are prohibited. Each person uses a named account.
3. Vendor access is time-boxed, approved per task, and the session is recorded.
4. Privileged accounts are reviewed at least every 90 days. Accounts unused for 90 days are disabled.
5. Default or vendor-set credentials must be changed before an asset is connected.

## 2. Access risk flag
An asset is flagged for access risk when any of these is true: a shared account exists, a privileged account has no MFA, two or more accounts are stale, or vendor remote access exists without MFA.

## 3. Exceptions
An exception needs written approval from the Head of Engineering and expires after 30 days.

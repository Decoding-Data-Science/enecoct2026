# SEC-PROC-ACCESS-REVIEW-001 - Privileged Access Review Procedure (APPROVED)

> Synthetic training document. Not for operational use.

Document ID: SEC-PROC-ACCESS-REVIEW-001 | Version 1.0 | Status: APPROVED | Effective: 2025-09-15 | Owner: Plant Cyber Security

## 1. Scope
Applies to every account that can reach a plant asset or its gateway, including staff, vendor and service accounts. The review data is held in `security_access_review` and `security_accounts`.

## 2. Frequency
- Privileged accounts: at least every 90 days.
- All other accounts: at least every 180 days.
- An asset whose last review is older than the interval is reported as overdue for access review.

## 3. Review steps
1. List all accounts and mark privileged, shared, stale and vendor accounts.
2. A stale account is one unused for 90 days. It is disabled unless its owner confirms a reason in writing.
3. Shared accounts are not permitted (see SEC-POL-REMOTE-001). Replace each with named accounts and record the date.
4. Confirm multi-factor authentication for every privileged and vendor account.
5. Record the reviewer, the date and every exception.

## 4. Outcomes
The reviewer sets the access risk flag for the asset. The flag is Yes when a shared account exists, a privileged account has no MFA, two or more stale accounts exist, or vendor access exists without MFA.

## 5. Limits
The reviewer decides and records. An automated tool may list accounts and prepare evidence. It does not disable accounts or approve exceptions.

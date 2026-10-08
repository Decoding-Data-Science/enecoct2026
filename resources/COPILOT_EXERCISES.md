# Copilot in Excel exercises

Use the Excel workbooks in `data/excel` (or the Copilot pack zip). Work on one workbook at a time.

## Before you start
- Save the workbook to **OneDrive or SharePoint** with **AutoSave on**; Copilot in Excel does not work on files stored on your computer.
- The file must be `.xlsx` and the data must be an **Excel table** (all sheets here already are). Click inside the table before opening Copilot.
- Tables up to two million cells are supported. The largest sheets here have 14,000 to 23,000 rows; large tables can answer slowly, so ask narrow questions.
- Your Microsoft 365 licence must include Copilot. Check the current requirements on Microsoft Support.

## Exercises

| ID | Role | Workbook | Sheet | Prompt | Check your answer against |
|---|---|---|---|---|---|
| E01 | All roles | ENEC_Asset_360_Security.xlsx | Asset_360 | Which assets are Critical and have an overdue patch? Show asset_id, Network_Exposure and Open_Security_Issues, sorted by Open_Security_Issues. | 7 assets: A-001, A-065, A-010, A-110, A-097, A-098, A-070 |
| E02 | Management | ENEC_Asset_360_Security.xlsx | Asset_Priority_View | Show the top 10 assets by Priority_Score as a bar chart and explain in two sentences why the first one ranks first. | A-001 first (score 97.8): Critical, health score 68.05, 3 open issues, patch overdue, restricted exposure |
| E03 | Operations, Application | ENEC_Asset_360_Security.xlsx | Asset_Priority_View | List High and Critical assets that have Ops_Attention_Flag Yes and at least one open security issue. | 5 assets: A-001, A-040, A-033, A-109, A-115 |
| E04 | Cybersecurity | ENEC_Asset_360_Security.xlsx | Asset_360 | Create a pivot table counting assets by Asset_Criticality and Network_Exposure. Which cell is largest? | Counts by criticality x exposure: {'Critical': {'External': 1, 'Internal': 7, 'Restricted': 4}, 'High': {'External': 3, 'Internal': 16, 'Restricted': 6}, 'Low': {'External': 2, 'Internal': 20, 'Restricted': 6}, 'Medium': {'External': 4, 'Internal': 45, 'Restricted': 14}} |
| E05 | Cybersecurity, Assurance | ENEC_Asset_360_Security.xlsx | Asset_360 | Add a column Days_Since_Review using 2026-08-25 as today and highlight Critical assets over 180 days. | 1 Critical assets over 180 days: A-001 |
| E06 | Assurance, Project manager | ENEC_Asset_360_Security.xlsx | Vulnerabilities | Count overdue vulnerabilities by severity and show the five longest overdue open items. | Overdue by severity: {'Critical': 1, 'High': 24, 'Low': 1, 'Medium': 29} |
| E07 | Technical Security Services | ENEC_Asset_360_Security.xlsx | Security_Alerts | Which rule has the most alerts closed as false positives? Propose one tuning change and say what you would measure first. | R-OT-01 (52 closed as false positive), then R-AUTH-01 (17) |
| E08 | Cybersecurity, Delivery | ENEC_Asset_360_Security.xlsx | Access_Review | Which assets have a shared account and no MFA? Group them by Network_Exposure. | 5 assets: A-001, A-025, A-032, A-053, A-067 |
| E09 | Incident preparedness | ENEC_Security_Logs.xlsx | Auth_Logs | Which source address has the most LOGIN_FAILURE events against A-001, and over how many minutes? | 203.0.113.45 with 34 failures in about 20 minutes on 2026-08-14 |
| E10 | OT assurance | ENEC_Security_Logs.xlsx | Controller_Commands | How many state-changing commands (not READ) have no change ticket? Show the top 5 users. | 152 state-changing commands without a ticket |
| E11 | Cybersecurity, Architect | ENEC_Security_Logs.xlsx | Network_Flows | List flows to an External destination larger than 30 MB, with asset_id and service. | 62 flows |
| E12 | Integration, Development | ENEC_Security_Log_Windows.xlsx | Log_Windows | Compare the share of attack windows when off_hours is 1 versus 0, and name the attack types most common off hours. | Attack share: off_hours=1 3.7%, off_hours=0 0.6% |
| E13 | Development | ENEC_Security_Log_Windows.xlsx | Log_Windows | Which columns differ most between attack and normal windows? Show averages for auth_failures, distinct_dst_ports, bytes_out_kb and unapproved_commands. | Attack windows show far higher failures, ports, bytes out and unapproved commands |
| E14 | Operations | asset_360.xlsx | a001_sensor_hourly | Plot the daily average vibration for A-001 and say when the rise starts and when anomaly minutes first appear. | Rise from about 2026-07-22; anomaly minutes first appear 2026-08-18 |
| E15 | Project manager | project_360.xlsx | risks | Which five risks have the highest exposure_score? Group them by risk_category. | Compare with the sorted risks table |
| E16 | All roles | ENEC_Asset_360_Security.xlsx | Security_Incidents | Write a three-sentence status for the open incidents, ordered by severity, and list what a human must decide next. | Mentions SEC-INC-0040 (open, A-001) among open items; ends with human decisions, not actions taken by the tool |

## What to write down
For each exercise: what Copilot got right, what you had to correct, and what it could not know. Copilot prepares evidence. A person decides.

## Data note
Synthetic training data as of 2026-08-25. Security values are simulated.
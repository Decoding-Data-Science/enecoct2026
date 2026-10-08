# Documents: where they are and how to use them

All 19 documents are **synthetic training material**. They exist in two forms:

| Form | Folder | Use it for |
|---|---|---|
| **Word (.docx)** | `documents/word/` | **Day 1, Copilot chat.** Upload a file to Copilot, or store the folder in OneDrive and refer to the file by name. |
| **Markdown (.md)** | `documents/a001/` and `documents/security/` | **Day 2 onward.** The notebooks read these files for RAG. Also readable on GitHub. |

Seven further project documents for the Day 4 capstone are in `documents/project_pdfs_text/` (text). They are not part of Days 1 to 3.

## How to use a document in Copilot (Day 1)
1. Open Copilot chat with your official Microsoft account.
2. Attach the Word file (or open it in Word and use Copilot there).
3. Use a structured prompt: name the document **ID and version**, say which sections to use, and ask it to quote what it used. See `Day_1_Copilot_and_Data_Understanding/PROMPT_ENGINEERING_GUIDE.md`, examples B and prompts PE5 and PE6.

## The version traps (on purpose)
Two documents exist in three versions each. Only one version of each is authoritative.

| Document family | Authoritative | Not authoritative |
|---|---|---|
| A-001 inspection procedure `A001-PROC-INS-001` | **V2**, APPROVED | V1 SUPERSEDED, V3D DRAFT |
| Patch standard `SEC-PROC-PATCH-001` | **V2**, APPROVED, effective 2025-06-01 | V1 SUPERSEDED, V3D DRAFT |

A good answer cites V2 and says why V1 and V3D are not used.

## A-001 documents (9)

| ID | Title | Ver | Status | Effective | Owner | Markdown | Word |
|---|---|---|---|---|---|---|---|
| `REL-POL-001` | Enterprise Asset Reliability and Escalation Policy | 2.1 | **APPROVED** | 2026-07-01 | Reliability Governance Office | [md](../documents/a001/01_REL-POL-001_Enterprise_Asset_Reliability_and_Escalation_Policy.md) | [docx](../documents/word/01_REL-POL-001_Enterprise_Asset_Reliability_and_Escalation_Policy.docx) |
| `A001-OPS-001` | A-001 Operating and Usage Guide | 1.4 | **APPROVED** | 2026-05-15 | Utilities Engineering | [md](../documents/a001/02_A001-OPS-001_Operating_and_Usage_Guide.md) | [docx](../documents/word/02_A001-OPS-001_Operating_and_Usage_Guide.docx) |
| `A001-PROC-INS-001-V1` | A-001 Condition Inspection Procedure - Historical Version | 1.0 | **SUPERSEDED** | 2025-03-01 | Maintenance Engineering | [md](../documents/a001/03_A001-PROC-INS-001-V1_Superseded_Inspection_Procedure.md) | [docx](../documents/word/03_A001-PROC-INS-001-V1_Superseded_Inspection_Procedure.docx) |
| `A001-PROC-INS-001-V2` | A-001 Condition Inspection and Preventive Maintenance Procedure | 2.0 | **APPROVED** | 2026-02-01 | Maintenance Engineering | [md](../documents/a001/04_A001-PROC-INS-001-V2_Approved_Inspection_and_PM_Procedure.md) | [docx](../documents/word/04_A001-PROC-INS-001-V2_Approved_Inspection_and_PM_Procedure.docx) |
| `A001-PROC-INS-001-V3D` | A-001 Condition Inspection Procedure - Draft Revision | 3.0-draft | **DRAFT** | 2026-08-20 | Maintenance Engineering | [md](../documents/a001/05_A001-PROC-INS-001-V3D_Draft_Procedure.md) | [docx](../documents/word/05_A001-PROC-INS-001-V3D_Draft_Procedure.docx) |
| `A001-TSG-001` | A-001 Troubleshooting and Diagnostic Guide | 1.2 | **APPROVED** | 2026-04-10 | Reliability Engineering | [md](../documents/a001/06_A001-TSG-001_Troubleshooting_and_Diagnostic_Guide.md) | [docx](../documents/word/06_A001-TSG-001_Troubleshooting_and_Diagnostic_Guide.docx) |
| `A001-CMR-2026-08` | A-001 Monthly Condition Monitoring Report - August 2026 | 1.0 | **APPROVED** | 2026-08-25 | Condition Monitoring Team | [md](../documents/a001/07_A001-CMR-2026-08_Condition_Monitoring_Report.md) | [docx](../documents/word/07_A001-CMR-2026-08_Condition_Monitoring_Report.docx) |
| `WO-2026-0817` | Inspection Work Order - A-001 Elevated Vibration Review | 1.0 | **OPEN** | 2026-08-21 | Maintenance Planning | [md](../documents/a001/08_WO-2026-0817_A001_Inspection_Work_Order.md) | [docx](../documents/word/08_WO-2026-0817_A001_Inspection_Work_Order.docx) |
| `CR-2026-0819-A001` | Field Condition Report - A-001 Observation | 1.0 | **APPROVED** | 2026-08-19 | Operations Support | [md](../documents/a001/09_CR-2026-0819_A001_Field_Condition_Report.md) | [docx](../documents/word/09_CR-2026-0819_A001_Field_Condition_Report.docx) |

## Security documents (10)

| ID | Title | Ver | Status | Effective | Owner | Markdown | Word |
|---|---|---|---|---|---|---|---|
| `A001-SEC-2026-08` | A-001 Security Posture Review - August 2026 | 1.0 | **APPROVED** | 2026-08-25 | Plant Cyber Security | [md](../documents/security/A001-SEC-2026-08_A001_Security_Posture_Review.md) | [docx](../documents/word/A001-SEC-2026-08_A001_Security_Posture_Review.docx) |
| `SEC-POL-REMOTE-001` | Remote and Vendor Access Policy | 1.2 | **APPROVED** | 2025-09-01 | Plant Cyber Security | [md](../documents/security/SEC-POL-REMOTE-001_Remote_and_Vendor_Access_Policy.md) | [docx](../documents/word/SEC-POL-REMOTE-001_Remote_and_Vendor_Access_Policy.docx) |
| `SEC-PROC-ACCESS-REVIEW-001` | Privileged Access Review Procedure | 1.0 | **APPROVED** | 2025-09-15 | Plant Cyber Security | [md](../documents/security/SEC-PROC-ACCESS-REVIEW-001_Privileged_Access_Review_Procedure.md) | [docx](../documents/word/SEC-PROC-ACCESS-REVIEW-001_Privileged_Access_Review_Procedure.docx) |
| `SEC-PROC-INC-001` | Security Incident Triage Runbook | 1.0 | **APPROVED** | 2025-11-15 | Plant Cyber Security | [md](../documents/security/SEC-PROC-INC-001_Security_Incident_Response_Runbook.md) | [docx](../documents/word/SEC-PROC-INC-001_Security_Incident_Response_Runbook.docx) |
| `SEC-PROC-PATCH-001-V1` | Plant Patch and Vulnerability Handling (superseded) | 1.0 | **SUPERSEDED** | 2024-03-01 | Plant Cyber Security | [md](../documents/security/SEC-PROC-PATCH-001-V1_Superseded_Patch_Standard.md) | [docx](../documents/word/SEC-PROC-PATCH-001-V1_Superseded_Patch_Standard.docx) |
| `SEC-PROC-PATCH-001-V2` | Plant Patch and Vulnerability Management Standard | 2.0 | **APPROVED** | 2025-06-01 | Plant Cyber Security | [md](../documents/security/SEC-PROC-PATCH-001-V2_Approved_Patch_Standard.md) | [docx](../documents/word/SEC-PROC-PATCH-001-V2_Approved_Patch_Standard.docx) |
| `SEC-PROC-PATCH-001-V3D` | Plant Patch and Vulnerability Management Standard (draft) | 3.0-DRAFT | **DRAFT** | nan | Plant Cyber Security | [md](../documents/security/SEC-PROC-PATCH-001-V3D_Draft_Patch_Standard.md) | [docx](../documents/word/SEC-PROC-PATCH-001-V3D_Draft_Patch_Standard.docx) |
| `SEC-STD-CHANGE-001` | OT Change Control and Ticketing Standard | 2.0 | **APPROVED** | 2025-07-01 | Head of Engineering | [md](../documents/security/SEC-STD-CHANGE-001_OT_Change_Control_and_Ticketing_Standard.md) | [docx](../documents/word/SEC-STD-CHANGE-001_OT_Change_Control_and_Ticketing_Standard.docx) |
| `SEC-STD-DETECT-001` | Detection Rule Catalogue and Tuning Rules | 1.0 | **APPROVED** | 2025-12-01 | Technical Security Services | [md](../documents/security/SEC-STD-DETECT-001_Detection_Rule_Catalogue_and_Tuning_Rules.md) | [docx](../documents/word/SEC-STD-DETECT-001_Detection_Rule_Catalogue_and_Tuning_Rules.docx) |
| `SEC-STD-ZONES-001` | OT Network Segmentation and Zone Standard | 1.1 | **APPROVED** | 2025-10-01 | Plant Cyber Security | [md](../documents/security/SEC-STD-ZONES-001_OT_Network_Segmentation_and_Zone_Standard.md) | [docx](../documents/word/SEC-STD-ZONES-001_OT_Network_Segmentation_and_Zone_Standard.docx) |

## Which questions use which document

| Question | Document |
|---|---|
| Remediation target days per severity | `SEC-PROC-PATCH-001-V2` |
| What must happen before a controller change | `SEC-STD-CHANGE-001` |
| Who may use remote or vendor access, and how | `SEC-POL-REMOTE-001` |
| How incidents are triaged and escalated | `SEC-PROC-INC-001` |
| Which alert rules exist and how to tune them | `SEC-STD-DETECT-001` |
| How network zones are separated | `SEC-STD-ZONES-001` |
| How privileged access is reviewed | `SEC-PROC-ACCESS-REVIEW-001` |
| What the August 2026 security posture of A-001 was | `A001-SEC-2026-08` |
| What the inspection procedure requires for A-001 | `A001-PROC-INS-001-V2` |
| What the field and condition reports observed | `CR-2026-0819-A001`, `A001-CMR-2026-08` |

## Where the document data table is
The register is also a table: `data/csv/a001_source_documents.csv` and `data/security/security_documents.csv`. Both are in the Excel pack.

The original PDF versions of the nine A-001 documents are not stored in this repository. The Markdown and Word files here carry the same text.

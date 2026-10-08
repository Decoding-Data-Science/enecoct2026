# A-001 Enterprise RAG Corpus

This folder contains **readable Markdown mirrors** of the nine synthetic A-001 documents used throughout the RAG, agent and governance exercises.

The original PDFs are distributed in the companion Release asset:

`ENEC_2026_V2_2_Data_and_PDF_Corpus.zip`

## Corpus

| # | Document | Status |
|---|---|---|
| 01 | REL-POL-001 — Enterprise Asset Reliability and Escalation Policy | APPROVED |
| 02 | A001-OPS-001 — Operating and Usage Guide | APPROVED |
| 03 | A001-PROC-INS-001 V1 — Historical Inspection Procedure | SUPERSEDED |
| 04 | A001-PROC-INS-001 V2 — Inspection & PM Procedure | APPROVED / current |
| 05 | A001-PROC-INS-001 V3D — Revision | DRAFT |
| 06 | A001-TSG-001 — Troubleshooting and Diagnostic Guide | APPROVED |
| 07 | A001-CMR-2026-08 — Condition Monitoring Report | APPROVED |
| 08 | WO-2026-0817 — Inspection Work Order | OPEN |
| 09 | CR-2026-0819-A001 — Field Condition Report | APPROVED |

## Core teaching trap

The most recent-looking or most semantically similar document is not automatically authoritative.

For the inspection procedure:

- V1 is **SUPERSEDED**
- V2 is **APPROVED and current**
- V3D is newer but **DRAFT**

Therefore retrieval must consider both relevance **and** document authority.

## Original PDFs

For PDF-specific ingestion exercises, extract the companion ZIP and upload all nine PDFs to:

`/Workspace/Nuclear_Enterprise_360/A001 Documents/`

For repo-native exercises, the notebooks can use the Markdown mirrors in this folder.

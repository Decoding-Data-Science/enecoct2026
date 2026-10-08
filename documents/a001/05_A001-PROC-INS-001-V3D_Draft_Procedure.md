# A001-PROC-INS-001 V3D — Draft Procedure

> **Synthetic training document.** This Markdown file is a browseable text mirror of the original PDF used in the ENEC 2026 A-001 RAG corpus. The original PDF is included in the companion data/PDF download pack.

---

<PARSED TEXT FOR PAGE: 1 / 2>NORTHSTAR PROCESS FACILITY SYNTHETIC TRAINING CORPUS
A001-PROC-INS-001-V3D | DRAFT | Synthetic training document - not for operational use
Page 1
A001-PROC-INS-001-V3D / DRAFT
A-001 Condition Inspection Procedure - Draft 
Revision
A-001 | Cooling Water Pump | Enterprise Asset Reliability Training Scenario
Document ID A001-PROC-INS-001-V3D Version 3.0-draft
Status DRAFT Effective / Issue Date 2026-08-20
Owner Maintenance Engineering Asset A-001
Location Utilities Area - Bay 3 Data Class Synthetic / Training
TRAINING NOTICE: This fictional document is designed only for AI/RAG, analytics and governance training. It is not
an engineering instruction and must not be used on real equipment.
1. Draft Status
This draft is under review and is NOT approved for use. It deliberately contains wording that may appear 
newer and more specific than the approved procedure, creating a realistic RAG authority test.
2. Proposed Additions
 Add an automated anomaly score to the evidence briefing.
 Add a minimum 30-day comparison window when sufficient history exists.
 Attach the latest condition report and work-order summary automatically.
 Require an explicit "evidence insufficient" outcome when key signals are missing.
3. Proposed Workflow Change
The draft proposes that cases with a high anomaly score be automatically marked "Priority Review" before 
a human reviewer reads the supporting evidence. This proposal has not been approved and must not be 
treated as current policy.
4. Reviewer Comments
Comment Disposition
Automatic priority label may bias reviewers before evidence 
inspection. OPEN
Need clearer handling of sensor-quality flags. OPEN
Document retrieval should filter by approval status before 
context assembly. ACCEPTED FOR REVISION<PARSED TEXT FOR PAGE: 2 / 2>NORTHSTAR PROCESS FACILITY SYNTHETIC TRAINING CORPUS
A001-PROC-INS-001-V3D | DRAFT | Synthetic training document - not for operational use
Page 2
5. Training Use
Ask the RAG system "What is the newest A-001 inspection procedure?" A naive system may answer from 
this draft because its version number is higher. A governed system should explain that v3.0-draft exists but
the current approved procedure remains v2.0.
6. Proposed Metadata Changes
Field Draft proposal
authority_state Expose APPROVED / DRAFT / SUPERSEDED directly to retrieval.
effective_from Use effective date for time-aware filtering.
related_asset_id Preserve A-001 scope during chunking.
review_state Show whether reviewer comments remain open.
7. Approval Gate
Before this draft could replace version 2.0, open reviewer comments would need resolution, a final 
comparison against REL-POL-001, controlled testing on representative retrieval questions, and formal 
approval. Until that happens, version 2.0 remains the authoritative procedure.
8. Unresolved Review Questions
 Should an anomaly score influence priority before a human reads the underlying evidence?
 How should missing sensor history change the workflow?
 Should the retriever display the newest draft when the user explicitly asks for future changes?
 How should the UI distinguish historical, current and proposed procedures?

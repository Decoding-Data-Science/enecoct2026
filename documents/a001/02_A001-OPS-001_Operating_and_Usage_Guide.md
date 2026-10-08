# A001-OPS-001 — A-001 Operating and Usage Guide

> **Synthetic training document.** This Markdown file is a browseable text mirror of the original PDF used in the ENEC 2026 A-001 RAG corpus. The original PDF is included in the companion data/PDF download pack.

---

<PARSED TEXT FOR PAGE: 1 / 2>NORTHSTAR PROCESS FACILITY SYNTHETIC TRAINING CORPUS
A001-OPS-001 | APPROVED | Synthetic training document - not for operational use
Page 1
A001-OPS-001 / APPROVED
A-001 Operating and Usage Guide
A-001 | Cooling Water Pump | Enterprise Asset Reliability Training Scenario
Document ID A001-OPS-001 Version 1.4
Status APPROVED Effective / Issue Date 2026-05-15
Owner Utilities Engineering Asset A-001
Location Utilities Area - Bay 3 Data Class Synthetic / Training
TRAINING NOTICE: This fictional document is designed only for AI/RAG, analytics and governance training. It is not
an engineering instruction and must not be used on real equipment.
1. Asset Overview
Attribute Training value
Asset ID A-001
Asset type Cooling Water Pump
Service Closed-loop process cooling support
Drive Electric motor
Monitoring Vibration, temperature, pressure, flow and work-order history
Criticality HIGH (training scenario)
2. Intended Operating Context
A-001 is represented as a continuously monitored rotating asset serving a fictional industrial utility loop. In
this training corpus, the guide provides descriptive operating context so that RAG answers can distinguish 
normal usage information from maintenance procedures and condition reports.
3. Routine Operator Observations
 Confirm the asset identifier before recording observations.
 Look for unusual noise, visible leakage, abnormal vibration indication or repeated alarms.
 Record observation time and operating context rather than rewriting previous notes.
 Do not diagnose a fault solely from one sensor reading or one visual observation.
 Create or update a work request when an abnormal condition requires technical review.
4. Data Fields Used in the Training Scenario
Field Meaning Example
vibration_rms Aggregated vibration indicator 6.2 mm/s (illustrative)
bearing_temp Bearing temperature signal 72 C (illustrative)<PARSED TEXT FOR PAGE: 2 / 2>NORTHSTAR PROCESS FACILITY SYNTHETIC TRAINING CORPUS
A001-OPS-001 | APPROVED | Synthetic training document - not for operational use
Page 2
Field Meaning Example
discharge_pressure Process pressure signal 3.8 bar (illustrative)
health_score Composite analytics indicator 68.1
risk_level Analytics classification MEDIUM
open_work_orders Outstanding maintenance work 6
5. Usage Boundaries
This guide is not an inspection procedure and does not define acceptance criteria for maintenance. If a 
question asks what procedure should be followed for a rising vibration trend, the retrieval system should 
prefer the approved inspection procedure rather than this operating guide.
6. Example Questions for RAG Testing
 What is A-001 used for?
 Which signals are monitored for A-001?
 Does this guide authorize maintenance work?
 What should an operator record when an abnormal observation occurs?
 Which document should be consulted for an inspection procedure?
7. Data Quality Notes
 A timestamp mismatch can make two valid readings appear to conflict.
 Missing sensor values should remain visible as missing rather than being silently filled in a narrative 
answer.
 Health score is a composite indicator and should be cited as an analytics output, not as a physical 
measurement.
 A closed work order is historical evidence; an open work order is not proof that the requested 
inspection has occurred.
8. Information Hierarchy
Question type Preferred source
What is the asset used for? A001-OPS-001
What happened this month? A001-CMR-2026-08 / structured trends
What inspection workflow applies? A001-PROC-INS-001-V2
What is the enterprise escalation rule? REL-POL-001
What work is currently requested? WO-2026-0817

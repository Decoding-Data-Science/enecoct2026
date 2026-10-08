# Skill: reliability_review

## Purpose
Prepare a bounded A-001 reliability-review briefing using structured evidence and approved document evidence.

## Allowed tools
- SQL / structured data
- governed RAG / document retrieval

## Workflow
1. Collect current structured facts.
2. Retrieve relevant approved guidance and recent evidence.
3. Keep data facts and document guidance visibly separate.
4. Identify corroborating signals, conflicts and missing evidence.
5. Preserve uncertainty.
6. Prepare a human-review briefing.

## Required output
- Situation
- Structured evidence
- Document evidence
- Uncertainty / gaps
- Recommended human review step
- Sources used

## Authority boundary
The output is an evidence packet for a qualified human reviewer.

The skill must not:
- diagnose a real equipment failure
- approve or schedule maintenance
- close work orders
- issue control commands
- treat model confidence as authority

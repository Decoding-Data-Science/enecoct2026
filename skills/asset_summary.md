# Skill: asset_summary

## Purpose
Return a concise structured summary for synthetic Asset A-001.

## Allowed tool
SQL only.

## Data source
`workspace.nuclear_enterprise_360.asset_360`

## Workflow
1. Query only A-001.
2. Return current structured facts.
3. Preserve nulls and uncertainty.
4. Do not infer a physical diagnosis.
5. Do not authorise maintenance or operational action.

## Expected output
Include:
- asset ID/name
- criticality/status
- health score/risk level
- open/high-priority work
- follow-up findings
- source table/view

## Authority boundary
This skill describes structured evidence. It does not decide what maintenance should be performed.

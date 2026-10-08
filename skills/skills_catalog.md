# A-001 Agent Skills Catalog

The agent reads this small catalog first, then loads only the detailed skill required for the current task.

| Skill | Purpose | Allowed capabilities |
|---|---|---|
| `asset_summary` | Return current structured facts for A-001 | SQL |
| `approved_procedure` | Identify the current approved procedure and relevant guidance | RAG |
| `reliability_review` | Prepare an evidence-backed review briefing | SQL + RAG |

## Routing examples

- “What is the health score of A-001?” → `asset_summary`
- “Which procedure is currently approved?” → `approved_procedure`
- “Should A-001 be escalated for review?” → `reliability_review`

The catalog is intentionally small. Detailed instructions are progressively disclosed only after skill selection.

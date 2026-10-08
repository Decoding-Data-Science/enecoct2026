# Skill: approved_procedure

## Purpose
Identify current approved A-001 procedural guidance from the document corpus.

## Allowed tool
RAG/document retrieval only.

## Workflow
1. Retrieve relevant A-001 documents.
2. Inspect document ID, version and approval status.
3. Prefer current `APPROVED` material.
4. Treat `DRAFT` as non-authoritative.
5. Treat `SUPERSEDED` as historical evidence only.
6. Cite the document ID and version.
7. If authority is unclear, say so and request human review.

## Important training trap
A newer document is not necessarily the current authority. A draft can be newer than the approved version.

## Authority boundary
This skill retrieves guidance; it does not authorise work or replace qualified human judgement.

import os
from nbcommon import *

OUT = os.path.join(os.path.dirname(__file__), "..", "Day_2_GenAI_and_RAG")
os.makedirs(OUT, exist_ok=True)

# =============================================================================== 01 basics + RAG from scratch
cells = [header("Day 2", "GenAI Basics and RAG From Scratch", 75,
                "Understand tokens, context and hallucination, then build a working retrieval-augmented assistant over the A-001 documents with no framework: chunk, embed, retrieve, answer with citations.")]
cells += setup_cells(extra="tiktoken")
cells.append(md("""
## 1. Tokens and context

An LLM does not read words. It reads **tokens** (pieces of words). The **context window** is how many tokens it can consider at once, including your prompt and its answer. Cost and speed depend on tokens.
"""))
cells.append(code('''
import tiktoken, pandas as pd, numpy as np, json, re
enc = tiktoken.get_encoding("o200k_base")

print(enc.encode("Pump A-001 vibration"))
print([enc.decode([t]) for t in enc.encode("Pump A-001 vibration is rising")])

docs = enec.load_documents()
pd.DataFrame([{"doc_id": d["doc_id"], "status": d["status"], "version": d["version"],
               "characters": len(d["text"]), "tokens": len(enc.encode(d["text"]))} for d in docs])
'''))
cells.append(md("""
**Question:** The nine documents total only a few thousand tokens. Why not paste them all into every prompt? (Think: 9 documents today, 9,000 tomorrow. Cost, latency, and the model losing the needle in the haystack.) **RAG** retrieves only the few relevant pieces.

## 2. Why we need grounding: the hallucination test
"""))
cells.append(code('''
q = "Is the A-001 inspection procedure version 3.0 approved and in force?"
print(enec.ask(client, q))
'''))
cells.append(md("""
The model has no access to our documents, so any confident answer is a guess. Now we build the retrieval pipeline step by step.

## 3. The documents and their governance metadata

Every document has a **status**. This matters later: a newer document is not necessarily the current authority.
"""))
cells.append(code('''
pd.DataFrame([{k: d[k] for k in ("doc_id", "title", "status", "version", "date")} for d in docs])
'''))
cells.append(md("""
## 4. Chunking

We split each document into pieces of about 900 characters (with a little overlap) so each piece holds one idea. Too big and the search is vague. Too small and the context is lost.
"""))
cells.append(code('''
def chunk_text(text, size=900, overlap=150):
    paras = [p.strip() for p in re.split(r"\\n\\s*\\n", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 2 <= size:
            cur = (cur + "\\n\\n" + p).strip()
        else:
            if cur: chunks.append(cur)
            tail = cur[-overlap:] if cur else ""
            cur = (tail + "\\n\\n" + p).strip()
    if cur: chunks.append(cur)
    return chunks

chunks = []
for d in docs:
    for i, c in enumerate(chunk_text(d["text"])):
        chunks.append({"doc_id": d["doc_id"], "title": d["title"], "status": d["status"],
                       "version": d["version"], "chunk_no": i, "text": c})
print(len(chunks), "chunks")
print(chunks[3]["doc_id"], "chunk", chunks[3]["chunk_no"], "\\n")
print(chunks[3]["text"][:500])
'''))
cells.append(md("""
## 5. Embeddings

An **embedding** turns text into a list of numbers so that texts with similar meaning end up close together. We embed every chunk once.
"""))
cells.append(code('''
texts = [f"{c['title']} ({c['status']} v{c['version']})\\n{c['text']}" for c in chunks]
vectors = enec.embed(client, texts)
vectors = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-9)
print("vectors:", vectors.shape, "(chunks x dimensions)")
'''))
cells.append(md("""
## 6. Retrieval: cosine similarity

Embed the question the same way, then rank chunks by similarity. Because vectors are normalised, cosine similarity is just a dot product.
"""))
cells.append(code('''
def retrieve(question, k=4):
    qv = enec.embed(client, [question])[0]
    qv = qv / (np.linalg.norm(qv) + 1e-9)
    scores = vectors @ qv
    top = np.argsort(-scores)[:k]
    return [{**chunks[i], "score": float(scores[i])} for i in top]

for h in retrieve("Which inspection procedure is currently approved for A-001?"):
    print(f"{h['score']:.3f}  {h['doc_id']:<24} {h['status']:<11} {h['text'][:90]!r}")
'''))
cells.append(md("""
## 7. Generate a grounded answer with citations

The prompt has three parts: **rules**, **evidence** (labelled with document ID, status, version) and the **question**.
"""))
cells.append(code('''
RULES = """You answer questions about synthetic asset A-001 using ONLY the EVIDENCE.
- Cite document IDs in square brackets, e.g. [A001-PROC-INS-001-V2].
- Only APPROVED documents are current authority. DRAFT is not authoritative. SUPERSEDED is historical only.
- If the evidence does not answer the question, say so. Do not guess.
- You support a human reviewer. You never authorise work."""

def answer(question, k=4):
    hits = retrieve(question, k)
    evidence = "\\n\\n---\\n\\n".join(
        f"[{h['doc_id']} | {h['status']} | v{h['version']}]\\n{h['text']}" for h in hits)
    reply = enec.ask(client, f"EVIDENCE:\\n{evidence}\\n\\nQUESTION: {question}", system=RULES)
    return reply, hits

reply, hits = answer("Is the A-001 inspection procedure version 3.0 approved and in force?")
print(reply)
print("\\nSources:", sorted({h["doc_id"] for h in hits}))
'''))
cells.append(md("Compare this with the ungrounded answer in section 2.\n\n## 8. Ask more questions"))
cells.append(code('''
for q in ["What did the field observer report on 19 August, and was the source of the wet area confirmed?",
          "Does work order WO-2026-0817 authorise component replacement?",
          "What should be checked when vibration is rising?"]:
    r, h = answer(q)
    print("Q:", q); print(r); print("Sources:", [x["doc_id"] for x in h], "\\n" + "-" * 70)
'''))
cells.append(md("""
## 9. What do the retrieval settings change?

Try different chunk sizes and values of k. We only run retrieval here (cheap), and look at *which documents* come back for one question.
"""))
cells.append(code('''
question = "What does the approved procedure say about evidence to review before classifying the condition?"

def build(size, overlap=150):
    cs = []
    for d in docs:
        for i, c in enumerate(chunk_text(d["text"], size, overlap)):
            cs.append({"doc_id": d["doc_id"], "status": d["status"], "text": c})
    v = enec.embed(client, [c["text"] for c in cs]); v = v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-9)
    return cs, v

rows = []
qv = enec.embed(client, [question])[0]; qv = qv / np.linalg.norm(qv)
for size in (400, 900, 1600):
    cs, v = build(size)
    top = np.argsort(-(v @ qv))[:4]
    rows.append({"chunk_size": size, "chunks": len(cs), "top4_docs": [cs[i]["doc_id"] for i in top]})
pd.DataFrame(rows)
'''))
cells.append(md("""
## Takeaways

- RAG = **chunk, embed, retrieve, generate**. No framework is required to understand it.
- Retrieval quality decides answer quality. Always look at the retrieved chunks.
- Label evidence with **ID, status and version**, and tell the model how to treat each status.
- The model can still be wrong. Citations let a human check.

## Exercise

1. Ask a question the documents cannot answer (for example: "What is the replacement cost of the A-001 bearing?"). Does the assistant say it does not know?
2. Change `RULES` to remove the "do not guess" line. Re-ask. What changes?
3. Change `k` from 4 to 1 and to 8. When does the answer get worse?
"""))
save(cells, os.path.join(OUT, "Day2_01_GenAI_Basics_and_RAG_from_Scratch.ipynb"))

# =============================================================================== 02 governed RAG + evaluation
cells = [header("Day 2", "Governed RAG and Evaluation", 60,
                "Make retrieval respect document authority (APPROVED vs DRAFT vs SUPERSEDED), combine SQL with RAG, and measure the assistant with the 18-question evaluation set.")]
cells += setup_cells()
cells.append(md("""
## 1. Build the index

`enec.RAGIndex` is the same chunk, embed and cosine search you wrote in the previous notebook, packaged with metadata filters.
"""))
cells.append(code('''
import pandas as pd, numpy as np, json, re
docs = enec.load_documents()
index = enec.RAGIndex.build(client, docs)
print(len(index.chunks), "chunks from", len(docs), "documents")
pd.DataFrame([{k: d[k] for k in ("doc_id", "status", "version", "date")} for d in docs])
'''))
cells.append(md("""
## 2. The version trap

There are three versions of the inspection procedure: V1 (superseded), V2 (approved) and V3D (a newer draft). A naive system returns whatever is most similar. Watch the evidence.
"""))
cells.append(code('''
q = "Which inspection procedure should be followed for A-001?"
for h in index.search(q, k=6):
    print(f"{h['score']:.3f}  {h['doc_id']:<24} {h['status']:<11} v{h['version']}")
'''))
cells.append(code('''
# A naive prompt: no authority rules
hits = index.search(q, k=6)
naive = enec.ask(client, f"EVIDENCE:\\n{enec.format_hits(hits)}\\n\\nQUESTION: {q}")
print("NAIVE:\\n", naive)
'''))
cells.append(code('''
# Governed prompt: rules about status + citations
out = enec.rag_answer(client, index, q, k=6)
print("GOVERNED:\\n", out["answer"])
'''))
cells.append(code('''
# Hard filter: retrieve only APPROVED documents
out = enec.rag_answer(client, index, q, k=4, statuses=["APPROVED"])
print("APPROVED ONLY:\\n", out["answer"])
print([ (h["doc_id"], h["status"]) for h in out["hits"] ])
'''))
cells.append(md("""
### Authority table

| Status | Meaning | Allowed use |
|---|---|---|
| APPROVED | Current, controlled document | Authority for guidance |
| DRAFT | Proposed, not yet approved | Mention as pending; never as authority |
| SUPERSEDED | Replaced by a later approved version | Historical context only |
| OPEN (work order) | A request for work | Evidence of intent, not authorisation |

**Which is better: filter in code, or instruct in the prompt?** Filtering is stricter. Instructing keeps useful context ("a draft exists and is not in force"). Many teams do both.

## 3. Hybrid question: SQL + RAG

*"What is the health score of A-001 and which procedure applies?"* needs a database fact **and** a document fact. RAG alone cannot answer it.
"""))
cells.append(code('''
con = enec.make_db()
facts = enec.run_sql(con, "SELECT asset_id, health_score, risk_level, recommended_action, open_work_orders, high_priority_open_work FROM asset_360 WHERE asset_id='A-001'")
doc_hits = index.search("Which inspection procedure applies to A-001 and what is its status?", k=4, statuses=["APPROVED"])

prompt = f"""DATABASE FACT (table asset_360):
{facts.to_csv(index=False)}

DOCUMENT EVIDENCE:
{enec.format_hits(doc_hits)}

QUESTION: What is the health score of A-001 and which procedure applies?
Label each part of your answer as DATABASE or DOCUMENT."""
print(enec.ask(client, prompt, system=enec.RAG_SYSTEM))
'''))
cells.append(md("""
## 4. Evaluate: does retrieval find the right document?

`evaluation/rag_eval_questions.csv` has 18 questions with the expected source. First metric: **retrieval hit rate**, meaning the expected document appears in the top-k chunks. This costs only embeddings.
"""))
cells.append(code('''
ev = pd.read_csv(enec.EVAL_DIR / "rag_eval_questions.csv")
doc_ids = {d["doc_id"] for d in docs}

def expected_docs(s):
    return [p.strip() for p in str(s).split("+") if p.strip() in doc_ids]

def evaluate(k=4, statuses=None):
    rows = []
    for r in ev.itertuples():
        exp = expected_docs(r.expected_source)
        if not exp:
            continue                      # e.g. asset_360 only: that is a SQL question, not retrieval
        got = {h["doc_id"] for h in index.search(r.question, k=k, statuses=statuses)}
        rows.append({"question": r.question, "category": r.category, "expected": exp,
                     "hit": all(e in got for e in exp), "got": sorted(got)})
    return pd.DataFrame(rows)

res = evaluate(k=4)
print(f"Hit rate @4: {res.hit.mean():.0%}  ({int(res.hit.sum())}/{len(res)})")
res.groupby("category").hit.agg(["mean", "count"])
'''))
cells.append(code('''
res[~res.hit][["question", "expected", "got"]]      # failure analysis: read every miss
'''))
cells.append(code('''
# Does a larger k help? What does it cost (more text for the model to read)?
pd.DataFrame([{"k": k, "hit_rate": evaluate(k=k).hit.mean()} for k in (2, 4, 6, 8)])
'''))
cells.append(md("""
## 5. Evaluate answers (optional LLM judge)

Retrieval can succeed and the answer can still be wrong. A second model can grade answers against the expected behaviour. Treat the judge as a **screening tool**, not ground truth: read the low scores yourself.
"""))
cells.append(code('''
RUN_JUDGE = True      # set False to skip the extra model calls
SAMPLE = 6

if RUN_JUDGE:
    judge_rows = []
    sample = ev[ev.expected_source.apply(lambda s: len(expected_docs(s)) > 0)].head(SAMPLE)
    for r in sample.itertuples():
        out = enec.rag_answer(client, index, r.question, k=4)
        jp = (f"QUESTION: {r.question}\\nEXPECTED BEHAVIOUR: {r.expected_behavior}\\nANSWER: {out['answer']}\\n"
              'Score 1-5 how well the answer matches the expected behaviour and respects document authority. '
              'Return JSON: {"score": int, "reason": str}')
        j = json.loads(enec.ask(client, jp, json_mode=True))
        judge_rows.append({"question": r.question, "score": j.get("score"), "reason": j.get("reason")})
    pd.DataFrame(judge_rows)
'''))
cells.append(md("""
## Takeaways

- **Authority is data, not a vibe.** Carry status and version with every chunk and use them.
- A hybrid question needs a hybrid system: SQL for facts, RAG for documents.
- **Measure.** A small, fixed evaluation set turns "it seems fine" into numbers you can improve.
- Read the failures. They tell you whether to change chunking, k, metadata or the prompt.

## Exercise

1. Add a question to the evaluation set that tests the DRAFT trap and check the hit rate.
2. Retrieval misses a question. Rewrite the query with an LLM (query rewriting), retrieve again, and compare.
3. Add a rule: if retrieved evidence contains both a DRAFT and an APPROVED version of the same procedure, the answer must say so explicitly. Test it.
"""))
save(cells, os.path.join(OUT, "Day2_02_Governed_RAG_and_Evaluation.ipynb"))
print("day 2 built")

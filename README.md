# ENEC 2026 (October): AI for Coders & Software Engineers

**Four days, one plant, one common data set.** Day 1 uses **Microsoft Copilot**. Days 2 to 4 use **Python in Google Colab, OpenAI and LlamaIndex**, with GitHub for the course files. All data and documents are **synthetic training material**. Nothing here is an engineering diagnosis or a maintenance authorisation.

Instructor: **Mohammad Arshad Ahmed**

## The four-day journey

| Day | Theme | Platform | Start here |
|---|---|---|---|
| 1 | Generative AI, prompt engineering and data understanding | Microsoft Copilot | [`Day_1_Copilot_and_Data_Understanding/`](Day_1_Copilot_and_Data_Understanding/README.md) |
| 2 | Building generative AI applications and RAG | Colab, OpenAI, LlamaIndex, GitHub | [`Day_2_GenAI_and_RAG/`](Day_2_GenAI_and_RAG/README.md) |
| 3 | Agentic AI, tools and intelligent decision-making (includes a decision tree as an agent tool) | Colab, OpenAI, LlamaIndex | [`Day_3_Agentic_AI/`](Day_3_Agentic_AI/README.md) |
| 4 | Capstone, governance and final demonstration | Colab, OpenAI, LlamaIndex, GitHub | [`Day_4_Integrated_Capstone/`](Day_4_Integrated_Capstone/README.md) |

Scenarios are adapted to IT, cybersecurity, applications and plant operations under one common journey: asset **A-001**, a cooling-water pump, and the plant around it.

## Start in 3 minutes
1. Read [`START_HERE.md`](START_HERE.md).
2. Day 1: open the Excel workbooks in `data/excel` through OneDrive or SharePoint and follow [`Day_1_Copilot_and_Data_Understanding`](Day_1_Copilot_and_Data_Understanding/README.md).
3. Day 2 onward: open the notebooks with the links below. The first cells clone this repository and load the data.

## Notebooks (open in Colab)
The Colab links work once this repository is public on the `main` branch. The same list is in [`RUN_THE_NOTEBOOKS.md`](RUN_THE_NOTEBOOKS.md).

| Day | Notebook | Minutes | What you build |
|---|---|---:|---|
| Day 1 (optional lab) | [Data understanding in Python](https://colab.research.google.com/github/Decoding-Data-Science/enec2026oct/blob/main/Day_1_Copilot_and_Data_Understanding/Day1_01_Data_Understanding_Python.ipynb) | 60 | No key, no install: file types, pandas, SQL, joins, documents, quality checks |
| Day 2 | [Colab setup and first prompts in code](https://colab.research.google.com/github/Decoding-Data-Science/enec2026oct/blob/main/Day_2_GenAI_and_RAG/Day2_00_Colab_Setup_and_First_Prompts.ipynb) | 40 | OpenAI key, Colab Secrets, structured prompts in Python |
| Day 2 | [GenAI basics and RAG from scratch](https://colab.research.google.com/github/Decoding-Data-Science/enec2026oct/blob/main/Day_2_GenAI_and_RAG/Day2_01_GenAI_Basics_and_RAG_from_Scratch.ipynb) | 75 | Tokens, hallucination, chunk, embed, retrieve, cited answers |
| Day 2 | [Governed RAG and evaluation](https://colab.research.google.com/github/Decoding-Data-Science/enec2026oct/blob/main/Day_2_GenAI_and_RAG/Day2_02_Governed_RAG_and_Evaluation.ipynb) | 60 | Approved vs draft vs superseded, SQL + RAG, evaluation set |
| Day 3 | [Tool-calling agent](https://colab.research.google.com/github/Decoding-Data-Science/enec2026oct/blob/main/Day_3_Agentic_AI/Day3_01_Tool_Calling_Agent_SQL_RAG_Forecast.ipynb) | 75 | Agent loop with SQL, document search and forecast tools |
| Day 3 | [Decision tree as an agent tool](https://colab.research.google.com/github/Decoding-Data-Science/enec2026oct/blob/main/Day_3_Agentic_AI/Day3_02_Decision_Tree_as_an_Agent_Tool.ipynb) | 75 | Train and judge a tree on log windows, give it to an agent, human review queue |
| Day 3 | [Skills, memory and governed agents](https://colab.research.google.com/github/Decoding-Data-Science/enec2026oct/blob/main/Day_3_Agentic_AI/Day3_03_Skills_Memory_and_Governed_Agents.ipynb) | 75 | Skills, memory, audit trail, approval gate, supervisor and specialists |
| Day 4 | [Capstone: review briefing](https://colab.research.google.com/github/Decoding-Data-Science/enec2026oct/blob/main/Day_4_Integrated_Capstone/Day4_01_Capstone_A001_Review_Briefing.ipynb) | 90 | Evidence packet, 8-section briefing, automatic checks |
| Day 4 | [The review app, in Colab](https://colab.research.google.com/github/Decoding-Data-Science/enec2026oct/blob/main/Day_4_Integrated_Capstone/Day4_02_A001_Review_App_in_Colab.ipynb) | 45 | Three-tab app inside the Colab session |
| Optional | [Extension 1: explore with SQL](https://colab.research.google.com/github/Decoding-Data-Science/enec2026oct/blob/main/Optional_Colab_Extensions/Ext01_Asset360_Explore_with_SQL.ipynb) | 50 | SQL, joins, data quality, charts, text-to-SQL with a guard |
| Optional | [Extension 2: anomaly and forecast](https://colab.research.google.com/github/Decoding-Data-Science/enec2026oct/blob/main/Optional_Colab_Extensions/Ext02_A001_Anomaly_and_Forecast.ipynb) | 60 | Anomaly flags, baseline, Ridge model, 7-day vibration forecast |
| Optional | [Extension 3: security logs](https://colab.research.google.com/github/Decoding-Data-Science/enec2026oct/blob/main/Optional_Colab_Extensions/Ext03_Security_Logs_Investigate_and_Detect.ipynb) | 50 | Investigate A-001 from raw logs, detection rules and alert fatigue |

## Where things are

| Need | Go to |
|---|---|
| Prompt engineering guide and practice prompts | [`Day_1_Copilot_and_Data_Understanding/PROMPT_ENGINEERING_GUIDE.md`](Day_1_Copilot_and_Data_Understanding/PROMPT_ENGINEERING_GUIDE.md) |
| Copilot exercises E01 to E16 with check answers | [`resources/COPILOT_EXERCISES.md`](resources/COPILOT_EXERCISES.md) |
| Task card for your job title | [`resources/PARTICIPANT_ROLES_GUIDE.md`](resources/PARTICIPANT_ROLES_GUIDE.md) |
| **All 19 documents (Word and Markdown), with status and version** | [`documents/README.md`](documents/README.md) |
| Excel workbooks for Copilot | `data/excel/` |
| CSV tables used by the notebooks | `data/csv/` (Asset 360) and `data/security/` (security layer) |
| Slides | `slides/` (one deck per day) |
| Instructor run of show | [`resources/INSTRUCTOR_GUIDE.md`](resources/INSTRUCTOR_GUIDE.md) |
| Problems | [`resources/TROUBLESHOOTING.md`](resources/TROUBLESHOOTING.md) |

## What is in the repo

```
Day_1_Copilot_and_Data_Understanding/   prompt engineering guide, Day 1 plan (no code)
Day_2_GenAI_and_RAG/                    3 notebooks: Colab setup, RAG from scratch, governed RAG
Day_3_Agentic_AI/                       3 notebooks: agent, decision tree as a tool, governance
Day_4_Integrated_Capstone/              2 notebooks, capstone brief, rubric
Optional_Colab_Extensions/              3 optional notebooks: SQL, forecast, security-log investigation
colab/enec_colab.py                     shared helper: OpenAI client, read-only SQL, RAG index, agent loop, checks
data/csv/                               Asset 360 slice (12 tables)
data/security/                          security layer: logins, firewall flows, controller commands, alerts, vulnerabilities, access review, windows
data/excel/                             Excel Tables for Copilot
documents/                              19 documents as Word and Markdown, plus the index
skills/                                 agent skill playbooks
evaluation/                             RAG evaluation set, security questions, instructor answer key
resources/                              guides, exercises, troubleshooting
slides/                                 4 decks (the original Colab-first Day 1 deck is in slides/archive)
tools/  tests/                          notebook builders and the offline test
```

## Status of this edition
- Day 1 is Copilot-first. The earlier Colab-first Day 1 notebooks are now Day 2 setup and the three optional extensions.
- Notebooks pass an **offline** test with a fake OpenAI client. Run each once with a real key before teaching.
- Day 2 and Day 3 notebooks currently build RAG and agents directly on the OpenAI API so every step is visible. The Day 3 decision-tree notebook also shows a LlamaIndex tool and agent. Moving the Day 2 RAG notebooks fully onto LlamaIndex is planned.

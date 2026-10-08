# Run the notebooks

Open each notebook with its link. The first cells install what is needed, clone this repository, and read your key from Colab Secrets. Run cells top to bottom with Shift + Enter.

**Before the first notebook:** sign in to <https://colab.research.google.com>, click the key icon, add a secret named `OPENAI_API_KEY`, and switch Notebook access on. See [`START_HERE.md`](START_HERE.md).

**These links work once the repository is public on the `main` branch** at <https://github.com/Decoding-Data-Science/enec2026oct>.

| Day | Notebook | Minutes | What you do |
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

## Practice order if you work alone
1. Day 2: 00, 01, 02. 2. Day 3: 01, 02, 03. 3. Day 4: 01, 02. 4. Optional extensions at any time.

## If something fails
- Secret not found: follow the numbered message the cell prints, then run the cell again.
- Clone fails (GitHub blocked): upload `enec2026oct.zip` in the Files panel, run `!unzip -q enec2026oct.zip -d /content`, run the setup cell again.
- Anything else: [`resources/TROUBLESHOOTING.md`](resources/TROUBLESHOOTING.md).

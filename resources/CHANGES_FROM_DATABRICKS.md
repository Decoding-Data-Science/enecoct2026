# Changes from the Databricks version

| Area | Before | Now |
|---|---|---|
| Platform | Databricks workspace | Google Colab |
| Model access | Databricks serving endpoints | OpenAI API, key in Colab Secrets |
| Data | 120 MB SQLite database, Delta tables | 12 small CSVs loaded into in-memory SQLite |
| Retrieval | LlamaIndex | OpenAI embeddings and cosine search written by hand |
| Agents | Framework agents | A visible tool-calling loop with a step limit |
| App | Hosted app | Gradio app running inside the Colab session only |
| Day 1 prompting | Slides | Hands-on notebook on asset data |

Not updated: the original slide decks and PDFs in the earlier repository still describe the Databricks flow.

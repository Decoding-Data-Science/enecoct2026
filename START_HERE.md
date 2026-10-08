# Participant Start Here

## What you need, by day

| Day | You need |
|---|---|
| 1 | A browser and your **official Microsoft account with Copilot**. No code. See `Day_1_Copilot_and_Data_Understanding/README.md` |
| 2 to 4 | A **Google account**, a browser, and an **OpenAI API key**. Nothing to install |

The steps below are for Days 2 to 4. Do them before Day 2.

## 1. Open Google Colab

Go to <https://colab.research.google.com> and sign in with your Google account.

## 2. Add your OpenAI key to Colab Secrets (once)

1. In Colab, click the **key icon** in the left sidebar.
2. Click **Add new secret**.
3. Name: `OPENAI_API_KEY`   Value: your OpenAI API key.
4. Switch **Notebook access** ON.

Rules for the key:

- Never type the key into a code cell.
- Never share a notebook that contains the key.
- If you think the key has leaked, revoke it in your OpenAI account and create a new one.

Secrets are per Google account, not per notebook. You add the key once, then switch Notebook access on for each new notebook you open.

## 3. Open the Day 2 notebook

Use the Colab links in [RUN_THE_NOTEBOOKS.md](RUN_THE_NOTEBOOKS.md), starting with `Day2_00`. The first code cells will:

1. install the `openai` library,
2. clone this repository into `/content/enec2026oct` (data, documents, skills, helper module),
3. read your key from Secrets and pick an available model.

If the third step prints a message about the secret, follow the numbered steps it shows and run the cell again.

## 4. Run cells top to bottom

Press **Shift + Enter** to run a cell. If you change something and get lost, use **Runtime, then Restart session and run all**.

## If you cannot reach GitHub from your network

1. Download `enec2026oct.zip` from your instructor.
2. In Colab, open the **Files** panel (folder icon), and upload the zip.
3. Run `!unzip -q enec2026oct.zip -d /content` in a cell, then run the notebook's setup cell again.

## What it costs

The notebooks use small models and short texts. A full run of the notebooks is typically a small cost per participant. Check your usage on the OpenAI dashboard after Day 2 so there are no surprises.

## Data and safety

All data and documents are synthetic. Do not paste real company data into any notebook. The assistant supports a qualified human reviewer; it never authorises maintenance, shutdown or replacement.

## Student guide (open in a browser)

`guides/ENEC_AI_Student_Guide.html` is the single page with the plan, checklists, practice exercises and help. Download it and open it in any browser.

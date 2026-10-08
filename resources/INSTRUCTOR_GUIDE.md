# Instructor Guide

## Pre-flight (the day before)

1. Push this repository to `main` and make it public, so the Colab links and the `git clone` cell work.
2. Open Day2_00 yourself in Colab with your own key and run every cell. Then run all remaining notebooks once. The offline test proves control flow only; a real run proves the answers read well.
3. Check your OpenAI usage page and set a monthly budget limit on the key or project.
4. Confirm the venue network reaches `github.com`, `pypi.org` and `api.openai.com`. If GitHub is blocked, hand out `enec2026oct.zip` (see START_HERE).
5. Ask every participant to add `OPENAI_API_KEY` to Colab Secrets before Day 2, and to confirm Copilot access in Excel before Day 1 (START_HERE steps 1-2).
6. Decide key policy: one key per participant (recommended) or a shared project key with a spend cap. Never paste a shared key on a slide.

## Run of show

### Day 1: Generative AI, prompt engineering and data understanding (Copilot, no code)

Slides: `slides/ENEC2026_Day1_Copilot_GenAI_and_Data.pptx` (28). Guide: `Day_1_Copilot_and_Data_Understanding/PROMPT_ENGINEERING_GUIDE.md`.

| Time | Block | Teaching point |
|---|---|---|
| 0:00 | Icebreaker, journey, agenda (slides 1 to 4) | Mixed room, one journey. No code today. |
| 0:20 | AI and GenAI ecosystem, how an LLM works, enterprise uses (5 to 8) | Fluent is not true. It only knows what is in the conversation. |
| 0:50 | Prompt engineering: work order, seven-part prompt, techniques, patterns (9 to 12) | Weak vs structured on the same question. Expected answer 4 assets (A-001, A-010, A-065, A-110). |
| 1:30 | Copilot for analysis, summarisation, extraction, productivity; setup; verification (13 to 15) | Setup is where the day goes wrong: OneDrive or SharePoint, AutoSave, table. |
| 2:00 | The data: A-001, structured vs unstructured, data map, vibration chart, five questions (16 to 20) | Rise starts 22 Jul, before any security event. |
| 2:30 | Security layer and four perspectives (21, 22) | One join key. Target query returns 5 assets. |
| 2:50 | Lab 1: PE1 to PE8, then E01 to E16 (23) | Weak prompt first, structured second, compare with check answer. Collect "right, fixed, could not know". |
| 3:50 | Lab 2: lanes, then use cases and guardrails (24 to 26) | One page per role; two use-case ideas. |
| 4:20 | Bridge to Day 2 (27) | Day 2 preparation: Google sign-in, OpenAI key, GitHub reachable. |

If Copilot is unavailable for someone: pair them, or have them filter and pivot in Excel and use the check answers. If time is short, cut Lab 2 to the lane table and move the use-case slide to the end of Day 2. The optional extensions (`Optional_Colab_Extensions`) are homework. The attack answer key is `evaluation/security_attack_episodes_answer_key.csv`; keep it for the debrief.

### Day 2: GenAI and RAG (175 min of notebooks)

| Time | Notebook | Teaching point |
|---|---|---|
| 0:00 | Day2_00 Colab setup and first prompts | Secrets, model fallback. Day 1 structured prompt becomes a system message. |
| 0:40 | Day2_01 Basics and RAG from scratch | Tokens, hallucination, chunk, embed, retrieve, cite. |
| 1:55 | Day2_02 Governed RAG and evaluation | Status labels decide authority. Run the 18-question set and read the failures together. |

### Day 3: Agents and machine learning (225 min)

| Time | Notebook | Teaching point |
|---|---|---|
| 0:00 | Day3_01 Tool-calling agent | The loop, the step limit, the tool trace. |
| 1:15 | Day3_02 Decision tree as an agent tool | Accuracy trap (98%), time split, recall 0.95 and precision 0.78 at depth 5, then the tree as a read-only tool and a human review queue. |
| 2:30 | Day3_03 Skills, memory, governance | Skills load on demand, memory is a file, risky actions go to an approval queue. |

### Day 4: Capstone (135 min)

| Time | Notebook | Teaching point |
|---|---|---|
| 0:00 | Day4_01 Review briefing | Evidence packet, 8 sections, automatic checks, rubric. Participants work on their own wording of the briefing. |
| 1:30 | Day4_02 App in Colab | Three-tab app inside the session. Show it only if time permits; the briefing notebook is the assessed work. |

## Key and cost handling

- Keep `SHARE=False` in the app notebook. A public Gradio share link would let anyone use the participant's key.
- Models are tried in order: gpt-5.4-mini, gpt-5-mini, gpt-4o-mini. If none is available to a key, the setup cell says so.
- If rate limits appear, ask participants to pause 30 seconds and re-run the cell. Do not have the whole room run the embedding cells at the same second.
- Revoke any key that appears on a screen or in a saved notebook.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Secret not found | Add `OPENAI_API_KEY` in the key icon panel and switch Notebook access ON, then re-run the cell. |
| `git clone` fails | Use the zip fallback in START_HERE. |
| No model available | The key's project has no access to the listed models. Enable one in the OpenAI project settings. |
| 429 or quota error | Check billing and limits; wait and retry. |
| `ModuleNotFoundError` | Re-run the first install cell, then Runtime, Restart session. |
| Forecast looks flat | Expected on a 90-day slice; compare the backtest numbers, not the picture. |
| Answers differ between runs | Normal. Grade the evidence and the checks, not exact wording. |

## Honest limits to tell the room

- The data is synthetic and small by design.
- Any score from the rule-based checks shows structure, not truth. A human reviewer decides.
- The assistant never authorises maintenance, shutdown or replacement.

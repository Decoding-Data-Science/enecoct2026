"""Shared bits for building the Colab notebooks with nbformat."""
import nbformat as nbf

REPO = "Decoding-Data-Science/enec2026oct"


def md(s):
    return nbf.v4.new_markdown_cell(s.strip("\n"))


def code(s):
    return nbf.v4.new_code_cell(s.strip("\n"))


def header(day, title, minutes, goal, needs_ai=True):
    key = "OpenAI key in Colab Secrets (`OPENAI_API_KEY`)" if needs_ai else "No API key needed for this notebook"
    return md(f"""
# ENEC 2026 · {day} · {title}

**Time:** about {minutes} minutes  |  **Runs in:** Google Colab (free tier is fine)  |  **Needs:** {key}

**Data:** a small slice of the synthetic *Nuclear Enterprise 360* dataset, focused on **Asset A-001** (a cooling-water pump). All data is synthetic training data.

**Goal:** {goal}

> Training notice: nothing in this notebook is an engineering diagnosis or a maintenance authorisation. The AI supports a qualified human reviewer.
""")


PIP_CELL = """
# Install what Colab does not already have (about 20 seconds)
%pip install -q -U openai {extra}
"""

BOOT_CELL = '''
# Get the course files (data, documents, skills) and the helper module.
# In Colab this clones the public course repo into /content/enec2026oct.
import os, sys, subprocess

REPO_URL = "https://github.com/Decoding-Data-Science/enec2026oct"
IN_COLAB = os.path.isdir("/content") and "google.colab" in sys.modules
ROOT = "/content/enec2026oct" if IN_COLAB else os.getcwd()

if IN_COLAB and not os.path.isdir(ROOT):
    r = subprocess.run(["git", "clone", "--depth", "1", REPO_URL, ROOT], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(
            "Could not clone the course repo:\\n" + r.stderr[-300:] +
            "\\nFallback: upload enec2026oct.zip in the Files panel (left sidebar), "
            "run  !unzip -q enec2026oct.zip -d /content  and run this cell again."
        )

sys.path.insert(0, os.path.join(ROOT, "colab"))
import enec_colab as enec
print("Course files ready at:", enec.ROOT)
'''


def setup_cells(extra="", need_ai=True, pip=True):
    cells = []
    if pip:
        cells.append(code(PIP_CELL.format(extra=extra).replace("  \n", "\n")))
    cells.append(code(BOOT_CELL))
    if need_ai:
        cells.append(code('''
# Connect to OpenAI. The key comes from Colab Secrets and is never printed.
client = enec.get_client()
MODEL = enec.pick_model(client)     # first available of: gpt-5.4-mini, gpt-5-mini, gpt-4o-mini
'''))
    return cells


def save(nb_cells, path, kernel="python3"):
    nb = nbf.v4.new_notebook()
    nb.cells = nb_cells
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": kernel},
        "language_info": {"name": "python"},
        "colab": {"provenance": [], "toc_visible": True},
    }
    nbf.validate(nb)
    nbf.write(nb, path)

"""Execute every course notebook offline with a fake OpenAI (see tests/fakes). Usage: python tests/run_notebooks.py [pattern]"""
import glob, os, sys, re, time
import nbformat
from nbclient import NotebookClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAKES = os.path.join(ROOT, "tests", "fakes")
os.environ["PYTHONPATH"] = FAKES + os.pathsep + os.environ.get("PYTHONPATH", "")
os.environ["OPENAI_API_KEY"] = "test-key"
pat = sys.argv[1] if len(sys.argv) > 1 else ""
failed = 0
for path in sorted(glob.glob(os.path.join(ROOT, "Day_*", "*.ipynb")) + glob.glob(os.path.join(ROOT, "Optional_Colab_Extensions", "*.ipynb"))):
    if pat and pat not in path:
        continue
    nb = nbformat.read(path, as_version=4)
    for c in nb.cells:
        if c.cell_type == "code":
            c.source = re.sub(r"^%pip.*$", "pass  # (pip skipped in offline test)", c.source, flags=re.M)
            c.source = c.source.replace("demo.launch(share=SHARE, debug=False)", "demo.launch(prevent_thread_lock=True, share=False); demo.close()")
    t = time.time()
    try:
        NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": ROOT}}).execute()
        sd=os.environ.get("SAVE_DIR")
        if sd:
            os.makedirs(sd,exist_ok=True); nbformat.write(nb, os.path.join(sd, os.path.basename(path)))
        print(f"PASS  {os.path.basename(path)}  ({time.time()-t:.0f}s)")
    except Exception as e:
        failed += 1
        print(f"FAIL  {os.path.basename(path)}\n{str(e)[-1800:]}")
sys.exit(1 if failed else 0)

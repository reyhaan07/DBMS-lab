"""Generate narration WAV per slide with Piper (runs in parallel)."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
manifest = json.load(open(sys.argv[1])); model = sys.argv[2]
def run(s):
    wav = s["html"].replace(".html", ".wav")
    if os.path.exists(wav): return
    subprocess.run([sys.executable, "-m", "piper", "-m", model, "-f", wav, "--length-scale", "1.08",
                    "--sentence-silence", "0.35"], input=s["say"].encode(), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
with ThreadPoolExecutor(4) as ex: list(ex.map(run, manifest))
print("tts done", len(manifest))

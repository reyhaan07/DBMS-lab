"""Build one MP4 per part (slide image + narration), plus a full-course MP4."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from content import PARTS
manifest = json.load(open(sys.argv[1])); outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)
safe = {p["num"]: p["name"].split(" (")[0].replace("&", "and").replace("+", "and").replace("/", "-")
        .replace(",", "").replace(" ", "_") for p in PARTS}

def clip(s):
    png, wav = s["html"].replace(".html", ".png"), s["html"].replace(".html", ".wav")
    mp4 = s["html"].replace(".html", ".mp4")
    dur = float(subprocess.check_output(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", wav]).decode()) + 1.6
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "12", "-i", png, "-i", wav,
        "-af", "adelay=500|500,apad", "-t", f"{dur:.2f}", "-c:v", "libx264", "-tune", "stillimage",
        "-preset", "medium", "-crf", "26", "-g", "120", "-pix_fmt", "yuv420p", "-r", "12",
        "-c:a", "aac", "-b:a", "96k", "-ar", "44100", "-ac", "1", mp4], check=True)
    return mp4, dur

with ThreadPoolExecutor(4) as ex: results = list(ex.map(clip, manifest))
total_all, all_list = 0, []
for p in PARTS:
    items = [(r, s) for r, s in zip(results, manifest) if s["part"] == p["num"]]
    lst = os.path.join(os.path.dirname(items[0][1]["html"]), "list.txt")
    open(lst, "w").write("".join(f"file '{r[0]}'\n" for r, _ in items))
    out = os.path.join(outdir, f"Part{p['num']}_{safe[p['num']]}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", "-movflags", "+faststart", out], check=True)
    d = sum(r[1] for r, _ in items); total_all += d; all_list += [r[0] for r, _ in items]
    print(f"{os.path.basename(out)}  {d/60:.1f} min  {os.path.getsize(out)/1e6:.1f} MB")
lst = os.path.join(os.path.dirname(sys.argv[1]), "all.txt")
open(lst, "w").write("".join(f"file '{f}'\n" for f in all_list))
out = os.path.join(outdir, "FULL_COURSE_All_Parts.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                "-c", "copy", "-movflags", "+faststart", out], check=True)
print(f"FULL  {total_all/60:.1f} min  {os.path.getsize(out)/1e6:.1f} MB")

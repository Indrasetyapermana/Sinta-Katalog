#!/usr/bin/env python3
"""
Build assets/demo.gif: a captioned walkthrough of the app (search -> filter -> draft analysis).

Same method as capture_screenshots.py (headless Chromium rendering of the APK's bundled web app),
so it is a browser render, not a screen recording of a physical device.

    pip install playwright pillow && playwright install chromium   # plus ffmpeg on PATH
    python scripts/make_demo_gif.py path/to/app-debug.apk
"""
import functools, http.server, io, pathlib, shutil, subprocess, sys, tempfile, threading, zipfile
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "demo.gif"
apk = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "app-debug.apk")
GIF_WIDTH = 300

work = pathlib.Path(tempfile.mkdtemp())
with zipfile.ZipFile(apk) as z:
    z.extractall(work, [n for n in z.namelist() if n.startswith("assets/public/")])
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(work / "assets" / "public"))
handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

def font(size):
    for p in ("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if pathlib.Path(p).exists(): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

frames = []  # (PIL image, seconds)
def grab(pg, seconds, caption):
    pg.wait_for_timeout(260)
    im = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
    im = im.resize((GIF_WIDTH, round(im.height * GIF_WIDTH / im.width)), Image.LANCZOS)
    d = ImageDraw.Draw(im, "RGBA")
    f = font(13); w = d.textlength(caption, font=f)
    box_h = 30
    d.rectangle([0, im.height - box_h, im.width, im.height], fill=(11, 22, 34, 232))
    d.text(((im.width - w) / 2, im.height - box_h + 7), caption, font=f, fill=(239, 230, 208, 255))
    frames.append((im, seconds))

def scroll_to(pg, sel, off=10):
    pg.evaluate("([s,o])=>{const e=document.querySelector(s);window.scrollTo({top:e.getBoundingClientRect().top+scrollY-o,behavior:'instant'})}", [sel, off])

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 412, "height": 915}, device_scale_factor=1, is_mobile=True, has_touch=True, locale="id-ID", timezone_id="Asia/Makassar")
    ctx.route("**/fonts.googleapis.com/**", lambda r: r.abort()); ctx.route("**/fonts.gstatic.com/**", lambda r: r.abort())
    pg = ctx.new_page(); pg.goto(f"http://127.0.0.1:{srv.server_port}/index.html")
    pg.wait_for_function("!document.getElementById('meta-line').textContent.startsWith('Memuat')", timeout=60000)

    grab(pg, 1.6, "1 · Offline catalogue of 15,250 journals")
    # --- search
    pg.click("#topic-input")
    for i, part in enumerate(["per", "pertan", "pertanian"]):
        pg.fill("#topic-input", part); grab(pg, 0.5 if i < 2 else 0.9, "2 · Type a topic")
    pg.wait_for_timeout(350)
    scroll_to(pg, "#level-filters"); grab(pg, 1.8, "Results ranked by title + subject")
    # --- filter
    pg.click('.chip[data-level="S1"]'); grab(pg, 1.0, "3 · Filter by SINTA level")
    pg.click('.chip[data-level="S2"]'); grab(pg, 1.6, "S1 + S2 selected")
    for y in (260, 520):
        pg.evaluate(f"window.scrollBy({{top:{y if y==260 else 260},behavior:'instant'}})"); grab(pg, 0.7, "Scroll the result cards")
    pg.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    pg.click("#chip-reset")
    # --- draft analysis
    pg.click("#tab-btn-predictor"); grab(pg, 1.2, "4 · Analyse a draft article")
    pg.fill("#draft-input", (ROOT / "samples" / "draft-en-full.txt").read_text()); grab(pg, 1.2, "Paste the manuscript text")
    pg.click("#predictor-form button[type=submit]"); pg.wait_for_timeout(300)
    scroll_to(pg, "#predictor-report", 12); grab(pg, 2.4, "Rough tier estimate (a heuristic)")
    scroll_to(pg, "#predictor-status", 12); grab(pg, 2.2, "…and recommended journals")
    b.close()

# --- assemble with ffmpeg (shared optimised palette, bayer dither)
tmp = pathlib.Path(tempfile.mkdtemp()); lines = []
for i, (im, sec) in enumerate(frames):
    fp = tmp / f"f{i:03d}.png"; im.save(fp); lines += [f"file '{fp}'", f"duration {sec}"]
lines.append(f"file '{tmp / f'f{len(frames)-1:03d}.png'}'")  # concat quirk: repeat last frame
(tmp / "list.txt").write_text("\n".join(lines))
OUT.parent.mkdir(exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
                "-vf", "fps=12,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4",
                "-loop", "0", str(OUT)], check=True)
print(f"{len(frames)} frames -> {OUT} ({OUT.stat().st_size/1024:.0f} KB)")

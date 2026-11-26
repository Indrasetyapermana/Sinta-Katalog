#!/usr/bin/env python3
"""
Regenerate every screenshot in ../screenshots from an APK.

Sinta Katalog is a Capacitor app: its whole UI is a web app bundled in the APK
under assets/public/. This script unpacks that web app, serves it locally and
drives it with headless Chromium at a phone-sized viewport.

    pip install playwright && playwright install chromium
    python scripts/capture_screenshots.py path/to/app-debug.apk

NOTE: these are renders of the bundled web assets, not captures from a physical
device or emulator. Google Fonts are blocked (the app loads them from the
network), so the browser's fallback fonts are used for the serif and mono text.
"""
import functools, http.server, sys, threading, zipfile, tempfile, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "screenshots"
SAMPLES = ROOT / "samples"
apk = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "app-debug.apk")

work = pathlib.Path(tempfile.mkdtemp())
with zipfile.ZipFile(apk) as z:
    z.extractall(work, [n for n in z.namelist() if n.startswith("assets/public/")])
web = work / "assets" / "public"

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(web))
handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{srv.server_port}/index.html"

OUT.mkdir(exist_ok=True)
log = {}

def ready(pg):
    pg.wait_for_function("!document.getElementById('meta-line').textContent.startsWith('Memuat')", timeout=60000)

def snap(pg, name, full=False):
    pg.wait_for_timeout(450)  # search is debounced 220 ms
    pg.screenshot(path=str(OUT / f"{name}.png"), full_page=full)
    print("saved", name)

def to(pg, selector, offset=12):
    """Scroll so `selector` sits near the top of the viewport."""
    pg.evaluate("([s,o]) => { const e=document.querySelector(s); window.scrollTo(0, e.getBoundingClientRect().top + scrollY - o); }", [selector, offset])
    pg.wait_for_timeout(150)

def search(pg, q):
    pg.fill("#topic-input", q)
    pg.press("#topic-input", "Enter")

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 412, "height": 915}, device_scale_factor=2,
                        is_mobile=True, has_touch=True, locale="id-ID", timezone_id="Asia/Makassar")
    ctx.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    ctx.route("**/fonts.gstatic.com/**", lambda r: r.abort())
    pg = ctx.new_page()
    dialogs = []
    pg.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
    pg.goto(URL); ready(pg)

    # 01 – launch screen (search tab)
    snap(pg, "01-home")
    # 02 – the full catalogue as it appears before any query
    to(pg, "#status-line", 8); snap(pg, "02-catalogue-default")

    # 03 – topic search
    pg.evaluate("scrollTo(0,0)"); search(pg, "pendidikan IPA"); to(pg, "#level-filters", 8); snap(pg, "03-search-topic")
    log["pendidikan IPA"] = pg.inner_text("#status-line")

    # 04 – Indonesian keyword → English subject label (synonym map)
    search(pg, "pertanian"); to(pg, "#level-filters", 8); snap(pg, "04-search-synonym")
    log["pertanian"] = pg.inner_text("#status-line")

    # 05 – topic + level filter
    search(pg, "kesehatan")
    pg.click('.chip[data-level="S1"]'); pg.click('.chip[data-level="S2"]')
    to(pg, "#level-filters", 8); snap(pg, "05-filter-s1-s2")
    log["kesehatan + S1,S2"] = pg.inner_text("#status-line")

    # 06 – S6 filter (no S6 journals in the bundled data)
    pg.click("#chip-reset"); search(pg, ""); pg.click('.chip[data-level="S6"]')
    to(pg, "#level-filters", 8); snap(pg, "06-filter-s6-empty")
    log["S6"] = pg.inner_text("#status-line")

    # 07 – no match
    pg.click("#chip-reset"); search(pg, "zzzxqv")
    to(pg, "#level-filters", 8); snap(pg, "07-no-results")
    log["zzzxqv"] = pg.inner_text("#status-line")

    # 08 – pagination button
    search(pg, "pendidikan"); pg.wait_for_timeout(400)
    to(pg, "#load-more", 600); snap(pg, "08-load-more")
    log["load-more pages"] = []
    log["load-more pages"].append(pg.locator("#results .card").count())
    pg.click("#load-more"); log["load-more pages"].append(pg.locator("#results .card").count())

    # 09 – a single card, zoomed (S1 + Scopus + Garuda)
    pg.evaluate("scrollTo(0,0)"); search(pg, "pendidikan IPA Indonesia")
    pg.click('.chip[data-level="S1"]'); pg.wait_for_timeout(500)
    pg.locator("#results .card").first.screenshot(path=str(OUT / "09-card-anatomy.png")); print("saved 09-card-anatomy")
    pg.click("#chip-reset")

    # 10 – draft-analysis tab, empty
    pg.evaluate("scrollTo(0,0)"); search(pg, "")
    pg.click("#tab-btn-predictor"); snap(pg, "10-draft-tab")

    # 11 – too-short draft → native alert (text recorded, alert itself is not in a screenshot)
    pg.fill("#draft-input", "Terlalu pendek."); pg.click("#predictor-form button[type=submit]")
    pg.wait_for_timeout(300); log["short-draft alert"] = dialogs[-1] if dialogs else None

    # 12 – pasted draft (Indonesian, short)
    pg.fill("#draft-input", (SAMPLES / "draft-id-short.txt").read_text())
    pg.evaluate("scrollTo(0,0)"); snap(pg, "11-draft-pasted")

    # 13 – result for Indonesian draft
    pg.click("#predictor-form button[type=submit]"); pg.wait_for_timeout(400)
    to(pg, "#predictor-report", 12); snap(pg, "12-draft-result-id")
    log["draft-id report"] = pg.inner_text("#predictor-report")
    to(pg, "#predictor-status", 12); snap(pg, "13-draft-recommendations-id")
    log["draft-id status"] = pg.inner_text("#predictor-status")

    # 14 – result for English draft
    pg.evaluate("scrollTo(0,0)")
    pg.fill("#draft-input", (SAMPLES / "draft-en-full.txt").read_text())
    pg.click("#predictor-form button[type=submit]"); pg.wait_for_timeout(400)
    to(pg, "#predictor-report", 12); snap(pg, "14-draft-result-en")
    log["draft-en report"] = pg.inner_text("#predictor-report")
    to(pg, "#predictor-status", 12); snap(pg, "15-draft-recommendations-en")
    log["draft-en status"] = pg.inner_text("#predictor-status")
    b.close()

import json
(ROOT / "screenshots" / "_capture-log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2))
print(json.dumps(log, ensure_ascii=False, indent=2))

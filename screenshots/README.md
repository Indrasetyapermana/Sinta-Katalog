# Screenshots

15 images plus [`_capture-log.json`](_capture-log.json), the app text and numbers recorded while capturing.

## How they were captured

| | |
|---|---|
| Source | `assets/public/` unpacked from `app-debug.apk` and served over HTTP |
| Renderer | Headless Chromium via Playwright (`scripts/capture_screenshots.py`) |
| Viewport | 412 × 915 CSS px at 2× (824 × 1830 px), touch + mobile emulation |
| Locale / timezone | `id-ID` / `Asia/Makassar` |
| Fonts | Google Fonts blocked, so the browser's fallback fonts are used |

**What this means:** layout, colours, copy, behaviour and data are exactly the app's. The Android status/navigation bars, WebView text rendering and the real web fonts are **not** reproduced. Native `alert()` dialogs cannot appear in page screenshots, so the short-draft alert is documented as text only.

Regenerate everything:

```bash
python scripts/capture_screenshots.py path/to/app-debug.apk
```

## Index

| File | Shows | State / input |
|---|---|---|
| [`01-home.png`](01-home.png) | Launch screen, search tab | fresh start |
| [`02-catalogue-default.png`](02-catalogue-default.png) | Whole catalogue, first cards | empty query, no filters (S1 first, A–Z) |
| [`03-search-topic.png`](03-search-topic.png) | Topic search | `pendidikan IPA` → 5,554 matches |
| [`04-search-synonym.png`](04-search-synonym.png) | Indonesian → English subject mapping | `pertanian` → 933 matches |
| [`05-filter-s1-s2.png`](05-filter-s1-s2.png) | Level filter + topic | `kesehatan`, S1 + S2 → 133 matches |
| [`06-filter-s6-empty.png`](06-filter-s6-empty.png) | S6 filter, nothing found | S6 only → 0 (shows issues #2, #3, #4) |
| [`07-no-results.png`](07-no-results.png) | No-match message | `zzzxqv` → 0 (shows issue #2) |
| [`08-load-more.png`](08-load-more.png) | Pagination button | `pendidikan`; 18 cards, then 36 after a tap |
| [`09-card-anatomy.png`](09-card-anatomy.png) | One result card, close-up | S1 journal with Scopus + Garuda |
| [`10-draft-tab.png`](10-draft-tab.png) | Draft-analysis tab, empty | |
| [`11-draft-pasted.png`](11-draft-pasted.png) | Draft pasted into the box | [`samples/draft-id-short.txt`](../samples/draft-id-short.txt) |
| [`12-draft-result-id.png`](12-draft-result-id.png) | Report for the Indonesian draft | SINTA 5-6, score 30 |
| [`13-draft-recommendations-id.png`](13-draft-recommendations-id.png) | Recommendations for it | status text + first cards |
| [`14-draft-result-en.png`](14-draft-result-en.png) | Report for the English draft | SINTA 1, score 80 (282 words, 24 citations) |
| [`15-draft-recommendations-en.png`](15-draft-recommendations-en.png) | Recommendations for it | S1 prioritised, topic first |

## Sample drafts

Both are **synthetic**, written only to exercise the analyser. They are not real research.

- [`samples/draft-id-short.txt`](../samples/draft-id-short.txt): Indonesian, 142 words, 5/5 section words, 2 citations.
- [`samples/draft-en-full.txt`](../samples/draft-en-full.txt): English, 282 words, 5/5 section words, 24 distinct citations.

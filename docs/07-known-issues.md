# 07 · Known issues

Findings from inspecting `app-debug.apk` v1.0. Each was **verified** against the bundled files or by running the app's own code in a headless browser. Fix snippets target the web project (`www/app.js`, `www/style.css`, the data pipeline), which was not available, so they are suggestions, not tested patches against your repo.

| # | Issue | Severity | Where |
|---|---|---|---|
| 1 | [Every SINTA profile link is broken](#1-every-sinta-profile-link-is-broken) | **High** | data |
| 2 | [Load-more button stays visible with zero results](#2-load-more-button-stays-visible-with-zero-results) | Medium | CSS |
| 3 | [The S6 filter always returns nothing](#3-the-s6-filter-always-returns-nothing) | Medium | data / UI |
| 7 | [The draft estimator is very coarse](#7-the-draft-estimator-is-very-coarse) | Medium | logic / wording |
| 4 | [Misleading empty-state message with a level filter only](#4-misleading-empty-state-message-with-a-level-filter-only) | Low | JS |
| 5 | [The `description` field does not exist in the data](#5-the-description-field-does-not-exist-in-the-data) | Low | data / JS |
| 6 | [Journals without a subject rank lower](#6-journals-without-a-subject-rank-lower) | Low | data / logic |
| 8 | [Leftover website-era messages](#8-leftover-website-era-messages) | Low | copy |
| 9 | [Fonts depend on the network](#9-fonts-depend-on-the-network) | Low | assets |
| 10 | [Debug build with default branding](#10-debug-build-with-default-branding) | Low | build |
| 11 | [No persistence, frozen data](#11-no-persistence-frozen-data) | Info | design |
| 12 | [URLs are not escaped when rendered](#12-urls-are-not-escaped-when-rendered) | Low | JS |
| 13 | [Empty results container on the draft tab](#13-empty-results-container-on-the-draft-tab) | Cosmetic | JS |

---

## 1. Every SINTA profile link is broken

**Evidence.** All 15,250 records have a `profile_url` with the domain repeated:

```
https://sinta.kemdiktisaintek.go.idhttps://sinta.kemdiktisaintek.go.id/journals/profile/671
```

**Impact.** The journal title on every card is a link to `profile_url`, so tapping any title opens an invalid address.

**Likely cause.** The scraper prefixed the site root onto a value that was already an absolute URL.

**Fix.** Best: correct it in the data pipeline. Defensive client-side patch in `cardTemplate()`:

```js
const fixUrl = (u) => { const i = u.indexOf("http", 1); return i > 0 ? u.slice(i) : u; };
// …
<a href="${fixUrl(journal.profile_url)}" target="_blank" rel="noopener">
```

(Tested: it turns the string above into `https://sinta.kemdiktisaintek.go.id/journals/profile/671` and leaves a correct URL unchanged.)

## 2. Load-more button stays visible with zero results

**Evidence.** For a query with no matches, the code sets `loadMoreWrap.hidden = true`, yet the browser reports `display: flex` for the element, and the button is visible ([screenshot 07](../screenshots/07-no-results.png), [06](../screenshots/06-filter-s6-empty.png)). Tapping it appends another copy of the "no match" message (1 → 3 after two taps).

**Cause.** `.load-more-wrap { display: flex }` overrides the browser's built-in `[hidden] { display: none }`. The stylesheet only restores `[hidden]` for `.tab-panel`.

**Fix.** One rule in `style.css`:

```css
[hidden] { display: none !important; }
```

## 3. The S6 filter always returns nothing

**Evidence.** The filter bar offers S1–S6, but the data contains S1 (262), S2 (1,616), S3 (3,287), S4 (5,778) and S5 (4,307) journals and **0** S6 ([screenshot 06](../screenshots/06-filter-s6-empty.png)). The draft estimator also maps "SINTA 5-6" to `S5` and `S6`.

**Fix.** Either include S6 journals when scraping, or remove the S6 chip. Say in the UI which levels the snapshot covers.

## 4. Misleading empty-state message with a level filter only

With an empty search box and only a level chip selected that has no journals, the app says *"Belum ada data jurnal untuk ditampilkan"* ("No journal data yet"), which suggests the data is missing. The condition is `state.query ? … : …` and ignores active filters.

**Fix.** `state.query || state.activeLevels.size` selects the "coba kata kunci lain / kosongkan saringan" message.

## 5. The `description` field does not exist in the data

`scoreJournal()` reads `journal.description` and awards +6 per query word found in it, but none of the 15,250 records has that field. That scoring branch never runs. It is harmless, but the ranking is purely title + subject. Either add descriptions to the dataset or remove the dead code.

## 6. Journals without a subject rank lower

26% of journals (3,966) have `subject_area: null`. Subject labels (including synonym matches) are the only tie-breaker between equal title scores, so a journal with no label loses ties to one with a label even when its level is higher. Example: for `pendidikan IPA`, the S1 *Jurnal Pendidikan IPA Indonesia* ranks 8th behind three S4 journals ([worked example](04-how-it-works.md#a-worked-example)).

**Fix.** Backfill missing subjects, or break score ties by level before subject bonus.

## 7. The draft estimator is very coarse

The "Estimasi Tingkat" is a point system over word count, distinct citation patterns, section keywords and an English-language check ([rules](04-how-it-works.md#draft-analysis)). Observed consequences:

- A **282-word English sample scores 80 → "SINTA 1"** ([screenshot 14](../screenshots/14-draft-result-en.png)), while a well-formed Indonesian draft is capped at 75 and so can never be "SINTA 1".
- Section detection is substring-based (*"menghasilkan"* counts as *hasil*).
- Citations are counted as distinct text patterns in the body, not verified references.
- Keywords are split into single words, so a phrase like "perpustakaan perguruan tinggi" becomes three independent terms.

The disclaimer in the app is honest, but the large red **"SINTA 1"** heading and a numeric score read as a prediction.

**Suggestions.** Present it as a "manuscript readiness checklist" showing which signals were found; avoid naming a tier; or at least drop the language bias.

## 8. Leftover website-era messages

Several strings assume the web version of the project and make no sense in an installed APK, where data is fixed at build time:

| Where shown | Text (translated) |
|---|---|
| Draft tab, no match | "…try running the data update (full-scrape) or check the 'Cari Jurnal' tab manually" |
| Draft tab, empty data | "The journal catalogue is empty. Run a data update first in the Cari Jurnal tab" |
| Under filter chips, if `last_updated` is `seed-data` | "sample data. Run the GitHub Action to fetch the full data" |
| Footer | "…re-archived periodically by a GitHub Actions workflow **in this repository**" |

## 9. Fonts depend on the network

`index.html` loads Source Serif 4, Inter and IBM Plex Mono from Google Fonts. Offline, or if blocked, the app falls back to generic serif/sans/monospace and looks noticeably different (this is also what the documentation screenshots show). **Fix:** bundle the `.woff2` files in `www/` and declare them with `@font-face`. This also removes the only third-party network request.

## 10. Debug build with default branding

- `debuggable="true"`, file named `app-debug.apk`, version 1.0 / code 1.
- Launcher icon and splash are the stock Capacitor "X" ([`assets/`](../assets)).
- Not suitable for Google Play. See [building a release](06-architecture.md#building-a-release).

## 11. No persistence, frozen data

By design, not a defect: the app keeps nothing between launches (no saved searches or drafts), and the catalogue is a snapshot dated 7 Oct 2026. A user cannot tell when the data becomes stale except by reading the date under the chips.

## 12. URLs are not escaped when rendered

`cardTemplate()` HTML-escapes titles, subjects and ISSNs, but puts `profile_url` and `website` straight into `href="…"`. The data is bundled and trusted, so this is not exploitable today. Escape them with the existing `escapeHtml()` to keep it safe if the data source ever changes.

## 13. Empty results container on the draft tab

`switchTab("predictor")` un-hides the draft results wrapper even before any analysis has run, so an empty report area exists on first visit. It has no visible content, so it is only a cosmetic oddity.

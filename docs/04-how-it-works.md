# 04 · How it works

Everything below is taken directly from the app's bundled `app.js` (≈24 KB, unminified). All processing happens on the phone, on the in-memory list of 15,250 journals.

## Topic search

### 1. Tokenising the query

The query is lower-cased, accent-normalised (Unicode NFKD), stripped of everything except letters, digits and spaces, split on whitespace, and filtered to words of **2+ characters that are not stop words**.

The stop-word list (122 words) covers Indonesian and English function words (*dan, yang, the, of…*) and also **generic academic words** such as *analisis, studi, penelitian, pengaruh, model, sistem, metode, hasil, jurnal, effect, analysis*. These are dropped because they appear in unrelated journal names (the code's own example: "Analisis: Jurnal Studi Keislaman").

> If every word you type is a stop word, no tokens remain. Only journals whose title contains your exact phrase can match.

### 2. Scoring each journal

| Signal | Points | Notes |
|---|---:|---|
| Whole query phrase appears in the title | +60 | strongest signal; needs a query longer than 2 characters |
| Each query word appears in the title **as a whole word** | +22 each | word-boundary match, so "seni" does not match inside "kesenian" |
| *All* query words appear in the title (2+ words) | +25 | bonus |
| Each query word appears in the description | +6 each | see [known issue](07-known-issues.md#5-the-description-field-does-not-exist-in-the-data): the data has no description |
| Each query word is a substring of `subject_area` | +3 each | substring, not whole-word |
| Each synonym of a query word appears in `subject_area` | +1.5 each | [synonym table](#subject-synonyms) |

```
score = (title points) × 10 + (subject/description points)
```

The ×10 means **title evidence always dominates**; subject labels only separate journals with equal title scores. Journals scoring 0 are dropped. The rest are sorted by score (high → low), then by level (S1 first).

### 3. Level filter

S1–S6 chips are applied **before** scoring, and combine as OR (S1 *or* S2). With an empty query and no chips, the full list is shown sorted by level then title.

### 4. Display

Results are shown 18 at a time. Typing re-runs the search after a 220 ms pause; Enter or the button runs it immediately.

### A worked example

For `pendidikan IPA` the app finds 5,554 matches. The first results are **LENSA (Lentera Sains): Jurnal Pendidikan IPA** (S4), **ScienceEdu : Jurnal Pendidikan IPA** (S4) and **VEKTOR: Jurnal Pendidikan IPA** (S4). The S1 journal *Jurnal Pendidikan IPA Indonesia* is only **8th**.

Why: all of their titles contain the phrase and both words, so the title points tie at 129 (60 + 22 + 22 + 25), i.e. 1,290 after the ×10. The tie is then broken by subject: LENSA, ScienceEdu and VEKTOR carry an *Education* label, which earns +1.5 through the *pendidikan → education* synonym (1,291.5 in total). The S1 journal has **no** `subject_area`, so it stays at 1,290. SINTA level only decides order when every score above is equal.

### Subject synonyms

47 Indonesian words map to English SINTA subject labels:

| Indonesian | Matches subject labels containing |
|---|---|
| pertanian | agriculture, agricultural, agro, farming |
| pangan | agriculture, food |
| agribisnis | agriculture, economy, business, agribusiness |
| agroindustri | agriculture, engineering, industry |
| komoditas | agriculture, economy |
| tanaman | agriculture, plant |
| perkebunan | agriculture, plantation |
| budidaya | agriculture, cultivation |
| pascapanen | agriculture, food |
| peternakan | agriculture, animal, veterinary |
| perikanan | agriculture, fisheries, marine |
| kehutanan | agriculture, forestry |
| gizi | health, nutrition, food |
| kesehatan | health, medicine, medical, nursing, pharmacy |
| kedokteran | health, medicine, medical |
| keperawatan | health, nursing |
| farmasi | health, pharmacy |
| pendidikan, pengajaran | education |
| ekonomi | economy, economics, business, finance, management |
| bisnis | economy, business, management |
| akuntansi | economy, accounting |
| manajemen | economy, management |
| teknik, rekayasa | engineering |
| komputer, informatika | engineering, science, computer, informatics |
| hukum | social, law |
| sosial | social |
| politik | social, politics |
| komunikasi | social, communication |
| psikologi | social, health, psychology |
| agama, islam, kristen | religion |
| filsafat | humanities, religion, philosophy |
| budaya | humanities, art, culture |
| bahasa | humanities, education, linguistics |
| sastra | humanities, art, literature |
| seni | art |
| sains | science |
| fisika | science, physics |
| kimia | science, chemistry |
| biologi | science, biology |
| matematika | science, mathematics |
| lingkungan | science, engineering, environment |
| geografi | science, geography, geospatial, geomatics |

---

## Draft analysis

> ⚠️ This is a **heuristic** over text patterns. It does not read, understand or evaluate the research. The app's own disclaimer says it is not an official assessment.

### 1. Input check

The text (trimmed) must be **at least 300 characters**, otherwise an alert is shown and nothing is computed.

### 2. Scoring

| Signal | Rule | Points |
|---|---|---:|
| English text | contains `abstract`, `research` or `background` **and** none of `abstrak`, `penelitian`, `latar belakang` | +25 |
| Length | > 3,000 words | +20 |
| | > 1,500 words | +10 |
| Citations | > 20 distinct | +30 |
| | > 10 distinct | +15 |
| | otherwise (even 0) | +5 |
| Structure | **4 or more** of 5 section words present | +25 |

Maximum possible score: **100**.

**Section words** (case-insensitive *substring* search over the whole text): `introduction|pendahuluan`, `method|metode`, `result|hasil`, `discussion|pembahasan`, `conclusion|kesimpulan`. Because it is substring matching, *"menghasilkan"* counts as *hasil* and *"methodology"* as *method*, so a body containing none of the actual headings can still score the structure bonus.

**Citations** are matches of any of: `[1]`, `[1, 2]`, `[1-3]`; `(Author, 2020)`; `(Author et al., 2020)`; `(2020)`. The count is the number of *distinct matching strings* in the text, not the length of a reference list.

### 3. Tier thresholds

| Score | Label | Report colour |
|---|---|---|
| ≥ 80 | **SINTA 1** | red |
| ≥ 65 | **SINTA 2** | gold |
| ≥ 50 | **SINTA 3-4** | teal |
| < 50 | **SINTA 5-6** | slate |

Consequences that follow directly from the rules:

- A draft that does not count as English (for example any text containing *abstrak*, *penelitian* or *latar belakang*, which is nearly every Indonesian manuscript) **can never score above 75**, so it can never be labelled SINTA 1. To reach SINTA 2 it needs > 3,000 words, > 20 citations and the structure bonus.
- A **short English draft can reach SINTA 1**: English (25) + > 20 citations (30) + structure (25) = 80, at any length. The bundled sample, 282 words, scores exactly that.
- Word count matters little; only two small thresholds (1,500 and 3,000 words) are checked.

### 4. Keyword extraction (up to 8)

1. Lines beginning `Kata kunci` / `Keywords` followed by `:` or `-` are read first. Their phrases (split on `,` or `;`) are tokenised into **single words** (so "perpustakaan perguruan tinggi" becomes three keywords).
2. Remaining slots are filled with the most frequent words of 4+ letters in the body (numbers and stop words excluded).

### 5. Journal recommendation (up to 12)

For every journal, `topicScore` uses the same formula as [topic search](#2-scoring-each-journal), with the detected keywords as the query. Then:

1. Keep only journals with `topicScore > 0`.
2. Add **+50** if the journal's level is one of the estimated tier's levels (SINTA 1 → S1; SINTA 2 → S2; SINTA 3-4 → S3, S4; SINTA 5-6 → S5, S6).
3. Sort by the combined score, then level. Take the top 12.

Since one title-word match is worth 220 points, the +50 level bonus acts only as a **tie-breaker** among similar topical matches. It never promotes a weak topic match.

**Fallback:** if *nothing* matches the keywords, the first 12 journals of the estimated levels are shown, ordered by level alone, with a status message saying so.

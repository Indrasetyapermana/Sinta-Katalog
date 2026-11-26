# 01 · Overview

## What it is

Sinta Katalog is a searchable, offline catalogue of **15,250 Indonesian academic journals** listed in SINTA (Science and Technology Index, run by Indonesia's Ministry of Higher Education, Science and Technology). It is styled as a library card catalogue: results are "cards", the search box is a "request slip" and accreditation levels are rubber "stamps".

## Who it is for

- **Researchers and lecturers** looking for a target journal for a manuscript.
- **Librarians and research-support staff** answering "which journals cover topic X, and at what SINTA level?".
- **Students** checking whether a journal is accredited and indexed.

## What it does

1. **Search by topic** (tab "🔎 Cari Jurnal"). Type a topic in Indonesian or English; results are ranked by how well the journal title and subject labels match. Indonesian topic words such as *pertanian* or *kesehatan* are mapped to the English subject labels SINTA uses (*Agriculture*, *Health*).
2. **Filter by SINTA level** with the S1–S6 chips (multi-select).
3. **Analyse a draft** (tab "📝 Analisis Draf & Rekomendasi"). Paste a full draft article. The app counts words, IMRaD sections and citations, produces a rough tier estimate, detects topic keywords and recommends up to 12 journals.

Each result card shows the journal title, SINTA level stamp, subject labels, a link to the journal website, Scopus/Garuda indexing badges and the E-ISSN.

## What it deliberately does not do

- It is **not an official SINTA or Scopus assessment**. The in-app disclaimer says so, and the draft estimator is a text-pattern heuristic ([details](04-how-it-works.md#draft-analysis)).
- It does not submit anything, create accounts, sync data or collect analytics. The app code makes no network calls other than loading its own bundled data files.
- It does not store searches or drafts. Closing the app clears everything.
- It does not update its data on its own. The catalogue is a snapshot baked into the APK ([05 · Data](05-data.md)).

## Credits shown in the app

The footer reads "Dibuat oleh **Indra**" (made by Indra) and credits SINTA as the data source. The app states it is not officially affiliated with Kemdiktisaintek.

# 05 · Data

## Where the data lives

| File (inside the APK) | Size | Purpose |
|---|---:|---|
| `assets/public/data/journals.json` | 6,802,736 B | The catalogue: a JSON array of journal records |
| `assets/public/data/meta.json` | 79 B | Snapshot date and record count shown under the filter chips |

Both are loaded once at start-up with `fetch()` from the app's own bundled files. The in-app footer says the data comes from [SINTA](https://sinta.kemdiktisaintek.go.id) and was archived by a GitHub Actions workflow in the project's web repository. Check SINTA's terms of use before redistributing the dataset.

## `meta.json`

```json
{ "last_updated": "2026-10-07T07:22:42+00:00", "total_journals": 15250 }
```

`last_updated` is displayed in the device's local timezone (07:22 UTC appears as 15.22 in Makassar). The special value `"seed-data"` makes the app show a "sample data" message instead.

## `journals.json` schema

Each record has exactly these 10 fields (verified across all 15,250 records):

| Field | Type | Example | Notes |
|---|---|---|---|
| `id` | string | `"671"` | SINTA journal ID |
| `title` | string | `"Jurnal Pendidikan IPA Indonesia (Indonesian Journal of Science Education)"` | Searched and displayed |
| `profile_url` | string | see [known issue 1](07-known-issues.md#1-every-sinta-profile-link-is-broken) | **Malformed in every record** |
| `website` | string | `"https://journal.unnes.ac.id/journals/jpii"` | `"#!"` is a placeholder for "none" (3 records); the app treats it as missing |
| `issn_p` | string | `"23391286"` | Print ISSN, stored without the hyphen |
| `issn_e` | string | `"20894392"` | Electronic ISSN, no hyphen; may end in `X` (4 records empty) |
| `subject_area` | string \| null | `"Science, Education"` | Comma-separated English labels; **null in 3,966 records (26.0%)** |
| `sinta_level` | string | `"S1"` | `S1`–`S5` in this snapshot |
| `scopus_indexed` | boolean | `true` | |
| `garuda_indexed` | boolean | `true` | |

There is **no** `description` field, although the code reads one ([known issue 5](07-known-issues.md#5-the-description-field-does-not-exist-in-the-data)).

## Snapshot statistics

Reproduce with `python scripts/data_stats.py app-debug.apk`.

| Measure | Value |
|---|---:|
| Journals | **15,250** |
| S1 | 262 |
| S2 | 1,616 |
| S3 | 3,287 |
| S4 | 5,778 |
| S5 | 4,307 |
| **S6** | **0** |
| Indexed in Scopus | 216 |
| Indexed in Garuda | 15,010 |
| Missing `subject_area` | 3,966 (26.0%) |
| Missing website (`"#!"`) | 3 |
| Missing `issn_e` | 4 |
| Records with a malformed `profile_url` | 15,250 (100%) |

### Most common subject labels

A journal can carry several labels, so these overlap.

| Label | Journals |
|---|---:|
| Education | 5,010 |
| Social | 4,646 |
| Science | 3,400 |
| Humanities | 2,450 |
| Economy | 2,233 |
| Health | 1,685 |
| Engineering | 1,629 |
| Religion | 1,587 |
| Agriculture | 870 |
| Art | 669 |

## Refreshing the data

The APK holds a frozen copy. To update it you must replace the two JSON files in the web project's `www/data/` folder, re-sync Capacitor and rebuild the APK ([06 · Architecture](06-architecture.md#updating-the-data)). The app has no way to refresh itself.

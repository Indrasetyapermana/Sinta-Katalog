#!/usr/bin/env python3
"""Print summary statistics of the journal dataset bundled in an APK."""
import collections, json, sys, zipfile

apk = sys.argv[1] if len(sys.argv) > 1 else "app-debug.apk"
z = zipfile.ZipFile(apk)
data = json.loads(z.read("assets/public/data/journals.json"))
meta = json.loads(z.read("assets/public/data/meta.json"))
n = len(data)
print("meta              :", meta)
print("records           :", n, "| file size:", z.getinfo("assets/public/data/journals.json").file_size, "bytes")
print("fields            :", sorted({k for j in data for k in j}))
print("by level          :", dict(sorted(collections.Counter(j["sinta_level"] for j in data).items())))
print("scopus / garuda   :", sum(j["scopus_indexed"] for j in data), "/", sum(j["garuda_indexed"] for j in data))
print("subject_area null :", sum(not j["subject_area"] for j in data), f"({100*sum(not j['subject_area'] for j in data)/n:.1f}%)")
print("website == '#!'   :", sum(j["website"] == "#!" for j in data))
print("issn_e missing    :", sum(not j["issn_e"] for j in data))
print("doubled profile_url:", sum(j["profile_url"].count("http") > 1 for j in data))
subj = collections.Counter(s.strip() for j in data for s in (j["subject_area"] or "").split(",") if s.strip())
print("top subject labels:", subj.most_common(10))

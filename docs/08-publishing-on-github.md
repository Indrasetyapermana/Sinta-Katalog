# 08 · Publishing this repo on GitHub

This repo is plain Markdown plus images, so GitHub shows it correctly with no build step. Screenshots, the animated GIF and the Mermaid diagram all render in the normal repository view, as long as the folder layout and relative paths stay as they are.

## 1. Create an empty repository

On github.com: **New repository** → name it (e.g. `sinta-katalog-docs`) → choose Public or Private.
Leave **"Add a README"**, **.gitignore** and **license** *unchecked*. This repo already has them, and ticking them creates a conflict on first push.

## 2. Push the files

Unzip `sinta-katalog-docs.zip`, open a terminal in the folder and run (replace `<user>`):

```bash
git init -b main
git add .
git commit -m "Add Sinta Katalog documentation"
git remote add origin https://github.com/<user>/sinta-katalog-docs.git
git push -u origin main
```

**Authentication.** GitHub no longer accepts account passwords over HTTPS. Use one of:

- **GitHub CLI** (simplest): `gh auth login`, then skip the `remote add` / `push` lines and run
  `gh repo create sinta-katalog-docs --public --source=. --push`
- **Personal access token**: paste it when Git asks for a password.
- **SSH**: use `git@github.com:<user>/sinta-katalog-docs.git` as the remote after adding an SSH key.

## 3. Check it rendered

Open the repo page and confirm:

- [ ] The three screenshots and `assets/demo.gif` appear in the README, and the GIF animates.
- [ ] The architecture diagram in `docs/06-architecture.md` is drawn, not shown as code.
- [ ] Links between docs and the image links in `docs/03-user-guide.md` all work.

If an image is missing, the cause is almost always a renamed folder or a different upper/lower-case in the path. GitHub paths are case-sensitive.

## 4. Share the APK as a Release, not as a file in the repo

`.gitignore` blocks `*.apk` on purpose. Binary files bloat Git history permanently, and this one is a **debug build** ([issue 10](07-known-issues.md#10-debug-build-with-default-branding)). If you want people to download it:

```bash
gh release create v1.0 path/to/app-debug.apk --title "Sinta Katalog 1.0 (debug)" --notes "Debug build. See docs/02-installation.md."
```

Or on github.com: **Releases → Draft a new release → attach the file**. Release assets can be much larger than repo files (GitHub warns at 50 MB and blocks repo files above 100 MB), so a release also avoids the size limit.

> **Before publishing publicly:** if the app is not yours, ask its author first. The footer credits "Indra", and the APK bundles a 15,250-record snapshot of SINTA data. Check SINTA's terms of use for redistribution.

## 5. Polish the repo page

- **About** (gear icon, top right): add a one-line description and topics such as `android`, `capacitor`, `documentation`, `sinta`, `indonesia`, `journals`.
- **Social preview**: Settings → General → Social preview. A 1280 × 640 px image works well, e.g. three screenshots side by side.
- **License**: choose one. The README currently says none has been chosen. Documentation is commonly released under CC BY 4.0; code samples under MIT.

## 6. Optional: GitHub Pages

Not required. The repository view is already a readable docs site. If you still want a web address, go to Settings → Pages → *Deploy from a branch* → `main` / `/ (root)`. Two caveats on a plain Jekyll build: the Mermaid diagram shows as code, and links between `.md` files may need the `jekyll-relative-links` plugin to resolve.

## 7. Keeping it up to date

When you get a new APK:

```bash
python scripts/inspect_manifest.py new.apk      # version, SDK, permissions
python scripts/data_stats.py       new.apk      # refresh docs/05-data.md numbers
python scripts/capture_screenshots.py new.apk   # regenerate screenshots
python scripts/make_demo_gif.py    new.apk      # regenerate assets/demo.gif
git add -A && git commit -m "Update docs for vX.Y" && git push
```

Then update the version and statistics tables by hand. Those are not generated automatically.

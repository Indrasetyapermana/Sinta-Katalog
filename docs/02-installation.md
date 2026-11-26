# 02 · Installation

## Requirements

| | |
|---|---|
| Android version | **7.0 (API 24) or newer** |
| Free storage | 5.2 MB for the APK, plus a few MB that Android generates at install time |
| Internet | Not required for search. Used only for Google Fonts and when opening journal links |

## Install (sideloading)

`app-debug.apk` is a **debug build**, not distributed through Google Play, so it must be sideloaded.

1. Copy `app-debug.apk` to the phone (USB, cloud drive, messaging app).
2. Open it from a file manager.
3. If Android blocks the install, allow **"Install unknown apps"** for the app you opened the file from (Settings → Apps → *that app* → Install unknown apps).
4. Tap **Install**. Google Play Protect may warn that the app is unrecognised. That is expected for a debug-signed APK from outside the Play Store.
5. Open **Sinta Katalog** from the launcher. You will see the default Capacitor splash (a blue "X" on white), then the search screen.

### Install from a computer with adb

```bash
adb install -r app-debug.apk
```

Requires USB debugging enabled on the phone. `-r` reinstalls over an existing copy.

## First launch check

The line under the filter chips should read:

> Katalog berisi 15.250 jurnal · diperbarui 7 Oktober 2026 …

("Catalogue contains 15,250 journals · updated 7 October 2026 …"). The time is shown in the device's local timezone. If you instead see *"Gagal memuat data katalog…"* the bundled data file failed to load. Reinstall the APK.

## Updating

There is no auto-update. A new data snapshot or fix requires a new APK. Android upgrades in place only when the new APK has the same package name and signing key and a higher `versionCode` (this build is `1`). Otherwise uninstall first.

## Uninstalling

Long-press the icon → App info → Uninstall, or:

```bash
adb uninstall com.sinta.katalog
```

The app stores no user data, so nothing is left behind.

## Security notes

- The manifest sets `debuggable=true`. Do not distribute this build publicly; build a release APK first ([06 · Architecture](06-architecture.md#building-a-release)).
- The only permission requested is `INTERNET`.
- `allowBackup` is `true`, which is harmless here because the app persists nothing.

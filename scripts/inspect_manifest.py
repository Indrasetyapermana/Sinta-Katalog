#!/usr/bin/env python3
"""Print the key facts from an APK's binary AndroidManifest.xml (no Android SDK needed)."""
import struct, sys, zipfile

def parse(data):
    # chunk header: type(2) headerSize(2) size(4)
    pos = 8
    strings = []
    out = []
    while pos < len(data):
        t, hs, sz = struct.unpack_from("<HHI", data, pos)
        if t == 0x0001:  # string pool
            n, _, flags, sstart, _ = struct.unpack_from("<IIIII", data, pos + 8)
            offs = struct.unpack_from(f"<{n}I", data, pos + 28)
            utf8 = flags & 0x100
            base = pos + sstart
            for o in offs:
                p = base + o
                if utf8:
                    p0 = p
                    p0 += 1 if not (data[p0] & 0x80) else 2          # skip u16 char length
                    bl = data[p0]; p0 += 1                           # u8 byte length
                    if bl & 0x80: bl = ((bl & 0x7f) << 8) | data[p0]; p0 += 1
                    strings.append(data[p0:p0 + bl].decode("utf8", "replace"))
                else:
                    l = struct.unpack_from("<H", data, p)[0]
                    if l & 0x8000: l = ((l & 0x7fff) << 16) | struct.unpack_from("<H", data, p + 2)[0]; p += 4
                    else: p += 2
                    strings.append(data[p:p + l * 2].decode("utf-16le", "replace"))
        elif t == 0x0102:  # start element
            ns, name, astart, asize, acount = struct.unpack_from("<iiHHH", data, pos + 16)
            attrs = {}
            ap = pos + 16 + astart
            for i in range(acount):
                ans, an, araw, vsize, _, vtype, vdata = struct.unpack_from("<iiiHBBI", data, ap + i * 20)
                val = strings[araw] if araw >= 0 else (bool(vdata) if vtype == 0x12 else vdata)
                attrs[strings[an]] = val
            out.append((strings[name], attrs))
        pos += sz
    return out

apk = sys.argv[1] if len(sys.argv) > 1 else "app-debug.apk"
els = parse(zipfile.ZipFile(apk).read("AndroidManifest.xml"))
for name, a in els:
    if name == "manifest":
        print("package      :", a.get("package")); print("versionName  :", a.get("versionName")); print("versionCode  :", a.get("versionCode"))
    elif name == "uses-sdk":
        print("minSdk       :", a.get("minSdkVersion")); print("targetSdk    :", a.get("targetSdkVersion"))
    elif name == "application":
        print("debuggable   :", a.get("debuggable")); print("allowBackup  :", a.get("allowBackup"))
    elif name in ("uses-permission", "permission"):
        print(f"{name:13}:", a.get("name"))
    elif name == "activity":
        print("activity     :", a.get("name"), "| exported:", a.get("exported"), "| launchMode:", a.get("launchMode"))

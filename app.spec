# -*- mode: python ; coding: utf-8 -*-
import shutil
import os


a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("mu.ico", "."),
        ("DejaVuSans.ttf", "."),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "ssl", "_ssl",
        "_asyncio", "asyncio",
        "_bz2", "bz2",
        "_lzma", "lzma",
        "_zstd",  # Python 3.14+ only; harmless on 3.12

        "_wmi",
        "_multiprocessing",
        "charset_normalizer",
        "_hashlib",
        "_decimal",
        "pyexpat",
        "_elementtree",
        "PIL._avif",
        "PIL._imagingcms",
        "PIL._webp",
        "PIL._imagingmath",
    ],
    noarchive=False,
    optimize=1,
)
# Drop Windows API Set stubs and ucrtbase — present in C:\Windows\System32 on Windows 10+
a.binaries = [b for b in a.binaries if not b[0].startswith("api-ms-") and b[0] != "ucrtbase.dll"]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Bohrprofil",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon="mu.ico",
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="Bohrprofil",
)

shutil.copytree("patterns", "dist/Bohrprofil/patterns", dirs_exist_ok=True)
shutil.copy("config.ini", "dist/Bohrprofil/config.ini")

# Remove unused Tcl timezone data (~2MB)
tzdata_path = os.path.join("dist", "Bohrprofil", "_internal", "_tcl_data", "tzdata")
if os.path.isdir(tzdata_path):
    shutil.rmtree(tzdata_path)

# Remove Tcl HTTP package (not used)
http_path = os.path.join("dist", "Bohrprofil", "_internal", "_tcl_data", "http1.0")
if os.path.isdir(http_path):
    shutil.rmtree(http_path)

# Remove unused Tcl packages (HTTP client and test framework) — match by name prefix, not version
import glob as _glob
for _pattern in [
    os.path.join("dist", "Bohrprofil", "_internal", "tcl8", "8.6", "http-*.tm"),
    os.path.join("dist", "Bohrprofil", "_internal", "tcl8", "8.5", "tcltest-*.tm"),
]:
    for _tm in _glob.glob(_pattern):
        os.remove(_tm)

# Remove CJK and specialty Tcl encodings (~1.4MB) — not needed for a German/European app
_REMOVE_ENCODINGS = {
    "big5.enc", "cns11643.enc",
    "cp932.enc", "cp936.enc", "cp949.enc", "cp950.enc",
    "euc-cn.enc", "euc-jp.enc", "euc-kr.enc",
    "gb12345.enc", "gb1988.enc", "gb2312.enc", "gb2312-raw.enc",
    "jis0201.enc", "jis0208.enc", "jis0212.enc",
    "ksc5601.enc", "shiftjis.enc", "macJapan.enc",
    "tis-620.enc", "ebcdic.enc", "dingbats.enc", "symbol.enc",
}
_enc_dir = os.path.join("dist", "Bohrprofil", "_internal", "_tcl_data", "encoding")
if os.path.isdir(_enc_dir):
    for f in os.listdir(_enc_dir):
        if f in _REMOVE_ENCODINGS:
            os.remove(os.path.join(_enc_dir, f))

# Trim locale msg files — keep only de and en
_KEEP_LOCALES = {"de.msg", "en.msg", "en_gb.msg"}
for msgs_dir in [
    os.path.join("dist", "Bohrprofil", "_internal", "_tcl_data", "msgs"),
    os.path.join("dist", "Bohrprofil", "_internal", "_tk_data", "msgs"),
]:
    if os.path.isdir(msgs_dir):
        for f in os.listdir(msgs_dir):
            if f not in _KEEP_LOCALES:
                os.remove(os.path.join(msgs_dir, f))

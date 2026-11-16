import glob
import os
import shutil
import subprocess
import sys

subprocess.run([
    sys.executable, "-m", "nuitka",
    "--standalone",
    "--assume-yes-for-downloads",  # non-interactive (CI): fetch dependency tools without prompting
    "--windows-console-mode=disable",
    "--windows-icon-from-ico=mu.ico",
    "--enable-plugin=tk-inter",
    "--enable-plugin=anti-bloat",
    "--include-data-files=mu.ico=mu.ico",
    "--include-data-files=DejaVuSans.ttf=DejaVuSans.ttf",
    "--output-dir=dist",
    "--output-filename=Bohrprofil",
    "app.py",
], check=True)

out = "dist/app.dist"
shutil.copytree("patterns", f"{out}/patterns", dirs_exist_ok=True)
shutil.copy("config.ini", f"{out}/config.ini")

# SSL — no network in this app
for f in ["libcrypto-3-x64.dll", "libssl-3-x64.dll", "_ssl.pyd"]:
    p = os.path.join(out, f)
    if os.path.isfile(p):
        os.remove(p)

# Unused Python extension modules
for f in ["_decimal.pyd", "pyexpat.pyd", "_lzma.pyd", "_bz2.pyd",
          "_elementtree.pyd", "_hashlib.pyd", "_wmi.pyd",
          "_socket.pyd", "select.pyd"]:
    p = os.path.join(out, f)
    if os.path.isfile(p):
        os.remove(p)

# Unused PIL codecs
for f in ["_webp.pyd", "_imagingcms.pyd", "_imagingmath.pyd"]:
    p = os.path.join(out, "PIL", f)
    if os.path.isfile(p):
        os.remove(p)

# Tcl timezone data
tzdata = os.path.join(out, "tcl", "tzdata")
if os.path.isdir(tzdata):
    shutil.rmtree(tzdata)

# Tcl http1.0 package
http = os.path.join(out, "tcl", "http1.0")
if os.path.isdir(http):
    shutil.rmtree(http)

# Tcl8 http/tcltest .tm files
for pattern in [
    os.path.join(out, "tcl8", "8.6", "http-*.tm"),
    os.path.join(out, "tcl8", "8.5", "tcltest-*.tm"),
]:
    for f in glob.glob(pattern):
        os.remove(f)

# CJK and specialty Tcl encodings
_REMOVE_ENCODINGS = {
    "big5.enc", "cns11643.enc",
    "cp932.enc", "cp936.enc", "cp949.enc", "cp950.enc",
    "euc-cn.enc", "euc-jp.enc", "euc-kr.enc",
    "gb12345.enc", "gb1988.enc", "gb2312.enc", "gb2312-raw.enc",
    "jis0201.enc", "jis0208.enc", "jis0212.enc",
    "ksc5601.enc", "shiftjis.enc", "macJapan.enc",
    "tis-620.enc", "ebcdic.enc", "dingbats.enc", "symbol.enc",
}
enc_dir = os.path.join(out, "tcl", "encoding")
if os.path.isdir(enc_dir):
    for f in os.listdir(enc_dir):
        if f in _REMOVE_ENCODINGS:
            os.remove(os.path.join(enc_dir, f))

# Tcl/Tk locale messages — keep only de and en
_KEEP_LOCALES = {"de.msg", "de_at.msg", "de_be.msg", "en.msg", "en_gb.msg"}
for msgs_dir in [
    os.path.join(out, "tcl", "msgs"),
    os.path.join(out, "tk", "msgs"),
]:
    if os.path.isdir(msgs_dir):
        for f in os.listdir(msgs_dir):
            if f not in _KEEP_LOCALES:
                os.remove(os.path.join(msgs_dir, f))

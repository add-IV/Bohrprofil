import subprocess
import shutil
import sys

subprocess.run([
    sys.executable, "-m", "nuitka",
    "--standalone",
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

# PyInstaller spec: bouwt twee losse .exe-bestanden:
#   - BJAssistant.exe   (src/main.py)      - de live tool
#   - BJKalibreren.exe  (src/calibrate.py) - de kalibratietool
#
# Bouwen (op Windows, met de venv actief):
#   pyinstaller build.spec
#
# Resultaat komt in dist/BJAssistant.exe en dist/BJKalibreren.exe.
# Zet beide .exe-bestanden in dezelfde map (ze delen config.json en templates/,
# die naast de .exe-bestanden worden aangemaakt).

import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE

block_cipher = None
common_kwargs = dict(
    pathex=["src"],
    binaries=[],
    datas=[],
    hiddenimports=["cv2", "mss", "numpy"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

# ---- BJAssistant.exe (main.py) ----
a_main = Analysis(["src/main.py"], **common_kwargs)
pyz_main = PYZ(a_main.pure, a_main.zipped_data, cipher=block_cipher)
exe_main = EXE(
    pyz_main, a_main.scripts, a_main.binaries, a_main.zipfiles, a_main.datas, [],
    name="BJAssistant",
    console=True,       # console venster blijft zichtbaar (handig voor foutmeldingen)
    icon=None,
)

# ---- BJKalibreren.exe (calibrate.py) ----
a_cal = Analysis(["src/calibrate.py"], **common_kwargs)
pyz_cal = PYZ(a_cal.pure, a_cal.zipped_data, cipher=block_cipher)
exe_cal = EXE(
    pyz_cal, a_cal.scripts, a_cal.binaries, a_cal.zipfiles, a_cal.datas, [],
    name="BJKalibreren",
    console=True,
    icon=None,
)

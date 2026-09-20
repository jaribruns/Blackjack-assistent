"""
Bepaalt waar config.json en de templates/-map horen te staan.

Belangrijk voor de .exe-versie: PyInstaller pakt in 'onefile'-modus alle
code uit naar een TIJDELIJKE map die na afsluiten weer verdwijnt. Als we
daar config/templates in zouden opslaan, ben je na elke herstart je
kalibratie kwijt. Daarom gebruiken we bij een gecompileerde .exe altijd de
map WAAR HET .EXE-BESTAND STAAT, niet de tijdelijke uitpakmap.
"""
import os
import sys


def base_dir():
    if getattr(sys, "frozen", False):
        # Gecompileerde .exe: gebruik de map van het .exe-bestand zelf.
        return os.path.dirname(sys.executable)
    # Normale Python-run: project root = 1 map boven src/
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

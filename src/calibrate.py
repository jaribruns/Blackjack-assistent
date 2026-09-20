"""
Kalibratietool: leert de app hoe elke kaart eruitziet op JOUW specifieke site.

Werkwijze:
1. Start een gratis potje blackjack op de site.
2. Draai (indien mogelijk) net zo lang tot je 1 kaart alleen op tafel ziet
   (bv. je eigen eerste kaart), of gebruik de site's "kaart demo"/instant-play
   als die een losse kaart toont.
3. Dit script laat je telkens een vak om 1 kaart tekenen, en vraagt in de
   console welke kaart het is (bv. "AS" voor Aas Schoppen, "10H" voor 10 Harten).
4. Herhaal voor zoveel mogelijk van de 52 kaarten (hoe meer, hoe beter de
   herkenning; minimaal alle 13 rangen in 1 kleur helpt al, maar per site
   kunnen cijfers/symbolen per kleur verschillen dus liefst alle 52).

Templates worden opgeslagen in de map templates/ als "<RANG><KLEUR>.png",
bv AS.png, 10H.png, JD.png, KC.png.
"""
import os
import sys
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capture import grab_region
from region_selector import select_region
from card_matcher import RANKS, SUITS, TEMPLATE_DIR
from calibrate_overlay import CalibrationOverlay

SUIT_NAMES = {"S": "Schoppen (Spades)", "H": "Harten (Hearts)", "D": "Ruiten (Diamonds)", "C": "Klaveren (Clubs)"}


def main():
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    print("=== Blackjack Assistant - Kalibratie ===")
    print("Voor elke kaart: leg 'm zichtbaar op tafel, teken er een vak omheen,")
    print("en typ het label in de console (bv A S, 10 H, K D). Typ 'stop' om te stoppen.\n")

    existing = {f[:-4] for f in os.listdir(TEMPLATE_DIR) if f.endswith(".png")}
    if existing:
        print(f"Al {len(existing)} kaarten gekalibreerd: {sorted(existing)}\n")

    progress = CalibrationOverlay(done_labels=existing)
    print("(Er staat nu ook een voortgangsvenster op je scherm dat live bijhoudt")
    print(" welke kaarten al gekalibreerd zijn.)\n")

    while True:
        rank = input("Rang (A,2-9,10,J,Q,K) of 'stop': ").strip().upper()
        if rank == "STOP":
            break
        if rank not in RANKS:
            print("Onbekende rang, probeer opnieuw.")
            continue
        suit = input("Kleur (S/H/D/C): ").strip().upper()
        if suit not in SUITS:
            print("Onbekende kleur, probeer opnieuw.")
            continue

        label = f"{rank}{suit}"
        print(f">> Teken nu een vak strak om de {rank} van {SUIT_NAMES[suit]}...")
        region = select_region(f"Teken een vak om: {rank} {SUIT_NAMES[suit]}")
        if not region or region[2] < 5 or region[3] < 5:
            print("Geen geldige regio geselecteerd, sla over.")
            continue

        img = grab_region(region)
        path = os.path.join(TEMPLATE_DIR, f"{label}.png")
        cv2.imwrite(path, img)
        progress.mark_done(label)
        print(f"Opgeslagen: {path}\n")

    progress.close()
    print("Kalibratie klaar.")


if __name__ == "__main__":
    main()

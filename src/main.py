"""
Blackjack Assistant - hoofdprogramma (exacte-samenstelling-versie).

Pipeline per cyclus:
  scherm lezen -> kaarten herkennen -> exacte schoen-samenstelling bijwerken
  -> exacte kansberekening (achtergrondthread) -> advies tonen in overlay.

De schoen-tracker onthoudt precies welke kaarten er zijn geweest en hoeveel
er per rang nog over zijn; de kansberekening gebruikt die werkelijke
samenstelling (geen Hi-Lo-benadering).

Bedoeld voor gratis / play-money spellen.
"""
import sys
import os
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config, save_config
from region_selector import select_region
from capture import grab_region
from card_detect import find_card_boxes, crop_boxes
from card_matcher import CardMatcher, label_to_rank
from shoe import ExactShoe, GROUP_ORDER
from engine_worker import EngineWorker
from overlay import Overlay


def _to_group(rank13):
    return "10" if rank13 in ("10", "J", "Q", "K") else rank13


def setup_regions(cfg):
    print("Selecteer het vak rond JOUW kaarten (speler).")
    time.sleep(1)
    cfg["player_region"] = select_region("Teken een vak om JOUW kaarten")
    print("Speler-regio:", cfg["player_region"])

    print("Selecteer het vak rond de kaart(en) van de DEALER.")
    time.sleep(1)
    cfg["dealer_region"] = select_region("Teken een vak om de DEALER-kaart(en)")
    print("Dealer-regio:", cfg["dealer_region"])

    save_config(cfg)
    print("Regio's opgeslagen.\n")


def recognize_region(region, matcher):
    """
    Retourneert (labels, info) waarbij info aangeeft hoe zeker de herkenning is:
      - unmatched: aantal gevonden kaartvormen die NIET aan een template
        gekoppeld konden worden (dit zijn potentieel GEMISTE kaarten - ze
        tellen niet mee in de berekening, wat het schoen-geheugen laat afwijken)
      - low_confidence: aantal kaarten die wel herkend zijn, maar met een
        magere score (net over de drempel) - waarschijnlijk goed, niet zeker
      - boxes_found: totaal aantal kaartvormen gevonden in de regio
    """
    img = grab_region(region)
    boxes = find_card_boxes(img)
    crops = crop_boxes(img, boxes)
    labels = []
    unmatched = 0
    low_confidence = 0
    safe_margin = 1.15  # score moet 15% boven de kale drempel zitten om "zeker" te zijn
    for crop in crops:
        label, score = matcher.identify(crop)
        if label and label_to_rank(label):
            labels.append(label)
            if score < matcher.threshold * safe_margin:
                low_confidence += 1
        else:
            unmatched += 1
    return labels, {"unmatched": unmatched, "low_confidence": low_confidence, "boxes_found": len(boxes)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", action="store_true", help="Regio's opnieuw instellen")
    parser.add_argument("--decks", type=int, default=None, help="Aantal decks in het schoen")
    args = parser.parse_args()

    cfg = load_config()
    if args.decks:
        cfg["num_decks"] = args.decks
        save_config(cfg)

    if args.setup or not cfg.get("player_region") or not cfg.get("dealer_region"):
        setup_regions(cfg)

    matcher = CardMatcher(threshold=cfg["match_threshold"])
    if len(matcher.templates) == 0:
        print("WAARSCHUWING: geen kaart-templates gevonden. Draai eerst calibrate.py")

    shoe = ExactShoe(num_decks=cfg["num_decks"])
    worker = EngineWorker()

    ox, oy = cfg.get("overlay_position", [40, 40])
    overlay = Overlay(x=ox, y=oy)

    def on_new_shoe():
        shoe.reset()
        worker.clear_cache()
        print("Schoen gereset (nieuw schoen).")

    overlay.new_shoe_callback = on_new_shoe

    round_id = 0
    print("Live herkenning gestart. Sluit het overlay-venster om te stoppen.")

    try:
        while True:
            try:
                player_labels, p_info = recognize_region(cfg["player_region"], matcher)
                dealer_labels, d_info = recognize_region(cfg["dealer_region"], matcher)
            except Exception as e:
                overlay.status_label.config(text=f"Herkenningsfout: {e}")
                overlay.tick()
                time.sleep(cfg["capture_interval_ms"] / 1000)
                continue

            # Betrouwbaarheid van deze cyclus: zijn er kaartvormen gevonden die
            # NIET aan een template gekoppeld konden worden (potentieel gemist),
            # of alleen met een magere score herkend (onzeker)?
            missed = p_info["unmatched"] + d_info["unmatched"]
            uncertain_low = p_info["low_confidence"] + d_info["low_confidence"]
            reliability_warning = None
            if missed > 0:
                reliability_warning = (f"⚠ {missed} kaartvorm(en) NIET herkend — deze tellen niet mee. "
                                        f"Berekening is NIET betrouwbaar deze cyclus.")
            elif uncertain_low > 0:
                reliability_warning = (f"⚠ {uncertain_low} kaart(en) met lage herkenningszekerheid — "
                                        f"controleer of dit klopt.")

            # Nieuwe ronde zodra beide vakken leeg zijn -> schermposities weer vrijgeven
            if not player_labels and not dealer_labels:
                round_id += 1
                shoe.new_round()

            # Elke zichtbare kaart precies 1x per ronde uit het schoen halen.
            # De verdekte dealerkaart is nog niet zichtbaar en wordt dus (terecht)
            # nog niet verwijderd - de engine behandelt hem als onbekende kaart.
            for i, lbl in enumerate(player_labels):
                shoe.register(f"r{round_id}_player_{i}", lbl)
            for i, lbl in enumerate(dealer_labels):
                shoe.register(f"r{round_id}_dealer_{i}", lbl)

            calib_text = f"Kalibratie: {len(matcher.templates)}/52 kaarten geladen"
            if len(matcher.templates) < 52:
                calib_text += "  (mist mogelijk kaarten!)"
            shoe_text = (f"{shoe.summary_text()}\n"
                         f"Gespeeld: {shoe.total_dealt()} kaarten ({shoe.penetration()*100:.0f}% van schoen)\n"
                         f"{calib_text}")

            player_groups = [_to_group(label_to_rank(l)) for l in player_labels]
            dealer_groups = [_to_group(label_to_rank(l)) for l in dealer_labels]

            if player_groups and dealer_groups:
                dealer_up = dealer_groups[0]
                can_split = (len(player_groups) == 2 and player_groups[0] == player_groups[1])
                can_double = (len(player_groups) == 2)

                worker.request(player_groups, dealer_up, shoe.group_counts_tuple(),
                               can_split=can_split, can_double=can_double)
                result, busy = worker.latest()

                hand_text = f"Jij: {'+'.join(player_groups)}   Dealer toont: {dealer_up}"
                status = "Berekenen..." if busy else ""
                if result:
                    overlay.show_result(result, hand_text, shoe_text, status, warning=reliability_warning)
                else:
                    overlay.show_waiting(shoe_text, "Berekenen...", warning=reliability_warning)
            else:
                overlay.show_waiting(shoe_text, warning=reliability_warning)

            overlay.tick()
            time.sleep(cfg["capture_interval_ms"] / 1000)

    except Exception as e:
        import tkinter
        if not isinstance(e, tkinter.TclError):
            raise
    except KeyboardInterrupt:
        pass
    print("Gestopt.")


if __name__ == "__main__":
    main()

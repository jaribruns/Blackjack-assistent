"""
Configuratie voor de Blackjack Assistant.
Regio's en instellingen worden opgeslagen in config.json naast dit script.
"""
import json
import os
from paths import base_dir

CONFIG_PATH = os.path.join(base_dir(), "config.json")

DEFAULT_CONFIG = {
    "num_decks": 6,                # aantal decks in het schoen (staat meestal op de site vermeld)
    "player_region": None,         # [x, y, w, h] - vak rond de kaarten van de speler
    "dealer_region": None,         # [x, y, w, h] - vak rond de kaart(en) van de dealer
    "capture_interval_ms": 800,    # hoe vaak (ms) het scherm wordt gecheckt
    "match_threshold": 0.72,       # minimale overeenkomst (0-1) om een kaart te herkennen
    "overlay_position": [40, 40],  # startpositie van het adviesvenster
}


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        merged = {**DEFAULT_CONFIG, **cfg}
        return merged
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

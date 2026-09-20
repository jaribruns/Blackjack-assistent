"""
Blackjack basisstrategie (4-8 decks, dealer staat op soft 17, double-after-split
toegestaan, geen surrender aangenomen - conservatieve default die op vrijwel
elke site geldig/veilig is) + een verkorte set count-gebaseerde afwijkingen
(vereenvoudigde 'Illustrious 18'-achtige deviaties op basis van de true count).

Acties: "HIT", "STAND", "DOUBLE" (anders HIT), "DOUBLE_STAND" (anders STAND),
"SPLIT"
"""

RANK_VALUES = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11,
}

DEALER_COLS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "A"]

# ---- HARD TOTALS (player_total 5..17, boven 17 altijd STAND, 8 en lager altijd HIT) ----
# rij per player total, kolom per dealer upcard
HARD_TABLE = {
    5:  {c: "HIT" for c in DEALER_COLS},
    6:  {c: "HIT" for c in DEALER_COLS},
    7:  {c: "HIT" for c in DEALER_COLS},
    8:  {c: "HIT" for c in DEALER_COLS},
    9:  {"2": "HIT", "3": "DOUBLE", "4": "DOUBLE", "5": "DOUBLE", "6": "DOUBLE",
         "7": "HIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},
    10: {"2": "DOUBLE", "3": "DOUBLE", "4": "DOUBLE", "5": "DOUBLE", "6": "DOUBLE",
         "7": "DOUBLE", "8": "DOUBLE", "9": "DOUBLE", "10": "HIT", "A": "HIT"},
    11: {c: "DOUBLE" for c in DEALER_COLS},
    12: {"2": "HIT", "3": "HIT", "4": "STAND", "5": "STAND", "6": "STAND",
         "7": "HIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},
    13: {"2": "STAND", "3": "STAND", "4": "STAND", "5": "STAND", "6": "STAND",
         "7": "HIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},
    14: {"2": "STAND", "3": "STAND", "4": "STAND", "5": "STAND", "6": "STAND",
         "7": "HIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},
    15: {"2": "STAND", "3": "STAND", "4": "STAND", "5": "STAND", "6": "STAND",
         "7": "HIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},
    16: {"2": "STAND", "3": "STAND", "4": "STAND", "5": "STAND", "6": "STAND",
         "7": "HIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},
    17: {c: "STAND" for c in DEALER_COLS},
}

# ---- SOFT TOTALS (A+2 .. A+9) ----
SOFT_TABLE = {
    13: {"2": "HIT", "3": "HIT", "4": "HIT", "5": "DOUBLE", "6": "DOUBLE",
         "7": "HIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},         # A,2
    14: {"2": "HIT", "3": "HIT", "4": "HIT", "5": "DOUBLE", "6": "DOUBLE",
         "7": "HIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},         # A,3
    15: {"2": "HIT", "3": "HIT", "4": "DOUBLE", "5": "DOUBLE", "6": "DOUBLE",
         "7": "HIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},         # A,4
    16: {"2": "HIT", "3": "HIT", "4": "DOUBLE", "5": "DOUBLE", "6": "DOUBLE",
         "7": "HIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},         # A,5
    17: {"2": "HIT", "3": "DOUBLE", "4": "DOUBLE", "5": "DOUBLE", "6": "DOUBLE",
         "7": "HIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},         # A,6
    18: {"2": "DOUBLE_STAND", "3": "DOUBLE_STAND", "4": "DOUBLE_STAND", "5": "DOUBLE_STAND", "6": "DOUBLE_STAND",
         "7": "STAND", "8": "STAND", "9": "HIT", "10": "HIT", "A": "HIT"},     # A,7
    19: {c: "STAND" for c in DEALER_COLS},                                     # A,8
    20: {c: "STAND" for c in DEALER_COLS},                                     # A,9
}

# ---- PAIRS ----
PAIR_TABLE = {
    "2":  {"2": "SPLIT", "3": "SPLIT", "4": "SPLIT", "5": "SPLIT", "6": "SPLIT",
           "7": "SPLIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},
    "3":  {"2": "SPLIT", "3": "SPLIT", "4": "SPLIT", "5": "SPLIT", "6": "SPLIT",
           "7": "SPLIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},
    "4":  {"2": "HIT", "3": "HIT", "4": "HIT", "5": "SPLIT", "6": "SPLIT",
           "7": "HIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},
    "5":  {c: "DOUBLE" if c != "10" and c != "A" else "HIT" for c in DEALER_COLS},  # speel als harde 10
    "6":  {"2": "SPLIT", "3": "SPLIT", "4": "SPLIT", "5": "SPLIT", "6": "SPLIT",
           "7": "HIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},
    "7":  {"2": "SPLIT", "3": "SPLIT", "4": "SPLIT", "5": "SPLIT", "6": "SPLIT",
           "7": "SPLIT", "8": "HIT", "9": "HIT", "10": "HIT", "A": "HIT"},
    "8":  {c: "SPLIT" for c in DEALER_COLS},
    "9":  {"2": "SPLIT", "3": "SPLIT", "4": "SPLIT", "5": "SPLIT", "6": "SPLIT",
           "7": "STAND", "8": "SPLIT", "9": "SPLIT", "10": "STAND", "A": "STAND"},
    "10": {c: "STAND" for c in DEALER_COLS},
    "A":  {c: "SPLIT" for c in DEALER_COLS},
}

# ---- Vereenvoudigde count-afwijkingen (true count drempels) ----
# key: (hand_beschrijving, dealer_up) -> (min_true_count, actie_bij_of_boven_drempel)
DEVIATIONS = {
    ("hard_16", "10"): (0, "STAND"),     # 16 vs 10: stand bij TC >= 0 ipv hit
    ("hard_15", "10"): (4, "STAND"),     # 15 vs 10: stand bij TC >= 4
    ("hard_12", "3"):  (2, "STAND"),
    ("hard_12", "2"):  (3, "STAND"),
    ("hard_13", "2"):  (-1, "HIT"),      # 13 vs 2: hit als TC < -1 (dus stand blijft bij >= -1)
    ("hard_10", "10"): (4, "DOUBLE"),
    ("hard_10", "A"):  (4, "DOUBLE"),
    ("hard_9", "2"):   (1, "DOUBLE"),
    ("insurance", "A"): (3, "TAKE_INSURANCE"),
}

ACTION_LABELS = {
    "HIT": "HIT (kaart nemen)",
    "STAND": "STAND (blijven staan)",
    "DOUBLE": "DOUBLE DOWN (of anders HIT)",
    "DOUBLE_STAND": "DOUBLE DOWN (of anders STAND)",
    "SPLIT": "SPLIT",
    "TAKE_INSURANCE": "VERZEKERING NEMEN",
}


def hand_total(ranks):
    """Retourneert (total, is_soft) voor een lijst kaartrangen.
    is_soft = True zolang er nog minstens 1 aas als 11 meetelt (zonder bust)."""
    total = 0
    aces_as_eleven = 0
    for r in ranks:
        total += RANK_VALUES[r]
        if r == "A":
            aces_as_eleven += 1
    while total > 21 and aces_as_eleven > 0:
        total -= 10
        aces_as_eleven -= 1
    return total, aces_as_eleven > 0


def get_recommendation(player_ranks, dealer_upcard, true_count=0.0, can_split=True, can_double=True):
    """
    player_ranks: lijst zoals ['A', '7'] of ['10', '6']
    dealer_upcard: '2'..'10','J','Q','K','A'
    true_count: huidige Hi-Lo true count
    Retourneert dict met action, label, en eventuele toelichting.
    """
    d = "10" if dealer_upcard in ("10", "J", "Q", "K") else dealer_upcard

    # Pair-check (alleen als beide kaarten dezelfde waarde hebben en split nog mag)
    if can_split and len(player_ranks) == 2 and player_ranks[0] == player_ranks[1]:
        rank = player_ranks[0]
        action = PAIR_TABLE[rank][d]
        return _finalize(action, f"pair_{rank}", d, true_count, can_double)

    total, is_soft = hand_total(player_ranks)

    if total > 21:
        return {"action": "BUST", "label": "Al voorbij 21 (bust)", "detail": ""}

    if is_soft and total <= 20 and len(player_ranks) >= 2 and total in SOFT_TABLE:
        action = SOFT_TABLE[total][d]
        return _finalize(action, f"soft_{total}", d, true_count, can_double)

    # Hard totals
    if total >= 17:
        return _finalize("STAND", f"hard_{total}", d, true_count, can_double)
    action = HARD_TABLE.get(total, {}).get(d, "HIT")
    return _finalize(action, f"hard_{total}", d, true_count, can_double)


def _finalize(action, hand_key, dealer_col, true_count, can_double):
    detail = ""
    dev = DEVIATIONS.get((hand_key, dealer_col))
    if dev is not None:
        threshold, dev_action = dev
        if true_count >= threshold:
            if action != dev_action:
                detail = f"Count-afwijking: basis zegt {action}, bij TC {true_count:+.1f} (>= {threshold:+.1f}) -> {dev_action}"
                action = dev_action

    if action in ("DOUBLE", "DOUBLE_STAND") and not can_double:
        action = "HIT" if action == "DOUBLE" else "STAND"
        detail += " (double niet beschikbaar, dus fallback)"

    return {
        "action": action,
        "label": ACTION_LABELS.get(action, action),
        "detail": detail.strip(),
    }

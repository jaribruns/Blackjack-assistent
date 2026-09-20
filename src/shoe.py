"""
Houdt de EXACTE samenstelling van het schoen bij (geen puntensysteem-benadering
zoals Hi-Lo, maar het werkelijke aantal resterende kaarten per rang), plus een
volledig geheugenlogboek van elke specifieke kaart die is gezien.

Twee lagen geheugen:
  1. exact_counts: per specifieke kaart (bv. "AS", "10H", "KD") hoeveel
     exemplaren er nog in het schoen zitten - dit is de brongegevens.
  2. group_counts: hetzelfde, opgeteld per waarde-groep (A,2..9,10) - dit is
     wat de kansrekenmachine (exact_engine.py) nodig heeft, want voor de
     wiskunde maakt de kleur niets uit, alleen de waarde.

seen_log bevat een chronologische lijst van elke gezien kaart (voor
transparantie/debug - "welke kaarten zijn er geweest").
"""

RANKS_13 = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["S", "H", "D", "C"]
GROUP_ORDER = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10"]  # 10 = 10/J/Q/K samen

RANK_VALUES = {
    "A": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "10": 10, "J": 10, "Q": 10, "K": 10, "A_LOW": 1,
}


def _to_group(rank13):
    """'J','Q','K','10' -> '10'; rest ongewijzigd."""
    return "10" if rank13 in ("10", "J", "Q", "K") else rank13


class ExactShoe:
    def __init__(self, num_decks=6):
        self.num_decks = num_decks
        self.reset()

    def reset(self):
        """Nieuw schoen: volle samenstelling, geheugen leeg."""
        self.exact_counts = {f"{r}{s}": self.num_decks for r in RANKS_13 for s in SUITS}
        self.seen_log = []          # chronologisch: elke geziene specifieke kaart, bv "AS"
        self._seen_instance_ids = set()   # voorkomt dubbel tellen van dezelfde schermpositie binnen 1 ronde

    # ---- registratie vanuit de kaartherkenning ----
    def register(self, instance_id, label13):
        """
        instance_id: unieke sleutel voor deze kaart-instantie op tafel dit moment
                     (bv. 'r3_player_0') - voorkomt dat dezelfde positie elk
                     frame opnieuw geteld wordt.
        label13: specifiek kaartlabel zoals de matcher teruggeeft, bv 'AS','10H','KD'.
        Retourneert True als de kaart nieuw geregistreerd is.
        """
        if instance_id in self._seen_instance_ids:
            return False
        if label13 not in self.exact_counts:
            return False
        self._seen_instance_ids.add(instance_id)
        if self.exact_counts[label13] > 0:
            self.exact_counts[label13] -= 1
        self.seen_log.append(label13)
        return True

    def new_round(self):
        """Roep aan bij het begin van een nieuwe hand (niet bij nieuw schoen!) -
        maakt schermposities weer 'vrij' zodat ze opnieuw geteld kunnen worden."""
        self._seen_instance_ids = set()

    # ---- afgeleide, geaggregeerde info voor de kansrekenmachine ----
    def group_counts(self):
        """dict: 'A'..'10' -> aantal resterend (10 = som van 10/J/Q/K)."""
        g = {r: 0 for r in GROUP_ORDER}
        for label, cnt in self.exact_counts.items():
            rank13 = label[:-1]
            g[_to_group(rank13)] += cnt
        return g

    def group_counts_tuple(self):
        g = self.group_counts()
        return tuple(g[r] for r in GROUP_ORDER)

    def total_remaining(self):
        return sum(self.exact_counts.values())

    def total_dealt(self):
        return self.num_decks * 52 - self.total_remaining()

    def penetration(self):
        """Fractie van het schoen dat al gespeeld is (0-1)."""
        total_start = self.num_decks * 52
        return self.total_dealt() / total_start if total_start else 0.0

    def summary_text(self):
        g = self.group_counts()
        parts = ", ".join(f"{r}:{g[r]}" for r in GROUP_ORDER)
        return f"Nog in schoen ({self.total_remaining()}/{self.num_decks*52}) -> {parts}"

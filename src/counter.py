"""
Hi-Lo kaarttelling.
Waarden: 2-6 = +1, 7-9 = 0, 10/J/Q/K/A = -1
True count = running count / resterende decks (geschat).
"""

HI_LO_VALUES = {
    "2": 1, "3": 1, "4": 1, "5": 1, "6": 1,
    "7": 0, "8": 0, "9": 0,
    "10": -1, "J": -1, "Q": -1, "K": -1, "A": -1,
}


class CardCounter:
    def __init__(self, num_decks=6):
        self.num_decks = num_decks
        self.running_count = 0
        self.cards_seen = 0
        self.seen_labels = set()  # unieke kaart-instanties (label + volgorde) om dubbeltellen te voorkomen

    def reset(self):
        self.running_count = 0
        self.cards_seen = 0
        self.seen_labels = set()

    def register_card(self, instance_id, rank):
        """
        instance_id: unieke sleutel voor DEZE kaart-instantie op tafel
                     (bv. "player_0", "dealer_1") zodat dezelfde kaart niet
                     twee keer geteld wordt zolang hij op het scherm staat.
        rank: '2'..'10','J','Q','K','A'
        """
        if instance_id in self.seen_labels:
            return False  # al geteld
        self.seen_labels.add(instance_id)
        self.running_count += HI_LO_VALUES.get(rank, 0)
        self.cards_seen += 1
        return True

    def decks_remaining(self):
        decks_used = self.cards_seen / 52.0
        remaining = max(self.num_decks - decks_used, 0.25)  # voorkom delen door (bijna) 0
        return remaining

    def true_count(self):
        return self.running_count / self.decks_remaining()

    def new_shoe(self):
        """Roep aan als je weet dat er geschud is (nieuw schoen)."""
        self.reset()

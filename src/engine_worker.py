"""
Draait de exacte kansberekening in een achtergrondthread, zodat het
overlay-venster soepel blijft ook als een zware hand (bv. A,A) enkele
seconden rekenwerk kost.

Resultaten worden gecached op (hand, upcard, schoen-samenstelling), zodat
dezelfde situatie niet telkens opnieuw berekend wordt terwijl het scherm
onveranderd blijft.
"""
import threading

from exact_engine import evaluate_hand


class EngineWorker:
    def __init__(self):
        self._lock = threading.Lock()
        self._cache = {}
        self._current_key = None
        self._result = None
        self._busy = False
        self._thread = None

    def request(self, player_ranks, dealer_up, counts_tuple, can_split=True, can_double=True):
        """
        Vraag een berekening aan. Retourneert direct (non-blocking).
        Als het antwoord al gecached is, staat het meteen klaar via latest().
        """
        key = (tuple(player_ranks), dealer_up, counts_tuple, can_split, can_double)

        with self._lock:
            if key in self._cache:
                self._current_key = key
                self._result = self._cache[key]
                return
            if self._busy and self._current_key == key:
                return  # al mee bezig
            self._current_key = key
            self._busy = True

        def run():
            try:
                res = evaluate_hand(list(key[0]), key[1], key[2],
                                     can_split=key[3], can_double=key[4])
            except Exception as e:
                res = {"error": str(e)}
            with self._lock:
                self._cache[key] = res
                if self._current_key == key:
                    self._result = res
                self._busy = False

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def latest(self):
        """(result_or_None, is_busy) voor de laatst gevraagde situatie."""
        with self._lock:
            key = self._current_key
            res = self._cache.get(key) if key else None
            return res, self._busy and res is None

    def clear_cache(self):
        with self._lock:
            self._cache = {}

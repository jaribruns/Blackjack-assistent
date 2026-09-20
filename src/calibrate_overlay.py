"""
Klein always-on-top venster dat tijdens calibrate.py live laat zien welke van
de 52 kaarten al gekalibreerd zijn. Draait in zijn eigen thread met eigen
Tk-mainloop, omdat calibrate.py zelf blokkeert op console-input() - via een
thread-safe queue geven we voortgang door.
"""
import tkinter as tk
import threading
import queue

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["S", "H", "D", "C"]
SUIT_COLOR = {"S": "#dddddd", "C": "#dddddd", "H": "#ff6666", "D": "#ff6666"}


class CalibrationOverlay:
    def __init__(self, done_labels=None, x=40, y=40):
        self._queue = queue.Queue()
        self._initial_done = set(done_labels or [])
        self._ready = threading.Event()
        self._x, self._y = x, y
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=3)

    def mark_done(self, label):
        """Thread-safe: mag vanuit calibrate.py's hoofdthread aangeroepen worden."""
        self._queue.put(("done", label))

    def close(self):
        self._queue.put(("close", None))

    # ---- interne Tk-thread ----
    def _run(self):
        self.root = tk.Tk()
        self.root.title("Kalibratie voortgang")
        self.root.attributes("-topmost", True)
        self.root.geometry(f"+{self._x}+{self._y}")
        self.root.configure(bg="#161616")

        tk.Label(self.root, text="Kalibratie voortgang", fg="white", bg="#161616",
                 font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=len(SUITS) + 1, pady=(10, 2), padx=10)

        self.progress_label = tk.Label(self.root, text="", fg="#66ccff", bg="#161616", font=("Segoe UI", 10))
        self.progress_label.grid(row=1, column=0, columnspan=len(SUITS) + 1, pady=(0, 10))

        self.cells = {}
        done = self._initial_done
        for r_idx, rank in enumerate(RANKS):
            tk.Label(self.root, text=rank, fg="#888888", bg="#161616",
                     font=("Consolas", 10, "bold"), width=3).grid(row=r_idx + 2, column=0, padx=(10, 2))
            for s_idx, suit in enumerate(SUITS):
                label = f"{rank}{suit}"
                is_done = label in done
                cell = tk.Label(self.root, text=suit, width=3, font=("Consolas", 10, "bold"),
                                 bg=("#2ecc71" if is_done else "#333333"),
                                 fg=("#111111" if is_done else SUIT_COLOR[suit]))
                cell.grid(row=r_idx + 2, column=s_idx + 1, padx=1, pady=1)
                self.cells[label] = (cell, is_done)

        tk.Label(self.root, text="groen = gekalibreerd   grijs = nog niet", fg="#777777", bg="#161616",
                 font=("Segoe UI", 8)).grid(row=len(RANKS) + 2, column=0, columnspan=len(SUITS) + 1, pady=(6, 10))

        self._update_progress_text()
        self.root.after(150, self._poll)
        self._ready.set()
        self.root.mainloop()

    def _update_progress_text(self):
        n_done = sum(1 for _, is_done in self.cells.values() if is_done)
        self.progress_label.config(text=f"{n_done}/52 kaarten gekalibreerd")

    def _poll(self):
        try:
            while True:
                kind, payload = self._queue.get_nowait()
                if kind == "close":
                    self.root.destroy()
                    return
                if kind == "done":
                    label = payload
                    if label in self.cells:
                        cell, _ = self.cells[label]
                        cell.config(bg="#2ecc71", fg="#111111")
                        self.cells[label] = (cell, True)
                        self._update_progress_text()
        except queue.Empty:
            pass
        try:
            self.root.after(150, self._poll)
        except tk.TclError:
            pass  # venster al gesloten

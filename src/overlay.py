"""
Klein, verplaatsbaar, always-on-top venster dat het advies toont, inclusief
de exacte EV per actie, de win/push/lose-kansen en de schoen-status.
"""
import tkinter as tk

ACTION_LABELS = {
    "HIT": "HIT",
    "STAND": "STAND",
    "DOUBLE": "DOUBLE DOWN",
    "SPLIT": "SPLIT",
    "BUST": "BUST",
    "WAIT": "Wachten op kaarten...",
}

COLORS = {
    "HIT": "#4da3ff",
    "STAND": "#4dff7a",
    "DOUBLE": "#ffcc4d",
    "SPLIT": "#ff884d",
    "BUST": "#ff4d4d",
    "WAIT": "#999999",
}


class Overlay:
    def __init__(self, x=40, y=40):
        self.root = tk.Tk()
        self.root.title("BJ Assistant")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.93)
        self.root.configure(bg="#161616")
        self.root.geometry(f"330x320+{x}+{y}")

        self._make_draggable(self.root)

        self.action_label = tk.Label(self.root, text="Wachten op kaarten...", fg="#999999", bg="#161616",
                                      font=("Segoe UI", 20, "bold"), wraplength=310)
        self.action_label.pack(pady=(16, 2))

        self.warning_label = tk.Label(self.root, text="", fg="#161616", bg="#ffb300",
                                       font=("Segoe UI", 9, "bold"), wraplength=310, justify="center")
        # wordt alleen ge-pack't wanneer er daadwerkelijk een waarschuwing is (zie _set_warning)

        self.hand_label = tk.Label(self.root, text="", fg="#dddddd", bg="#161616",
                                    font=("Segoe UI", 10))
        self.hand_label.pack()

        tk.Frame(self.root, bg="#333333", height=1).pack(fill="x", padx=14, pady=8)

        tk.Label(self.root, text="Verwachte waarde per actie", fg="#888888", bg="#161616",
                  font=("Segoe UI", 8)).pack()
        self.ev_label = tk.Label(self.root, text="-", fg="#eeeeee", bg="#161616",
                                  font=("Consolas", 10), justify="left")
        self.ev_label.pack(pady=(2, 6))

        self.prob_label = tk.Label(self.root, text="", fg="#66ccff", bg="#161616",
                                    font=("Segoe UI", 8), wraplength=310)
        self.prob_label.pack()

        tk.Frame(self.root, bg="#333333", height=1).pack(fill="x", padx=14, pady=8)

        self.shoe_label = tk.Label(self.root, text="", fg="#aaaaaa", bg="#161616",
                                    font=("Segoe UI", 8), wraplength=310, justify="center")
        self.shoe_label.pack()

        self.status_label = tk.Label(self.root, text="", fg="#ffaa44", bg="#161616",
                                      font=("Segoe UI", 8))
        self.status_label.pack(pady=(4, 0))

        btns = tk.Frame(self.root, bg="#161616")
        btns.pack(pady=(8, 0))
        self.new_shoe_callback = None
        tk.Button(btns, text="Nieuw schoen (geschud)", bg="#2a2a2a", fg="white", bd=0,
                   font=("Segoe UI", 8), command=self._on_new_shoe).pack(side="left", padx=4)

        tk.Button(self.root, text="x", command=self.root.destroy, bg="#2a2a2a", fg="white",
                   bd=0, font=("Segoe UI", 8), width=2).place(relx=1.0, y=0, anchor="ne")

    def _on_new_shoe(self):
        if self.new_shoe_callback:
            self.new_shoe_callback()

    def _make_draggable(self, widget):
        widget._drag = {"x": 0, "y": 0}

        def on_start(event):
            widget._drag["x"] = event.x
            widget._drag["y"] = event.y

        def on_move(event):
            x = widget.winfo_pointerx() - widget._drag["x"]
            y = widget.winfo_pointery() - widget._drag["y"]
            widget.geometry(f"+{x}+{y}")

        widget.bind("<ButtonPress-1>", on_start)
        widget.bind("<B1-Motion>", on_move)

    def _set_warning(self, warning):
        if warning:
            self.warning_label.config(text=warning)
            self.warning_label.pack(fill="x", padx=8, before=self.hand_label)
        else:
            self.warning_label.pack_forget()

    def show_waiting(self, shoe_text, status="", warning=None):
        self._set_warning(warning)
        self.action_label.config(text="Wachten op kaarten...", fg=COLORS["WAIT"])
        self.hand_label.config(text="")
        self.ev_label.config(text="-")
        self.prob_label.config(text="")
        self.shoe_label.config(text=shoe_text)
        self.status_label.config(text=status)

    def show_result(self, result, hand_text, shoe_text, status="", warning=None):
        self._set_warning(warning)
        if "error" in result:
            self.action_label.config(text="Fout", fg="#ff4d4d")
            self.status_label.config(text=result["error"][:60])
            return

        action = result["action"]
        action_text = ACTION_LABELS.get(action, action)
        if warning:
            action_text += "  (onzeker)"
        self.action_label.config(text=action_text,
                                  fg=COLORS.get(action, "#ffffff"))
        self.hand_label.config(text=hand_text)

        evs = {k: v for k, v in result["evs"].items() if v is not None}
        best = max(evs, key=evs.get) if evs else None
        ev_color = "#666666" if warning else "#eeeeee"
        lines = []
        for name in ["HIT", "STAND", "DOUBLE", "SPLIT"]:
            if name in evs:
                mark = "  <<" if name == best else ""
                lines.append(f"{name:<7}{evs[name]:+.4f}{mark}")
        self.ev_label.config(text="\n".join(lines) if lines else "-", fg=ev_color)

        self.prob_label.config(
            text=f"Bij STAND: win {result['win']*100:.1f}% | push {result['push']*100:.1f}% | verlies {result['lose']*100:.1f}%"
        )
        self.shoe_label.config(text=shoe_text)
        self.status_label.config(text=status)

    def tick(self):
        self.root.update_idletasks()
        self.root.update()

"""
Laat de gebruiker met de muis een rechthoek over het scherm slepen.
Retourneert [x, y, w, h] in absolute schermcoordinaten.
"""
import tkinter as tk


def select_region(prompt_text="Sleep een vak om de kaarten en laat los"):
    result = {}

    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.3)
    root.attributes("-topmost", True)
    root.configure(bg="black")
    root.config(cursor="cross")

    label = tk.Label(root, text=prompt_text, fg="white", bg="black", font=("Segoe UI", 16))
    label.place(relx=0.5, rely=0.05, anchor="n")

    canvas = tk.Canvas(root, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    start = {}
    rect_id = {"id": None}

    def on_press(event):
        start["x"] = event.x_root
        start["y"] = event.y_root
        if rect_id["id"]:
            canvas.delete(rect_id["id"])
        rect_id["id"] = canvas.create_rectangle(event.x, event.y, event.x, event.y,
                                                 outline="red", width=3)

    def on_drag(event):
        if rect_id["id"]:
            x0 = start["x"] - root.winfo_rootx()
            y0 = start["y"] - root.winfo_rooty()
            canvas.coords(rect_id["id"], x0, y0, event.x, event.y)

    def on_release(event):
        x0, y0 = start["x"], start["y"]
        x1, y1 = event.x_root, event.y_root
        x, y = min(x0, x1), min(y0, y1)
        w, h = abs(x1 - x0), abs(y1 - y0)
        result["region"] = [x, y, w, h]
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Escape>", lambda e: root.destroy())

    root.mainloop()
    return result.get("region")


if __name__ == "__main__":
    r = select_region()
    print("Geselecteerde regio:", r)

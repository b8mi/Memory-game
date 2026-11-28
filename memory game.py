import random
import time
import json
import tkinter as tk
from pathlib import Path

BG, PANEL, ACCENT = "#111a2b", "#253752", "#eb98dc"
SYMBOLS = ["★", "◆", "♥", "☀", "☂", "♫", "✿", "♠"]
SAVE_FILE = Path.home() / ".memory_flip_scores.json"
PREVIEW_SECONDS = 3


class MemoryApp:
    def __init__(self, root):
        self.root = root
        self.best_times = self.load_scores()
        self.mode = tk.StringVar(value="Classic")
        self.job = None

        root.title("Memory Flip")
        root.configure(bg=BG)
        root.resizable(False, False)

        tk.Label(root, text="MEMORY FLIP", bg=BG, fg=ACCENT, font=("Segoe UI", 23, "bold")).pack(pady=(12, 5))

        mode_frame = tk.Frame(root, bg=BG)
        mode_frame.pack(pady=5)

        tk.Label(mode_frame, text="Game Mode:", bg=BG, fg="white", font=("Segoe UI", 11)).pack(side="left", padx=5)

        mode_menu = tk.OptionMenu(mode_frame, self.mode, "Classic", "Preview", command=lambda _: self.reset())
        mode_menu.config(bg=PANEL, fg="white", activebackground=ACCENT, relief="flat", highlightthickness=0, width=10)
        mode_menu["menu"].config(bg=PANEL, fg="white")
        mode_menu.pack(side="left")

        self.info = tk.Label(root, bg=BG, fg="white", font=("Segoe UI", 12), width=36)
        self.info.pack()

        self.score_label = tk.Label(root, bg=BG, fg="#e9c575", font=("Segoe UI", 11, "bold"))
        self.score_label.pack(pady=5)

        frame = tk.Frame(root, bg=BG)
        frame.pack(padx=16, pady=12)

        self.buttons = []

        for i in range(16):
            button = tk.Button(frame, text="?", width=4, height=2, bg=PANEL, fg="white", font=("Segoe UI Symbol", 23, "bold"), relief="flat", command=lambda index=i: self.flip(index))
            button.grid(row=i // 4, column=i % 4, padx=5, pady=5)
            self.buttons.append(button)

        tk.Button(root, text="SHUFFLE / NEW GAME", command=self.reset, bg=ACCENT, relief="flat").pack(pady=(0, 14))

        self.reset()

    def load_scores(self):
        scores = {"Classic": None, "Preview": None}

        try:
            data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))

            if not isinstance(data, dict):
                return scores

            stored = data.get("best_times", {})

            if not isinstance(stored, dict):
                stored = {}

            for mode in scores:
                value = stored.get(mode)

                if mode == "Classic" and value is None:
                    value = data.get("best_time")

                try:
                    score = float(value)

                    if 0 < score < float("inf"):
                        scores[mode] = score

                except (ValueError, TypeError):
                    continue

        except (OSError, ValueError):
            pass

        return scores

    def save_scores(self):
        try:
            data = {
                "best_time": self.best_times["Classic"],
                "best_times": self.best_times
            }

            SAVE_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")
            return True

        except OSError:
            return False

    def update_score_label(self):
        best = self.best_times[self.mode.get()]

        if best is None:
            self.score_label.config(text="PERSONAL BEST: --")
        else:
            self.score_label.config(text=f"PERSONAL BEST: {best:.2f}s")

    def cancel_job(self):
        if self.job is not None:
            self.root.after_cancel(self.job)
            self.job = None

    def reset(self):
        self.cancel_job()

        self.deck = SYMBOLS * 2
        random.shuffle(self.deck)

        self.revealed = set()
        self.opened = []
        self.moves = 0
        self.locked = True
        self.finished = False
        self.start_time = None

        self.update_score_label()

        for button in self.buttons:
            button.config(text="?", bg=PANEL, fg="white")

        if self.mode.get() == "Preview":
            self.start_preview()
        else:
            self.start_game()

    def start_preview(self):
        self.locked = True

        for index, button in enumerate(self.buttons):
            button.config(text=self.deck[index], bg="#3f5375", fg=ACCENT)

        self.preview_countdown(PREVIEW_SECONDS)

    def preview_countdown(self, remaining):
        self.job = None

        if remaining <= 0:
            self.start_game()
            return

        self.info.config(text=f"Memorize the cards! {remaining}s")

        self.job = self.root.after(1000, lambda: self.preview_countdown(remaining - 1))

    def start_game(self):
        self.job = None

        for button in self.buttons:
            button.config(text="?", bg=PANEL, fg="white")

        self.locked = False
        self.start_time = time.monotonic()
        self.update_info()

    def update_info(self):
        pairs = len(self.revealed) // 2
        self.info.config(text=f"{pairs} pairs • {self.moves} moves")

    def flip(self, index):
        if self.finished or self.locked:
            return

        if index in self.revealed or index in self.opened:
            return

        self.buttons[index].config(text=self.deck[index], bg="#3f5375", fg=ACCENT)
        self.opened.append(index)

        if len(self.opened) != 2:
            return

        self.moves += 1

        first, second = self.opened

        if self.deck[first] == self.deck[second]:
            self.revealed.update(self.opened)

            for i in self.opened:
                self.buttons[i].config(bg="#2d876f", fg="white")

            self.opened.clear()

        else:
            self.locked = True
            self.job = self.root.after(800, self.hide)

        if len(self.revealed) == len(self.deck):
            self.finish_game()
        else:
            self.update_info()

    def finish_game(self):
        self.finished = True
        self.locked = True

        elapsed = time.monotonic() - self.start_time
        mode = self.mode.get()
        best = self.best_times[mode]

        if best is None or elapsed < best:
            self.best_times[mode] = elapsed
            saved = self.save_scores()

            self.info.config(text=f"NEW RECORD! {self.moves} moves • {elapsed:.2f}s")
            self.update_score_label()

            if not saved:
                self.score_label.config(text=f"PERSONAL BEST: {elapsed:.2f}s (Not saved)")

        else:
            self.info.config(text=f"YOU WON! {self.moves} moves • {elapsed:.2f}s")

    def hide(self):
        self.job = None

        for index in self.opened:
            self.buttons[index].config(text="?", bg=PANEL, fg="white")

        self.opened.clear()
        self.locked = False


if __name__ == "__main__":
    window = tk.Tk()
    MemoryApp(window)
    window.mainloop()

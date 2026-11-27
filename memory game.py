import random
import time
import json
import tkinter as tk
from pathlib import Path

BG, PANEL, ACCENT = "#111a2b", "#253752", "#eb98dc"
SYMBOLS = ["★", "◆", "♥", "☀", "☂", "♫", "✿", "♠"]
SAVE_FILE = Path.home() / ".memory_flip_scores.json"


class MemoryApp:
    def __init__(self, root):
        self.root = root
        self.best_time = self.load_score()

        root.title("Memory Flip")
        root.configure(bg=BG)
        root.resizable(False, False)

        tk.Label(root, text="MEMORY FLIP", bg=BG, fg=ACCENT, font=("Segoe UI", 23, "bold")).pack(pady=(12, 5))

        self.info = tk.Label(root, bg=BG, fg="white", font=("Segoe UI", 12))
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

        self.job = None
        self.reset()

    def load_score(self):
        try:
            data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
            score = float(data["best_time"])

            if 0 < score < float("inf"):
                return score

        except (OSError, ValueError, TypeError, KeyError):
            pass

        return None

    def save_score(self):
        try:
            data = {"best_time": self.best_time}
            SAVE_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")
            return True

        except OSError:
            return False

    def update_score_label(self):
        if self.best_time is None:
            self.score_label.config(text="PERSONAL BEST: --")
        else:
            self.score_label.config(text=f"PERSONAL BEST: {self.best_time:.2f}s")

    def reset(self):
        if self.job is not None:
            self.root.after_cancel(self.job)
            self.job = None

        self.deck = SYMBOLS * 2
        random.shuffle(self.deck)

        self.revealed = set()
        self.opened = []
        self.moves = 0
        self.locked = False
        self.finished = False
        self.start_time = time.monotonic()

        for button in self.buttons:
            button.config(text="?", bg=PANEL, fg="white")

        self.info.config(text="0 pairs  •  0 moves")
        self.update_score_label()

    def flip(self, index):
        if self.finished or self.locked or index in self.revealed or index in self.opened:
            return

        self.buttons[index].config(text=self.deck[index], bg="#3f5375", fg=ACCENT)
        self.opened.append(index)

        if len(self.opened) == 2:
            self.moves += 1
            first, second = self.opened

            if self.deck[first] == self.deck[second]:
                self.revealed.update(self.opened)

                for i in self.opened:
                    self.buttons[i].config(bg="#2d876f", fg="white")

                self.opened = []

            else:
                self.locked = True
                self.job = self.root.after(800, self.hide)

            if len(self.revealed) == len(self.deck):
                self.finish_game()

            else:
                self.info.config(text=f"{len(self.revealed) // 2} pairs • {self.moves} moves")

    def finish_game(self):
        self.finished = True
        self.locked = True

        elapsed = time.monotonic() - self.start_time

        if self.best_time is None or elapsed < self.best_time:
            self.best_time = elapsed
            saved = self.save_score()

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

        self.opened = []
        self.locked = False


if __name__ == "__main__":
    window = tk.Tk()
    MemoryApp(window)
    window.mainloop()

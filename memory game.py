
import random
import time
import json
import tkinter as tk
from pathlib import Path

BG, PANEL, ACCENT = "#111a2b", "#253752", "#eb98dc"
SYMBOLS = ["★", "◆", "♥", "☀", "☂", "♫", "✿", "♠"]
SAVE_FILE = Path.home() / ".memory_flip_score.json"


class MemoryApp:
    def __init__(self, root):
        self.root = root
        self.best = self.load_best()
        self.job = None

        root.title("Memory Flip")
        root.configure(bg=BG)
        root.resizable(False, False)

        tk.Label(root, text="MEMORY FLIP", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 23, "bold")).pack(pady=(12, 5))

        self.info = tk.Label(root, bg=BG, fg="white", font=("Segoe UI", 12))
        self.info.pack()

        self.best_label = tk.Label(root, bg=BG, fg=ACCENT, font=("Segoe UI", 11, "bold"))
        self.best_label.pack(pady=5)

        frame = tk.Frame(root, bg=BG)
        frame.pack(padx=16, pady=12)

        self.buttons = []

        for i in range(16):
            button = tk.Button(frame, text="?", width=4, height=2,
                               bg=PANEL, fg="white", relief="flat",
                               font=("Segoe UI Symbol", 23, "bold"),
                               command=lambda index=i: self.flip(index))
            button.grid(row=i // 4, column=i % 4, padx=5, pady=5)
            self.buttons.append(button)

        tk.Button(root, text="SHUFFLE / NEW GAME", command=self.reset,
                  bg=ACCENT, relief="flat").pack(pady=(0, 14))

        self.reset()

    def load_best(self):
        try:
            data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
            score = data.get("best_moves")

            if type(score) is int and score >= 8:
                return score

        except (OSError, ValueError, AttributeError):
            pass

        return None

    def save_best(self):
        try:
            temporary = SAVE_FILE.with_suffix(".tmp")
            temporary.write_text(json.dumps({"best_moves": self.best}), encoding="utf-8")
            temporary.replace(SAVE_FILE)
        except OSError as error:
            print(f"Could not save best score: {error}")

    def refresh_best(self):
        score = self.best if self.best is not None else "—"
        self.best_label.config(text=f"BEST SCORE: {score} moves")

    def check_record(self):
        if self.best is None or self.moves < self.best:
            self.best = self.moves
            self.save_best()
            self.refresh_best()
            return True

        return False

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
        self.start_time = time.monotonic()

        for button in self.buttons:
            button.config(text="?", bg=PANEL, fg="white")

        self.info.config(text="0 pairs  •  0 moves")
        self.refresh_best()

    def finish(self):
        elapsed = int(time.monotonic() - self.start_time)
        record = self.check_record()

        self.locked = True

        text = f"YOU WON! {self.moves} moves • {elapsed}s"

        if record:
            text += "\nNEW PERSONAL RECORD!"

        self.info.config(text=text)

    def flip(self, index):
        if self.locked or index in self.revealed or index in self.opened:
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

            self.opened = []
        else:
            self.locked = True
            self.job = self.root.after(800, self.hide)

        if len(self.revealed) == 16:
            self.finish()
        else:
            self.info.config(text=f"{len(self.revealed) // 2} pairs • {self.moves} moves")

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

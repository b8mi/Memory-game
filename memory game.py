import random
import time
import tkinter as tk

BG, PANEL, ACCENT = "#111a2b", "#253752", "#eb98dc"
SYMBOLS = ["★", "◆", "♥", "☀", "☂", "♫", "✿", "♠"]


class MemoryApp:
    def __init__(self, root):
        self.root = root
        root.title("Memory Flip")
        root.configure(bg=BG)
        root.resizable(False, False)
        tk.Label(root, text="MEMORY FLIP", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 23, "bold")).pack(pady=(12, 5))
        self.info = tk.Label(root, bg=BG, fg="white", font=("Segoe UI", 12))
        self.info.pack()
        frame = tk.Frame(root, bg=BG)
        frame.pack(padx=16, pady=12)
        self.buttons = []
        for i in range(16):
            button = tk.Button(frame, text="?", width=4, height=2, bg=PANEL, fg="white",
                               font=("Segoe UI Symbol", 23, "bold"), relief="flat",
                               command=lambda index=i: self.flip(index))
            button.grid(row=i // 4, column=i % 4, padx=5, pady=5)
            self.buttons.append(button)
        tk.Button(root, text="SHUFFLE / NEW GAME", command=self.reset,
                  bg=ACCENT, relief="flat").pack(pady=(0, 14))
        self.job = None
        self.reset()

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

    def flip(self, index):
        if self.locked or index in self.revealed or index in self.opened:
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
            if len(self.revealed) == 16:
                elapsed = int(time.monotonic() - self.start_time)
                self.info.config(text=f"YOU WON! {self.moves} moves • {elapsed}s")
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

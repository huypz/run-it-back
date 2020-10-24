import tkinter as tk
from main import *

from tkinter.filedialog import askopenfilename, asksaveasfilename


class GUI():
    def __init__(self): 
        self.root = tk.Tk()
        self.root.title("Run It Back")
        self.root.rowconfigure(0, minsize=800, weight=1)
        self.root.columnconfigure(1, minsize=800, weight=1)
        
        self.txt_edit = tk.Text(self.root)
        self.fr_buttons = tk.Frame(self.root, relief=tk.RAISED, bd=2)
        self.btn_open = tk.Button(self.fr_buttons, text="Open", command=lambda: open_file())
        self.btn_save = tk.Button(self.fr_buttons, text="Save As...", command=lambda: save_file(self))

        self.btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_save.grid(row=1, column=0, sticky="ew", padx=5)

        self.fr_buttons.grid(row=0, column=0, sticky="ns")
        self.txt_edit.grid(row=0, column=1, sticky="nsew")


def open_file():
    start()


def save_file(self):
    """Save the current file as a new file."""
    filepath = asksaveasfilename(
        defaultextension="txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    with open(filepath, "w") as output_file:
        text = self.txt_edit.get(1.0, tk.END)
        output_file.write(text)
    self.root.title(f"Simple Text Editor - {filepath}")
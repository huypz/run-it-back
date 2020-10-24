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
        self.btn_start = tk.Button(self.fr_buttons, text="Start", command=lambda: on_btn_start_click(self))
        self.btn_stop = tk.Button(self.fr_buttons, text="Stop", command=lambda: on_btn_stop_click(self))

        self.btn_start.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_stop.grid(row=1, column=0, sticky="ew", padx=5)

        self.fr_buttons.grid(row=0, column=0, sticky="ns")
        self.txt_edit.grid(row=0, column=1, sticky="nsew")


def on_btn_start_click(self):
    start()

def on_btn_stop_click(self):
    self.root.destroy()
    stop()



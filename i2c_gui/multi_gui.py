from __future__ import annotations

from .base_gui import Base_GUI

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging

import importlib.resources
from PIL import ImageTk, Image

class Multi_GUI(Base_GUI):
    def __init__(self, root: tk.Tk, logger: logging.Logger):
        super().__init__("Multi I2C GUI", root, logger)

    def _about_contents(self, element: tk.Tk, column: int, row: int):
        self._about_img = ImageTk.PhotoImage(Image.open(importlib.resources.open_binary("i2c_gui.static", "ETROC1.png")))
        self._about_img_label = tk.Label(element, image = self._about_img)
        self._about_img_label.grid(column=column, row=row, sticky='')
        element.rowconfigure(row, weight=1)

        self._about_info_label = tk.Label(element, justify=tk.LEFT, wraplength=450, text="The Multi I2C GUI was developed to read and write I2C registers from multiple connected I2C devices using a USB-ISS serial adapter. The code was developed and tested during a testbeam with an ETROC1 telescope (with ETROC2 Emulator?)")
        self._about_info_label.grid(column=column, row=row + 100, sticky='')
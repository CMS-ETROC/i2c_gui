from __future__ import annotations

from .base_gui import Base_GUI

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging

import importlib.resources
from PIL import ImageTk, Image

class ETROC1_GUI(Base_GUI):
    def __init__(self, root: tk.Tk, logger: logging.Logger):
        super().__init__("ETROC1 I2C GUI", root, logger)

        self._valid_i2c_address = False

    def _about_contents(self, element: tk.Tk, column: int, row: int):
        self._about_img = ImageTk.PhotoImage(Image.open(importlib.resources.open_binary("i2c_gui.static", "ETROC1.png")))
        self._about_img_label = tk.Label(element, image = self._about_img)
        self._about_img_label.grid(column=column, row=row, sticky='')
        element.rowconfigure(row, weight=1)

        self._about_info_label = tk.Label(element, justify=tk.LEFT, wraplength=450, text="The ETROC1 I2C GUI was developed to read and write I2C registers from a connected ETROC1 device using a USB-ISS serial adapter. The code was developed and tested using a FSxx board and during a testbeam with an ETROC1 telescope")
        self._about_info_label.grid(column=column, row=row + 100, sticky='')

    def _fill_notebook(self):
        from .chips import ETROC1_Chip
        self._chip = ETROC1_Chip(self._i2c_controller, i2c_controller=self._i2c_controller)

        self._full_chip_display(self._chip)

    def _connection_update(self, value):
        super()._connection_update(value)

    def extra_global_controls(self, element: tk.Tk, column: int, row: int):
        self._frame_extra_global = ttk.Frame(element)
        self._frame_extra_global.grid(column=column, row=row, sticky=(tk.W, tk.E))

        self._extra_i2c_label = ttk.Label(self._frame_extra_global, text="I2C Address:")
        self._extra_i2c_label.grid(column=100, row=100)

    def read_all(self):
        if self._valid_i2c_address:
            self.send_message("Reading full ETROC1 chip")
            self._chip.read_all()
        else:
            self.send_message("Unable to read full ETROC1 chip")
        pass

    def write_all(self):
        if self._valid_i2c_address:
            self.send_message("Writing full ETROC1 chip")
            self._chip.write_all()
        else:
            self.send_message("Unable to write full ETROC1 chip")
        pass
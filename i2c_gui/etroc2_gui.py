from __future__ import annotations

from .base_gui import Base_GUI

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging

import importlib.resources
from PIL import ImageTk, Image

class ETROC2_GUI(Base_GUI):
    _red_col = '#c00000'
    _green_col = '#00c000'

    def __init__(self, root: tk.Tk, logger: logging.Logger):
        super().__init__("ETROC2 I2C GUI", root, logger)

        self._valid_i2c_address = False

    def _about_contents(self, element: tk.Tk, column: int, row: int):
        self._about_img = ImageTk.PhotoImage(Image.open(importlib.resources.open_binary("i2c_gui.static", "ETROC2_Emulator.png")))
        self._about_img_label = tk.Label(element, image = self._about_img)
        self._about_img_label.grid(column=column, row=row, sticky='')
        element.rowconfigure(row, weight=1)

        self._about_info_label = tk.Label(element, justify=tk.LEFT, wraplength=450, text="The ETROC2 I2C GUI was developed to read and write I2C registers from a connected ETROC2 device using a USB-ISS serial adapter. The code was developed and tested using the ETROC2 Emulator")
        self._about_info_label.grid(column=column, row=row + 100, sticky='')

    def _fill_notebook(self):
        from .chips import ETROC2_Chip
        self._chip = ETROC2_Chip(parent=self, i2c_controller=self._i2c_controller)

        self._full_chip_display(self._chip)

    def _connection_update(self, value):
        super()._connection_update(value)
        if value:
            if hasattr(self, "_i2c_address_entry"):
                self._i2c_address_entry.config(state='normal')
                self._ws_i2c_address_entry.config(state='normal')
                self.check_i2c_address()
                self.check_ws_i2c_address()
        else:
            if hasattr(self, "_i2c_address_entry"):
                self._i2c_address_entry.config(state='disabled')
                self._ws_i2c_address_entry.config(state='disabled')
                self._chip_i2c_status_var.set("")
                self._valid_i2c_address = False
                self._chip_ws_i2c_status_var.set("")
                self._valid_ws_i2c_address = False

    def extra_global_controls(self, element: tk.Tk, column: int, row: int):
        self._frame_extra_global = ttk.Frame(element)
        self._frame_extra_global.grid(column=column, row=row, sticky=(tk.W, tk.E))

        self._extra_i2c_label = ttk.Label(self._frame_extra_global, text="I2C Address:")
        self._extra_i2c_label.grid(column=100, row=100)

        self._chip_i2c_address_var = tk.StringVar()
        self._chip_i2c_address_var.set("0x72")
        self._i2c_address_entry = ttk.Entry(self._frame_extra_global, textvariable=self._chip_i2c_address_var, width=5, state='disabled')
        self._i2c_address_entry.grid(column=101, row=100, sticky=(tk.W, tk.E))

        from .functions import validate_i2c_address
        self._i2c_validate_cmd = (self._frame.register(validate_i2c_address), '%P')
        self._i2c_invalid_cmd  = (self._frame.register(self.invalid_i2c_address), '%P')
        self._i2c_address_entry.config(validate='key', validatecommand=self._i2c_validate_cmd, invalidcommand=self._i2c_invalid_cmd)
        self._chip_i2c_address_var.trace('w', self.check_i2c_address)

        self._chip_i2c_status_var = tk.StringVar()
        self._chip_i2c_status_var.set("")
        self._i2c_status_label = ttk.Label(self._frame_extra_global, textvariable=self._chip_i2c_status_var)
        self._i2c_status_label.grid(column=200, row=100, padx=(15,25))

        self._extra_ws_i2c_label = ttk.Label(self._frame_extra_global, text="Waveform Sampler I2C Address:")
        self._extra_ws_i2c_label.grid(column=300, row=100)

        self._chip_ws_i2c_address_var = tk.StringVar()
        self._chip_ws_i2c_address_var.set("0x70")
        self._ws_i2c_address_entry = ttk.Entry(self._frame_extra_global, textvariable=self._chip_ws_i2c_address_var, width=5, state='disabled')
        self._ws_i2c_address_entry.grid(column=301, row=100, sticky=(tk.W, tk.E))

        self._ws_i2c_address_entry.config(validate='key', validatecommand=self._i2c_validate_cmd, invalidcommand=self._i2c_invalid_cmd)
        self._chip_ws_i2c_address_var.trace('w', self.check_ws_i2c_address)

        self._chip_ws_i2c_status_var = tk.StringVar()
        self._chip_ws_i2c_status_var.set("")
        self._ws_i2c_status_label = ttk.Label(self._frame_extra_global, textvariable=self._chip_ws_i2c_status_var)
        self._ws_i2c_status_label.grid(column=400, row=100, padx=(15,0))

    def check_ws_i2c_address(self, var=None, index=None, mode=None):
        address = self._chip_ws_i2c_address_var.get()
        if address == "0x" or address == "":
            address = "0x0"
        else:
            address = hex(int(address, 0))

        if self._i2c_controller.check_i2c_device(address):
            self._ws_i2c_status_label.config(foreground=self._green_col)
            self._chip_ws_i2c_status_var.set("(Available)")
            self._chip.config_waveform_sampler_i2c_address(int(address, 16))
            self._valid_ws_i2c_address = True
        else:
            self._ws_i2c_status_label.config(foreground=self._red_col)
            self._chip_ws_i2c_status_var.set("(Not available)")
            self._chip.config_waveform_sampler_i2c_address(None)
            self._valid_ws_i2c_address = False

    def check_i2c_address(self, var=None, index=None, mode=None):
        address = self._chip_i2c_address_var.get()
        if address == "0x" or address == "":
            address = "0x0"
        else:
            address = hex(int(address, 0))

        if self._i2c_controller.check_i2c_device(address):
            self._i2c_status_label.config(foreground=self._green_col)
            self._chip_i2c_status_var.set("(Available)")
            self._chip.config_i2c_address(int(address, 16))
            self._valid_i2c_address = True
        else:
            self._i2c_status_label.config(foreground=self._red_col)
            self._chip_i2c_status_var.set("(Not available)")
            self._chip.config_i2c_address(None)
            self._valid_i2c_address = False

    def read_all(self):
        if self._valid_i2c_address:
            self.send_message("Reading full ETROC2 chip")
            self._chip.read_all()
        else:
            self.send_message("Unable to read full ETROC2 chip")
        pass

    def write_all(self):
        if self._valid_i2c_address:
            self.send_message("Writing full ETROC2 chip")
            if not self._chip.write_all():
                self.send_message("Failed writing the full chip, one or more address spaces were not written to.", "Error")
        else:
            self.send_message("Unable to write full ETROC2 chip", "Error")
        pass
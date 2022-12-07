from __future__ import annotations

from .gui_helper import GUI_Helper
from .base_gui import Base_GUI
from .logging import Logging_Helper
from .connection_controller import Connection_Controller

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging

class Global_Controls(GUI_Helper):
    _parent: Base_GUI
    def __init__(self, parent: Base_GUI):
        super().__init__(parent, None, parent._logger)

        self._logging_helper = parent._logging_helper
        self._i2c_controller = parent._i2c_controller

    def prepare_display(self, element: tk.Tk, col, row):
        self._frame = ttk.Frame(element)
        self._frame.grid(column=col, row=row, sticky=(tk.N, tk.W, tk.E, tk.S))

        self._read_button = ttk.Button(self._frame, text="Read All", command=self._parent.read_all, state='disabled')
        self._read_button.grid(column=100, row=100, sticky=(tk.W, tk.E), padx=(0,10))

        self._write_button = ttk.Button(self._frame, text="Write All", command=self._parent.write_all, state='disabled')
        self._write_button.grid(column=200, row=100, sticky=(tk.W, tk.E), padx=(0,30))

        self._frame.columnconfigure(300, weight=1)
        self._parent.extra_global_controls(self._frame, 300, 100)

        self._logging_button = ttk.Button(self._frame, text="Logging", command=self._logging_helper.display_logging)
        self._logging_button.grid(column=2000, row=100, sticky=(tk.W, tk.E), padx=(10,0))

        self._i2c_controller.register_connection_callback(self._connection_update)

    def _connection_update(self, value):
        if value:
            if hasattr(self, "_read_button"):
                self._read_button.config(state="normal")
                self._write_button.config(state="normal")
        else:
            if hasattr(self, "_read_button"):
                self._read_button.config(state="disabled")
                self._write_button.config(state="disabled")

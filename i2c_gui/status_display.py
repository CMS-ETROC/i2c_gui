from __future__ import annotations

from .gui_helper import GUI_Helper
from .base_gui import Base_GUI

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging

class Status_Display(GUI_Helper):
    def __init__(self, parent: Base_GUI, max_len: int = 100):
        super().__init__(parent, None, parent._logger)

        self._connection_status_var = tk.StringVar()
        self._connection_status_var.set("Not Connected")

        self._local_status_var = tk.StringVar()
        self._local_status_var.set("Unknown")

        self._message_var = tk.StringVar()

        self._max_len = max_len

    @property
    def connection_status(self):
        return self._connection_status_var.get()

    @connection_status.setter
    def connection_status(self, value):
        if value not in ["Not Connected", "Connected", "Error"]:
            raise ValueError("Invalid connection status was attempted to be set: \"{}\"".format(value))
        self._connection_status_var.set(value)

    @property
    def local_status(self):
        return self._local_status_var.get()

    @local_status.setter
    def local_status(self, value):
        if value not in ["Unknown", "Modified", "Unmodified", "Error"]:
            raise ValueError("Invalid local status was attempted to be set: \"{}\"".format(value))
        self._local_status_var.set(value)

    @property
    def last_message(self):
        return self._message_var.get()

    def prepare_display(self, element: tk.Tk, col, row):
        self._frame = ttk.Frame(element)
        self._frame.grid(column=col, row=row, sticky=(tk.N, tk.W, tk.E, tk.S))

        self._connection_status_title = ttk.Label(self._frame, text="I2C Bus:")
        self._connection_status_title.grid(column=100, row=100, sticky=(tk.W, tk.E))
        self._connection_status_label = ttk.Label(self._frame, textvariable=self._connection_status_var)
        self._connection_status_label.grid(column=101, row=100, sticky=(tk.W, tk.E), padx=(0,15))

        self._local_status_title = ttk.Label(self._frame, text="Status:")
        self._local_status_title.grid(column=200, row=100, sticky=(tk.W, tk.E))
        self._local_status_label = ttk.Label(self._frame, textvariable=self._local_status_var)
        self._local_status_label.grid(column=201, row=100, sticky=(tk.W, tk.E), padx=(0,15))

        self._message_label = ttk.Label(self._frame, textvariable=self._message_var)
        self._message_label.grid(column=300, row=100, sticky=tk.E)
        self._frame.columnconfigure(300, weight=1)

    def send_message(self, message: str, status:str = "Message"):
        if status == "Error":
            self._logger.warn("Error Message: {}".format(message))
        else:
            self._logger.info("Message: {}".format(message))

        if len(message) > self._max_len:
            message = message[:self._max_len - 3] + " ⋯"  # "…"
        self._message_var.set(message)
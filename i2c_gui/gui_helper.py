from __future__ import annotations

import tkinter as tk
import logging

class GUI_Helper:
    def __init__(self, parent: 'GUI_Helper', frame: tk.Tk, logger: logging.Logger):
        self._parent = parent
        self._frame = frame
        self._logger = logger

    @property
    def is_connected(self):
        if self._parent is None:
            raise RuntimeError("You can only find if the app is connected from a stack of classes which handle the connection correctly")
        return self._parent.is_connected

    def send_message(self, message:str):
        if self._parent is None:
            raise RuntimeError("You can only call send_message from a stack of classes which route the message correctly")
        self._parent.send_message(message=message)
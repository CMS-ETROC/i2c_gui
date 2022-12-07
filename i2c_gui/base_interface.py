from __future__ import annotations

from .gui_helper import GUI_Helper

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging

class Base_Interface(GUI_Helper):
    _parent: GUI_Helper
    def __init__(self, parent: GUI_Helper, enabled: bool, reverse_polarity: bool = False):
        super().__init__(parent, None, parent._logger)

        self._enabled = enabled

        self._reverse_polarity = reverse_polarity

    @property
    def reverse_polarity(self):
        return self._reverse_polarity

    @property
    def enabled(self):
        return self._enabled

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False
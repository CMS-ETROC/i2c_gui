from __future__ import annotations

from .gui_helper import GUI_Helper

import tkinter as tk
import logging

class ScriptHelper(GUI_Helper):
    def __init__(self, logger: logging.Logger):
        # self._root = tk.Tk()  # Needed for some of the variables to work correctly
        super().__init__("Script Helper", tk.Tk(), logger)

    def _local_status_update(self, value):
        print("Updating local status to: {}".format(value))

    def send_message(self, message:str):
        print("GUI Message: {}".format(message))
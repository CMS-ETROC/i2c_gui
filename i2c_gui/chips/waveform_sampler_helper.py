#############################################################################
# zlib License
#
# (C) 2023 Cristóvão Beirão da Cruz e Silva <cbeiraod@cern.ch>
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#############################################################################

from __future__ import annotations

from ..gui_helper import GUI_Helper
from .base_chip import Base_Chip

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging
import time

class Waveform_Sampler_Helper(GUI_Helper):
    _orange_col = '#f0c010'
    _green_col = '#08ef10'
    _black_col = '#000000'

    _parent: Base_Chip
    def __init__(self, parent: Base_Chip):
        super().__init__(parent, None, parent._logger)
        self._is_connected = False

    def _connection_update(self, value):
        self._is_connected = value
        if value:
            if hasattr(self, "_status_display"):
                self._status_display.connection_status = "Connected"
        else:
            if hasattr(self, "_status_display"):
                self._status_display.connection_status = "Not Connected"
                self._status_display.local_status = "Unknown"

    def display_window(self):
        if hasattr(self, "_window"):
            self._logger.info("Waveform Sampler window already open")
            self._window.focus()
            return

        self._window = tk.Toplevel(self._parent._parent._root)
        self._window.title(self._parent._parent._title + " - Waveform Sampler Monitor")
        self._window.protocol('WM_DELETE_WINDOW', self.close_window)
        self._window.columnconfigure(100, weight=1)
        self._window.rowconfigure(100, weight=1)

    def close_window(self):
        if not hasattr(self, "_window"):
            self._logger.info("Waveform Sampler window does not exist")
            return

        self.is_logging = False

        self._window.destroy()
        del self._window

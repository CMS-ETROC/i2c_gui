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

    _control_decoded_assoc = {
        "Mode": ("sel1", ["Bypass", "VGA"]),
        "Power Mode": ("sel2", ["Single Shot", "Continuous"]),
        "Write Enable": ("sel3", ["on Chip", "off Chip"]),
    }
    def __init__(self, parent: Base_Chip):
        super().__init__(parent, None, parent._logger)
        self._is_connected = False

        self._decoded_display_vars = {}
        self._control_vars = {}
        self._control_var_updating = {}

        for control in self._control_decoded_assoc:
            var, values = self._control_decoded_assoc[control]
            self._decoded_display_vars[control] = self._parent.get_decoded_display_var("Waveform Sampler", "Config", var)
            self._control_vars[control] = tk.StringVar()
            self._control_var_updating[control] = None
            self._update_display_from_config(control)

            self._decoded_display_vars[control].trace_add('write', lambda var, index, mode, control_var=control : self._update_display_from_config(control_var, var, index, mode))
            self._control_vars[control].trace_add('write', lambda var, index, mode, control_var=control : self._update_config_from_display(control_var, var, index, mode))

    def _update_config_from_display(self, control_var, var=None, index=None, mode=None):
        if self._control_var_updating[control_var] is not None and self._control_var_updating[control_var] == "from config":
            return
        control_values = self._control_decoded_assoc[control_var][1]

        self._control_var_updating[control_var] = "from display"

        selected_value = self._control_vars[control_var].get()
        idx = control_values.index(selected_value)
        self._decoded_display_vars[control_var].set(idx)

        self._control_var_updating[control_var] = None

    def _update_display_from_config(self, control_var, var=None, index=None, mode=None):
        if self._control_var_updating[control_var] is not None and self._control_var_updating[control_var] == "from display":
            return
        control_values = self._control_decoded_assoc[control_var][1]

        self._control_var_updating[control_var] = "from config"

        idx = int(self._decoded_display_vars[control_var].get())
        selected_value = control_values[idx]
        self._control_vars[control_var].set(selected_value)

        self._control_var_updating[control_var] = None

    def _connection_update(self, value):
        self._is_connected = value
        if value:
            if hasattr(self, "_status_display"):
                self._status_display.connection_status = "Connected"
            if hasattr(self, "_control_dropdowns"):
                for control_var in self._control_dropdowns:
                    self._control_dropdowns[control_var].config(state="normal")
        else:
            if hasattr(self, "_status_display"):
                self._status_display.connection_status = "Not Connected"
                self._status_display.local_status = "Unknown"
            if hasattr(self, "_control_dropdowns"):
                for control_var in self._control_dropdowns:
                    self._control_dropdowns[control_var].config(state="disabled")

    def display_window(self):
        if hasattr(self, "_window"):
            self._logger.info("Waveform Sampler window already open")
            self._window.focus()
            return

        state = "disabled"
        if self._is_connected:
            state = "normal"

        self._window = tk.Toplevel(self._parent._parent._root)
        self._window.title(self._parent._parent._title + " - Waveform Sampler Monitor")
        self._window.protocol('WM_DELETE_WINDOW', self.close_window)
        self._window.columnconfigure(200, weight=1)
        self._window.rowconfigure(100, weight=1)

        self._control_frame = ttk.LabelFrame(self._window, text="Control")
        self._control_frame.grid(column=100, row=100)

        self._control_labels = {}
        self._control_dropdowns = {}
        current_row = 90
        for control_var in self._control_decoded_assoc:
            current_row += 10
            values = self._control_decoded_assoc[control_var][1]
            selected_val = values[int(self._decoded_display_vars[control_var].get())]

            self._control_labels[control_var] = ttk.Label(self._control_frame, text=control_var+":")
            self._control_labels[control_var].grid(column=100, row=current_row)

            self._control_dropdowns[control_var] = ttk.OptionMenu(self._control_frame, self._control_vars[control_var], selected_val, *values)
            self._control_dropdowns[control_var].grid(column=110, row=current_row)
            self._control_dropdowns[control_var].config(state=state)

    def close_window(self):
        if not hasattr(self, "_window"):
            self._logger.info("Waveform Sampler window does not exist")
            return

        self.is_logging = False

        self._window.destroy()
        del self._window

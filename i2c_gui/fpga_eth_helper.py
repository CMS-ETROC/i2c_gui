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

from .i2c_connection_helper import I2C_Connection_Helper
from .base_gui import Base_GUI

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging
import time

import socket
from .functions import validate_hostname

class FPGA_ETH_Helper(I2C_Connection_Helper):
    def __init__(self, parent: Base_GUI, max_seq_byte: int = 8, swap_endian: bool = False):
        super().__init__(parent, max_seq_byte, swap_endian)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._hostname_var = tk.StringVar(value='192.168.2.3') # FPGA IP address

        self._port_var = tk.IntVar(value=1024) # port number

    @property
    def hostname(self):
        return self._hostname_var.get()

    @hostname.setter
    def hostname(self, value: str):
        self._hostname_var.set(value)

    @property
    def port(self):
        return self._port_var.get()

    @port.setter
    def port(self, value: int):
        self._port_var.set(value)

    def _check_i2c_device(self, address: int):
        return False  # TODO: implement this for the FPGA

    def _write_i2c_device_memory(self, address: int, memory_address: int, data: list[int], register_bits: int = 16):
        return  # TODO: implement this for the FPGA

    def _read_i2c_device_memory(self, address: int, memory_address: int, byte_count: int, register_bits: int = 16) -> list[int]:
        return []  # TODO: implement this for the FPGA

    def display_in_frame(self, frame: ttk.Frame):
        if hasattr(self, '_frame') and self._frame is not None:
            tmp = self._frame.children.copy()
            for widget in tmp:
                tmp[widget].destroy()

        self._frame = frame

        self._hostname_label = ttk.Label(self._frame, text="Hostname:")
        self._hostname_label.grid(column=0, row=0, sticky=(tk.W, tk.E))

        self._hostname_entry = ttk.Entry(self._frame, textvariable=self._hostname_var, width=10)
        self._hostname_entry.grid(column=1, row=0, sticky=(tk.W, tk.E), padx=(0,30))

        self._frame.columnconfigure(2, weight=1)

        self._port_label = ttk.Label(self._frame, text="Port:")
        self._port_label.grid(column=3, row=0, sticky=(tk.W, tk.E))

        self._port_entry = ttk.Entry(self._frame, textvariable=self._port_var, width=7)
        self._port_entry.grid(column=4, row=0, sticky=(tk.W, tk.E), padx=(0,30))

        self._frame.columnconfigure(5, weight=1)

    def validate_connection_params(self):
        if not validate_hostname(self.hostname):
            self.send_message("Please enter a valid hostname", "Error")
            return False

        if self.port == "":
            self.send_message("Please enter a valid port", "Error")
            return False

        try:
            socket.gethostbyname(self.hostname)
        except socket.gaierror:
            self.send_message("Unable to find the host: {}".format(self.hostname))
            return False

        return True

    def connect(self, no_connect: bool = False):
        self._no_connect = no_connect
        if not no_connect:  # For emulated connection
            try:
                self._socket.connect((self.hostname, self.port))
            except socket.error:
                self.send_message("Unable to connect to {} on port {}".format(self.hostname, self.port))
                return False

        if hasattr(self, "_hostname_entry"):
            self._hostname_entry.config(state="disabled")
        if hasattr(self, "_port_entry"):
            self._port_entry.config(state="disabled")
        self.send_message("Connected to {} on port {}".format(self.hostname, self.port))
        return True

    def disconnect(self):
        if not self._no_connect:
            self._socket.close()

        if hasattr(self, "_hostname_entry"):
            self._hostname_entry.config(state="normal")
        if hasattr(self, "_port_entry"):
            self._port_entry.config(state="normal")
        self.send_message("Disconnected from {} on port {}".format(self.hostname, self.port))
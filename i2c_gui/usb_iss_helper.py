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

from .gui_helper import GUI_Helper
from .base_gui import Base_GUI

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging
import time

from usb_iss import UsbIss

class USB_ISS_Helper(GUI_Helper):
    _parent: Base_GUI
    def __init__(self, parent: Base_GUI, max_seq_byte = 8, swap_endian = True):
        super().__init__(parent, None, parent._logger)
        self._max_seq_byte = max_seq_byte
        self._swap_endian = swap_endian

        self._iss = UsbIss()

        self._port_var = tk.StringVar()
        self._port_var.set("COM3")

        self._clk_var = tk.IntVar(self._frame)
        self._clk_var.set(100)

        self._no_connect = None

    @property
    def port(self):
        return self._port_var.get()

    @port.setter
    def port(self, value):
        self._port_var.set(value)

    @property
    def clk(self):
        return self._clk_var.get()

    @clk.setter
    def clk(self, value):
        self._clk_var.set(value)

    def check_i2c_device(self, address: int):
        self._parent.send_i2c_logging_message("Trying to find the I2C device with address 0x{:02x}".format(address))

        if not self.is_connected or self._no_connect:
            self._parent.send_i2c_logging_message("   The USB-ISS module is not connected or you are using software emulated mode.\n")
            return False

        if not self._iss.i2c.test(address):
            self._parent.send_i2c_logging_message("   The I2C device can not be found.\n")
            return False
        self._parent.send_i2c_logging_message("   The I2C device was found.\n")
        return True

    def display_in_frame(self, frame: ttk.Frame):
        if hasattr(self, '_frame') and self._frame is not None:
            tmp = self._frame.children.copy()
            for widget in tmp:
                tmp[widget].destroy()

        self._frame = frame
        self._port_label = ttk.Label(self._frame, text="Port:")
        self._port_label.grid(column=0, row=0, sticky=(tk.W, tk.E))

        self._port_entry = ttk.Entry(self._frame, textvariable=self._port_var, width=10)
        self._port_entry.grid(column=1, row=0, sticky=(tk.W, tk.E), padx=(0,30))

        self._frame.columnconfigure(2, weight=1)

        self._clk_values = [ # These are the frequencies supported by the USB-ISS module (in kHz), two of them are supported in both hardware and software
            20,   # Supported in software bit bashed
            50,   # Supported in software bit bashed
            100,  # Supported in software bit bashed and hardware
            400,  # Supported in software bit bashed and hardware
            1000  # Supported in hardware
        ]

        self._clk_label = ttk.Label(self._frame, text="Clock Frequency:")
        self._clk_label.grid(column=3, row=0, sticky=(tk.W, tk.E))

        self._clk_option = ttk.OptionMenu(self._frame, self._clk_var, self._clk_values[2], *self._clk_values)
        self._clk_option.grid(column=4, row=0, sticky=(tk.W, tk.E))

        self._clk_units_label = ttk.Label(self._frame, text="kHz")
        self._clk_units_label.grid(column=5, row=0, sticky=(tk.W, tk.E), padx=(0,30))

        self._frame.columnconfigure(6, weight=1)

    def validate_connection_params(self):
        if self.port == "":
            self.send_message("Please enter a valid port")
            return False

        return True

    def connect(self, no_connect: bool = False):
        # Give preference to hardware I2C for clk which support both hardware and bit bashed
        use_hardware = True
        if self._clk_var.get() < 100:
            use_hardware = False

        self._no_connect = no_connect
        if not no_connect:  # For emulated connection
            try:
                self._iss.open(self.port)
                self._iss.setup_i2c(clock_khz=self.clk, use_i2c_hardware=use_hardware)
            except:
                self.send_message("Unable to connect to I2C bus on port {} using I2C at {} kHz".format(self.port, self.clk))
                return False

        if hasattr(self, "_port_entry"):
            self._port_entry.config(state="disabled")
        if hasattr(self, "_clk_option"):
            self._clk_option.config(state="disabled")
        self.send_message("Connected to I2C bus with a bitrate of {} kHz through port {}".format(self.clk, self.port))
        return True

    def disconnect(self):
        self._iss.close()

        if hasattr(self, "_port_entry"):
            self._port_entry.config(state="normal")
        if hasattr(self, "_clk_option"):
            self._clk_option.config(state="normal")
        self.send_message("Disconnected from I2C bus with a bitrate of {} kHz through port {}".format(self.clk, self.port))

    def swap_endian_16bit(self, address: int):
        from .functions import hex_0fill
        tmp = hex_0fill(address, 16)
        low_byte = tmp[-2:]
        high_byte = tmp[-4:-2]
        return int("0x" + low_byte + high_byte, 16)

    def read_device_memory(self, device_address: int, memory_address: int, byte_count: int = 1):
        if not self.is_connected:
            raise RuntimeError("You must first connect to a device before trying to read registers from it")

        from .functions import validate_i2c_address
        if not validate_i2c_address(hex(device_address)):
            raise RuntimeError("Invalid I2C address received: {}".format(hex(device_address)))

        if byte_count == 1:
            self._parent.send_i2c_logging_message("Trying to read the register 0x{:04x} of the I2C device with address 0x{:02x}:".format(memory_address, device_address))
        else:
            self._parent.send_i2c_logging_message("Trying to read a register block with size {} starting at register 0x{:04x} of the I2C device with address 0x{:02x}:".format(byte_count, memory_address, device_address))

        data = []
        if self._no_connect:
            if byte_count == 1:
                data = [42]
            else:
                data = [i for i in range(byte_count)]
            self._parent.send_i2c_logging_message("   Software emulation (no connect) is enabled, so returning dummy values.\n   {}\n".format(repr(data)))

        elif self._max_seq_byte is None:
            if self._swap_endian:
                memory_address = self.swap_endian_16bit(memory_address)
            data = self._iss.i2c.read_ad2(device_address, memory_address, byte_count)
            self._parent.send_i2c_logging_message("   {}\n".format(repr(data)))
        else:
            from math import ceil
            from time import sleep
            data = []
            seq_calls = ceil(byte_count/self._max_seq_byte)
            self._parent.send_i2c_logging_message("   Breaking the read into {} individual reads of {} bytes:".format(seq_calls, self._max_seq_byte))

            lastUpdateTime = time.time_ns()
            for i in range(seq_calls):
                thisTime = time.time_ns()
                if thisTime - lastUpdateTime > 0.2 * 10**9:
                    self.display_progress("Reading:", i*100./seq_calls)
                    self._frame.update_idletasks()

                this_block_address = memory_address + i*self._max_seq_byte
                bytes_to_read = min(self._max_seq_byte, byte_count - i*self._max_seq_byte)
                self._parent.send_i2c_logging_message("      Read operation {}: reading {} bytes starting from 0x{:04x}".format(i, bytes_to_read, this_block_address))

                if self._swap_endian:
                    this_block_address = self.swap_endian_16bit(this_block_address)
                this_data = self._iss.i2c.read_ad2(device_address, this_block_address, bytes_to_read)
                self._parent.send_i2c_logging_message("         {}".format(repr(this_data)))

                data += this_data
                sleep(0.00001)

            self.clear_progress()
            self._parent.send_i2c_logging_message("   Full data:\n      {}\n".format(repr(data)))
        return data

    def write_device_memory(self, device_address: int, memory_address: int, data: list[int]):
        if not self.is_connected:
            raise RuntimeError("You must first connect to a device before trying to write registers to it")

        from .functions import validate_i2c_address
        if not validate_i2c_address(hex(device_address)):
            raise RuntimeError("Invalid I2C address received: {}".format(hex(device_address)))

        byte_count = len(data)

        if byte_count == 1:
            self._parent.send_i2c_logging_message("Trying to write the value 0x{:02x} to the register 0x{:04x} of the I2C device with address 0x{:02x}:".format(data[0], memory_address, device_address))
        else:
            self._parent.send_i2c_logging_message("Trying to write a register block with size {} starting at register 0x{:04x} of the I2C device with address 0x{:02x}:\n   Writing the value array: {}".format(byte_count, memory_address, device_address, repr(data)))

        if self._no_connect:
            self._parent.send_i2c_logging_message("   Software emulation (no connect) is enabled, so no write action is taken.\n")
            return

        if self._max_seq_byte is None:
            self._parent.send_i2c_logging_message("   Writing the full block at once\n")
            if self._swap_endian:
                memory_address = self.swap_endian_16bit(memory_address)
            self._iss.i2c.write_ad2(device_address, memory_address, data)
        else:
            from math import ceil
            from time import sleep
            seq_calls = ceil(byte_count/self._max_seq_byte)
            self._parent.send_i2c_logging_message("   Breaking the write into {} individual writes of {} bytes:".format(seq_calls, self._max_seq_byte))

            lastUpdateTime = time.time_ns()
            for i in range(seq_calls):
                thisTime = time.time_ns()
                if thisTime - lastUpdateTime > 0.2 * 10**9:
                    self.display_progress("Writing:", i*100./seq_calls)
                    self._frame.update_idletasks()

                this_block_address = memory_address + i*self._max_seq_byte
                bytes_to_write = min(self._max_seq_byte, byte_count - i*self._max_seq_byte)
                self._parent.send_i2c_logging_message("      Write operation {}: writing {} bytes starting from 0x{:04x}".format(i, bytes_to_write, this_block_address))

                this_data = data[i*self._max_seq_byte:i*self._max_seq_byte+bytes_to_write]
                self._parent.send_i2c_logging_message("         {}".format(repr(this_data)))

                if self._swap_endian:
                    this_block_address = self.swap_endian_16bit(this_block_address)
                self._iss.i2c.write_ad2(device_address, this_block_address, this_data)

                sleep(0.00001)
            self._parent.send_i2c_logging_message("")
            self.clear_progress()
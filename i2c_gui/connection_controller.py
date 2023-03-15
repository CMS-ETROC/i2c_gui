from __future__ import annotations

from .gui_helper import GUI_Helper
from .base_gui import Base_GUI

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging

from usb_iss import UsbIss

class Connection_Controller(GUI_Helper):
    _parent: Base_GUI
    def __init__(self, parent: Base_GUI, usb_iss_max_seq_byte = 8, override_logger = None):
        if override_logger is None:
            super().__init__(parent, None, parent._logger)
        else:
            super().__init__(parent, None, override_logger)
        self._is_connected = False
        self._usb_iss_max_seq_byte = usb_iss_max_seq_byte

        self._iss = UsbIss()

        self._port_var = tk.StringVar()
        self._port_var.set("COM3")

        self._clk_var = tk.IntVar(self._frame)
        self._clk_var.set(100)

        self._registered_connection_callbacks = []

        from . import __no_connect__
        if __no_connect__:
            self._previous_write_value = None

    @property
    def is_connected(self):
        return self._is_connected

    def _set_connected(self, value):
        if value != self._is_connected:
            if value:
                self.send_message("Connected to I2C bus with a bitrate of {} kHz through port {}".format(self.clk, self.port))
            else:
                self.send_message("Disconnected from I2C bus with a bitrate of {} kHz through port {}".format(self.clk, self.port))
            self._is_connected = value
            for function in self._registered_connection_callbacks:
                function(value)

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

    def check_i2c_device(self, address: str):
        from . import __no_connect__
        if __no_connect__:
            return True

        if not self.is_connected:
            return False

        if not self._iss.i2c.test(int(address, 16)):
            return False
        return True

    def register_connection_callback(self, function):
        if function not in self._registered_connection_callbacks:
            self._registered_connection_callbacks += [function]

    def deregister_connection_callback(self, function):
        if function in self._registered_connection_callbacks:
            self._registered_connection_callbacks.remove(function)

    def prepare_display(self, element: tk.Tk, col: int, row: int):
        self._frame = ttk.LabelFrame(element, text="I2C Connection Configuration")
        self._frame.grid(column=col, row=row, sticky=(tk.N, tk.W, tk.E, tk.S))

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

        self._connect_button = ttk.Button(self._frame, text="Connect", command=self.connect)
        self._connect_button.grid(column=10, row=0, sticky=(tk.W, tk.E))

    def connect(self):
        if self.is_connected:
            self.disconnect()

        if self.port == "":
            self.send_message("Please enter a valid port")
            return

        # Give preference to hardware I2C for clk which support both hardware and bit bashed
        use_hardware = True
        if self._clk_var.get() < 100:
            use_hardware = False

        from . import __no_connect__
        if not __no_connect__:
            try:
                self._iss.open(self.port)
                self._iss.setup_i2c(clock_khz=self.clk, use_i2c_hardware=use_hardware)
            except:
                self.send_message("Unable to connect to I2C bus on port {} using I2C at {} kHz".format(self.port, self.clk))
                return

        # If connection successfull:
        if hasattr(self, "_connect_button"):
            self._connect_button.config(text="Disconnect", command=self.disconnect)
            self._port_entry.config(state="disabled")
            self._clk_option.config(state="disabled")
        self._set_connected(True)

    def disconnect(self):
        if not self.is_connected:
            return

        self._iss.close()

        if hasattr(self, "_connect_button"):
            self._connect_button.config(text="Connect", command=self.connect)
            self._port_entry.config(state="normal")
            self._clk_option.config(state="normal")
        self._set_connected(False)

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

        from . import __swap_endian__
        if __swap_endian__:
            memory_address = self.swap_endian_16bit(memory_address)

        from . import __no_connect__
        from . import __no_connect_type__
        if __no_connect__:
            retVal = []
            if __no_connect_type__ == "check" or self._previous_write_value is None:
                for i in range(byte_count):
                    retVal += [i]
                if byte_count == 1:
                    retVal[0] = 0x42
            elif __no_connect_type__ == "echo":
                for i in range(byte_count):
                    retVal += [self._previous_write_value]
                if byte_count == 1:
                    retVal[0] = self._previous_write_value
            else:
                self._logger.error("Massive error, no connect was set, but an incorrect no connect type was chosen, so the I2C emulation behaviour is unknown")
            return retVal

        from . import __swap_endian__
        if self._usb_iss_max_seq_byte is None:
            if __swap_endian__:
                memory_address = self.swap_endian_16bit(memory_address)
            return self._iss.i2c.read_ad2(device_address, memory_address, byte_count)
        else:
            from math import ceil
            from time import sleep
            tmp = []
            seq_calls = ceil(byte_count/self._usb_iss_max_seq_byte)
            for i in range(seq_calls):
                this_block_address = memory_address + i*self._usb_iss_max_seq_byte
                if __swap_endian__:
                    this_block_address = self.swap_endian_16bit(this_block_address)
                bytes_to_read = min(self._usb_iss_max_seq_byte, byte_count - i*self._usb_iss_max_seq_byte)
                tmp += self._iss.i2c.read_ad2(device_address, this_block_address, bytes_to_read)
                sleep(0.00001)
            return tmp

    def write_device_memory(self, device_address: int, memory_address: int, data: list[int]):
        if not self.is_connected:
            raise RuntimeError("You must first connect to a device before trying to write registers to it")

        from .functions import validate_i2c_address
        if not validate_i2c_address(hex(device_address)):
            raise RuntimeError("Invalid I2C address received: {}".format(hex(device_address)))

        from . import __no_connect__
        from . import __no_connect_type__
        if __no_connect__:
            if __no_connect_type__ == "echo":
                self._previous_write_value = data[len(data)-1]
            return

        from . import __swap_endian__
        if self._usb_iss_max_seq_byte is None:
            if __swap_endian__:
                memory_address = self.swap_endian_16bit(memory_address)
            self._iss.i2c.write_ad2(device_address, memory_address, data)
        else:
            from math import ceil
            from time import sleep
            byte_count = len(data)

            seq_calls = ceil(byte_count/self._usb_iss_max_seq_byte)
            for i in range(seq_calls):
                this_block_address = memory_address + i*self._usb_iss_max_seq_byte
                if __swap_endian__:
                    this_block_address = self.swap_endian_16bit(this_block_address)
                bytes_to_write = min(self._usb_iss_max_seq_byte, byte_count - i*self._usb_iss_max_seq_byte)
                self._iss.i2c.write_ad2(device_address, this_block_address, data[i*self._usb_iss_max_seq_byte:i*self._usb_iss_max_seq_byte+bytes_to_write])
                sleep(0.00001)

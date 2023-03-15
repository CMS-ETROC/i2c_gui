from __future__ import annotations

from .gui_helper import GUI_Helper
from .base_gui import Base_GUI

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging
import time

from usb_iss import UsbIss
from .usb_iss_helper import USB_ISS_Helper

class Connection_Controller(GUI_Helper):
    _parent: Base_GUI
    def __init__(self, parent: Base_GUI, usb_iss_max_seq_byte = 8, override_logger = None):
        if override_logger is None:
            super().__init__(parent, None, parent._logger)
        else:
            super().__init__(parent, None, override_logger)
        self._is_connected = False

        #  The i2c connection is instantiated as a helper class, the helper class will manage
        # the connection itself, allowing to replace the class with others in case other I2C
        # interfaces need to be supported
        self._i2c_connection = USB_ISS_Helper(self, usb_iss_max_seq_byte)

        self._registered_connection_callbacks = []

        from . import __no_connect__
        if __no_connect__:
            self._previous_write_value = None

    @property
    def is_connected(self):
        return self._is_connected

    def _set_connected(self, value):
        if value != self._is_connected:
            self._is_connected = value
            for function in self._registered_connection_callbacks:
                function(value)

    def check_i2c_device(self, address: str):
        from . import __no_connect__
        if __no_connect__:
            return True

        return self._i2c_connection.check_i2c_device(address)

    def register_connection_callback(self, function):
        if function not in self._registered_connection_callbacks:
            self._registered_connection_callbacks += [function]

    def deregister_connection_callback(self, function):
        if function in self._registered_connection_callbacks:
            self._registered_connection_callbacks.remove(function)

    def prepare_display(self, element: tk.Tk, col: int, row: int):
        self._frame = ttk.LabelFrame(element, text="I2C Connection Configuration")
        self._frame.grid(column=col, row=row, sticky=(tk.N, tk.W, tk.E, tk.S))

        # TODO: Add here the toggle for different I2C backends

        self._i2c_connection_frame = ttk.Frame(self._frame)
        self._i2c_connection_frame.grid(column=1, row=0, sticky=(tk.W, tk.E))
        self._frame.columnconfigure(1, weight=1)

        self._i2c_connection.display_in_frame(self._i2c_connection_frame)

        self._connect_button = ttk.Button(self._frame, text="Connect", command=self.connect)
        self._connect_button.grid(column=2, row=0, sticky=(tk.W, tk.E))

    def connect(self):
        if self.is_connected:
            self.disconnect()

        if not self._i2c_connection.validate_connection_params():
            return

        from . import __no_connect__
        if self._i2c_connection.connect(__no_connect__):
            if hasattr(self, "_connect_button"):
                self._connect_button.config(text="Disconnect", command=self.disconnect)
            self._set_connected(True)

    def disconnect(self):
        if not self.is_connected:
            return

        self._i2c_connection.disconnect()

        if hasattr(self, "_connect_button"):
            self._connect_button.config(text="Connect", command=self.connect)
        self._set_connected(False)

    def read_device_memory(self, device_address: int, memory_address: int, byte_count: int = 1):
        if not self.is_connected:
            raise RuntimeError("You must first connect to a device before trying to read registers from it")

        from .functions import validate_i2c_address
        if not validate_i2c_address(hex(device_address)):
            raise RuntimeError("Invalid I2C address received: {}".format(hex(device_address)))

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

        return self._i2c_connection.read_device_memory(device_address, memory_address, byte_count)

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

        self._i2c_connection.write_device_memory(device_address, memory_address, data)

from __future__ import annotations

__version__ = '0.0.2'
__platform__ = None  # For storing the result of automativ platform detection
__swap_endian__ = True  # Whether to swap register address bytes to correct for mixed up endianness
__no_connect__ = False  # Set to true if the connection to I2C is to be emulated

from .etroc1_gui import ETROC1_GUI
from .etroc2_gui import ETROC2_GUI
from .multi_gui import Multi_GUI

from .functions import validate_8bit_register
from .functions import validate_variable_bit_register
from .functions import validate_i2c_address
from .functions import validate_pixel_index
from .functions import hex_0fill

def set_platform(value):
    global __platform__
    __platform__ = value

def get_swap_endian():
    return __swap_endian__

def toggle_swap_endian():
    global __swap_endian__
    __swap_endian__ = not __swap_endian__

def set_swap_endian():
    global __swap_endian__
    __swap_endian__ = True

def unset_swap_endian():
    global __swap_endian__
    __swap_endian__ = False

__all__ = [
    "ETROC1_GUI",
    "ETROC2_GUI",
    "Multi_GUI",
    "validate_8bit_register",
    "validate_variable_bit_register",
    "validate_i2c_address",
    "validate_pixel_index",
    "hex_0fill",
    "set_platform",
    "get_swap_endian",
    "toggle_swap_endian",
    "set_swap_endian",
    "unset_swap_endian",
]

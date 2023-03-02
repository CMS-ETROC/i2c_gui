from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..connection_controller import Connection_Controller

from .base_chip import Base_Chip
from ..gui_helper import GUI_Helper

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging

register_model = {
    "ETROC2": {  # Address Space (i.e. separate I2C memory spaces)
        "Memory Size": 65536,  # 16 bit memory space
        "Register Blocks": {
            "Peripheral Config": {  # Register Block (i.e. group of registers to be handled as one unit)
                "Base Address": 0x0000,
                "Registers": {
                    "PeriCfg0": {
                        "offset": 0x0000,
                        "default": 0x2C,
                    },
                }
            },
        }
    },
}

register_decoding = {
    "ETROC2": {  # Address Space (i.e. separate I2C memory spaces)
        "Register Blocks":{
            "Peripheral Config": {  # Register Block (i.e. group of registers to be handled as one unit)
                "PLL_ClkGen_disCLK": {
                    "bits": 1,
                    "position": [("PeriCfg0", "0", "0")]  # The tuple should be 1st position is the register, 2nd position the bits in the register, 3rd position the bits in the value
                },
            },
            "Peripheral Status": {  # Register Block
            },
            "Pixel Config": {  # Register Block
            },
            "Pixel Status": {  # Register Block
            },
        }
    }
}

class ETROC1_Chip(Base_Chip):
    def __init__(self, parent: GUI_Helper, i2c_controller: Connection_Controller):
        super().__init__(
            parent=parent,
            chip_name="ETROC1",
            version="0.0.1",
            i2c_controller=i2c_controller,
            register_model=register_model,
            register_decoding=register_decoding
        )

        self.clear_tab("Empty")
        self.register_tab(
            "Graphical View",
            {
                "canvas": False,
            }
        )
        self.register_tab(
            "Array Registers",
            {
                "canvas": True,
                "builder": self.array_register_builder
            }
        )
        self.register_tab(
            "Full Pixel Registers",
            {
                "canvas": True,
            }
        )
        self.register_tab(
            "TDC Test Block Registers",
            {
                "canvas": False,
            }
        )
        self.register_tab(
            "Array Decoded",
            {
                "canvas": False,
            }
        )
        self.register_tab(
            "Full Pixel Decoded",
            {
                "canvas": False,
            }
        )
        self.register_tab(
            "TDC Test Block Decoded",
            {
                "canvas": False,
            }
        )

    def array_register_builder(self, frame: ttk.Frame):
        pass
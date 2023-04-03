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

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..connection_controller import Connection_Controller

from .base_chip import Base_Chip
from ..gui_helper import GUI_Helper

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging

etroc1_version = "0.0.1"

register_model = {
    "Array_Reg_A": {  # Address Space (i.e. separate I2C memory spaces)
        "Memory Size": 32,
        "Register Blocks": {
            "Registers": {  # Register Block (i.e. group of registers to be handled as one unit)
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
    "Array_Reg_B": {  # Address Space (i.e. separate I2C memory spaces)
        "Memory Size": 32,
        "Register Blocks": {
            "Registers": {  # Register Block (i.e. group of registers to be handled as one unit)
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
    "Full_Pixel": {  # Address Space (i.e. separate I2C memory spaces)
        "Memory Size": 32,
        "Register Blocks": {
            "Registers": {  # Register Block (i.e. group of registers to be handled as one unit)
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
    "TDC_Test_Block": {  # Address Space (i.e. separate I2C memory spaces)
        "Memory Size": 32,
        "Register Blocks": {
            "Registers": {  # Register Block (i.e. group of registers to be handled as one unit)
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
    "Array_Reg_A": {  # Address Space (i.e. separate I2C memory spaces)
        "Register Blocks":{
            "Registers": {  # Register Block (i.e. group of registers to be handled as one unit)
                "PLL_ClkGen_disCLK": {
                    "bits": 1,
                    "position": [("PeriCfg0", "0", "0")]  # The tuple should be 1st position is the register, 2nd position the bits in the register, 3rd position the bits in the value
                },
            },
        }
    },
    "Array_Reg_B": {  # Address Space (i.e. separate I2C memory spaces)
        "Register Blocks":{
            "Registers": {  # Register Block (i.e. group of registers to be handled as one unit)
                "PLL_ClkGen_disCLK": {
                    "bits": 1,
                    "position": [("PeriCfg0", "0", "0")]  # The tuple should be 1st position is the register, 2nd position the bits in the register, 3rd position the bits in the value
                },
            },
        }
    },
    "Full_Pixel": {  # Address Space (i.e. separate I2C memory spaces)
        "Register Blocks":{
            "Registers": {  # Register Block (i.e. group of registers to be handled as one unit)
                "PLL_ClkGen_disCLK": {
                    "bits": 1,
                    "position": [("PeriCfg0", "0", "0")]  # The tuple should be 1st position is the register, 2nd position the bits in the register, 3rd position the bits in the value
                },
            },
        }
    },
    "TDC_Test_Block": {  # Address Space (i.e. separate I2C memory spaces)
        "Register Blocks":{
            "Registers": {  # Register Block (i.e. group of registers to be handled as one unit)
                "PLL_ClkGen_disCLK": {
                    "bits": 1,
                    "position": [("PeriCfg0", "0", "0")]  # The tuple should be 1st position is the register, 2nd position the bits in the register, 3rd position the bits in the value
                },
            },
        }
    },
}

class ETROC1_Chip(Base_Chip):
    def __init__(self, parent: GUI_Helper, i2c_controller: Connection_Controller):
        super().__init__(
            parent=parent,
            chip_name="ETROC1",
            version=etroc1_version,
            i2c_controller=i2c_controller,
            register_model=register_model,
            register_decoding=register_decoding
        )

        self._i2c_address_a = None
        self._i2c_address_b = None
        self._i2c_address_full_pixel = None
        self._i2c_address_tdc_test_block = None

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
            "Array Decoded",
            {
                "canvas": False,
            }
        )
        self.register_tab(
            "Full Pixel Registers",
            {
                "canvas": True,
            }
        )
        self.register_tab(
            "Full Pixel Decoded",
            {
                "canvas": False,
            }
        )
        self.register_tab(
            "TDC Test Block Registers",
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
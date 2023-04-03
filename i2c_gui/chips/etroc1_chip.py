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
                "builder": self.graphical_interface_builder
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

    def update_whether_modified(self):
        if self._i2c_address_a is not None:
            state_a = self._address_space["Array_Reg_A"].is_modified
        else:
            state_a = None

        if self._i2c_address_b is not None:
            state_b = self._address_space["Array_Reg_B"].is_modified
        else:
            state_b = None

        if self._i2c_address_full_pixel is not None:
            state_full = self._address_space["Full_Pixel"].is_modified
        else:
            state_full = None

        if self._i2c_address_tdc_test_block is not None:
            state_tdc = self._address_space["TDC_Test_Block"].is_modified
        else:
            state_tdc = None

        state_summary = []
        if state_a is not None:
            state_summary += [state_a]
        if state_b is not None:
            state_summary += [state_b]
        if state_full is not None:
            state_summary += [state_full]
        if state_tdc is not None:
            state_summary += [state_tdc]

        if len(state_summary) == 0:
            final_state = "Unknown"
        elif len(state_summary) == 0:
            final_state = state_summary[0]
        else:
            if len(set(state_summary)) == 1: # If all elements are equal
                final_state = state_summary[0]
            elif "Unknown" in state_summary: # If at least one has unknown status, the full chip has unknown status
                final_state = "Unknown"
            elif True in state_summary: # If at least one is modified, the full chip is modified
                final_state = True
            else:
                final_state = False

        if final_state == True:
            final_state = "Modified"
        elif final_state == False:
            final_state = "Unmodified"

        self._parent._local_status_update(final_state)

    def graphical_interface_builder(self, frame: ttk.Frame):
        pass

    def array_register_builder(self, frame: ttk.Frame):
        frame.columnconfigure(100, weight=1)
        columns = 4

        self._ETROC2_peripheral_config_frame = self.build_block_interface(
            element=frame,
            title="Register Block A",
            internal_title="Register Block A",
            button_title="REG A",
            address_space="Array_Reg_A",
            block="Registers",
            col=100,
            row=100,
            register_columns=columns
        )

        self._ETROC2_peripheral_config_frame = self.build_block_interface(
            element=frame,
            title="Register Block B",
            internal_title="Register Block B",
            button_title="REG B",
            address_space="Array_Reg_B",
            block="Registers",
            col=100,
            row=200,
            register_columns=columns
        )
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
        "Memory Size": 48,
        "Register Blocks": {
            "Registers": {  # Register Block (i.e. group of registers to be handled as one unit)
                "Base Address": 0x0000,
                "Registers": {
                    "Reg_A_00": {
                        "offset": 0x0000,
                        "default": 0xF8,
                    },
                    "Reg_A_01": {
                        "offset": 0x0001,
                        "default": 0x37,
                    },
                    "Reg_A_02": {
                        "offset": 0x0002,
                        "default": 0xFF,
                    },
                    "Reg_A_03": {
                        "offset": 0x0003,
                        "default": 0xFF,
                    },
                    "Reg_A_04": {
                        "offset": 0x0004,
                        "default": 0x11,
                    },
                    "Reg_A_05": {
                        "offset": 0x0005,
                        "default": 0x01,
                    },
                    "Reg_A_06": {
                        "offset": 0x0006,
                        "default": 0x00,
                    },
                    "Reg_A_07": {
                        "offset": 0x0007,
                        "default": 0x01,
                    },
                    "Reg_A_08": {
                        "offset": 0x0008,
                        "default": 0x00,
                    },
                    "Reg_A_09": {
                        "offset": 0x0009,
                        "default": 0x00,
                    },
                    "Reg_A_0A": {
                        "offset": 0x000A,
                        "default": 0x00,
                    },
                    "Reg_A_0B": {
                        "offset": 0x000B,
                        "default": 0x02,
                    },
                    "Reg_A_0C": {
                        "offset": 0x000C,
                        "default": 0x08,
                    },
                    "Reg_A_0D": {
                        "offset": 0x000D,
                        "default": 0x20,
                    },
                    "Reg_A_0E": {
                        "offset": 0x000E,
                        "default": 0x80,
                    },
                    "Reg_A_0F": {
                        "offset": 0x000F,
                        "default": 0x00,
                    },
                    "Reg_A_10": {
                        "offset": 0x0010,
                        "default": 0x02,
                    },
                    "Reg_A_11": {
                        "offset": 0x0011,
                        "default": 0x08,
                    },
                    "Reg_A_12": {
                        "offset": 0x0012,
                        "default": 0x20,
                    },
                    "Reg_A_13": {
                        "offset": 0x0013,
                        "default": 0x80,
                    },
                    "Reg_A_14": {
                        "offset": 0x0014,
                        "default": 0x00,
                    },
                    "Reg_A_15": {
                        "offset": 0x0015,
                        "default": 0x02,
                    },
                    "Reg_A_16": {
                        "offset": 0x0016,
                        "default": 0x08,
                    },
                    "Reg_A_17": {
                        "offset": 0x0017,
                        "default": 0x20,
                    },
                    "Reg_A_18": {
                        "offset": 0x0018,
                        "default": 0x80,
                    },
                    "Reg_A_19": {
                        "offset": 0x0019,
                        "default": 0x00,
                    },
                    "Reg_A_1A": {
                        "offset": 0x001A,
                        "default": 0x02,
                    },
                    "Reg_A_1B": {
                        "offset": 0x001B,
                        "default": 0x08,
                    },
                    "Reg_A_1C": {
                        "offset": 0x001C,
                        "default": 0x20,
                    },
                    "Reg_A_1D": {
                        "offset": 0x001D,
                        "default": 0x80,
                    },
                    "Reg_A_1E": {
                        "offset": 0x001E,
                        "default": 0xFF,
                    },
                    "Reg_A_1F": {
                        "offset": 0x001F,
                        "default": 0xFF,
                    },
                    "Reg_A_20": {
                        "offset": 0x0020,
                        "default": 0x00,
                        "read_only": True,
                    },
                }
            },
        }
    },
    "Array_Reg_B": {
        "Memory Size": 32,
        "Register Blocks": {
            "Registers": {
                "Base Address": 0x0000,
                "Registers": {
                    "Reg_B_00": {
                        "offset": 0x0000,
                        "default": 0x1C,
                    },
                    "Reg_B_01": {
                        "offset": 0x0001,
                        "default": 0x01,
                    },
                    "Reg_B_02": {
                        "offset": 0x0002,
                        "default": 0x00,
                    },
                    "Reg_B_03": {
                        "offset": 0x0003,
                        "default": 0x09,
                    },
                    "Reg_B_04": {
                        "offset": 0x0004,
                        "default": 0x00,
                    },
                    "Reg_B_05": {
                        "offset": 0x0005,
                        "default": 0x03,
                    },
                    "Reg_B_06": {
                        "offset": 0x0006,
                        "default": 0x41,
                    },
                    "Reg_B_07": {
                        "offset": 0x0007,
                        "default": 0x38,
                    },
                    "Reg_B_08": {
                        "offset": 0x0008,
                        "default": 0x18,
                    },
                    "Reg_B_09": {
                        "offset": 0x0009,
                        "default": 0x18,
                    },
                    "Reg_B_0A": {
                        "offset": 0x000A,
                        "default": 0x38,
                    },
                    "Reg_B_0B": {
                        "offset": 0x000B,
                        "default": 0x77,
                    },
                }
            },
        }
    },
    "Full_Pixel": {
        "Memory Size": 48,
        "Register Blocks": {
            "Registers": {
                "Base Address": 0x0000,
                "Registers": {
                    "Reg_00": {
                        "offset": 0x0000,
                        "default": 0x2C,
                    },
                    "Reg_01": {
                        "offset": 0x0001,
                        "default": 0x2C,
                    },
                    "Reg_02": {
                        "offset": 0x0002,
                        "default": 0x2C,
                    },
                    "Reg_03": {
                        "offset": 0x0003,
                        "default": 0x2C,
                    },
                    "Reg_04": {
                        "offset": 0x0004,
                        "default": 0x2C,
                    },
                    "Reg_05": {
                        "offset": 0x0005,
                        "default": 0x2C,
                    },
                    "Reg_06": {
                        "offset": 0x0006,
                        "default": 0x2C,
                    },
                    "Reg_07": {
                        "offset": 0x0007,
                        "default": 0x2C,
                    },
                    "Reg_08": {
                        "offset": 0x0008,
                        "default": 0x2C,
                    },
                    "Reg_09": {
                        "offset": 0x0009,
                        "default": 0x2C,
                    },
                    "Reg_0A": {
                        "offset": 0x000A,
                        "default": 0x2C,
                    },
                    "Reg_0B": {
                        "offset": 0x000B,
                        "default": 0x2C,
                    },
                    "Reg_0C": {
                        "offset": 0x000C,
                        "default": 0x2C,
                    },
                    "Reg_0D": {
                        "offset": 0x000D,
                        "default": 0x2C,
                    },
                    "Reg_0E": {
                        "offset": 0x000E,
                        "default": 0x2C,
                    },
                    "Reg_0F": {
                        "offset": 0x000F,
                        "default": 0x2C,
                    },
                    "Reg_10": {
                        "offset": 0x0010,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_11": {
                        "offset": 0x0011,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_12": {
                        "offset": 0x0012,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_13": {
                        "offset": 0x0013,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_14": {
                        "offset": 0x0014,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_15": {
                        "offset": 0x0015,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_16": {
                        "offset": 0x0016,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_17": {
                        "offset": 0x0017,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_18": {
                        "offset": 0x0018,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_19": {
                        "offset": 0x0019,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_1A": {
                        "offset": 0x001A,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_1B": {
                        "offset": 0x001B,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_1C": {
                        "offset": 0x001C,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_1D": {
                        "offset": 0x001D,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_1E": {
                        "offset": 0x001E,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_1F": {
                        "offset": 0x001F,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_20": {
                        "offset": 0x0020,
                        "default": 0x2C,
                        "read_only": True,
                    },
                }
            },
        }
    },
    "TDC_Test_Block": {
        "Memory Size": 48,
        "Register Blocks": {
            "Registers": {
                "Base Address": 0x0000,
                "Registers": {
                    "Reg_00": {
                        "offset": 0x0000,
                        "default": 0x2C,
                    },
                    "Reg_01": {
                        "offset": 0x0001,
                        "default": 0x2C,
                    },
                    "Reg_02": {
                        "offset": 0x0002,
                        "default": 0x2C,
                    },
                    "Reg_03": {
                        "offset": 0x0003,
                        "default": 0x2C,
                    },
                    "Reg_04": {
                        "offset": 0x0004,
                        "default": 0x2C,
                    },
                    "Reg_05": {
                        "offset": 0x0005,
                        "default": 0x2C,
                    },
                    "Reg_06": {
                        "offset": 0x0006,
                        "default": 0x2C,
                    },
                    "Reg_07": {
                        "offset": 0x0007,
                        "default": 0x2C,
                    },
                    "Reg_08": {
                        "offset": 0x0008,
                        "default": 0x2C,
                    },
                    "Reg_09": {
                        "offset": 0x0009,
                        "default": 0x2C,
                    },
                    "Reg_0A": {
                        "offset": 0x000A,
                        "default": 0x2C,
                    },
                    "Reg_0B": {
                        "offset": 0x000B,
                        "default": 0x2C,
                    },
                    "Reg_0C": {
                        "offset": 0x000C,
                        "default": 0x2C,
                    },
                    "Reg_0D": {
                        "offset": 0x000D,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_0E": {
                        "offset": 0x000E,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_0F": {
                        "offset": 0x000F,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_10": {
                        "offset": 0x0010,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_11": {
                        "offset": 0x0011,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_12": {
                        "offset": 0x0012,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_13": {
                        "offset": 0x0013,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_14": {
                        "offset": 0x0014,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_15": {
                        "offset": 0x0015,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_16": {
                        "offset": 0x0016,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_17": {
                        "offset": 0x0017,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_18": {
                        "offset": 0x0018,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_19": {
                        "offset": 0x0019,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_1A": {
                        "offset": 0x001A,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_1B": {
                        "offset": 0x001B,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_1C": {
                        "offset": 0x001C,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_1D": {
                        "offset": 0x001D,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_1E": {
                        "offset": 0x001E,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_1F": {
                        "offset": 0x001F,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_20": {
                        "offset": 0x0020,
                        "default": 0x2C,
                        "read_only": True,
                    },
                    "Reg_21": {
                        "offset": 0x0021,
                        "default": 0x2C,
                        "read_only": True,
                    },
                    "Reg_22": {
                        "offset": 0x0022,
                        "default": 0x2C,
                        "read_only": True,
                    },
                    "Reg_23": {
                        "offset": 0x0023,
                        "default": 0x2C,
                        "read_only": True,
                    },
                    "Reg_24": {
                        "offset": 0x0024,
                        "default": 0x2C,
                        "read_only": True,
                    },
                    "Reg_25": {
                        "offset": 0x0025,
                        "default": 0x2C,
                        "read_only": True,
                    },
                    "Reg_26": {
                        "offset": 0x0026,
                        "default": 0x2C,
                        "read_only": True,
                    },
                    "Reg_27": {
                        "offset": 0x0027,
                        "default": 0x2C,
                        "read_only": True,
                    },
                    "Reg_28": {
                        "offset": 0x0028,
                        "default": 0x2C,
                        "read_only": True,
                    },
                    "Reg_29": {
                        "offset": 0x0029,
                        "default": 0x2C,
                        "read_only": True,
                    },
                    "Reg_2A": {
                        "offset": 0x002A,
                        "default": 0x2C,
                        "read_only": True,
                    },
                    "Reg_2B": {
                        "offset": 0x002B,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_2C": {
                        "offset": 0x002C,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_2D": {
                        "offset": 0x002D,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_2E": {
                        "offset": 0x002E,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
                    },
                    "Reg_2F": {
                        "offset": 0x002F,
                        "default": 0x2C,
                        "read_only": True,
                        "display": False,
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
                "EN_DiscriOut": {
                    "bits": 8,
                    "position": [
                        ("Reg_A_04", "7-0", "7-0"),  # The tuple should be 1st position is the register, 2nd position the bits in the register, 3rd position the bits in the value
                    ],
                    "info": "{0} enables the discriminator output, active high.\n Each bit in {0}[7:4] represents the row, and each bit in {0}[3:0] represents the column. Users can enable the discriminator output for a specified pixel. Only one row can be specified at a time. That means no more than one bit in {0}[7:4] can be set to 1 at a time.\n When more than one bit is set to 1, or all bits are set to 0 in {0}[3:0], the discriminator output is disabled.\n\nFor example:\n - 0b0010_0100→pixel in row 1 and column 2\n - 0b0001_0001→pixel in row 0 and column 0\n - 0b1000_0100→pixel in row 3 and column 2\n - 0bxxxx_0101→disable discriminator output, but invalid\n - 0b1011_xxxx→invalid\n - 0b0000_0111→disable discriminator output\n - 0b0000_0000→disable discriminator output",
                    "show_binary": "New Line"
                },
                "EN_DiscriOut_Row": {
                    "bits": 4,
                    "position": [
                        ("Reg_A_04", "7-4", "3-0"),
                    ],
                    "show_binary": True
                },
                "EN_DiscriOut_Column": {
                    "bits": 4,
                    "position": [
                        ("Reg_A_04", "3-0", "3-0"),
                    ],
                    "show_binary": True
                },
                "DIS_VTHInOut": {
                    "bits": 16,
                    "position": [
                        ("Reg_A_03", "7-0", "15-8"),
                        ("Reg_A_02", "7-0", "7-0"),
                    ],
                    "info": "{0} disables the threshold voltage input/output of the specified pixel, active high. Each bit controls a pixel according the pixels index map.\nOnly one of thresholds can be enabled at a time.\nFor example: DIS_VTHInOut = 0x4000.",
                    "show_binary": "New Line"
                },
                "EN_QInj": {
                    "bits": 16,
                    "position": [
                        ("Reg_A_06", "7-0", "15-8"),
                        ("Reg_A_05", "7-0", "7-0"),
                    ],
                    "info": "{0} enables the charge injection of the specified pixel, active high.\n Each bit controls a pixel.\n Users can specify none or more pixels to enable the charge injection.",
                    "show_binary": "New Line"
                },
                "PD_DACDiscri": {
                    "bits": 16,
                    "position": [
                        ("Reg_A_09", "7-0", "15-8"),
                        ("Reg_A_08", "7-0", "7-0"),
                    ],
                    "info": "{0} powers down the DAC and the discriminator in pixels, active high.\n Each bit controls a pixel.\n Users can specify none or more pixels to control.",
                    "show_binary": "New Line"
                },
                "ROI": {
                    "bits": 16,
                    "position": [
                        ("Reg_A_1F", "7-0", "15-8"),
                        ("Reg_A_1E", "7-0", "7-0"),
                    ],
                    "info": "{0} defines the region of interest. 16-bit vector specifies which pixels are enabled for readout.",
                    "show_binary": "New Line"
                },
                "OE_DMRO_Row": {
                    "bits": 4,
                    "position": [("Reg_A_07", "3-0", "3-0")],
                    "info": "{0} enables the output of DMRO in rows. Each bit represents a row. Only one row can be enabled for output at a time.\nFor example:\n - 0b0000→no DMRO output enabled\n - 0b0001→the row 0 of DMRO output is enabled\n - 0b0100→the row 2 of DMRO output is enabled\n - 0b1010→invalid",
                    "show_binary": True
                },
                "DMRO_COL": {
                    "bits": 2,
                    "position": [("Reg_A_07", "5-4", "1-0")],
                    "info": "{0} selects DMRO output from a specified column:\n - 0b00→column 0\n - 0b01→column 1\n - 0b10→column 2\n - 0b11→column 3",
                    "show_binary": True
                },
                "RO_SEL": {
                    "bits": 1,
                    "position": [("Reg_A_07", "6", "0")],
                    "info": "{0} selects readout mode from either SRO or DMRO:\n - Low→DMRO enabled\n - High→SRO enabled",
                },
                "CLSel": {
                    "bits": 2,
                    "position": [("Reg_A_00", "1-0", "1-0")],
                    "info": "Shared by all pixels.\n{0} selects the load capacitance of the preamp first stage:\n - 0b00: 0 fC\n - 0b01: 80 fC\n - 0b10: 80 fC\n - 0b11: 160 fC",
                    "show_binary": False
                },
                "HysSel": {
                    "bits": 4,
                    "position": [
                        ("Reg_A_00", "7-4", "3-0"),
                    ],
                    "info": "Shared by all pixels.\n{0} selects the hysteresis voltage:\n - 0b0000 --> Vhys1\n - 0b0001 --> Vhys2\n - 0b0011 --> Vhys3\n - 0b0111 --> Vhys4\n - 0b1111 --> Vhys5\nVhys1 > Vhys2 > Vhys3 > Vhys4 = Vhys5 = 0",
                    "show_binary": False
                },
                "IBSel": {
                    "bits": 3,
                    "position": [
                        ("Reg_A_01", "2-0", "2-0"),
                    ],
                    "info": "Shared by all pixels.\n{0} selects the bias current of the input transistor in the preamp:\n - 0b000 --> I1\n - 0b001, 0b010, 0b100 --> I2\n - 0b011, 0b110, 0b101 --> I3\n - 0b111 --> I4\nI1 > I2 > I3 > I4",
                    "show_binary": False
                },
                "QSel": {
                    "bits": 5,
                    "position": [
                        ("Reg_A_01", "7-3", "4-0"),
                    ],
                    "info": "Shared by all pixels.\n{0} selects the injected charge, from 1 fC(0b00000) to 32 fC(0b11111).\nTypical charge from LGAD sensor is 7 fC(0b00110)",
                    "show_binary": True
                },
                "RfSel": {
                    "bits": 2,
                    "position": [
                        ("Reg_A_00", "3-2", "1-0"),
                    ],
                    "info": "Shared by all pixels.\n{0} selects the feedback resistance:\n - 0b00 --> 20 kOHm\n - 0b01--> 10 kOHm\n - 0b10--> 5.7 kOHm\n - 0b11--> 4.4 kOHm",
                    "show_binary": False
                },

                "VTHIn_Pix0": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_0A", "7-0", "7-0"),
                        ("Reg_A_0B", "1-0", "9-8"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 0",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix1": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_0B", "7-2", "5-0"),
                        ("Reg_A_0C", "3-0", "9-6"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 1",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix2": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_0C", "7-4", "3-0"),
                        ("Reg_A_0D", "5-0", "9-4"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 2",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix3": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_0D", "7-6", "1-0"),
                        ("Reg_A_0E", "7-0", "9-2"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 3",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix4": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_0F", "7-0", "7-0"),
                        ("Reg_A_10", "1-0", "9-8"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 4",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix5": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_10", "7-2", "5-0"),
                        ("Reg_A_11", "3-0", "9-6"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 5",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix6": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_11", "7-4", "3-0"),
                        ("Reg_A_12", "5-0", "9-4"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 6",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix7": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_12", "7-6", "1-0"),
                        ("Reg_A_13", "7-0", "9-2"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 7",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix8": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_14", "7-0", "7-0"),
                        ("Reg_A_15", "1-0", "9-8"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 8",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix9": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_15", "7-2", "5-0"),
                        ("Reg_A_16", "3-0", "9-6"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 9",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix10": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_16", "7-4", "3-0"),
                        ("Reg_A_17", "5-0", "9-4"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 10",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix11": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_17", "7-6", "1-0"),
                        ("Reg_A_18", "7-0", "9-2"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 11",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix12": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_19", "7-0", "7-0"),
                        ("Reg_A_1A", "1-0", "9-8"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 12",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix13": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_1A", "7-2", "5-0"),
                        ("Reg_A_1B", "3-0", "9-6"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 13",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix14": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_1B", "7-4", "3-0"),
                        ("Reg_A_1C", "5-0", "9-4"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 14",
                    "show_binary": "New Line"
                },
                "VTHIn_Pix15": {
                    "bits": 10,
                    "position": [
                        ("Reg_A_1C", "7-6", "1-0"),
                        ("Reg_A_1D", "7-0", "9-2"),
                    ],
                    "info": "{0} is the threshold voltage input of pixel 15",
                    "show_binary": "New Line"
                },

                "dllLate": {
                    "bits": 1,
                    "position": [
                        ("Reg_A_20", "0", "0"),
                    ],
                    "info": "{0} is the lock status prompt",
                    "read_only": True,
                },
            },
        }
    },
    "Array_Reg_B": {  # Address Space (i.e. separate I2C memory spaces)
        "Register Blocks":{
            "Registers": {  # Register Block (i.e. group of registers to be handled as one unit)
                "autoReset_TDC": {
                    "bits": 1,
                    "position": [("Reg_B_00", "0", "0")],  # The tuple should be 1st position is the register, 2nd position the bits in the register, 3rd position the bits in the value
                },
                "enableMon_TDC": {
                    "bits": 1,
                    "position": [("Reg_B_00", "1", "0")],
                    "info": "This bit is actually used to control the readout test mode in ROTestGen.",
                },
                "enable_TDC": {
                    "bits": 1,
                    "position": [("Reg_B_00", "2", "0")],
                },
                "level_TDC": {
                    "bits": 3,
                    "position": [("Reg_B_01", "2-0", "2-0")],
                },
                "offset_TDC": {
                    "bits": 7,
                    "position": [("Reg_B_02", "6-0", "6-0")],
                },
                "polaritySel_TDC": {
                    "bits": 1,
                    "position": [("Reg_B_00", "3", "0")],
                },
                "resetn_TDC": {
                    "bits": 1,
                    "position": [("Reg_B_00", "4", "0")],
                },
                "selRawCode_TDC": {
                    "bits": 1,
                    "position": [("Reg_B_00", "5", "0")],
                },
                "testMode_TDC": {
                    "bits": 1,
                    "position": [("Reg_B_00", "6", "0")],
                },
                "timeStampMode_TDC": {
                    "bits": 1,
                    "position": [("Reg_B_00", "7", "0")],
                },
                "dllEnable": {
                    "bits": 1,
                    "position": [("Reg_B_03", "0", "0")],
                    "info": "{0} enables loop control of DLL. The control voltage is tied to ground when dllEnable==low."
                },
                "dllForceDown": {
                    "bits": 1,
                    "position": [("Reg_B_03", "1", "0")],
                    "info": "{0} forces to pull down the output of the phase detector, active high."
                },
                "dllCapReset": {
                    "bits": 1,
                    "position": [("Reg_B_03", "2", "0")],
                    "info": "{0} resets the control voltage of DLL to power supply, active high."
                },
                "dllCPCurrent": {
                    "bits": 4,
                    "position": [("Reg_B_03", "6-3", "3-0")],
                    "info": "{0} is the charge pump current control bits, ranging from 0 to 15uA for charge and discharge."
                },
                "PhaseAdj": {
                    "bits": 8,
                    "position": [("Reg_B_04", "7-0", "7-0")],
                    "info": "{0} is the Phase selecting control bits, {0}[7:3] for coarse, {0}[2:0] for fine.",
                    "show_binary": "New Line"
                },
                "RefStrSel": {
                    "bits": 8,
                    "position": [("Reg_B_05", "7-0", "7-0")],
                    "info": "{0} is the TDC reference strobe selection."
                },
                "ENScr_DMRO": {
                    "bits": 1,
                    "position": [("Reg_B_06", "0", "0")],
                    "info": "{0} enables scrambling, active high."
                },
                "REVCLK_DMRO": {
                    "bits": 1,
                    "position": [("Reg_B_06", "1", "0")],
                    "info": "{0} reverses the clock used for input data latch, active-high. When REVData=0 data is latched at the rising edges of CLKWord, otherwise data is latched at the falling edges of CLKWord."
                },
                "REVData_DMRO": {
                    "bits": 1,
                    "position": [("Reg_B_06", "2", "0")],
                    "info": "{0} reverses input data, active-high."
                },
                "TestMode_DMRO": {
                    "bits": 1,
                    "position": [("Reg_B_06", "3", "0")],
                    "info": "{0} is the test mode input, active high. The PRBS7 is sent out in test mode (TestMode == 1) while the data is sent out in normal mode (TestMode == 0)."
                },
                "TestCLK0": {
                    "bits": 1,
                    "position": [("Reg_B_06", "4", "0")],
                    "info": "When {0}=1, the phase shifter is bypassed and off-chip 40MHz and 320MHz are used."
                },
                "TestCLK1": {
                    "bits": 1,
                    "position": [("Reg_B_06", "5", "0")],
                    "info": "When {0}=1, the TDC reference strobe generator is bypassed and off-chip 40MHz and 320MHz are used."
                },
                "CLKOutSel": {
                    "bits": 1,
                    "position": [("Reg_B_06", "6", "0")],
                    "info": "{0} selects output from either 40 MHz clock or TDC reference strobe:\n - 0b0: 40 MHz clock\n - 0b1: TDC reference strobe"
                },
                "enableRx_1P28G": {
                    "bits": 1,
                    "position": [("Reg_B_07", "5", "0")],
                    "info": "{0} enables the Rx for 1.28 GHz clock, active high"
                },
                "setCM_1P28G": {
                    "bits": 1,
                    "position": [("Reg_B_07", "4", "0")],
                    "info": "{0} sets the common voltage of the Rx for the 1.28 GHz clock to 1/2 vdd, active high"
                },
                "enableTER_1P28G": {
                    "bits": 1,
                    "position": [("Reg_B_07", "3", "0")],
                    "info": "{0} enables internal termination of the Rx for the 1.28 GHz clock, active high"
                },
                "invertData_1P28G": {
                    "bits": 1,
                    "position": [("Reg_B_07", "2", "0")],
                    "info": "{0} inverts data of the Rx for the 1.28 GHz clock, active high"
                },
                "equ_1P28G": {
                    "bits": 2,
                    "position": [("Reg_B_07", "1-0", "1-0")],
                    "info": "{0} sets the equalization strength of the Rx for the 320 MHz clock\n - 0b00, equalization is turned off\n - 0b11, largest equalization"
                },
                "enableRx_320M": {
                    "bits": 1,
                    "position": [("Reg_B_08", "5", "0")],
                    "info": "{0} enables the Rx for the 320 MHz clock, active high"
                },
                "setCM_320M": {
                    "bits": 1,
                    "position": [("Reg_B_08", "4", "0")],
                    "info": "{0} sets the common voltage of the Rx for the 320 MHz clock to 1/2 vdd, active high"
                },
                "enableTER_320M": {
                    "bits": 1,
                    "position": [("Reg_B_08", "3", "0")],
                    "info": "{0} enables internal termination of the Rx for the 320 MHz clock, active high"
                },
                "invertData_320M": {
                    "bits": 1,
                    "position": [("Reg_B_08", "2", "0")],
                    "info": "{0} inverts data of the Rx for the 320 MHz clock, active high"
                },
                "equ_320M": {
                    "bits": 2,
                    "position": [("Reg_B_08", "1-0", "1-0")],
                    "info": "{0} set the equalization strength of the Rx for the 320 MHz clock\n - 0b00, equalization is turned off\n - 0b11, largest equalization"
                },
                "enableRx_40M": {
                    "bits": 1,
                    "position": [("Reg_B_09", "5", "0")],
                    "info": "{0} enables the Rx for the 40 MHz clock, active high"
                },
                "setCM_40M": {
                    "bits": 1,
                    "position": [("Reg_B_09", "4", "0")],
                    "info": "{0} sets the common voltage of the Rx for the 40 MHz clock to 1/2 vdd, active high"
                },
                "enableTER_40M": {
                    "bits": 1,
                    "position": [("Reg_B_09", "3", "0")],
                    "info": "{0} enables the internal termination of the Rx for the 40 MHz clock, active high"
                },
                "invertData_40M": {
                    "bits": 1,
                    "position": [("Reg_B_09", "2", "0")],
                    "info": "{0} inverts the data of the Rx for the 40 MHz clock, active high"
                },
                "equ_40M": {
                    "bits": 2,
                    "position": [("Reg_B_09", "1-0", "1-0")],
                    "info": "{0} sets the equalization strength of the Rx for the 40 MHz clock\n - 0b00, equalization is turned off\n - 0b11, largest equalization"
                },
                "enableRx_QInj": {
                    "bits": 1,
                    "position": [("Reg_B_0A", "5", "0")],
                    "info": "{0} enables the Rx for the QInj, active high"
                },
                "setCM_QInj": {
                    "bits": 1,
                    "position": [("Reg_B_0A", "4", "0")],
                    "info": "{0} sets the common voltage of the Rx for the QInj to 1/2 vdd, active high"
                },
                "enableTER_QInj": {
                    "bits": 1,
                    "position": [("Reg_B_0A", "3", "0")],
                    "info": "{0} enables internal termination of the Rx for the QInj, active high"
                },
                "invertData_QInj": {
                    "bits": 1,
                    "position": [("Reg_B_0A", "2", "0")],
                    "info": "{0} inverts data of the Rx for the QInj, active high"
                },
                "equ_QInj": {
                    "bits": 2,
                    "position": [("Reg_B_0A", "1-0", "1-0")],
                    "info": "{0} sets the equalization strength of the Rx for the QInj\n - 0b00, equalization is turned off\n - 0b11, largest equalization"
                },
                "AMPL_CLKTO": {
                    "bits": 3,
                    "position": [("Reg_B_0B", "2-0", "2-0")],
                    "info": "3bits to select different output amplitude.\n - 0b000 = min amplitude(50m)\n - 0b111 = max amplitude(320m)\n(Step size ≈ 40mV)"
                },
                "disCML_CLKTO": {
                    "bits": 1,
                    "position": [("Reg_B_0B", "3", "0")],
                    "info": "{0} disables the CML driver, active high"
                },
                "AMPL_DOut": {
                    "bits": 3,
                    "position": [("Reg_B_0B", "6-4", "2-0")],
                    "info": "3bits to select different output amplitude.\n - 0b000 = min amplitude(50m)\n - 0b111 = max amplitude(320m)\n(Step size ≈ 40mV)"
                },
                "disCML_DOut": {
                    "bits": 1,
                    "position": [("Reg_B_0B", "7", "0")],
                    "info": "{0} disables the CML driver, active high"
                },
            },
        }
    },
    "Full_Pixel": {  # Address Space (i.e. separate I2C memory spaces)
        "Register Blocks":{
            "Registers": {  # Register Block (i.e. group of registers to be handled as one unit)
                "PLL_ClkGen_disCLK": {
                    "bits": 1,
                    "position": [("Reg_00", "0", "0")]  # The tuple should be 1st position is the register, 2nd position the bits in the register, 3rd position the bits in the value
                },
            },
        }
    },
    "TDC_Test_Block": {  # Address Space (i.e. separate I2C memory spaces)
        "Register Blocks":{
            "Registers": {  # Register Block (i.e. group of registers to be handled as one unit)
                "PLL_ClkGen_disCLK": {
                    "bits": 1,
                    "position": [("Reg_00", "0", "0")]  # The tuple should be 1st position is the register, 2nd position the bits in the register, 3rd position the bits in the value
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
                "canvas": True,
                "builder": self.array_register_decoded_builder
            }
        )
        self.register_tab(
            "Full Pixel Registers",
            {
                "canvas": True,
                "builder": self.full_pixel_register_builder
            }
        )
        self.register_tab(
            "Full Pixel Decoded",
            {
                "canvas": True,
                "builder": self.full_pixel_register_decoded_builder
            }
        )
        self.register_tab(
            "TDC Test Block Registers",
            {
                "canvas": True,
                "builder": self.tdc_register_builder
            }
        )
        self.register_tab(
            "TDC Test Block Decoded",
            {
                "canvas": True,
                "builder": self.tdc_register_decoded_builder
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

    def config_i2c_address_a(self, address):
        self._i2c_address_a = address

        from .address_space_controller import Address_Space_Controller
        if "Array_Reg_A" in self._address_space:
            address_space: Address_Space_Controller = self._address_space["Array_Reg_A"]
            address_space.update_i2c_address(address)
        self.update_whether_modified()

    def config_i2c_address_b(self, address):
        self._i2c_address_b = address

        from .address_space_controller import Address_Space_Controller
        if "Array_Reg_B" in self._address_space:
            address_space: Address_Space_Controller = self._address_space["Array_Reg_B"]
            address_space.update_i2c_address(address)
        self.update_whether_modified()

    def config_i2c_address_full_pixel(self, address):
        self._i2c_address_full_pixel = address

        from .address_space_controller import Address_Space_Controller
        if "Full_Pixel" in self._address_space:
            address_space: Address_Space_Controller = self._address_space["Full_Pixel"]
            address_space.update_i2c_address(address)
        self.update_whether_modified()

    def config_i2c_address_tdc(self, address):
        self._i2c_address_tdc_test_block = address

        from .address_space_controller import Address_Space_Controller
        if "TDC_Test_Block" in self._address_space:
            address_space: Address_Space_Controller = self._address_space["TDC_Test_Block"]
            address_space.update_i2c_address(address)
        self.update_whether_modified()

    def graphical_interface_builder(self, frame: ttk.Frame):
        pass

    def array_register_builder(self, frame: ttk.Frame):
        frame.columnconfigure(100, weight=1)
        columns = 4

        self._array_register_a_frame = self.build_block_interface(
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

        self._array_register_b_frame = self.build_block_interface(
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

    def array_register_decoded_builder(self, frame: ttk.Frame):
        frame.columnconfigure(100, weight=1)
        columns = 3

        self._array_register_a_decoded_frame = self.build_decoded_block_interface(
            element=frame,
            title="Values Block A",
            internal_title="Values Block A",
            button_title="REG A",
            address_space="Array_Reg_A",
            block="Registers",
            col=100,
            row=100,
            value_columns=columns
        )

        self._array_register_b_decoded_frame = self.build_decoded_block_interface(
            element=frame,
            title="Values Block B",
            internal_title="Values Block B",
            button_title="REG B",
            address_space="Array_Reg_B",
            block="Registers",
            col=100,
            row=200,
            value_columns=columns,
        )

    def full_pixel_register_builder(self, frame: ttk.Frame):
        frame.columnconfigure(100, weight=1)
        columns = 4

        self._full_pixel_register_frame = self.build_block_interface(
            element=frame,
            title="Full Pixel",
            internal_title="Full Pixel",
            button_title="Pixel",
            address_space="Full_Pixel",
            block="Registers",
            col=100,
            row=100,
            register_columns=columns
        )

    def full_pixel_register_decoded_builder(self, frame: ttk.Frame):
        frame.columnconfigure(100, weight=1)
        columns = 3

        self._full_pixel_decoded_frame = self.build_decoded_block_interface(
            element=frame,
            title="Full Pixel",
            internal_title="Full Pixel Decoded",
            button_title="Pixel",
            address_space="Full_Pixel",
            block="Registers",
            col=100,
            row=100,
            value_columns=columns
        )

    def tdc_register_builder(self, frame: ttk.Frame):
        frame.columnconfigure(100, weight=1)
        columns = 4

        self._tdc_register_frame = self.build_block_interface(
            element=frame,
            title="TDC Test Block",
            internal_title="TDC Test Block",
            button_title="TDC",
            address_space="TDC_Test_Block",
            block="Registers",
            col=100,
            row=100,
            register_columns=columns
        )

    def tdc_register_decoded_builder(self, frame: ttk.Frame):
        frame.columnconfigure(100, weight=1)
        columns = 3

        self._tdc_decoded_frame = self.build_decoded_block_interface(
            element=frame,
            title="TDC Test Block",
            internal_title="TDC Test Block Decoded",
            button_title="TDC",
            address_space="TDC_Test_Block",
            block="Registers",
            col=100,
            row=100,
            value_columns=columns
        )
from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..connection_controller import Connection_Controller

from .base_chip import Base_Chip
from ..gui_helper import GUI_Helper
from .address_space_controller import Address_Space_Controller

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging

def etroc2_column_row_to_base_address(block: str, column: int, row: int, broadcast: bool = False):
    address = 0b1000000000000000

    if block == "Pixel Config":
        pass
    elif block == "Pixel Status":
        address = address | 0b0100000000000000
    else:
        raise RuntimeError("The etroc2 register block must be either 'Pixel Config' or 'Pixel Status'")

    if broadcast:
        address = address | 0b0010000000000000

    if column > 15 or column < 0:
        raise RuntimeError("The etroc2 column must be between 0 and 15")
    address = address | (column << 9)

    if row > 15 or row < 0:
        raise RuntimeError("The etroc2 row must be between 0 and 15")
    address = address | (row << 5)

    return address

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
                    "PeriCfg1": {
                        "offset": 0x0001,
                        "default": 0x98,
                    },
                    "PeriCfg2": {
                        "offset": 0x0002,
                        "default": 0x29,
                    },
                    "PeriCfg3": {
                        "offset": 0x0003,
                        "default": 0x18,
                    },
                    "PeriCfg4": {
                        "offset": 0x0004,
                        "default": 0x21,
                    },
                    "PeriCfg5": {
                        "offset": 0x0005,
                        "default": 0x00,
                    },
                    "PeriCfg6": {
                        "offset": 0x0006,
                        "default": 0x03,
                    },
                    "PeriCfg7": {
                        "offset": 0x0007,
                        "default": 0xA3,
                    },
                    "PeriCfg8": {
                        "offset": 0x0008,
                        "default": 0xE3,
                    },
                    "PeriCfg9": {
                        "offset": 0x0009,
                        "default": 0xE3,
                    },
                    "PeriCfg10": {
                        "offset": 0x000A,
                        "default": 0xD0,
                    },
                    "PeriCfg11": {
                        "offset": 0x000B,
                        "default": 0x10,
                    },
                    "PeriCfg12": {
                        "offset": 0x000C,
                        "default": 0x00,
                    },
                    "PeriCfg13": {
                        "offset": 0x000D,
                        "default": 0x80,
                    },
                    "PeriCfg14": {
                        "offset": 0x000E,
                        "default": 0xF0,
                    },
                    "PeriCfg15": {
                        "offset": 0x000F,
                        "default": 0x60,
                    },
                    "PeriCfg16": {
                        "offset": 0x0010,
                        "default": 0x90,
                    },
                    "PeriCfg17": {
                        "offset": 0x0011,
                        "default": 0x98,
                    },
                    "PeriCfg18": {
                        "offset": 0x0012,
                        "default": 0x00,
                    },
                    "PeriCfg19": {
                        "offset": 0x0013,
                        "default": 0x56,
                    },
                    "PeriCfg20": {
                        "offset": 0x0014,
                        "default": 0x40,
                    },
                    "PeriCfg21": {
                        "offset": 0x0015,
                        "default": 0x2C,
                    },
                    "PeriCfg22": {
                        "offset": 0x0016,
                        "default": 0x00,
                    },
                    "PeriCfg23": {
                        "offset": 0x0017,
                        "default": 0x00,
                    },
                    "PeriCfg24": {
                        "offset": 0x0018,
                        "default": 0x00,
                    },
                    "PeriCfg25": {
                        "offset": 0x0019,
                        "default": 0x00,
                    },
                    "PeriCfg26": {
                        "offset": 0x001A,
                        "default": 0xC5,
                    },
                    "PeriCfg27": {
                        "offset": 0x001B,
                        "default": 0x8C,
                    },
                    "PeriCfg28": {
                        "offset": 0x001C,
                        "default": 0xC7,
                    },
                    "PeriCfg29": {
                        "offset": 0x001D,
                        "default": 0xAC,
                    },
                    "PeriCfg30": {
                        "offset": 0x001E,
                        "default": 0xBB,
                    },
                    "PeriCfg31": {
                        "offset": 0x001F,
                        "default": 0x0B,
                    },
                }
            },
            "Peripheral Status": {  # Register Block
                "Base Address": 0x0100,
                "Registers": {
                    "PeriSta0": {
                        "offset": 0x0000,
                        "default": 0x00
                    },
                    "PeriSta1": {
                        "offset": 0x0001,
                        "default": 0x00
                    },
                    "PeriSta2": {
                        "offset": 0x0002,
                        "default": 0x00
                    },
                    "PeriSta3": {
                        "offset": 0x0003,
                        "default": 0x00
                    },
                    "PeriSta4": {
                        "offset": 0x0004,
                        "default": 0x00
                    },
                    "PeriSta5": {
                        "offset": 0x0005,
                        "default": 0x00
                    },
                    "PeriSta6": {
                        "offset": 0x0006,
                        "default": 0x00
                    },
                    "PeriSta7": {
                        "offset": 0x0007,
                        "default": 0x00
                    },
                    "PeriSta8": {
                        "offset": 0x0008,
                        "default": 0x00
                    },
                    "PeriSta9": {
                        "offset": 0x0009,
                        "default": 0x00
                    },
                    "PeriSta10": {
                        "offset": 0x000A,
                        "default": 0x00
                    },
                    "PeriSta11": {
                        "offset": 0x000B,
                        "default": 0x00
                    },
                    "PeriSta12": {
                        "offset": 0x000C,
                        "default": 0x00
                    },
                    "PeriSta13": {
                        "offset": 0x000D,
                        "default": 0x00
                    },
                    "PeriSta14": {
                        "offset": 0x000E,
                        "default": 0x00
                    },
                    "PeriSta15": {
                        "offset": 0x000F,
                        "default": 0x00
                    },
                }
            },
            "Pixel Config": {  # Register Block
                "Indexer":{
                    "vars": ["block", "column", "row"],
                    "min": [None,  0,  0],
                    "max": [None, 16, 16],
                    "function": etroc2_column_row_to_base_address,
                },
                "Registers": {
                    "PixCfg0": {
                        "offset": 0x0000,
                        "default": 0x5C,
                    },
                    "PixCfg1": {
                        "offset": 0x0001,
                        "default": 0x06,
                    },
                    "PixCfg2": {
                        "offset": 0x0002,
                        "default": 0x0F,
                    },
                    "PixCfg3": {
                        "offset": 0x0003,
                        "default": 0x05,
                    },
                    "PixCfg4": {
                        "offset": 0x0004,
                        "default": 0x00,
                    },
                    "PixCfg5": {
                        "offset": 0x0005,
                        "default": 0x28,
                    },
                    "PixCfg6": {
                        "offset": 0x0006,
                        "default": 0xC2,
                    },
                    "PixCfg7": {
                        "offset": 0x0007,
                        "default": 0x01,
                    },
                    "PixCfg8": {
                        "offset": 0x0008,
                        "default": 0x81,
                    },
                    "PixCfg9": {
                        "offset": 0x0009,
                        "default": 0xFA,
                    },
                    "PixCfg10": {
                        "offset": 0x000a,
                        "default": 0x10,
                    },
                    "PixCfg11": {
                        "offset": 0x000b,
                        "default": 0x00,
                    },
                    "PixCfg12": {
                        "offset": 0x000c,
                        "default": 0x08,
                    },
                    "PixCfg13": {
                        "offset": 0x000d,
                        "default": 0x02,
                    },
                    "PixCfg14": {
                        "offset": 0x000e,
                        "default": 0x80,
                    },
                    "PixCfg15": {
                        "offset": 0x000f,
                        "default": 0x10,
                    },
                    "PixCfg16": {
                        "offset": 0x0010,
                        "default": 0x00,
                    },
                    "PixCfg17": {
                        "offset": 0x0011,
                        "default": 0x42,
                    },
                    "PixCfg18": {
                        "offset": 0x0012,
                        "default": 0x00,
                    },
                    "PixCfg19": {
                        "offset": 0x0013,
                        "default": 0x20,
                    },
                    "PixCfg20": {
                        "offset": 0x0014,
                        "default": 0x08,
                    },
                    "PixCfg21": {
                        "offset": 0x0015,
                        "default": 0x00,
                    },
                    "PixCfg22": {
                        "offset": 0x0016,
                        "default": 0x42,
                    },
                    "PixCfg23": {
                        "offset": 0x0017,
                        "default": 0x00,
                    },
                    "PixCfg24": {
                        "offset": 0x0018,
                        "default": 0x02,
                    },
                    "PixCfg25": {
                        "offset": 0x0019,
                        "default": 0x00,
                    },
                    "PixCfg26": {
                        "offset": 0x001a,
                        "default": 0x00,
                    },
                    "PixCfg27": {
                        "offset": 0x001b,
                        "default": 0x00,
                    },
                    "PixCfg28": {
                        "offset": 0x001c,
                        "default": 0x00,
                    },
                    "PixCfg29": {
                        "offset": 0x001d,
                        "default": 0x00,
                    },
                    "PixCfg30": {
                        "offset": 0x001e,
                        "default": 0x00,
                    },
                    "PixCfg31": {
                        "offset": 0x001f,
                        "default": 0x00,
                    },
                },
            },
            "Pixel Status": {  # Register Block
                "Indexer":{
                    "vars": ["block", "column", "row"],
                    "min": [None,  0,  0],
                    "max": [None, 16, 16],
                    "function": etroc2_column_row_to_base_address,
                },
                "Registers": {
                    "PixSta0": {
                        "offset": 0x0000,
                        "default": 0x00
                    },
                    "PixSta1": {
                        "offset": 0x0001,
                        "default": 0x00
                    },
                    "PixSta2": {
                        "offset": 0x0002,
                        "default": 0x00
                    },
                    "PixSta3": {
                        "offset": 0x0003,
                        "default": 0x00
                    },
                    "PixSta4": {
                        "offset": 0x0004,
                        "default": 0x00
                    },
                    "PixSta5": {
                        "offset": 0x0005,
                        "default": 0x00
                    },
                    "PixSta6": {
                        "offset": 0x0006,
                        "default": 0x00
                    },
                    "PixSta7": {
                        "offset": 0x0007,
                        "default": 0x00
                    },
                }
            },
        }
    },
    "Waveform Sampler": {  # Address Space
        "Memory Size": 10,
        "Register Blocks": {
        }
    }
}

register_decoding = {
    "ETROC2": {  # Address Space (i.e. separate I2C memory spaces)
        "Register Blocks":{
            "Peripheral Config": {  # Register Block (i.e. group of registers to be handled as one unit)
                "PLL_ClkGen_disCLK": {
                    "bits": 1,
                    "position": [("PeriCfg0", "0", "0")],  # The tuple should be 1st position is the register, 2nd position the bits in the register, 3rd position the bits in the value
                    "info": "{0} disables the internal clock buffers and ½ clock divider in prescaler, active high. Debugging use only.\nWhen {0} is high, all output clocks are disabled.",
                    "show_binary": False
                },
                "PLL_ClkGen_disDES": {
                    "bits": 1,
                    "position": [("PeriCfg0", "1", "0")],
                    "info": "{0} disables output clocks for deserializer, active high. Debugging use only.\nWhen {0} is high, the following clocks are disabled:\n - clk2g56Qp\n - clk2g56Qn\n - clk2g56Ip\n - clk2g56In\n(clk2g56Q is the 2.56 GHz clock for test in ETROC_PLL. clk2g56Q is used as Waveform Sampler clock in ETROC2)",
                    "show_binary": False
                },
                "PLL_ClkGen_disEOM": {
                    "bits": 1,
                    "position": [("PeriCfg0", "2", "0")],
                    "info": "{0} disables output clocks for EOM. Debugging use only.\nWhen {0} is high, the following clocks are disabled:\n - clk5g12EOMp\n - clk5g12EOMn",
                    "show_binary": False
                },
                "PLL_ClkGen_disSER": {
                    "bits": 1,
                    "position": [("PeriCfg0", "3", "0")],
                    "info": "{0} disables output clocks for serializer, active high. Debugging use only.\nWhen {0} is high, the following clocks are disabled:\n - clk2g56S\n - clk2g56SN\n - clk5g12S\n - clk5g12SN",
                    "show_binary": False
                },
                "PLL_ClkGen_disVCO": {
                    "bits": 1,
                    "position": [("PeriCfg0", "4", "0")],
                    "info": "{0} disables VCO output buffer (associated with clk5g12lshp, clk5g12lshn), active high. clk5g12lsh is the output clock of the first input buffer in prescaler, and the source clock for all output clocks. Once disabled, all output clocks are disabled. Debugging use only.",
                    "show_binary": False
                },
                "CLKSel": {
                    "bits": 1,
                    "position": [("PeriCfg0", "5", "0")],
                    "info": "{0} selects the PLL clock or off-chip clock for TDC and readout. Debug use only.\n - Low: use off-chip clocks for TDC and readout\n - High: use PLL clocks for TDC and readout",
                    "show_binary": False
                },
                "PLL_FBDiv_clkTreeDisable": {
                    "bits": 1,
                    "position": [("PeriCfg0", "6", "0")],
                    "info": "Disable the feedback divider, active high. Debugging use only.\n - 0b0: all output clocks with different frequencies (40MHz-2.56GHz) are enabled.\n - 0b1 The input clk2G56 from the prescaler and all output clocks are disabled.",
                    "show_binary": False
                },
                "PLL_FBDiv_skip": {
                    "bits": 1,
                    "position": [("PeriCfg0", "7", "0")],
                    "info": "{0} adjusts the phase of the output clk1G28 of the freqPrescaler in the feedback divider (N=64) by one skip from low to high. Debugging use only.",
                    "show_binary": False
                },
                "PLL_BiasGen_CONFIG": {
                    "bits": 4,
                    "position": [("PeriCfg1", "3-0", "3-0")],
                    "info": "Charge pump bias current selection, [0 : 8 : 120] uA. Debugging use only",
                    "show_binary": False
                },
                "PLL_CONFIG_I_PLL": {
                    "bits": 4,
                    "position": [("PeriCfg1", "7-4", "3-0")],
                    "info": "Bias current selection of the I-filter unit cell in PLL mode [0 : 1.1 : 8] uA. Debugging use only.",
                    "show_binary": False
                },
                "PLL_CONFIG_P_PLL": {
                    "bits": 4,
                    "position": [("PeriCfg2", "3-0", "3-0")],
                    "info": "Bias current selection of the P-filter unit cell in PLL mode [0 : 5.46 : 82] uA. Debugging use only.",
                    "show_binary": False
                },
                "PLL_R_CONFIG": {
                    "bits": 4,
                    "position": [("PeriCfg2", "7-4", "3-0")],
                    "info": "Resistor selection of the P-path in PLL mode [R = 1/2 * 79.8k / CONFIG] Ohm. Debugging use only.",
                    "show_binary": False
                },
                "PLL_vcoDAC": {
                    "bits": 4,
                    "position": [("PeriCfg3", "3-0", "3-0")],
                    "info": "Bias current selection of the VCO core [0 : 0.470 : 7.1] mA. Debugging use only.",
                    "show_binary": False
                },
                "PLL_vcoRailMode": {
                    "bits": 1,
                    "position": [("PeriCfg3", "4", "0")],
                    "info": "Output rail-to-rail mode selection of the VCO, active low. Debugging use only.\n - 0b0: rail-to-rail output\n - 0b1: CML output",
                    "show_binary": False
                },
                "PLL_ENABLEPLL": {
                    "bits": 1,
                    "position": [("PeriCfg3", "5", "0")],
                    "info": "Enable PLL mode, active high. Debugging use only.",
                    "show_binary": False
                },
                "VrefGen_PD": {
                    "bits": 1,
                    "position": [("PeriCfg3", "7", "0")],
                    "info": "Power down voltage reference generator, active high.\n - High: the voltage reference generator is down\n - Low: the voltage reference generator is up",
                    "show_binary": False
                },
                "PS_CPCurrent": {
                    "bits": 4,
                    "position": [("PeriCfg4", "3-0", "3-0")],
                    "info": "Charge pump current control bits, range from 0 to 15 uA for charge and discharge. Debugging use only.",
                    "show_binary": False
                },
                "PS_CapRst": {
                    "bits": 1,
                    "position": [("PeriCfg4", "4", "0")],
                    "info": "Reset the control voltage of DLL to power supply, active high. Debugging use only.",
                    "show_binary": False
                },
                "PS_Enable": {
                    "bits": 1,
                    "position": [("PeriCfg4", "5", "0")],
                    "info": "{0} enables DLL, active high. Debugging use only.",
                    "show_binary": False
                },
                "PS_ForceDown": {
                    "bits": 1,
                    "position": [("PeriCfg4", "6", "0")],
                    "info": "Force to pull down the output of the phase detector, active high. Debugging use only.",
                    "show_binary": False
                },
                "TS_PD": {
                    "bits": 1,
                    "position": [("PeriCfg4", "7", "0")],
                    "info": "Power down the temperature sensor, active high.\n - High: the temperature sensor is down\n - Low: the temperature sensor is up",
                    "show_binary": False
                },
                "PS_PhaseAdj": {
                    "bits": 8,
                    "position": [("PeriCfg5", "7-0", "7-0")],
                    "info": "Phase selecting control bits, {0}[7:3] for coarse, {0}[2:0] for fine",
                    "show_binary": False
                },
                "RefStrSel": {
                    "bits": 8,
                    "position": [("PeriCfg6", "7-0", "7-0")],
                    "info": "TDC reference strobe selection",
                    "show_binary": False
                },
                "CLK40_EnRx": {
                    "bits": 1,
                    "position": [("PeriCfg7", "0", "0")],
                    "info": "Enable the Rx for the 40 MHz reference clock, active high.",
                    "show_binary": False
                },
                "CLK40_EnTer": {
                    "bits": 1,
                    "position": [("PeriCfg7", "1", "0")],
                    "info": "Enable internal termination of the Rx for the 40 MHz reference clock, active high.",
                    "show_binary": False
                },
                "CLK40_Equ": {
                    "bits": 2,
                    "position": [("PeriCfg7", "3-2", "1-0")],
                    "info": "Equalization strength of the Rx for the 40 MHz reference clock.\n - 0b00: equalization is turned off\n - 0b11: maximal equalization",
                    "show_binary": "New Line"
                },
                "CLK40_InvData": {
                    "bits": 1,
                    "position": [("PeriCfg7", "4", "0")],
                    "info": "Inverting data of the Rx for the 40 MHz reference clock, active high.",
                    "show_binary": False
                },
                "CLK40_SetCM": {
                    "bits": 1,
                    "position": [("PeriCfg7", "5", "0")],
                    "info": "Set common voltage of the Rx for the 40 MHz reference clock to ½ vdd, active high.",
                    "show_binary": False
                },
                "GRO_Start": {
                    "bits": 1,
                    "position": [("PeriCfg7", "6", "0")],
                    "info": "GROStart, active high",
                    "show_binary": False
                },
                "GRO_TOARST_N": {
                    "bits": 1,
                    "position": [("PeriCfg7", "7", "0")],
                    "info": "GRO TOA reset, active low",
                    "show_binary": False
                },
                "CLK1280_EnRx": {
                    "bits": 1,
                    "position": [("PeriCfg8", "0", "0")],
                    "info": "Enable the Rx for the 1.26 GHz clock, active high.",
                    "show_binary": False
                },
                "CLK1280_EnTer": {
                    "bits": 1,
                    "position": [("PeriCfg8", "1", "0")],
                    "info": "Enable the internal termination of the Rx for the 1.28 GHz clock, active high.",
                    "show_binary": False
                },
                "CLK1280_Equ": {
                    "bits": 2,
                    "position": [("PeriCfg8", "3-2", "1-0")],
                    "info": "Equalization strength of the Rx for the 1.28 GHz clock.\n - 0b00: equalization is turned off\n - 0b11: maximal equalization",
                    "show_binary": "New Line"
                },
                "CLK1280_InvData": {
                    "bits": 1,
                    "position": [("PeriCfg8", "4", "0")],
                    "info": "Inverting data of the Rx for the 1.28 GHz clock, active high.",
                    "show_binary": False
                },
                "CLK1280_SetCM": {
                    "bits": 1,
                    "position": [("PeriCfg8", "5", "0")],
                    "info": "Set common voltage of the Rx for the 1.28 GHz clock to  ½ vdd, active high.",
                    "show_binary": False
                },
                "GRO_TOA_CK": {
                    "bits": 1,
                    "position": [("PeriCfg8", "6", "0")],
                    "info": "GRO TOA clock",
                    "show_binary": False
                },
                "GRO_TOA_Latch": {
                    "bits": 1,
                    "position": [("PeriCfg8", "7", "0")],
                    "info": "GRO TOA latch clock",
                    "show_binary": False
                },
                "FC_EnRx": {
                    "bits": 1,
                    "position": [("PeriCfg9", "0", "0")],
                    "info": "Enable the Rx for the fast command, active high.",
                    "show_binary": False
                },
                "FC_EnTer": {
                    "bits": 1,
                    "position": [("PeriCfg9", "1", "0")],
                    "info": "Enable the internal termination of the Rx for the fast command, active high.",
                    "show_binary": False
                },
                "FC_Equ": {
                    "bits": 2,
                    "position": [("PeriCfg9", "3-2", "1-0")],
                    "info": "Equalization strength of the Rx for the fast command.\n - 0b00: equalization is turned off\n - 0b11: maximal equalization",
                    "show_binary": "New Line"
                },
                "FC_InvData": {
                    "bits": 1,
                    "position": [("PeriCfg9", "4", "0")],
                    "info": "Inverting data of the Rx for the fast command, active high",
                    "show_binary": False
                },
                "FC_SetCM": {
                    "bits": 1,
                    "position": [("PeriCfg9", "5", "0")],
                    "info": "Set common voltage of the Rx for the fast command to  ½ vdd, active high.",
                    "show_binary": False
                },
                "GRO_TOTRST_N": {
                    "bits": 1,
                    "position": [("PeriCfg9", "6", "0")],
                    "info": "GRO TOT reset, active low",
                    "show_binary": False
                },
                "GRO_TOT_CK": {
                    "bits": 1,
                    "position": [("PeriCfg9", "7", "0")],
                    "info": "GRO TOT clock",
                    "show_binary": False
                },
                "BCIDoffset": {
                    "bits": 12,
                    "position": [("PeriCfg10", "7-0", "7-0"), ("PeriCfg11", "3-0", "11-8")],
                    "info": "BCID when BCID is reset",
                    "show_binary": False
                },
                "emptySlotBCID": {
                    "bits": 12,
                    "position": [("PeriCfg11", "7-4", "3-0"), ("PeriCfg12", "7-0", "11-4")],
                    "info": "empty BCID slot for synchronization",
                    "show_binary": False
                },
                "readoutClockDelayPixel": {
                    "bits": 5,
                    "position": [("PeriCfg13", "4-0", "4-0")],
                    "info": "Phase delay of pixel readout clock, 780 ps a step",
                    "show_binary": False
                },
                "asyAlignFastcommand": {
                    "bits": 1,
                    "position": [("PeriCfg13", "5", "0")],
                    "info": "Align fastCommand issued by I2C. Initializing the clock phase alignment process at its rising edge (sychronized by the 40 MHz PLL clock)",
                    "show_binary": False
                },
                "asyLinkReset": {
                    "bits": 1,
                    "position": [("PeriCfg13", "6", "0")],
                    "info": "Link reset signal from I2C, active high.",
                    "show_binary": False
                },
                "asyPLLReset": {
                    "bits": 1,
                    "position": [("PeriCfg13", "7", "0")],
                    "info": "Reset PLL from I2C, active low.",
                    "show_binary": False
                },
                "readoutClockWidthPixel": {
                    "bits": 5,
                    "position": [("PeriCfg14", "4-0", "4-0")],
                    "info": "Positive pulse width of pixel clock, 780 ps a step",
                    "show_binary": False
                },
                "asyResetChargeInj": {
                    "bits": 1,
                    "position": [("PeriCfg14", "5", "0")],
                    "info": "Reset charge injection module, active low.",
                    "show_binary": False
                },
                "asyResetFastcommand": {
                    "bits": 1,
                    "position": [("PeriCfg14", "6", "0")],
                    "info": "Reset fastcommand from I2C, active low.",
                    "show_binary": False
                },
                "asyResetGlobalReadout": {
                    "bits": 1,
                    "position": [("PeriCfg14", "7", "0")],
                    "info": "Reset globalReadout module, active low.",
                    "show_binary": False
                },
                "readoutClockDelayGlobal": {
                    "bits": 5,
                    "position": [("PeriCfg15", "4-0", "4-0")],
                    "info": "Phase deloay of global readout clock, 780 ps a step",
                    "show_binary": False
                },
                "asyResetLockDetect": {
                    "bits": 1,
                    "position": [("PeriCfg15", "5", "0")],
                    "info": "Reset lock detect, active low.",
                    "show_binary": False
                },
                "asyStartCalibration": {
                    "bits": 1,
                    "position": [("PeriCfg15", "6", "0")],
                    "info": "Start PLL calibration process, active high.",
                    "show_binary": False
                },
                "readoutClockWidthGlobal": {
                    "bits": 5,
                    "position": [("PeriCfg16", "4-0", "4-0")],
                    "info": "Positive pulse width of global readout clock, 780 ps a step",
                    "show_binary": False
                },
                "LTx_AmplSel": {
                    "bits": 3,
                    "position": [("PeriCfg16", "7-5", "2-0")],
                    "info": "Left Tx amplitude selection.\n - 0b000: min amplitude (50mV)\n - 0b111: max amplitude (320mV)\nStep size is about 40mV",
                    "show_binary": "New Line"
                },
                "chargeInjectionDelay": {
                    "bits": 5,
                    "position": [("PeriCfg17", "4-0", "4-0")],
                    "info": "The charge injection delay to the 40MHz clock rising edge. Start from the rising edge to the 40 MHz clock, each step is 781 ps. The pulse width is fixed to 50 ns",
                    "show_binary": False
                },
                "RTx_AmplSel": {
                    "bits": 3,
                    "position": [("PeriCfg17", "7-5", "2-0")],
                    "info": "Right Tx amplitude selection.\n - 0b000: min amplitude (50mV)\n - 0b111: max amplitude (320mV)\nStep size is about 40mV",
                    "show_binary": "New Line"
                },
                "disPowerSequence": {
                    "bits": 1,
                    "position": [("PeriCfg18", "0", "0")],
                    "info": "{0} disabled the power up sequence, active high.",
                    "show_binary": False
                },
                "softBoot": {
                    "bits": 1,
                    "position": [("PeriCfg18", "1", "0")],
                    "info": "{0} resets the power sequencer controller, active high.",
                    "show_binary": False
                },
                "fcSelfAlignEn": {
                    "bits": 1,
                    "position": [("PeriCfg18", "2", "0")],
                    "info": "Fast command decoder self-alignment mode enable, active high.\n - High: Self-alignment mode enabled\n - Low: manual alignment mode enabled",
                    "show_binary": False
                },
                "fcClkDelayEn": {
                    "bits": 1,
                    "position": [("PeriCfg18", "3", "0")],
                    "info": "Fast command decoder self-alignment mode enable, active high.\n - High: Self-alignment mode enabled\n - Low: manual alignment mode enabled",
                    "show_binary": False
                },
                "fcDataDelayEn": {
                    "bits": 1,
                    "position": [("PeriCfg18", "4", "0")],
                    "info": "Enable data delay in fast command manual alignment mode, active high",
                    "show_binary": False
                },
                "onChipL1AConf": {
                    "bits": 2,
                    "position": [("PeriCfg18", "6-5", "1-0")],
                    "info": "On-chip L1A mode:\n - 0b0x: on-chip L1A disable\n - 0b10: periodic L1A\n - 0b11: random L1A",
                    "show_binary": "New Line"
                },
                "disLTx": {
                    "bits": 1,
                    "position": [("PeriCfg18", "7", "0")],
                    "info": "Left Tx disable, active high",
                    "show_binary": False
                },
                "disScrambler": {
                    "bits": 1,
                    "position": [("PeriCfg19", "0", "0")],
                    "info": "Disable scrambler:\n - Low: scrambler enabled\n - High: scrambler disabled",
                    "show_binary": False
                },
                "linkResetTestPattern": {
                    "bits": 1,
                    "position": [("PeriCfg19", "1", "0")],
                    "info": "Link reset test pattern selection:\n - 0: PRBS\n - 1: fixed pattern",
                    "show_binary": False
                },
                "serRateLeft": {
                    "bits": 2,
                    "position": [("PeriCfg19", "3-2", "1-0")],
                    "info": "Data rate selection of the left data port:\n - 0b00: 320 Mbps\n - 0b01: 640 Mbps\n - 0b10: 1280 Mbps",
                    "show_binary": "New Line"
                },
                "serRateRight": {
                    "bits": 2,
                    "position": [("PeriCfg19", "5-4", "1-0")],
                    "info": "Data rate selection of the right data port:\n - 0b00: 320 Mbps\n - 0b01: 640 Mbps\n - 0b10: 1280 Mbps",
                    "show_binary": "New Line"
                },
                "singlePort": {
                    "bits": 1,
                    "position": [("PeriCfg19", "6", "0")],
                    "info": "Enable single port or both ports:\n - Low: use both left and right serial ports\n - use right serial port only",
                    "show_binary": False
                },
                "disRTx": {
                    "bits": 1,
                    "position": [("PeriCfg19", "7", "0")],
                    "info": "Right Tx disable, active high",
                    "show_binary": False
                },
                "mergeTriggerData": {
                    "bits": 1,
                    "position": [("PeriCfg20", "0", "0")],
                    "info": "Merge trigger and data in a port:\n - Low: trigger and data in separate port, only valid when singlePort os Low\n - High: trigger and data are merged in serial port",
                    "show_binary": False
                },
                "triggerGranularity": {
                    "bits": 3,
                    "position": [("PeriCfg20", "3-1", "2-0")],
                    "info": "The trigger data size varies from 0, 1, 2, 4, 8, 16\n - 0: trigger data size is 0\n - 1: trigger data size is 1",
                    "show_binary": False
                },
                "EFuse_TCKHP": {
                    "bits": 4,
                    "position": [("PeriCfg20", "7-4", "3-0")],
                    "info": "The register controlling the SCLK pulse width, ranges from 3 us to 10 us with step of 0.5us. The default value is 4, corresponding to 5 us pulse width. Debugging use only.",
                    "show_binary": False
                },
                "EFuse_EnClk": {
                    "bits": 1,
                    "position": [("PeriCfg21", "0", "0")],
                    "info": "EFuse clock enable.\n - High: enables the clock of the EFuse controller\n - Low: disables the clock of the EFuse controller",
                    "show_binary": False
                },
                "EFuse_Mode": {
                    "bits": 2,
                    "position": [("PeriCfg21", "2-1", "1-0")],
                    "info": "Operation mode of the eFuse:\n - 0b01: programming mode\n - 0b10: reading mode",
                    "show_binary": False
                },
                "EFuse_Rstn": {
                    "bits": 1,
                    "position": [("PeriCfg21", "3", "0")],
                    "info": "Reset signal of the uFuse controller, active low",
                    "show_binary": False
                },
                "EFuse_Start": {
                    "bits": 1,
                    "position": [("PeriCfg21", "4", "0")],
                    "info": "Start signal of the eFuse programming. A positive pulse will start programming.",
                    "show_binary": False
                },
                "EFuse_Bypass": {
                    "bits": 1,
                    "position": [("PeriCfg21", "5", "0")],
                    "info": "Bypass eFuse\n - 0b0: eFuse output Q[31-0] is output\n - 0b1: eFuse raw data form I2C (EFuse_Prog) is output.",
                    "show_binary": False
                },
                "EFuse_Prog": {
                    "bits": 32,
                    "position": [
                        ("PeriCfg22", "7-0", "7-0"),
                        ("PeriCfg23", "7-0", "15-8"),
                        ("PeriCfg24", "7-0", "23-16"),
                        ("PeriCfg25", "7-0", "31-24"),
                    ],
                    "info": "Data to be written into EFuse",
                    "show_binary": False
                },
                "linkResetFixedPattern": {
                    "bits": 32,
                    "position": [
                        ("PeriCfg26", "7-0", "7-0"),
                        ("PeriCfg27", "7-0", "15-8"),
                        ("PeriCfg28", "7-0", "23-16"),
                        ("PeriCfg29", "7-0", "31-24"),
                    ],
                    "info": "User-specified pattern to be sent during link reset, LSB-first",
                    "show_binary": False
                },
                "lfLockThrCounter": {
                    "bits": 4,
                    "position": [("PeriCfg30", "3-0", "3-0")],
                    "info": "If the number of instantLock is true for 256 (1 << 8) in a row, the PLL is locked in the initial status.",
                    "show_binary": False
                },
                "lfReLockThrCounter": {
                    "bits": 4,
                    "position": [("PeriCfg30", "7-4", "3-0")],
                    "info": "If the number of instatLock is true for 256 (1 << 8) in a row, the PLL is relocked before the unlock status is confirmed.",
                    "show_binary": False
                },
                "lfUnLockThrCounter": {
                    "bits": 4,
                    "position": [("PeriCfg31", "3-0", "3-0")],
                    "info": "If the number of instantLock is false for 256 (1 << 8) in a row, the PLL is unlocked.",
                    "show_binary": False
                },
                "TDCClockTest": {
                    "bits": 1,
                    "position": [("PeriCfg31", "4", "0")],
                    "info": "The TDC clock testing enable.\n - High: sending TDC clock at the left serial port\n - Low: sending left serializer data at the left port",
                    "show_binary": False
                },
                "TDCStrobeTest": {
                    "bits": 1,
                    "position": [("PeriCfg31", "5", "0")],
                    "info": "The TDC reference strobe testing enable.\n - High: sending TDC reference strobe at the right serial port\n - Low: sending right serializer data at the right port",
                    "show_binary": False
                },
            },
            "Peripheral Status": {  # Register Block
                "PS_Lat": {
                    "bits": 1,
                    "position": [("PeriSta0", "7", "0")],
                    "info": "Phase Shifter late",
                    "show_binary": False
                },
                "AFCcalCap": {
                    "bits": 6,
                    "position": [("PeriSta0", "6-1", "5-0")],
                    "info": "AFC capacitance",
                    "show_binary": False
                },
                "AFCBusy": {
                    "bits": 1,
                    "position": [("PeriSta0", "0", "0")],
                    "info": "AFC busy",
                    "show_binary": False
                },
                "fcAlignFinalState": {
                    "bits": 4,
                    "position": [("PeriSta1", "7-4", "3-0")],
                    "info": "fast command alignment FSM state",
                    "show_binary": False
                },
                "controllerState": {
                    "bits": 4,
                    "position": [("PeriSta1", "3-0", "3-0")],
                    "info": "global control FSM",
                    "show_binary": False
                },
                "fcAlignStatus": {
                    "bits": 4,
                    "position": [("PeriSta2", "7-4", "3-0")],
                    "info": "fast command alignment status",
                    "show_binary": False
                },
                "fcBitAlignError": {
                    "bits": 1,
                    "position": [("PeriSta2", "0", "0")],
                    "info": "fast command bit alignment error",
                    "show_binary": False
                },
                "invalidFCCount": {
                    "bits": 12,
                    "position": [("PeriSta4", "3-0", "11-8"), ("PeriSta3", "7-0", "7-0")],
                    "info": "?",
                    "show_binary": False
                },
                "pllUnlockCount": {
                    "bits": 12,
                    "position": [("PeriSta5", "7-0", "11-4"), ("PeriSta4", "7-4", "3-0")],
                    "info": "?",
                    "show_binary": False
                },
                "EFuseQ": {
                    "bits": 32,
                    "position": [
                        ("PeriSta9", "7-0", "31-24"),
                        ("PeriSta8", "7-0", "23-16"),
                        ("PeriSta7", "7-0", "15-8"),
                        ("PeriSta6", "7-0", "7-0"),
                    ],
                    "info": "32-bit EFuse output",
                    "show_binary": False
                },
            },
            "Pixel Config": {  # Register Block
            },
            "Pixel Status": {  # Register Block
            },
        }
    }
}

class ETROC2_Chip(Base_Chip):

    _indexer_info = {
        "vars": ["block", "column", "row", "broadcast"],
        "min": [None,  0,  0, 0],
        "max": [None, 16, 16, 1],
    }

    def __init__(self, parent: GUI_Helper, i2c_controller: Connection_Controller):
        super().__init__(
            parent=parent,
            chip_name="ETROC2",
            i2c_controller=i2c_controller,
            register_model=register_model,
            register_decoding=register_decoding,
            indexer_info = self._indexer_info
        )

        self._i2c_address = None
        self._waveform_sampler_i2c_address = None

        self.clear_tab("Empty")
        self.register_tab(
            "Graphical View",
            {
                "canvas": False,
                "builder": self.graphical_interface_builder,
            }
        )
        self.register_tab(
            "Peripheral Registers",
            {
                "canvas": True,
                "builder": self.peripheral_register_builder,
            }
        )
        self.register_tab(
            "Peripheral Decoded",
            {
                "canvas": True,
                "builder": self.peripheral_decoded_builder,
            }
        )
        self.register_tab(
            "Pixel Registers",
            {
                "canvas": True,
                "builder": self.pixel_register_builder,
            }
        )
        self.register_tab(
            "Pixel Decoded",
            {
                "canvas": True,
                "builder": self.pixel_decoded_builder,
            }
        )

        # Set indexer vars callback, so we can update the displayed block array
        self._callback_indexer_var = {}
        for var in self._indexer_vars:
            indexer_var = self._indexer_vars[var]['variable']
            self._callback_indexer_var[var] = indexer_var.trace_add('write', self._update_indexed_vars)

    def _update_indexed_vars(self, var=None, index=None, mode=None):
        #if self._indexer_vars['column']['variable'].get() == "" or self._indexer_vars['row']['variable'].get() == "":
        #    return
        if hasattr(self, "_ETROC2_pixel_config_frame"):
            self._ETROC2_pixel_config_frame.update_array_display_vars()
        if hasattr(self, "_ETROC2_pixel_status_frame"):
            self._ETROC2_pixel_status_frame.update_array_display_vars()
        if hasattr(self, "_ETROC2_pixel_decoded_config_frame"):
            self._ETROC2_pixel_decoded_config_frame.update_array_display_vars()
        if hasattr(self, "_ETROC2_pixel_decoded_status_frame"):
            self._ETROC2_pixel_decoded_status_frame.update_array_display_vars()

    def update_whether_modified(self):
        if self._i2c_address is not None:
            state = self._address_space["ETROC2"].is_modified
        else:
            state = None

        if self._waveform_sampler_i2c_address is not None:
            ws_state = self._address_space["Waveform Sampler"].is_modified
        else:
            ws_state = None

        if state is None and ws_state is None:
            final_state = "Unknown"
        elif ws_state is None:
            final_state = state
        elif state is None:
            final_state = ws_state
        else:
            if state == ws_state:
                final_state = state
            elif state == "Unknown" or ws_state == "Unknown":
                final_state = "Unknown"
            elif state or ws_state:
                final_state = True
            else:
                final_state = False

        if final_state == True:
            final_state = "Modified"
        elif final_state == False:
            final_state = "Unmodified"

        self._parent._local_status_update(final_state)

    def get_indexed_var(self, address_space, block, var_name):
        if address_space in self._register_model and block in self._register_model[address_space]['Register Blocks'] and 'Indexer' in self._register_model[address_space]['Register Blocks'][block]:
            # This is an array block, so for accessing the individual vars we need to modify the block name with the indexing data
            column = self._indexer_vars['column']['variable'].get()
            row = self._indexer_vars['row']['variable'].get()

            if column == "":
                column = "0"
            else:
                column = str(int(column))
            if row == "":
                row = "0"
            else:
                row = str(int(row))

            block_name = block + ":{}:{}".format(column, row)
            return self._address_space[address_space].get_display_var(block_name + "/" + var_name)
        return self._address_space[address_space].get_display_var(block + "/" + var_name)

    #  Since there is the broadcast feature, we can not allow to write a full adress space
    # because the broadcast feature would overwrite previous addresses, so we write in blocks
    # since they do not cover the broadcast range
    def write_all_address_space(self, address_space_name: str):
        if address_space_name == "ETROC2":
            self._logger.info("Writing full address space: {}".format(address_space_name))
            for block in self._register_model[address_space_name]["Register Blocks"]:
                super().write_all_block(address_space_name, block, full_array=True)
        else:
            super().write_all_address_space(address_space_name)


    def config_i2c_address(self, address):
        self._i2c_address = address

        from .address_space_controller import Address_Space_Controller
        if "ETROC2" in self._address_space:
            address_space: Address_Space_Controller = self._address_space["ETROC2"]
            address_space.update_i2c_address(address)
        self.update_whether_modified()

    def config_waveform_sampler_i2c_address(self, address):
        self._waveform_sampler_i2c_address = address

        from .address_space_controller import Address_Space_Controller
        if "Waveform Sampler" in self._address_space:
            address_space: Address_Space_Controller = self._address_space["Waveform Sampler"]
            address_space.update_i2c_address(address)
        self.update_whether_modified()

    def graphical_interface_builder(self, frame: ttk.Frame):
        pass

    def peripheral_register_builder(self, frame: ttk.Frame):
        frame.columnconfigure(100, weight=1)
        columns = 4

        self._ETROC2_peripheral_config_frame = self.build_block_interface(
            element=frame,
            title="Configuration Registers",
            internal_title="Peripheral Configuration Registers",
            button_title="Config",
            address_space="ETROC2",
            block="Peripheral Config",
            col=100,
            row=100,
            register_columns=columns
        )

        self._ETROC2_peripheral_status_frame = self.build_block_interface(
            element=frame,
            title="Status Registers",
            internal_title="Peripheral Status Registers",
            button_title="Status",
            address_space="ETROC2",
            block="Peripheral Status",
            col=100,
            row=200,
            register_columns=columns
        )

    def peripheral_decoded_builder(self, frame: ttk.Frame):
        frame.columnconfigure(100, weight=1)
        columns = 3

        self._ETROC2_peripheral_decoded_config_frame = self.build_decoded_block_interface(
            element=frame,
            title="Configuration Values",
            internal_title="Peripheral Configuration Values",
            button_title="Config",
            address_space="ETROC2",
            block="Peripheral Config",
            col=100,
            row=100,
            value_columns=columns
        )

        self._ETROC2_peripheral_decoded_status_frame = self.build_decoded_block_interface(
            element=frame,
            title="Status Values",
            internal_title="Peripheral Status Values",
            button_title="Status",
            address_space="ETROC2",
            block="Peripheral Status",
            col=100,
            row=200,
            value_columns=columns
        )

    def pixel_register_builder(self, frame: ttk.Frame):
        frame.columnconfigure(100, weight=1)

        self._ETROC2_pixel_control_frame = self.build_block_array_controls(
            control_variables=self._indexer_vars,
            element=frame,
            title="Pixel Selection",
            internal_title="Register Pixel Selection",
            col=100,
            row=100
        )

        columns = 4
        self._ETROC2_pixel_config_frame = self.build_block_array_interface(
            element=frame,
            title="Configuration Registers",
            internal_title="Pixel Configuration Registers",
            button_title="Config",
            address_space="ETROC2",
            block="Pixel Config",
            col=100,
            row=200,
            register_columns=columns
        )

        self._ETROC2_pixel_status_frame = self.build_block_array_interface(
            element=frame,
            title="Status Registers",
            internal_title="Pixel Status Registers",
            button_title="Status",
            address_space="ETROC2",
            block="Pixel Status",
            col=100,
            row=300,
            register_columns=columns
        )

        return

    def pixel_decoded_builder(self, frame: ttk.Frame):
        frame.columnconfigure(100, weight=1)
        columns = 3

        self._ETROC2_pixel_decoded_control_frame = self.build_block_array_controls(
            self._indexer_vars,
            frame,
            "Pixel Selection",
            "Decoded Register Pixel Selection",
            100,
            100
        )

        return

        self._ETROC2_pixel_decoded_config_frame = self.build_decoded_block_interface(
            frame,
            "Configuration Values",
            "Config",
            "ETROC2",
            "Peripheral Config",
            100,
            200,
            columns
        )

        self._ETROC2_pixel_decoded_status_frame = self.build_decoded_block_interface(
            frame,
            "Status Values",
            "Status",
            "ETROC2",
            "Peripheral Status",
            100,
            300,
            columns
        )

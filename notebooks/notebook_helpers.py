#############################################################################
# zlib License
#
# (C) 2023 Zach FLowers, Murtaza Safdari <musafdar@cern.ch>
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
#import visa
import threading
import numpy as np
import os, sys
from queue import Queue
from collections import deque
import queue
import datetime
from tqdm import tqdm
import pandas
import logging
import i2c_gui
import i2c_gui.chips
from i2c_gui.usb_iss_helper import USB_ISS_Helper
from i2c_gui.fpga_eth_helper import FPGA_ETH_Helper
from i2c_gui.chips.etroc2_chip import register_decoding
#========================================================================================#
'''
@author: Zach Flowers, Murtaza Safdari
@date: 2023-03-24
This script is composed of all the helper functions needed for I2C comms, FPGA, etc
'''
#--------------------------------------------------------------------------#

class i2c_connection():
    def __init__(self, port, chip_addresses, chip_names, chip_fc_delays):
        self.chip_addresses = chip_addresses
        self.chip_names = chip_names
        # 2-tuple of binary numbers represented as strings ("0","1")
        # Here "0" is the "fcClkDelayEn" and "1" is the fcDataDelayEn
        self.chip_fc_delays = chip_fc_delays
        i2c_gui.__no_connect__ = False  # Set to fake connecting to an ETROC2 device
        i2c_gui.__no_connect_type__ = "echo"  # for actually testing readback
        #i2c_gui.__no_connect_type__ = "check"  # default behaviour
        ## Logger
        log_level=30
        logging.basicConfig(format='%(asctime)s - %(levelname)s:%(name)s:%(message)s')
        logger = logging.getLogger("Script_Logger")
        self.Script_Helper = i2c_gui.ScriptHelper(logger)
        self.conn = i2c_gui.Connection_Controller(self.Script_Helper)
        self.conn.connection_type = "USB-ISS"
        self.conn.handle: USB_ISS_Helper
        self.conn.handle.port = port
        self.conn.handle.clk = 100
        self.conn.connect()
        logger.setLevel(log_level)

        self.BL_map_THCal = {}
        self.NW_map_THCal = {}
        self.BL_df = {}

    # func_string is an 8-bit binary number, LSB->MSB is function 0->7
    # "0" means don't call the corr function, and vice-versa
    def config_chips(self, func_string = '00000000'):
        for chip_address, chip_name, chip_fc_delay in zip(self.chip_addresses, self.chip_names, self.chip_fc_delays):
            chip = self.get_chip_i2c_connection(chip_address)
            if(int(func_string[-1])): self.pixel_check(chip_address, chip)
            if(int(func_string[-2])): self.basic_peripheral_register_check(chip_address, chip)
            if(int(func_string[-3])): self.set_chip_peripherals(chip_address, chip_fc_delay, chip)
            if(int(func_string[-4])): self.auto_calibration(chip_address, chip_name, chip)
            if(int(func_string[-5])): self.disable_all_pixels(chip_address, chip)
            # if(int(func_string[-6])): self.disable_all_pixels(chip_address, chip)
            
    def enable_pixels_chips(self, pixel_list):
        for chip_address in self.chip_addresses:
            chip = self.get_chip_i2c_connection(chip_address)
            for row,col in pixel_list:
                self.enable_pixel(chip_address, row, col, chip)

    def __del__(self):
        self.conn.disconnect()

    #--------------------------------------------------------------------------#
    ## Useful helper functions to streamline register reading and writing
    def pixel_decoded_register_write(self, decodedRegisterName, data_to_write, chip=None):
        if(chip==None): print("Need chip to access registers!")
        bit_depth = register_decoding["ETROC2"]["Register Blocks"]["Pixel Config"][decodedRegisterName]["bits"]
        handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", decodedRegisterName)
        chip.read_decoded_value("ETROC2", "Pixel Config", decodedRegisterName)
        if len(data_to_write)!=bit_depth: print("Binary data_to_write is of incorrect length for",decodedRegisterName, "with bit depth", bit_depth)
        data_hex_modified = hex(int(data_to_write, base=2))
        if(bit_depth>1): handle.set(data_hex_modified)
        elif(bit_depth==1): handle.set(data_to_write)
        else: print(decodedRegisterName, "!!!ERROR!!! Bit depth <1, how did we get here...")
        chip.write_decoded_value("ETROC2", "Pixel Config", decodedRegisterName)

    def pixel_decoded_register_read(self, decodedRegisterName, key, chip, need_int=False):
        if(chip==None): print("Need chip to access registers!")
        handle = chip.get_decoded_indexed_var("ETROC2", f"Pixel {key}", decodedRegisterName)
        chip.read_decoded_value("ETROC2", f"Pixel {key}", decodedRegisterName)
        if(need_int): return int(handle.get(), base=16)
        else: return handle.get()

    def peripheral_decoded_register_write(self, decodedRegisterName, data_to_write, chip, chip_address=None):
        if(chip==None and chip_address!=None): chip = self.get_chip_i2c_connection(chip_address)
        elif(chip==None and chip_address==None): print("Need either a chip or chip address to access registers!")
        bit_depth = register_decoding["ETROC2"]["Register Blocks"]["Peripheral Config"][decodedRegisterName]["bits"]
        handle = chip.get_decoded_display_var("ETROC2", "Peripheral Config", decodedRegisterName)
        chip.read_decoded_value("ETROC2", "Peripheral Config", decodedRegisterName)
        if len(data_to_write)!=bit_depth: print("Binary data_to_write is of incorrect length for",decodedRegisterName, "with bit depth", bit_depth)
        data_hex_modified = hex(int(data_to_write, base=2))
        if(bit_depth>1): handle.set(data_hex_modified)
        elif(bit_depth==1): handle.set(data_to_write)
        else: print(decodedRegisterName, "!!!ERROR!!! Bit depth <1, how did we get here...")
        chip.write_decoded_value("ETROC2", "Peripheral Config", decodedRegisterName)

    def peripheral_decoded_register_read(self, decodedRegisterName, key, chip, need_int=False, chip_address=None):
        if(chip==None and chip_address!=None): chip = self.get_chip_i2c_connection(chip_address)
        elif(chip==None and chip_address==None): print("Need either a chip or chip address to access registers!")
        handle = chip.get_decoded_display_var("ETROC2", f"Peripheral {key}", decodedRegisterName)
        chip.read_decoded_value("ETROC2", f"Peripheral {key}", decodedRegisterName)
        if(need_int): return int(handle.get(), base=16)
        else: return handle.get()
    #--------------------------------------------------------------------------#

    #--------------------------------------------------------------------------#
    def get_chip_i2c_connection(self, chip_address):
        chip = i2c_gui.chips.ETROC2_Chip(parent=self.Script_Helper, i2c_controller=self.conn)
        chip.config_i2c_address(chip_address)
        # chip.config_waveform_sampler_i2c_address(ws_address)  # Not needed if you do not access WS registers
        # logger.setLevel(log_level)
        return chip
    
    def get_pixel_chip(self, chip_address, row, col):
        chip = self.get_chip_i2c_connection(chip_address)
        row_indexer_handle,_,_ = chip.get_indexer("row")
        column_indexer_handle,_,_ = chip.get_indexer("column")
        row_indexer_handle.set(row)
        column_indexer_handle.set(col)
        return chip
    #--------------------------------------------------------------------------#

    #--------------------------------------------------------------------------#
    # Function 0
    def pixel_check(self, chip_address, chip=None):
        if(chip==None): chip = self.get_chip_i2c_connection(chip_address)
        row_indexer_handle,_,_ = chip.get_indexer("row")
        column_indexer_handle,_,_ = chip.get_indexer("column")
        pixel_flag_fail = False
        for row in range(16):
            for col in range(16):
                column_indexer_handle.set(col)
                row_indexer_handle.set(row)
                fetched_row = self.pixel_decoded_register_read("PixelID-Row", "Status", chip, need_int=True)
                fetched_col = self.pixel_decoded_register_read("PixelID-Col", "Status", chip, need_int=True)
                if(row!=fetched_row or col!=fetched_col):
                    print(chip_address, f"Pixel ({row},{col}) returned ({fetched_row}{fetched_col}), failed consistency check!")
                    pixel_flag_fail = True
        if(not pixel_flag_fail):
            print(f"Passed pixel check for chip: {hex(chip_address)}")

    # Function 1
    def basic_peripheral_register_check(self,chip_address,chip=None):
        if(chip==None): chip = self.get_chip_i2c_connection(chip_address)
        peri_flag_fail = False
        peripheralRegisterKeys = [i for i in range(32)]
        for peripheralRegisterKey in peripheralRegisterKeys:
            # Fetch the register
            handle_PeriCfgX = chip.get_display_var("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
            chip.read_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
            data_bin_PeriCfgX = format(int(handle_PeriCfgX.get(), base=16), '08b')
            # Make the flipped bits
            # data_bin_modified_PeriCfgX = list(data_bin_PeriCfgX)
            data_bin_modified_PeriCfgX = data_bin_PeriCfgX.replace('1', '2').replace('0', '1').replace('2', '0')
            # data_bin_modified_PeriCfgX = ''.join(data_bin_modified_PeriCfgX)
            data_hex_modified_PeriCfgX = hex(int(data_bin_modified_PeriCfgX, base=2))
            # Set the register with the value
            handle_PeriCfgX.set(data_hex_modified_PeriCfgX)
            chip.write_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
            # Perform two reads to verify the persistence of the change
            chip.read_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
            data_bin_new_1_PeriCfgX = format(int(handle_PeriCfgX.get(), base=16), '08b')
            chip.read_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
            data_bin_new_2_PeriCfgX = format(int(handle_PeriCfgX.get(), base=16), '08b')
            # Undo the change to recover the original register value, and check for consistency
            handle_PeriCfgX.set(hex(int(data_bin_PeriCfgX, base=2)))
            chip.write_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
            chip.read_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
            data_bin_recover_PeriCfgX = format(int(handle_PeriCfgX.get(), base=16), '08b')
            # Handle what we learned from the tests
            # print(f"PeriCfg{peripheralRegisterKey:2}", data_bin_PeriCfgX, "To", data_bin_new_1_PeriCfgX,  "To", data_bin_new_2_PeriCfgX, "To", data_bin_recover_PeriCfgX)
            if(data_bin_new_1_PeriCfgX!=data_bin_new_2_PeriCfgX or data_bin_new_2_PeriCfgX!=data_bin_modified_PeriCfgX or data_bin_recover_PeriCfgX!=data_bin_PeriCfgX): 
                print(f"{chip_address}, PeriCfg{peripheralRegisterKey:2}", "FAILURE")
                peri_flag_fail = True
        if(not peri_flag_fail):
            print(f"Passed peripheral write check for chip: {hex(chip_address)}")

    # Function 2
    def set_chip_peripherals(self, chip_address, chip_fc_delay, chip=None):
        if(chip==None): chip = self.get_chip_i2c_connection(chip_address)
        self.peripheral_decoded_register_write("EFuse_Prog", format(0x00017f0f, '032b'), chip)     # chip ID
        self.peripheral_decoded_register_write("singlePort", '1', chip)                            # Set data output to right port only
        self.peripheral_decoded_register_write("serRateLeft", '00', chip)                          # Set Data Rates to 320 mbps
        self.peripheral_decoded_register_write("serRateRight", '00', chip)                         # ^^
        self.peripheral_decoded_register_write("onChipL1AConf", '00', chip)                        # Switches off the onboard L1A
        self.peripheral_decoded_register_write("PLL_ENABLEPLL", '1', chip)                         # "Enable PLL mode, active high. Debugging use only."
        self.peripheral_decoded_register_write("chargeInjectionDelay", format(0x0a, '05b'), chip)  # User tunable delay of Qinj pulse
        self.peripheral_decoded_register_write("triggerGranularity", format(0x01, '03b'), chip)    # only for trigger bit
        ## "0" means disable
        ## "1" means enable
        self.peripheral_decoded_register_write("fcClkDelayEn", chip_fc_delay[0], chip)
        self.peripheral_decoded_register_write("fcDataDelayEn", chip_fc_delay[1], chip)
        print(f"Peripherals set for chip: {hex(chip_address)}")

    # Function 3
    def auto_calibration(self, chip_address, chip_name, chip=None):
        # Reset the maps
        BL_map_THCal = np.zeros((16,16))
        NW_map_THCal = np.zeros((16,16))
        if(chip==None): chip = self.get_chip_i2c_connection(chip_address)
        row_indexer_handle,_,_ = chip.get_indexer("row")
        column_indexer_handle,_,_ = chip.get_indexer("column")
        data = []
        # Loop for threshold calibration
        for row in tqdm(range(16), desc=" row", position=0):
            for col in tqdm(range(16), desc=" col", position=1, leave=False):
            # for index,row,col in zip(tqdm(range(16)), row_list, col_list):
                column_indexer_handle.set(col)
                row_indexer_handle.set(row)
                # Maybe required to make this work
                # self.pixel_decoded_register_write("enable_TDC", "0", chip)
                # self.pixel_decoded_register_write("testMode_TDC", "0", chip)
                # Enable THCal clock and buffer, disable bypass
                self.pixel_decoded_register_write("CLKEn_THCal", "1", chip)
                self.pixel_decoded_register_write("BufEn_THCal", "1", chip)
                self.pixel_decoded_register_write("Bypass_THCal", "0", chip)
                self.pixel_decoded_register_write("TH_offset", format(0x07, '06b'), chip)
                # Reset the calibration block (active low)
                self.pixel_decoded_register_write("RSTn_THCal", "0", chip)
                self.pixel_decoded_register_write("RSTn_THCal", "1", chip)
                # Start and Stop the calibration, (25ns x 2**15 ~ 800 us, ACCumulator max is 2**15)
                self.pixel_decoded_register_write("ScanStart_THCal", "1", chip)
                self.pixel_decoded_register_write("ScanStart_THCal", "0", chip)
                # Check the calibration done correctly
                if(self.pixel_decoded_register_read("ScanDone", "Status", chip)!="1"): print("!!!ERROR!!! Scan not done!!!")
                BL_map_THCal[row, col] = self.pixel_decoded_register_read("BL", "Status", chip, need_int=True)
                NW_map_THCal[row, col] = self.pixel_decoded_register_read("NW", "Status", chip, need_int=True)
                data += [{
                    'col': col,
                    'row': row,
                    'baseline': BL_map_THCal[row, col],
                    'noise_width': NW_map_THCal[row, col],
                    'timestamp': datetime.datetime.now(),
                    'chip_name': chip_name,
                }]
                # Disable clock and buffer before charge injection 
                self.pixel_decoded_register_write("CLKEn_THCal", "0", chip) 
                self.pixel_decoded_register_write("BufEn_THCal", "0", chip)
                # Set Charge Inj Q to 15 fC
                self.pixel_decoded_register_write("QSel", format(0x0e, '05b'), chip)
                # Set Th Offset to 12
                self.pixel_decoded_register_write("TH_offset", format(0x0c, '06b'), chip) 
                # Set DAC to max
                self.pixel_decoded_register_write("Bypass_THCal", "1", chip)
                self.pixel_decoded_register_write("DAC", format(0x3ff, '010b'), chip)
        BL_df = pandas.DataFrame(data = data)
        self.BL_map_THCal[chip_address] = BL_map_THCal
        self.NW_map_THCal[chip_address] = NW_map_THCal
        self.BL_df[chip_address] = BL_df
        print(f"Auto calibration finished for chip: {hex(chip_address)}")
    
    def get_auto_cal_maps(self, chip_address):
        return self.BL_map_THCal[chip_address],self.NW_map_THCal[chip_address],self.BL_df[chip_address]

    # Function 4
    def disable_all_pixels(self, chip_address, chip=None):
        if(chip==None): chip = self.get_chip_i2c_connection(chip_address)
        row_indexer_handle,_,_ = chip.get_indexer("row")
        column_indexer_handle,_,_ = chip.get_indexer("column")
        for row in tqdm(range(16), desc=" row", position=0):
            for col in tqdm(range(16), desc=" col", position=1, leave=False):
                column_indexer_handle.set(col)
                row_indexer_handle.set(row)
                self.pixel_decoded_register_write("disDataReadout", "1", chip)
                self.pixel_decoded_register_write("QInjEn", "0", chip)
                self.pixel_decoded_register_write("disTrigPath", "1", chip)
                ## Release trigger and data range
                self.pixel_decoded_register_write("upperTOATrig", format(0x3ff, '010b'), chip)
                self.pixel_decoded_register_write("lowerTOATrig", format(0x000, '010b'), chip)
                self.pixel_decoded_register_write("upperTOTTrig", format(0x1ff, '09b'), chip)
                self.pixel_decoded_register_write("lowerTOTTrig", format(0x000, '09b'), chip)
                self.pixel_decoded_register_write("upperCalTrig", format(0x3ff, '010b'), chip)
                self.pixel_decoded_register_write("lowerCalTrig", format(0x000, '010b'), chip)
                self.pixel_decoded_register_write("upperTOA", format(0x3ff, '010b'), chip)
                self.pixel_decoded_register_write("lowerTOA", format(0x000, '010b'), chip)
                self.pixel_decoded_register_write("upperTOT", format(0x1ff, '09b'), chip)
                self.pixel_decoded_register_write("lowerTOT", format(0x000, '09b'), chip)
                self.pixel_decoded_register_write("upperCal", format(0x3ff, '010b'), chip)
                self.pixel_decoded_register_write("lowerCal", format(0x000, '010b'), chip)
        print(f"Disabled pixels for chip: {hex(chip_address)}")
    #--------------------------------------------------------------------------#

    #--------------------------------------------------------------------------#
    def enable_pixel(self, chip_address, row, col, chip=None):
        if(chip==None): chip = self.get_chip_i2c_connection(chip_address)
        row_indexer_handle,_,_ = chip.get_indexer("row")
        column_indexer_handle,_,_ = chip.get_indexer("column")
        print(f"Enabling Pixel ({row},{col}) for chip {hex(chip_address)}")
        column_indexer_handle.set(col)
        row_indexer_handle.set(row)
        self.pixel_decoded_register_write("Bypass_THCal", "0", chip)      
        # self.pixel_decoded_register_write("TH_offset", format(0x0c, '06b'), chip)  # Offset used to add to the auto BL for real triggering
        # self.pixel_decoded_register_write("QSel", format(0x0e, '05b'), chip)       # Ensure we inject 15 fC of charge
        self.pixel_decoded_register_write("disDataReadout", "0", chip)             # ENable readout
        self.pixel_decoded_register_write("QInjEn", "1", chip)                     # ENable charge injection for the selected pixel
        self.pixel_decoded_register_write("L1Adelay", format(0x01f5, '09b'), chip) # Change L1A delay - circular buffer in ETROC2 pixel
        self.pixel_decoded_register_write("disTrigPath", "0", chip)                # Enable trigger path

    def onchipL1A(self, chip_address, chip=None, comm='00'):
        if(chip==None): chip = self.get_chip_i2c_connection(chip_address)
        self.peripheral_decoded_register_write("onChipL1AConf", comm, chip)
        print(f"OnChipL1A action {comm} done for chip: {hex(chip_address)}")

    def asyAlignFastcommand(self, chip_address, chip=None):
        if(chip==None): chip = self.get_chip_i2c_connection(chip_address)
        self.peripheral_decoded_register_write("asyAlignFastcommand", "1")
        self.peripheral_decoded_register_write("asyAlignFastcommand", "0")
        print(f"asyAlignFastcommand action done for chip: {hex(chip_address)}")
    #--------------------------------------------------------------------------#

    

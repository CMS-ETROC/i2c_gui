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
import pickle
from pathlib import Path
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

## TODO DEL CHIP OBJECTS AND HANDLER OBJECTS
## TODO Broadcast function check

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
        for chip_address in chip_addresses:
            self.BL_map_THCal[chip_address] = np.zeros((16,16))
            self.NW_map_THCal[chip_address] = np.zeros((16,16))
            self.BL_df[chip_address] = []

    # func_string is an 8-bit binary number, LSB->MSB is function 0->7
    # "0" means don't call the corr function, and vice-versa
    def config_chips(self, func_string = '00000000'):
        for chip_address, chip_name, chip_fc_delay in zip(self.chip_addresses, self.chip_names, self.chip_fc_delays):
            chip = self.get_chip_i2c_connection(chip_address)
            if(int(func_string[-1])): self.pixel_check(chip_address, chip)
            if(int(func_string[-2])): self.basic_peripheral_register_check(chip_address, chip)
            if(int(func_string[-3])): self.set_chip_peripherals(chip_address, chip_fc_delay, chip)
            if(int(func_string[-4])): self.disable_all_pixels(chip_address, chip)
            if(int(func_string[-5])): self.auto_calibration(chip_address, chip_name, chip)
            if(int(func_string[-6])): self.auto_calibration_and_disable(chip_address, chip)
            if(int(func_string[-7])): pass
            if(int(func_string[-8])): pass
            del chip
            
    def enable_select_pixels_in_chips(self, pixel_list, QInjEn=True, Bypass_THCal=False, triggerWindow=True, cbWindow=True, verbose=True):
        for chip_address in self.chip_addresses:
            chip = self.get_chip_i2c_connection(chip_address)
            row_indexer_handle,_,_ = chip.get_indexer("row")
            column_indexer_handle,_,_ = chip.get_indexer("column")
            for row,col in pixel_list:
                self.enable_pixel_modular(row=row, col=col, verbose=verbose, chip_address=chip_address, chip=chip, row_indexer_handle=row_indexer_handle, column_indexer_handle=column_indexer_handle, QInjEn=QInjEn, Bypass_THCal=Bypass_THCal, triggerWindow=triggerWindow, cbWindow=cbWindow)
            del chip, row_indexer_handle, column_indexer_handle

    def enable_all_pixels(self, chip_address, chip=None, QInjEn=True, Bypass_THCal=False, triggerWindow=True, cbWindow=True, verbose=False):
        del_chip = False
        if(chip==None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip = True
        row_indexer_handle,_,_ = chip.get_indexer("row")
        column_indexer_handle,_,_ = chip.get_indexer("column")
        for row in tqdm(range(16), desc="Enabling row", position=0):
            for col in range(16):
                self.enable_pixel_modular(row=row, col=col, verbose=verbose, chip_address=chip_address, chip=chip, row_indexer_handle=row_indexer_handle, column_indexer_handle=column_indexer_handle, QInjEn=QInjEn, Bypass_THCal=Bypass_THCal, triggerWindow=triggerWindow, cbWindow=cbWindow)
        # Delete created components
        if(del_chip): del chip
        del row_indexer_handle, column_indexer_handle
        print(f"Enabled pixels for chip: {hex(chip_address)}")

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
        del_chip = False
        if(chip==None and chip_address!=None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip = True
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
        if(del_chip): del chip

    def peripheral_decoded_register_read(self, decodedRegisterName, key, chip, need_int=False, chip_address=None):
        del_chip = False
        if(chip==None and chip_address!=None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip = True
        elif(chip==None and chip_address==None): print("Need either a chip or chip address to access registers!")
        handle = chip.get_decoded_display_var("ETROC2", f"Peripheral {key}", decodedRegisterName)
        chip.read_decoded_value("ETROC2", f"Peripheral {key}", decodedRegisterName)
        value_to_return = handle.get()
        if(del_chip): del chip
        if(need_int): return int(value_to_return, base=16)
        else: return value_to_return
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
        del_chip = False
        if(chip==None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
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
        # Delete created components
        if(del_chip): del chip

    # Function 1
    def basic_peripheral_register_check(self,chip_address,chip=None):
        del_chip = False
        if(chip==None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
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
        # Delete created components
        if(del_chip): del chip
        del peripheralRegisterKeys

    # Function 2
    def set_chip_peripherals(self, chip_address, chip_fc_delay, chip=None):
        del_chip = False
        if(chip==None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
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
        # Delete created components
        if(del_chip): del chip
        print(f"Peripherals set for chip: {hex(chip_address)}")

    # Function 3
    def disable_all_pixels(self, chip_address, chip=None):
        del_chip = False
        if(chip==None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
        row_indexer_handle,_,_ = chip.get_indexer("row")
        column_indexer_handle,_,_ = chip.get_indexer("column")
        column_indexer_handle.set(0)
        row_indexer_handle.set(0)
        broadcast_handle,_,_ = chip.get_indexer("broadcast")
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("disDataReadout", "1", chip)
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("QInjEn", "0", chip)
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("disTrigPath", "1", chip)
        ## Close the trigger and data windows
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("upperTOATrig", format(0x000, '010b'), chip)
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("lowerTOATrig", format(0x000, '010b'), chip)
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("upperTOTTrig", format(0x1ff, '09b'), chip)
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("lowerTOTTrig", format(0x1ff, '09b'), chip)
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("upperCalTrig", format(0x3ff, '010b'), chip)
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("lowerCalTrig", format(0x3ff, '010b'), chip)
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("upperTOA", format(0x000, '010b'), chip)
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("lowerTOA", format(0x000, '010b'), chip)
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("upperTOT", format(0x1ff, '09b'), chip)
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("lowerTOT", format(0x1ff, '09b'), chip)
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("upperCal", format(0x3ff, '010b'), chip)
        broadcast_handle.set(True)
        self.pixel_decoded_register_write("lowerCal", format(0x3ff, '010b'), chip)
        # Disable TDC
        self.pixel_decoded_register_write("enable_TDC", "0", chip)
        # Broadcase self consistency check
        upperTOT = self.pixel_decoded_register_read("upperTOT", "Config", chip)
        if (upperTOT != "0x1ff"):
            print("Broadcast failed! \n Will manually disable pixels")
            for row in tqdm(range(16), desc="Disabling row", position=0):
                for col in range(16):
                    self.disable_pixel(row=row, col=col, verbose=False, chip_address=None, chip=chip, row_indexer_handle=row_indexer_handle, column_indexer_handle=column_indexer_handle)
        if(del_chip): del chip
        del row_indexer_handle, column_indexer_handle
        print(f"Disabled pixels for chip: {hex(chip_address)}")

    # Function 4
    def auto_calibration(self, chip_address, chip_name, chip=None):
        del_chip = False
        if(chip==None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
        row_indexer_handle,_,_ = chip.get_indexer("row")
        column_indexer_handle,_,_ = chip.get_indexer("column")
        data = []
        # Loop for threshold calibration
        for row in tqdm(range(16), desc="Calibrating row", position=0):
            for col in range(16):
                self.auto_cal_pixel(chip_name=chip_name, row=row, col=col, verbose=False, chip_address=chip_address, chip=chip, data=data, row_indexer_handle=row_indexer_handle, column_indexer_handle=column_indexer_handle)
        BL_df = pandas.DataFrame(data = data)
        self.BL_df[chip_address] = BL_df
        # Delete created components
        if(del_chip): del chip
        del row_indexer_handle, column_indexer_handle, data, BL_df
        print(f"Auto calibration finished for chip: {hex(chip_address)}")
    
    def get_auto_cal_maps(self, chip_address):
        return self.BL_map_THCal[chip_address],self.NW_map_THCal[chip_address],self.BL_df[chip_address]

    def save_auto_cal_BL_map(self, chip_address, chip_name, user_path=""):
        outdir = Path('../ETROC-Data/'+(datetime.date.today().isoformat() + '_Array_Test_Results/')+user_path)
        outdir.mkdir(parents=True,exist_ok=True)
        outfile_BL_map = outdir / (chip_name+"_BL_map.pickle")
        with open(outfile_BL_map,'wb') as f:
            pickle.dump(self.BL_map_THCal[chip_address],f,pickle.HIGHEST_PROTOCOL)
    
    def save_auto_cal_NW_map(self, chip_address, chip_name, user_path=""):
        outdir = Path('../ETROC-Data/'+(datetime.date.today().isoformat() + '_Array_Test_Results/')+user_path)
        outdir.mkdir(parents=True,exist_ok=True)
        outfile_NW_map = outdir / (chip_name+"_NW_map.pickle")
        with open(outfile_NW_map,'wb') as f:
            pickle.dump(self.NW_map_THCal[chip_address],f,pickle.HIGHEST_PROTOCOL)

    def save_auto_cal_BL_df(self, chip_address, chip_name, user_path=""):
        outdir = Path('../ETROC-Data/'+(datetime.date.today().isoformat() + '_Array_Test_Results')+user_path)
        outdir.mkdir(parents=True,exist_ok=True)
        outfile_BL_df = outdir / (chip_name+"_BL_df.pickle")
        with open(outfile_BL_df,'wb') as f:
            pickle.dump(self.BL_df[chip_address],f,pickle.HIGHEST_PROTOCOL)

    def load_auto_cal_BL_map(self, chip_address, chip_name, user_path=""):
        indir = Path('../ETROC-Data/'+(datetime.date.today().isoformat() + '_Array_Test_Results/')+user_path)
        infile_BL_map = indir / (chip_name+"_BL_map.pickle")
        with open(infile_BL_map, 'rb') as f:
            self.BL_map_THCal[chip_address]=pickle.load(f)
    
    def load_auto_cal_NW_map(self, chip_address, chip_name, user_path=""):
        indir = Path('../ETROC-Data/'+(datetime.date.today().isoformat() + '_Array_Test_Results/')+user_path)
        infile_NW_map = indir / (chip_name+"_NW_map.pickle")
        with open(infile_NW_map, 'rb') as f:
            self.NW_map_THCal[chip_address]=pickle.load(f)
    
    def load_auto_cal_BL_df(self, chip_address, chip_name, user_path=""):
        indir = Path('../ETROC-Data/'+(datetime.date.today().isoformat() + '_Array_Test_Results/')+user_path)
        infile_BL_df = indir / (chip_name+"_BL_df.pickle")
        with open(infile_BL_df, 'rb') as f:
            self.BL_df[chip_address]=pickle.load(f)

    def save_auto_cal_maps(self, chip_address, chip_name, user_path=""):
        self.save_auto_cal_BL_map(chip_address, chip_name, user_path)
        self.save_auto_cal_NW_map(chip_address, chip_name, user_path)
        self.save_auto_cal_BL_df(chip_address, chip_name, user_path)
    
    def load_auto_cal_maps(self, chip_address, chip_name, user_path=""):
        self.load_auto_cal_BL_map(chip_address, chip_name, user_path)
        self.load_auto_cal_NW_map(chip_address, chip_name, user_path)
        self.load_auto_cal_BL_df(chip_address, chip_name, user_path)

    # Function 5
    def auto_calibration_and_disable(self, chip_address, chip_name, chip=None):
        del_chip = False
        if(chip==None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip = True
        row_indexer_handle,_,_ = chip.get_indexer("row")
        column_indexer_handle,_,_ = chip.get_indexer("column")
        data = []
        # Loop for threshold calibration
        self.disable_all_pixels(chip_address=chip_address, chip=chip)
        for row in tqdm(range(16), desc="Calibrating and Disabling row", position=0):
            for col in tqdm(range(16), desc=" col", position=1, leave=False):
                # self.disable_pixel(row=row, col=col, verbose=False, chip_address=chip_address, chip=chip, row_indexer_handle=row_indexer_handle, column_indexer_handle=column_indexer_handle)
                self.auto_cal_pixel(chip_name=chip_name, row=row, col=col, verbose=False, chip_address=chip_address, chip=chip, data=data, row_indexer_handle=row_indexer_handle, column_indexer_handle=column_indexer_handle)
        BL_df = pandas.DataFrame(data = data)
        self.BL_df[chip_address] = BL_df
        # Delete created components
        if(del_chip): del chip
        del row_indexer_handle, column_indexer_handle, data, BL_df
        print(f"Auto calibration and Disable Pixel operations finished for chip: {hex(chip_address)}")

    #--------------------------------------------------------------------------#

    def disable_pixel(self, row, col, verbose=False, chip_address=None, chip=None, row_indexer_handle=None, column_indexer_handle=None):
        del_chip = False
        if(chip==None and chip_address!=None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
        elif(chip==None and chip_address==None): 
            print("Need chip address to make a new chip in disable pixel!")
            return
        del_row_handle, del_col_handle = False, False
        if(row_indexer_handle==None):
            row_indexer_handle,_,_ = chip.get_indexer("row")
            del_row_handle = True
        if(column_indexer_handle==None):
            column_indexer_handle,_,_ = chip.get_indexer("column")
            del_col_handle = True
        column_indexer_handle.set(col)
        row_indexer_handle.set(row)
        self.pixel_decoded_register_write("disDataReadout", "1", chip)
        self.pixel_decoded_register_write("QInjEn", "0", chip)
        self.pixel_decoded_register_write("disTrigPath", "1", chip)
        ## Close the trigger and data windows
        self.pixel_decoded_register_write("upperTOATrig", format(0x000, '010b'), chip)
        self.pixel_decoded_register_write("lowerTOATrig", format(0x000, '010b'), chip)
        self.pixel_decoded_register_write("upperTOTTrig", format(0x1ff, '09b'), chip)
        self.pixel_decoded_register_write("lowerTOTTrig", format(0x1ff, '09b'), chip)
        self.pixel_decoded_register_write("upperCalTrig", format(0x3ff, '010b'), chip)
        self.pixel_decoded_register_write("lowerCalTrig", format(0x3ff, '010b'), chip)
        self.pixel_decoded_register_write("upperTOA", format(0x000, '010b'), chip)
        self.pixel_decoded_register_write("lowerTOA", format(0x000, '010b'), chip)
        self.pixel_decoded_register_write("upperTOT", format(0x1ff, '09b'), chip)
        self.pixel_decoded_register_write("lowerTOT", format(0x1ff, '09b'), chip)
        self.pixel_decoded_register_write("upperCal", format(0x3ff, '010b'), chip)
        self.pixel_decoded_register_write("lowerCal", format(0x3ff, '010b'), chip)
        # Disable TDC
        self.pixel_decoded_register_write("enable_TDC", "0", chip)
        # Delete created components
        if(del_chip): del chip
        if(del_row_handle): del row_indexer_handle
        if(del_col_handle): del column_indexer_handle
        if(verbose): print(f"Disabled pixel ({row},{col}) for chip: {hex(chip_address)}")

    # def enable_pixel(self, row, col, verbose=False, chip_address=None, chip=None, row_indexer_handle=None, column_indexer_handle=None):
    #     del_chip = False
    #     if(chip==None and chip_address!=None): 
    #         chip = self.get_chip_i2c_connection(chip_address)
    #         del_chip=True
    #     elif(chip==None and chip_address==None): 
    #         print("Need chip address to make a new chip in disable pixel!")
    #         return
    #     del_row_handle, del_col_handle = False, False
    #     if(row_indexer_handle==None):
    #         row_indexer_handle,_,_ = chip.get_indexer("row")
    #         del_row_handle = True
    #     if(column_indexer_handle==None):
    #         column_indexer_handle,_,_ = chip.get_indexer("column")
    #         del_col_handle = True
    #     column_indexer_handle.set(col)
    #     row_indexer_handle.set(row)
    #     self.pixel_decoded_register_write("disDataReadout", "0", chip)
    #     self.pixel_decoded_register_write("QInjEn", "1", chip)
    #     self.pixel_decoded_register_write("disTrigPath", "0", chip)
    #     self.pixel_decoded_register_write("L1Adelay", format(0x01f5, '09b'), chip) # Change L1A delay - circular buffer in ETROC2 pixel
    #     self.pixel_decoded_register_write("Bypass_THCal", "0", chip)      
    #     self.pixel_decoded_register_write("TH_offset", format(0x0f, '06b'), chip)  # Offset used to add to the auto BL for real triggering
    #     self.pixel_decoded_register_write("QSel", format(0x14, '05b'), chip)       # Ensure we inject 20 fC of charge
    #     ## Open the trigger and data windows
    #     self.TDC_window_pixel(chip_address, row, col, verbose=verbose, chip=chip, row_indexer_handle=row_indexer_handle, column_indexer_handle=column_indexer_handle, alreadySetPixel=True, triggerWindow=True, cbWindow=True)
    #     # Enable TDC
    #     self.pixel_decoded_register_write("enable_TDC", "1", chip)
    #     # Delete created components
    #     if(del_chip): del chip
    #     if(del_row_handle): del row_indexer_handle
    #     if(del_col_handle): del column_indexer_handle
    #     if(verbose): print(f"Enabled pixel ({row},{col}) for chip: {hex(chip_address)}")

    def enable_pixel_modular(self, row, col, verbose=False, chip_address=None, chip=None, row_indexer_handle=None, column_indexer_handle=None, QInjEn=False, Bypass_THCal=False, triggerWindow=True, cbWindow=True):
        del_chip = False
        if(chip==None and chip_address!=None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
        elif(chip==None and chip_address==None): 
            print("Need chip address to make a new chip in disable pixel!")
            return
        del_row_handle, del_col_handle = False, False
        if(row_indexer_handle==None):
            row_indexer_handle,_,_ = chip.get_indexer("row")
            del_row_handle = True
        if(column_indexer_handle==None):
            column_indexer_handle,_,_ = chip.get_indexer("column")
            del_col_handle = True
        column_indexer_handle.set(col)
        row_indexer_handle.set(row)
        self.pixel_decoded_register_write("disDataReadout", "0", chip)
        self.pixel_decoded_register_write("QInjEn", "1" if QInjEn else "0", chip)
        self.pixel_decoded_register_write("disTrigPath", "0", chip)
        self.pixel_decoded_register_write("L1Adelay", format(0x01f5, '09b'), chip) # Change L1A delay - circular buffer in ETROC2 pixel
        self.pixel_decoded_register_write("Bypass_THCal", "1" if Bypass_THCal else "0", chip)      
        self.pixel_decoded_register_write("TH_offset", format(0x0a, '06b'), chip)  # Offset 10 used to add to the auto BL for real triggering
        self.pixel_decoded_register_write("QSel", format(0x1b, '05b'), chip)       # Ensure we inject 27 fC of charge
        self.pixel_decoded_register_write("DAC", format(0x3ff, '010b'), chip)
        ## Open the trigger and data windows
        self.TDC_window_pixel(chip_address, row, col, verbose=verbose, chip=chip, row_indexer_handle=row_indexer_handle, column_indexer_handle=column_indexer_handle, alreadySetPixel=True, triggerWindow=triggerWindow, cbWindow=cbWindow)
        # Enable TDC
        self.pixel_decoded_register_write("enable_TDC", "1", chip)
        # Delete created components
        if(del_chip): del chip
        if(del_row_handle): del row_indexer_handle
        if(del_col_handle): del column_indexer_handle
        if(verbose): print(f"Enabled pixel ({row},{col}) for chip: {hex(chip_address)}")

    # def enable_pixel_triggerbit(self, row, col, verbose=False, chip_address=None, chip=None, row_indexer_handle=None, column_indexer_handle=None):
    #     del_chip = False
    #     if(chip==None and chip_address!=None): 
    #         chip = self.get_chip_i2c_connection(chip_address)
    #         del_chip=True
    #     elif(chip==None and chip_address==None): 
    #         print("Need chip address to make a new chip in disable pixel!")
    #         return
    #     del_row_handle, del_col_handle = False, False
    #     if(row_indexer_handle==None):
    #         row_indexer_handle,_,_ = chip.get_indexer("row")
    #         del_row_handle = True
    #     if(column_indexer_handle==None):
    #         column_indexer_handle,_,_ = chip.get_indexer("column")
    #         del_col_handle = True
    #     column_indexer_handle.set(col)
    #     row_indexer_handle.set(row)
    #     self.pixel_decoded_register_write("disDataReadout", "1", chip)
    #     self.pixel_decoded_register_write("QInjEn", "0", chip)
    #     self.pixel_decoded_register_write("disTrigPath", "0", chip)
    #     self.pixel_decoded_register_write("Bypass_THCal", "1", chip)
    #     self.pixel_decoded_register_write("DAC", format(0x3ff, '010b'), chip)
    #     ## Open the trigger and close data windows
    #     self.TDC_window_pixel(chip_address, row, col, verbose=verbose, chip=chip, row_indexer_handle=row_indexer_handle, column_indexer_handle=column_indexer_handle, alreadySetPixel=True, triggerWindow=True, cbWindow=False)
    #     # Enable TDC
    #     self.pixel_decoded_register_write("enable_TDC", "1", chip)
    #     # Delete created components
    #     if(del_chip): del chip
    #     if(del_row_handle): del row_indexer_handle
    #     if(del_col_handle): del column_indexer_handle
    #     if(verbose): print(f"Enabled pixel ({row},{col}) for chip: {hex(chip_address)}")

    # def enable_pixel_data_qinj(self, row, col, verbose=False, chip_address=None, chip=None, row_indexer_handle=None, column_indexer_handle=None):
    #     del_chip = False
    #     if(chip==None and chip_address!=None): 
    #         chip = self.get_chip_i2c_connection(chip_address)
    #         del_chip=True
    #     elif(chip==None and chip_address==None): 
    #         print("Need chip address to make a new chip in disable pixel!")
    #         return
    #     del_row_handle, del_col_handle = False, False
    #     if(row_indexer_handle==None):
    #         row_indexer_handle,_,_ = chip.get_indexer("row")
    #         del_row_handle = True
    #     if(column_indexer_handle==None):
    #         column_indexer_handle,_,_ = chip.get_indexer("column")
    #         del_col_handle = True
    #     column_indexer_handle.set(col)
    #     row_indexer_handle.set(row)
    #     self.pixel_decoded_register_write("disDataReadout", "0", chip)
    #     self.pixel_decoded_register_write("QInjEn", "1", chip)
    #     self.pixel_decoded_register_write("disTrigPath", "0", chip)
    #     self.pixel_decoded_register_write("L1Adelay", format(0x01f5, '09b'), chip) # Change L1A delay - circular buffer in ETROC2 pixel
    #     self.pixel_decoded_register_write("Bypass_THCal", "1", chip)    
    #     self.pixel_decoded_register_write("DAC", format(0x3ff, '010b'), chip)  
    #     self.pixel_decoded_register_write("QSel", format(0x1b, '05b'), chip)       # Ensure we inject 27 fC of charge
    #     ## Open the trigger and data windows
    #     self.TDC_window_pixel(chip_address, row, col, verbose=verbose, chip=chip, row_indexer_handle=row_indexer_handle, column_indexer_handle=column_indexer_handle, alreadySetPixel=True, triggerWindow=True, cbWindow=True)
    #     # Enable TDC
    #     self.pixel_decoded_register_write("enable_TDC", "1", chip)
    #     # Delete created components
    #     if(del_chip): del chip
    #     if(del_row_handle): del row_indexer_handle
    #     if(del_col_handle): del column_indexer_handle
    #     if(verbose): print(f"Enabled pixel ({row},{col}) for chip: {hex(chip_address)}")
    
    # def enable_pixel_data(self, row, col, verbose=False, chip_address=None, chip=None, row_indexer_handle=None, column_indexer_handle=None):
    #     del_chip = False
    #     if(chip==None and chip_address!=None): 
    #         chip = self.get_chip_i2c_connection(chip_address)
    #         del_chip=True
    #     elif(chip==None and chip_address==None): 
    #         print("Need chip address to make a new chip in disable pixel!")
    #         return
    #     del_row_handle, del_col_handle = False, False
    #     if(row_indexer_handle==None):
    #         row_indexer_handle,_,_ = chip.get_indexer("row")
    #         del_row_handle = True
    #     if(column_indexer_handle==None):
    #         column_indexer_handle,_,_ = chip.get_indexer("column")
    #         del_col_handle = True
    #     column_indexer_handle.set(col)
    #     row_indexer_handle.set(row)
    #     self.pixel_decoded_register_write("disDataReadout", "0", chip)
    #     self.pixel_decoded_register_write("QInjEn", "0", chip)
    #     self.pixel_decoded_register_write("disTrigPath", "0", chip)
    #     self.pixel_decoded_register_write("L1Adelay", format(0x01f5, '09b'), chip) # Change L1A delay - circular buffer in ETROC2 pixel
    #     self.pixel_decoded_register_write("Bypass_THCal", "1", chip)    
    #     self.pixel_decoded_register_write("DAC", format(0x3ff, '010b'), chip)  
    #     self.pixel_decoded_register_write("QSel", format(0x1b, '05b'), chip)       # Ensure we inject 27 fC of charge
    #     ## Open the trigger and data windows
    #     self.TDC_window_pixel(chip_address, row, col, verbose=verbose, chip=chip, row_indexer_handle=row_indexer_handle, column_indexer_handle=column_indexer_handle, alreadySetPixel=True, triggerWindow=True, cbWindow=True)
    #     # Enable TDC
    #     self.pixel_decoded_register_write("enable_TDC", "1", chip)
    #     # Delete created components
    #     if(del_chip): del chip
    #     if(del_row_handle): del row_indexer_handle
    #     if(del_col_handle): del column_indexer_handle
    #     if(verbose): print(f"Enabled pixel ({row},{col}) for chip: {hex(chip_address)}")

    def auto_cal_pixel(self, chip_name, row, col, verbose=False, chip_address=None, chip=None, data=None, row_indexer_handle=None, column_indexer_handle=None):
        del_chip = False
        if(chip==None and chip_address!=None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
        elif(chip==None and chip_address==None): 
            print("Need chip address to make a new chip in disable pixel!")
            return
        del_row_handle, del_col_handle = False, False
        if(row_indexer_handle==None):
            row_indexer_handle,_,_ = chip.get_indexer("row")
            del_row_handle = True
        if(column_indexer_handle==None):
            column_indexer_handle,_,_ = chip.get_indexer("column")
            del_col_handle = True
        # BL_map_THCal, NW_map_THCal, BL_df = self.get_auto_cal_maps(chip_address)
        column_indexer_handle.set(col)
        row_indexer_handle.set(row)
        # Disable TDC
        self.pixel_decoded_register_write("enable_TDC", "0", chip)
        # Enable THCal clock and buffer, disable bypass
        self.pixel_decoded_register_write("CLKEn_THCal", "1", chip)
        self.pixel_decoded_register_write("BufEn_THCal", "1", chip)
        self.pixel_decoded_register_write("Bypass_THCal", "0", chip)
        self.pixel_decoded_register_write("TH_offset", format(0x0a, '06b'), chip)
        # Reset the calibration block (active low)
        self.pixel_decoded_register_write("RSTn_THCal", "0", chip)
        self.pixel_decoded_register_write("RSTn_THCal", "1", chip)
        # Start and Stop the calibration, (25ns x 2**15 ~ 800 us, ACCumulator max is 2**15)
        self.pixel_decoded_register_write("ScanStart_THCal", "1", chip)
        self.pixel_decoded_register_write("ScanStart_THCal", "0", chip)
        # Check the calibration done correctly
        if(self.pixel_decoded_register_read("ScanDone", "Status", chip)!="1"): print("!!!ERROR!!! Scan not done!!!")
        self.BL_map_THCal[chip_address][row, col] = self.pixel_decoded_register_read("BL", "Status", chip, need_int=True)
        self.NW_map_THCal[chip_address][row, col] = self.pixel_decoded_register_read("NW", "Status", chip, need_int=True)
        if(data != None):
            data += [{
                'col': col,
                'row': row,
                'baseline': self.BL_map_THCal[chip_address][row, col],
                'noise_width': self.NW_map_THCal[chip_address][row, col],
                'timestamp': datetime.datetime.now(),
                'chip_name': chip_name,
            }]
        # Disable clock and buffer before charge injection 
        self.pixel_decoded_register_write("CLKEn_THCal", "0", chip) 
        self.pixel_decoded_register_write("BufEn_THCal", "0", chip)
        # Set DAC to max
        self.pixel_decoded_register_write("Bypass_THCal", "1", chip)
        self.pixel_decoded_register_write("DAC", format(0x3ff, '010b'), chip)
        # Delete created components
        if(del_chip): del chip
        if(del_row_handle): del row_indexer_handle
        if(del_col_handle): del column_indexer_handle
        if(verbose): print(f"Auto calibration finished for pixel ({row},{col}) on chip: {hex(chip_address)}")

    # def auto_cal_pixel_TDCon(self, chip_name, row, col, verbose=False, chip_address=None, chip=None, data=None, row_indexer_handle=None, column_indexer_handle=None):
    #     del_chip = False
    #     if(chip==None and chip_address!=None): 
    #         chip = self.get_chip_i2c_connection(chip_address)
    #         del_chip=True
    #     elif(chip==None and chip_address==None): 
    #         print("Need chip address to make a new chip in disable pixel!")
    #         return
    #     del_row_handle, del_col_handle = False, False
    #     if(row_indexer_handle==None):
    #         row_indexer_handle,_,_ = chip.get_indexer("row")
    #         del_row_handle = True
    #     if(column_indexer_handle==None):
    #         column_indexer_handle,_,_ = chip.get_indexer("column")
    #         del_col_handle = True
    #     # BL_map_THCal, NW_map_THCal, BL_df = self.get_auto_cal_maps(chip_address)
    #     column_indexer_handle.set(col)
    #     row_indexer_handle.set(row)
    #     # Disable TDC
    #     self.pixel_decoded_register_write("enable_TDC", "1", chip)
    #     # Enable THCal clock and buffer, disable bypass
    #     self.pixel_decoded_register_write("CLKEn_THCal", "1", chip)
    #     self.pixel_decoded_register_write("BufEn_THCal", "1", chip)
    #     self.pixel_decoded_register_write("Bypass_THCal", "0", chip)
    #     self.pixel_decoded_register_write("TH_offset", format(0x07, '06b'), chip)
    #     # Reset the calibration block (active low)
    #     self.pixel_decoded_register_write("RSTn_THCal", "0", chip)
    #     self.pixel_decoded_register_write("RSTn_THCal", "1", chip)
    #     # Start and Stop the calibration, (25ns x 2**15 ~ 800 us, ACCumulator max is 2**15)
    #     self.pixel_decoded_register_write("ScanStart_THCal", "1", chip)
    #     self.pixel_decoded_register_write("ScanStart_THCal", "0", chip)
    #     # Check the calibration done correctly
    #     if(self.pixel_decoded_register_read("ScanDone", "Status", chip)!="1"): print("!!!ERROR!!! Scan not done!!!")
    #     self.BL_map_THCal[chip_address][row, col] = self.pixel_decoded_register_read("BL", "Status", chip, need_int=True)
    #     self.NW_map_THCal[chip_address][row, col] = self.pixel_decoded_register_read("NW", "Status", chip, need_int=True)
    #     if(data != None):
    #         data += [{
    #             'col': col,
    #             'row': row,
    #             'baseline': self.BL_map_THCal[chip_address][row, col],
    #             'noise_width': self.NW_map_THCal[chip_address][row, col],
    #             'timestamp': datetime.datetime.now(),
    #             'chip_name': chip_name,
    #         }]
    #     # Enable TDC
    #     self.pixel_decoded_register_write("enable_TDC", "1", chip)
    #     # Disable clock and buffer before charge injection 
    #     self.pixel_decoded_register_write("CLKEn_THCal", "0", chip) 
    #     self.pixel_decoded_register_write("BufEn_THCal", "0", chip)
    #     self.pixel_decoded_register_write("QSel", format(0x1b, '05b'), chip)
    #     self.pixel_decoded_register_write("TH_offset", format(0x0a, '06b'), chip) 
    #     # Set DAC to max
    #     self.pixel_decoded_register_write("Bypass_THCal", "1", chip)
    #     self.pixel_decoded_register_write("DAC", format(0x3ff, '010b'), chip)
    #     # Delete created components
    #     if(del_chip): del chip
    #     if(del_row_handle): del row_indexer_handle
    #     if(del_col_handle): del column_indexer_handle
    #     if(verbose): print(f"Auto calibration finished for pixel ({row},{col}) on chip: {hex(chip_address)}")

    # def close_TDC_pixel(self, chip_address, row, col, verbose=False, chip=None, row_indexer_handle=None, column_indexer_handle=None, alreadySetPixel=False):
    #     del_chip = False
    #     if(chip==None): 
    #         chip = self.get_chip_i2c_connection(chip_address)
    #         del_chip=True
    #     del_row_handle, del_col_handle = False, False
    #     if(row_indexer_handle==None):
    #         row_indexer_handle,_,_ = chip.get_indexer("row")
    #         del_row_handle = True
    #     if(column_indexer_handle==None):
    #         column_indexer_handle,_,_ = chip.get_indexer("column")
    #         del_col_handle = True
    #     if(not alreadySetPixel):
    #         column_indexer_handle.set(col)
    #         row_indexer_handle.set(row)
    #     ## Close trigger and data range
    #     self.pixel_decoded_register_write("upperTOATrig", format(0x3ff, '010b'), chip)
    #     self.pixel_decoded_register_write("lowerTOATrig", format(0x000, '010b'), chip)
    #     self.pixel_decoded_register_write("upperTOTTrig", format(0x1ff, '09b'), chip)
    #     self.pixel_decoded_register_write("lowerTOTTrig", format(0x000, '09b'), chip)
    #     self.pixel_decoded_register_write("upperCalTrig", format(0x3ff, '010b'), chip)
    #     self.pixel_decoded_register_write("lowerCalTrig", format(0x000, '010b'), chip)
    #     self.pixel_decoded_register_write("upperTOA", format(0x000, '010b'), chip)
    #     self.pixel_decoded_register_write("lowerTOA", format(0x000, '010b'), chip)
    #     self.pixel_decoded_register_write("upperTOT", format(0x1ff, '09b'), chip)
    #     self.pixel_decoded_register_write("lowerTOT", format(0x1ff, '09b'), chip)
    #     self.pixel_decoded_register_write("upperCal", format(0x3ff, '010b'), chip)
    #     self.pixel_decoded_register_write("lowerCal", format(0x3ff, '010b'), chip)
    #     # Delete created components
    #     if(del_chip): del chip
    #     if(del_row_handle): del row_indexer_handle
    #     if(del_col_handle): del column_indexer_handle
    #     if verbose: print(f"Closed TDC on pixel ({row},{col}) for chip: {hex(chip_address)}")

    # def open_TDC_pixel(self, chip_address, row, col, verbose=False, chip=None, row_indexer_handle=None, column_indexer_handle=None, alreadySetPixel=False):
    #     del_chip = False
    #     if(chip==None): 
    #         chip = self.get_chip_i2c_connection(chip_address)
    #         del_chip=True
    #     del_row_handle, del_col_handle = False, False
    #     if(row_indexer_handle==None):
    #         row_indexer_handle,_,_ = chip.get_indexer("row")
    #         del_row_handle = True
    #     if(column_indexer_handle==None):
    #         column_indexer_handle,_,_ = chip.get_indexer("column")
    #         del_col_handle = True
    #     if(not alreadySetPixel):
    #         column_indexer_handle.set(col)
    #         row_indexer_handle.set(row)
    #     ## Release trigger and data range
    #     self.pixel_decoded_register_write("upperTOATrig", format(0x3ff, '010b'), chip)
    #     self.pixel_decoded_register_write("lowerTOATrig", format(0x000, '010b'), chip)
    #     self.pixel_decoded_register_write("upperTOTTrig", format(0x1ff, '09b'), chip)
    #     self.pixel_decoded_register_write("lowerTOTTrig", format(0x000, '09b'), chip)
    #     self.pixel_decoded_register_write("upperCalTrig", format(0x3ff, '010b'), chip)
    #     self.pixel_decoded_register_write("lowerCalTrig", format(0x000, '010b'), chip)
    #     self.pixel_decoded_register_write("upperTOA", format(0x3ff, '010b'), chip)
    #     self.pixel_decoded_register_write("lowerTOA", format(0x000, '010b'), chip)
    #     self.pixel_decoded_register_write("upperTOT", format(0x1ff, '09b'), chip)
    #     self.pixel_decoded_register_write("lowerTOT", format(0x000, '09b'), chip)
    #     self.pixel_decoded_register_write("upperCal", format(0x3ff, '010b'), chip)
    #     self.pixel_decoded_register_write("lowerCal", format(0x000, '010b'), chip)
    #     # Delete created components
    #     if(del_chip): del chip
    #     if(del_row_handle): del row_indexer_handle
    #     if(del_col_handle): del column_indexer_handle
    #     if verbose: print(f"Opened TDC on pixel ({row},{col}) for chip: {hex(chip_address)}")
    
    def TDC_window_pixel(self, chip_address, row, col, verbose=False, chip=None, row_indexer_handle=None, column_indexer_handle=None, alreadySetPixel=False, triggerWindow=True, cbWindow=True):
        del_chip = False
        if(chip==None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
        del_row_handle, del_col_handle = False, False
        if(row_indexer_handle==None):
            row_indexer_handle,_,_ = chip.get_indexer("row")
            del_row_handle = True
        if(column_indexer_handle==None):
            column_indexer_handle,_,_ = chip.get_indexer("column")
            del_col_handle = True
        if(not alreadySetPixel):
            column_indexer_handle.set(col)
            row_indexer_handle.set(row)
        ## Release trigger and data range
        self.pixel_decoded_register_write("upperTOATrig", format(0x3ff if triggerWindow else 0x000, '010b'), chip)
        self.pixel_decoded_register_write("lowerTOATrig", format(0x000, '010b'), chip)
        self.pixel_decoded_register_write("upperTOTTrig", format(0x1ff if triggerWindow else 0x000, '09b'), chip)
        self.pixel_decoded_register_write("lowerTOTTrig", format(0x000, '09b'), chip)
        self.pixel_decoded_register_write("upperCalTrig", format(0x3ff if triggerWindow else 0x000, '010b'), chip)
        self.pixel_decoded_register_write("lowerCalTrig", format(0x000, '010b'), chip)
        self.pixel_decoded_register_write("upperTOA", format(0x3ff if cbWindow else 0x000, '010b'), chip)
        self.pixel_decoded_register_write("lowerTOA", format(0x000, '010b'), chip)
        self.pixel_decoded_register_write("upperTOT", format(0x1ff if cbWindow else 0x000, '09b'), chip)
        self.pixel_decoded_register_write("lowerTOT", format(0x000, '09b'), chip)
        self.pixel_decoded_register_write("upperCal", format(0x3ff if cbWindow else 0x000, '010b'), chip)
        self.pixel_decoded_register_write("lowerCal", format(0x000, '010b'), chip)
        # Delete created components
        if(del_chip): del chip
        if(del_row_handle): del row_indexer_handle
        if(del_col_handle): del column_indexer_handle
        if verbose: print(f"Opened TDC on pixel ({row},{col}) for chip: {hex(chip_address)}")

    def open_TDC_all(self, chip_address, chip=None):
        del_chip = False
        if(chip==None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
        for row in tqdm(range(16), desc="Disabling row", position=0):
            for col in tqdm(range(16), desc=" col", position=1, leave=False):
                self.TDC_window_pixel(row=row, col=col, verbose=False, chip=chip, triggerWindow=True, cbWindow=True)
        # Delete created components
        if(del_chip): del chip
        print(f"Opened TDC for pixels for chip: {hex(chip_address)}")
    
    def close_TDC_all(self, chip_address, chip=None):
        del_chip = False
        if(chip==None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
        for row in tqdm(range(16), desc="Disabling row", position=0):
            for col in tqdm(range(16), desc=" col", position=1, leave=False):
                self.TDC_window_pixel(row=row, col=col, verbose=False, chip=chip, triggerWindow=True, cbWindow=False)
        # Delete created components
        if(del_chip): del chip
        print(f"Closed TDC for pixels for chip: {hex(chip_address)}")
    
    #--------------------------------------------------------------------------#

    def onchipL1A(self, chip_address, chip=None, comm='00'):
        del_chip = False
        if(chip==None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
        self.peripheral_decoded_register_write("onChipL1AConf", comm, chip)
        # Delete created components
        if(del_chip): del chip
        print(f"OnChipL1A action {comm} done for chip: {hex(chip_address)}")
    
    def asyAlignFastcommand(self, chip_address, chip=None):
        del_chip = False
        if(chip==None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
        self.peripheral_decoded_register_write("asyAlignFastcommand", "1", chip)
        time.sleep(0.2)
        self.peripheral_decoded_register_write("asyAlignFastcommand", "0", chip)
        # Delete created components
        if(del_chip): del chip
        print(f"asyAlignFastcommand action done for chip: {hex(chip_address)}")

    def asyResetGlobalReadout(self, chip_address, chip=None):
        del_chip = False
        if(chip==None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
        self.peripheral_decoded_register_write("asyResetGlobalReadout", "0", chip)
        time.sleep(0.2)
        self.peripheral_decoded_register_write("asyResetGlobalReadout", "1", chip)
        # Delete created components
        if(del_chip): del chip
        print(f"Reset Global Readout done for chip: {hex(chip_address)}")

    def calibratePLL(self, chip_address, chip=None):
        del_chip = False
        if(chip==None): 
            chip = self.get_chip_i2c_connection(chip_address)
            del_chip=True
        self.peripheral_decoded_register_write("asyPLLReset", "0", chip)
        time.sleep(0.2)
        self.peripheral_decoded_register_write("asyPLLReset", "1", chip)
        self.peripheral_decoded_register_write("asyStartCalibration", "0", chip)
        time.sleep(0.2)
        self.peripheral_decoded_register_write("asyStartCalibration", "1", chip)
        # Delete created components
        if(del_chip): del chip
        print(f"PLL Calibrated for chip: {hex(chip_address)}")
    #--------------------------------------------------------------------------#

    

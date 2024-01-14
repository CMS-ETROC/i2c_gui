#############################################################################
# zlib License
#
# (C) 2023 Zach FLowers, Murtaza Safdari <musafdar@cern.ch>, Cristóvão Beirão da Cruz e Silva, Jongho Lee
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
import numpy as np
import os, sys
import datetime
from tqdm import tqdm
import pandas
import logging
import multiprocessing
import signal
from pathlib import Path
sys.path(f'/home/{os.getlogin()}/ETROC2/ETROC_DAQ')
# os.chdir(f'/home/{os.getlogin()}/ETROC2/ETROC_DAQ')
import run_script
import parser_arguments
import importlib
importlib.reload(run_script)
importlib.reload(parser_arguments)
import sqlite3
import i2c_gui
import i2c_gui.chips
from i2c_gui.usb_iss_helper import USB_ISS_Helper
from i2c_gui.fpga_eth_helper import FPGA_ETH_Helper
from i2c_gui.chips.etroc2_chip import register_decoding
#========================================================================================#


#--------------------------------------------------------------------------#
def run_ProbeStation(
    wafer_name: str,
    chip_name: str,
    comment_str: str,
    fpga_ip = "192.168.2.3",
    port = "/dev/ttyACM0",
    chip_address = 0x60,
    ws_address = None,
    polarity = "0x0027",
    do_pixel_id_check: bool = False,
    do_i2c_check: bool = False,
    do_baseline: bool = False,
    do_qinj: bool = False,
    do_offline: bool = False,
    row: int = 0,
    col: int = 0,
):

    i2c_gui.__no_connect__ = False  # Set to fake connecting to an ETROC2 device
    i2c_gui.__no_connect_type__ = "echo"  # for actually testing readback
    #i2c_gui.__no_connect_type__ = "check"  # default behaviour

    ## Logger
    log_level=30
    logging.basicConfig(format='%(asctime)s - %(levelname)s:%(name)s:%(message)s')
    logger = logging.getLogger("Script_Logger")
    Script_Helper = i2c_gui.ScriptHelper(logger)

    conn = i2c_gui.Connection_Controller(Script_Helper)
    conn.connection_type = "USB-ISS"
    conn.handle: USB_ISS_Helper
    conn.handle.port = port
    conn.handle.clk = 100
    conn.connect()
    logger.setLevel(log_level)

    conn.connect()
    chip = i2c_gui.chips.ETROC2_Chip(parent=Script_Helper, i2c_controller=conn)
    chip.config_i2c_address(chip_address)  # Not needed if you do not access ETROC registers (i.e. only access WS registers)
    # chip.config_waveform_sampler_i2c_address(ws_address)  # Not needed if you do not access WS registers

    ### Making directories
    data_dir = Path('../ETROC-Data/') / (datetime.date.today().isoformat() + '_Array_Test_Results')
    data_dir.mkdir(exist_ok=True)
    i2c_log_dir = data_dir / f'{comment_str}_{wafer_name}_{chip_name}_R{row}_C{col}_I2C'
    i2c_log_dir.mkdir(exist_ok = False)

    ### Define handles
    disDataReadout_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "disDataReadout")
    QInjEn_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "QInjEn")
    disTrigPath_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "disTrigPath")

    upperTOATrig_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "upperTOATrig")
    lowerTOATrig_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "lowerTOATrig")
    upperTOTTrig_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "upperTOTTrig")
    lowerTOTTrig_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "lowerTOTTrig")
    upperCalTrig_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "upperCalTrig")
    lowerCalTrig_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "lowerCalTrig")
    upperTOA_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "upperTOA")
    lowerTOA_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "lowerTOA")
    upperTOT_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "upperTOT")
    lowerTOT_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "lowerTOT")
    upperCal_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "upperCal")
    lowerCal_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "lowerCal")
    enable_TDC_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "enable_TDC")

    disDataReadout = "1"
    QInjEn = "0"
    disTrigPath = "1"
    upperTOA = hex(0x000)
    lowerTOA = hex(0x000)
    upperTOT = hex(0x1ff)
    lowerTOT = hex(0x1ff)
    upperCal = hex(0x3ff)
    lowerCal = hex(0x3ff)
    enable_TDC = "0"

    ## Disabling chips by manually
    for this_row in tqdm(range(16), desc="Disabling row", position=0):
        for this_col in range(16):
            column_indexer_handle.set(this_col)
            row_indexer_handle.set(this_row)

            chip.read_all_block("ETROC2", "Pixel Config")

            disDataReadout_handle.set(disDataReadout)
            QInjEn_handle.set(QInjEn)
            disTrigPath_handle.set(disTrigPath)
            upperTOATrig_handle.set(upperTOA)
            lowerTOATrig_handle.set(lowerTOA)
            upperTOTTrig_handle.set(upperTOT)
            lowerTOTTrig_handle.set(lowerTOT)
            upperCalTrig_handle.set(upperCal)
            lowerCalTrig_handle.set(lowerCal)
            upperTOA_handle.set(upperTOA)
            lowerTOA_handle.set(lowerTOA)
            upperTOT_handle.set(upperTOT)
            lowerTOT_handle.set(lowerTOT)
            upperCal_handle.set(upperCal)
            lowerCal_handle.set(lowerCal)
            enable_TDC_handle.set(enable_TDC)

            chip.write_all_block("ETROC2", "Pixel Config")

    print(f"Disabled pixels for chip: {hex(chip_address)}")

    if do_pixel_id_check:
        Failure_map = np.zeros((16,16))
        data = []
        pixel_success = True
        status_string = ""
        for this_row in range(16):
            for this_col in range(16):
                column_indexer_handle.set(this_col)
                row_indexer_handle.set(this_row)

                handle_rowID = chip.get_decoded_display_var("ETROC2", "Pixel Status", "PixelID-Row")
                chip.read_decoded_value("ETROC2", "Pixel Status", "PixelID-Row")
                fetched_row = handle_rowID.get()

                handle_colID = chip.get_decoded_display_var("ETROC2", "Pixel Status", "PixelID-Col")
                chip.read_decoded_value("ETROC2", "Pixel Status", "PixelID-Col")
                fetched_col = handle_colID.get()

                data += [{
                    'col': this_col,
                    'row': this_row,
                    'fetched_col': fetched_col,
                    'fetched_row': fetched_row,
                    'timestamp': datetime.datetime.now(),
                    'chip_name': chip_name,
                }]
                if(this_row != fetched_row or this_col != fetched_col):
                    pixel_success = False
                    Failure_map[15-this_row,15-this_col] = 1
                    if status_string == "":
                        status_string = f"({this_row},{this_col})"
                    else:
                        status_string += f", ({this_row},{this_col})"

        ## Back to original index (0, 0)
        column_indexer_handle.set(col)
        row_indexer_handle.set(row)

        if pixel_success:
            print("Pixel Address Check: Success")
        else:
            print("Pixel Address Check: Failure")
            print(f"  Failed pixels: {status_string}")

        Failure_df = pandas.DataFrame(data = data)

        # Store for later use
        failOut = data_dir / f'{wafer_name}_{chip_name}_{comment_str}_FailedPixelsAt_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")}.csv'
        Failure_df.to_csv(failOut, index=False)

    if do_i2c_check:

        selected_peripheralRegisterKeys = [0]
        data = []
        this_log_file = i2c_log_dir / 'Simplei2cCheckPeripheralConsistency.sqlite'
        peripheral_success = True

        for peripheralRegisterKey in selected_peripheralRegisterKeys:
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
            # chip.read_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")  # By default, write already does a read at the end
            data_bin_new_1_PeriCfgX = format(int(handle_PeriCfgX.get(), base=16), '08b')
            chip.read_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
            data_bin_new_2_PeriCfgX = format(int(handle_PeriCfgX.get(), base=16), '08b')
            # Undo the change to recover the original register value, and check for consistency
            handle_PeriCfgX.set(hex(int(data_bin_PeriCfgX, base=2)))
            chip.write_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
            # chip.read_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
            data_bin_recover_PeriCfgX = format(int(handle_PeriCfgX.get(), base=16), '08b')
            timestamp = datetime.datetime.now().isoformat()
            data += [{
                'register': f"PeriCfg{peripheralRegisterKey}",
                'original_value': data_bin_PeriCfgX,
                'attempted_set_value': data_bin_modified_PeriCfgX,
                'new_value': data_bin_new_1_PeriCfgX,
                'repeated_read_new_value': data_bin_new_2_PeriCfgX,
                'reset_value': data_bin_recover_PeriCfgX,
                'timestamp': timestamp,
                'chip_name': f'{wafer_name}_{chip_name}',
            }]

            if(data_bin_new_1_PeriCfgX!=data_bin_new_2_PeriCfgX or data_bin_new_2_PeriCfgX!=data_bin_modified_PeriCfgX or data_bin_recover_PeriCfgX!=data_bin_PeriCfgX):
                peripheral_success = False
            else:
                peripheral_success = True

        this_df = pandas.DataFrame(data = data)

        with sqlite3.connect(this_log_file) as sqlconn:
            this_df.to_sql('registers', sqlconn, if_exists='append', index=False)

        if peripheral_success:
            print(f"Simple I2C Check - Peripheral: Success")
        else:
            print(f"Simple I2C Check - Peripheral: Failure")

        ##############################
        selected_pixelRegisterKeys = [0]
        data = []
        this_log_file = i2c_log_dir / 'Simplei2cPixelConsistency.sqlite'
        pixel_success = None

        for pixelRegisterKey in selected_pixelRegisterKeys:
                # Fetch the register
                handle_PixCfgX = chip.get_indexed_var("ETROC2", "Pixel Config", f"PixCfg{pixelRegisterKey}")
                chip.read_register("ETROC2", "Pixel Config", f"PixCfg{pixelRegisterKey}")
                data_bin_PixCfgX = format(int(handle_PixCfgX.get(), base=16), '08b')
                # Make the flipped byte
                data_bin_modified_PixCfgX = data_bin_PixCfgX.replace('1', '2').replace('0', '1').replace('2', '0')
                data_hex_modified_PixCfgX = hex(int(data_bin_modified_PixCfgX, base=2))
                # Set the register with the value
                handle_PixCfgX.set(data_hex_modified_PixCfgX)
                chip.write_register("ETROC2", "Pixel Config", f"PixCfg{pixelRegisterKey}")
                # Perform two reads to verify the persistence of the change
                # chip.read_register("ETROC2", "Pixel Config", f"PixCfg{pixelRegisterKey}")
                data_bin_new_1_PixCfgX = format(int(handle_PixCfgX.get(), base=16), '08b')
                chip.read_register("ETROC2", "Pixel Config", f"PixCfg{pixelRegisterKey}")
                data_bin_new_2_PixCfgX = format(int(handle_PixCfgX.get(), base=16), '08b')
                # Undo the change to recover the original register value, and check for consistency
                handle_PixCfgX.set(hex(int(data_bin_PixCfgX, base=2)))
                chip.write_register("ETROC2", "Pixel Config", f"PixCfg{pixelRegisterKey}")
                # chip.read_register("ETROC2", "Pixel Config", f"PixCfg{pixelRegisterKey}")
                data_bin_recover_PixCfgX = format(int(handle_PixCfgX.get(), base=16), '08b')
                data += [{
                    'row': row,
                    'col': col,
                    'register': f"PixCfg{pixelRegisterKey}",
                    'original_value': data_bin_PixCfgX,
                    'attempted_set_value': data_bin_modified_PixCfgX,
                    'new_value': data_bin_new_1_PixCfgX,
                    'repeated_read_new_value': data_bin_new_2_PixCfgX,
                    'reset_value': data_bin_recover_PixCfgX,
                    'timestamp': timestamp,
                    'chip_name': f'{wafer_name}_{chip_name}',
                }]

                if(data_bin_new_1_PixCfgX!=data_bin_new_2_PixCfgX or data_bin_new_2_PixCfgX!=data_bin_modified_PixCfgX or data_bin_recover_PixCfgX!=data_bin_PixCfgX):
                    pixel_success = False
                else:
                    pixel_success = True

        this_df = pandas.DataFrame(data = data)

        with sqlite3.connect(this_log_file) as sqlconn:
            this_df.to_sql('registers', sqlconn, if_exists='append', index=False)

        if pixel_success:
            print(f"Simple I2C Check - Pixel: Success")
        else:
            print(f"Simple I2C Check - Pixel: Failure")

    if do_baseline:

        data = []
        row_indexer_handle,_,_ = chip.get_indexer("row")
        column_indexer_handle,_,_ = chip.get_indexer("column")

        row_indexer_handle.set(row)
        column_indexer_handle.set(col)

        chip.read_all_block("ETROC2", "Pixel Config")

        enable_TDC_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "enable_TDC")
        CLKEn_THCal_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "CLKEn_THCal")
        BufEn_THCal_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "BufEn_THCal")
        Bypass_THCal_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "Bypass_THCal")
        TH_offset_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "TH_offset")
        RSTn_THCal_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "RSTn_THCal")
        ScanStart_THCal_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "ScanStart_THCal")
        DAC_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "DAC")
        ScanDone_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Status", "ScanDone")
        BL_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Status", "BL")
        NW_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Status", "NW")

        # Disable TDC
        enable_TDC_handle.set("0")

        # Enable THCal clock and buffer, disable bypass
        CLKEn_THCal_handle.set("1")
        BufEn_THCal_handle.set("1")
        Bypass_THCal_handle.set("0")
        TH_offset_handle.set(hex(0x0a))

        # Send changes to chip
        chip.write_all_block("ETROC2", "Pixel Config")

        # Reset the calibration block (active low)
        RSTn_THCal_handle.set("0")
        chip.write_decoded_value("ETROC2", "Pixel Config", "RSTn_THCal")
        RSTn_THCal_handle.set("1")
        chip.write_decoded_value("ETROC2", "Pixel Config", "RSTn_THCal")

        # Start and Stop the calibration, (25ns x 2**15 ~ 800 us, ACCumulator max is 2**15)
        ScanStart_THCal_handle.set("1")
        chip.write_decoded_value("ETROC2", "Pixel Config", "ScanStart_THCal")
        ScanStart_THCal_handle.set("0")
        chip.write_decoded_value("ETROC2", "Pixel Config", "ScanStart_THCal")

        # Wait for the calibration to be done correctly
        retry_counter = 0
        chip.read_all_block("ETROC2", "Pixel Status")
        while ScanDone_handle.get() != "1":
            time.sleep(0.01)
            chip.read_all_block("ETROC2", "Pixel Status")
            retry_counter += 1
            if retry_counter == 5 and ScanDone_handle.get() != "1":
                print(f"!!!ERROR!!! Scan not done for row {row}, col {col}!!!")
                break

        data += [{
            'col': col,
            'row': row,
            'baseline': int(BL_handle.get(), 0),
            'noise_width': int(NW_handle.get(), 0),
            'timestamp': datetime.datetime.now(),
            'chip_name': chip_name,
        }]

        # Enable TDC
        enable_TDC_handle.set("1")

        # Disable THCal clock and buffer, enable bypass
        CLKEn_THCal_handle.set("0")
        BufEn_THCal_handle.set("0")
        Bypass_THCal_handle.set("1")
        DAC_handle.set(hex(0x3ff))

        # Send changes to chip
        chip.write_all_block("ETROC2", "Pixel Config")
        print(f"Pixel ({row},{col}) on chip: {hex(chip_address)}")
        print(f'BL: {int(BL_handle.get(), 0)}, NW: {int(NW_handle.get(), 0)}')

    if do_qinj:

        chip.read_all_block("ETROC2", "Peripheral Config")

        handle = chip.get_decoded_display_var("ETROC2", "Peripheral Config", "EFuse_Prog")           # chip ID
        handle.set(hex(0x00017f0f))
        handle = chip.get_decoded_display_var("ETROC2", "Peripheral Config", "singlePort")           # Set data output to right port only
        handle.set('1')
        handle = chip.get_decoded_display_var("ETROC2", "Peripheral Config", "serRateLeft")          # Set Data Rates to 320 mbps
        handle.set(hex(0b00))
        handle = chip.get_decoded_display_var("ETROC2", "Peripheral Config", "serRateRight")         # ^^
        handle.set(hex(0b00))
        handle = chip.get_decoded_display_var("ETROC2", "Peripheral Config", "onChipL1AConf")        # Switches off the onboard L1A
        handle.set(hex(0b00))
        handle = chip.get_decoded_display_var("ETROC2", "Peripheral Config", "PLL_ENABLEPLL")        # "Enable PLL mode, active high. Debugging use only."
        handle.set('1')
        handle = chip.get_decoded_display_var("ETROC2", "Peripheral Config", "chargeInjectionDelay") # User tunable delay of Qinj pulse
        handle.set(hex(0x0a))
        handle = chip.get_decoded_display_var("ETROC2", "Peripheral Config", "triggerGranularity")   # only for trigger bit
        handle.set(hex(0x00))
        handle = chip.get_decoded_display_var("ETROC2", "Peripheral Config", "fcClkDelayEn")
        handle.set('1')
        handle = chip.get_decoded_display_var("ETROC2", "Peripheral Config", "fcDataDelayEn")
        handle.set('1')

        chip.write_all_block("ETROC2", "Peripheral Config")
        print(f"Peripherals set for chip: {hex(chip_address)}")

        ### Enable pixel
        row_indexer_handle,_,_ = chip.get_indexer("row")
        column_indexer_handle,_,_ = chip.get_indexer("column")
        column_indexer_handle.set(col)
        row_indexer_handle.set(row)

        chip.read_all_block("ETROC2", "Pixel Config")

        L1Adelay_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "L1Adelay")
        Bypass_THCal_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "Bypass_THCal")
        TH_offset_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "TH_offset")
        QSel_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "QSel")
        DAC_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "DAC")
        enable_TDC_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "enable_TDC")
        # IBSel_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "IBSel")

        disDataReadout_handle.set("0")
        disTrigPath_handle.set("0")
        QInjEn_handle.set("1")
        L1Adelay_handle.set(hex(0x01f5)) # Change L1A delay - circular buffer in ETROC2 pixel
        Bypass_THCal_handle.set("0")
        TH_offset_handle.set(hex(0x0a))  # Offset 10 used to add to the auto BL for real
        QSel_handle.set(hex(0x1b))       # Ensure we inject 27 fC of charge
        enable_TDC_handle.set("1")

        upperTOATrig_handle.set(hex(0x3ff))
        lowerTOATrig_handle.set(hex(0x000))
        upperTOTTrig_handle.set(hex(0x1ff))
        lowerTOTTrig_handle.set(hex(0x000))
        upperCalTrig_handle.set(hex(0x3ff))
        lowerCalTrig_handle.set(hex(0x000))
        upperTOA_handle.set(hex(0x3ff))
        lowerTOA_handle.set(hex(0x000))
        upperTOT_handle.set(hex(0x1ff))
        lowerTOT_handle.set(hex(0x000))
        upperCal_handle.set(hex(0x3ff))
        lowerCal_handle.set(hex(0x000))

        chip.write_all_block("ETROC2", "Pixel Config")
        print(f"Enabled pixel ({row},{col}) for chip: {hex(chip_address)}")

        ## PLL Calibration (active low)
        handle_PLL_asyPLLReset = chip.get_decoded_display_var("ETROC2", "Peripheral Config", "asyPLLReset")
        handle_PLL_asyPLLReset.set("0")
        chip.write_decoded_value("ETROC2", "Peripheral Config", "asyPLLReset")
        handle_PLL_asyPLLReset.set("1")
        chip.write_decoded_value("ETROC2", "Peripheral Config", "asyPLLReset")
        # chip.read_decoded_value("ETROC2", "Peripheral Config", "asyPLLReset")
        # print(handle_PLL_asyPLLReset.get())

        handle_PLL_asyStartCalibration = chip.get_decoded_display_var("ETROC2", "Peripheral Config", "asyStartCalibration")
        handle_PLL_asyStartCalibration.set("0")
        chip.write_decoded_value("ETROC2", "Peripheral Config", "asyStartCalibration")
        handle_PLL_asyStartCalibration.set("1")
        chip.write_decoded_value("ETROC2", "Peripheral Config", "asyStartCalibration")
        # chip.read_decoded_value("ETROC2", "Peripheral Config", "asyStartCalibration")
        # print(handle_PLL_asyStartCalibration.get())

        ## FC Cabliration (active low)
        handle_PLL_asyAlignFastcommand = chip.get_decoded_display_var("ETROC2", "Peripheral Config", "asyAlignFastcommand")
        handle_PLL_asyAlignFastcommand.set("1")
        chip.write_decoded_value("ETROC2", "Peripheral Config", "asyAlignFastcommand")
        handle_PLL_asyAlignFastcommand.set("0")
        chip.write_decoded_value("ETROC2", "Peripheral Config", "asyAlignFastcommand")
        # chip.read_decoded_value("ETROC2", "Peripheral Config", "asyAlignFastcommand")
        # print(handle_PLL_asyAlignFastcommand.get())

        ## Run DAQ
        parser = parser_arguments.create_parser()
        (options, args) = parser.parse_args(args=f"-f --useIPC --hostname {fpga_ip} -t 15 -o clear_fifo -v -w -s 0x0000 -p {polarity} -d 0x1800 -a 0x000f --clear_fifo".split())
        IPC_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=run_script.main_process, args=(IPC_queue, options, None))
        process.start()

        IPC_queue.put('memoFC Start Triggerbit QInj L1A BCR')
        while not IPC_queue.empty():
            pass
        time.sleep(10)
        IPC_queue.put('stop DAQ')
        IPC_queue.put('memoFC Triggerbit')
        while not IPC_queue.empty():
            pass
        IPC_queue.put('allow threads to exit')
        process.join()

        del IPC_queue, process, parser

    if do_offline:
        pass

    # Disconnect chip
    conn.disconnect()

def main():
    import argparse

    parser = argparse.ArgumentParser(
                    prog='Wafer Testing',
                    description='Control them!',
                    #epilog='Text at the bottom of help'
                    )

    parser.add_argument(
        '-w',
        '--waferName',
        metavar = 'NAME',
        type = str,
        help = 'Name of the wafer - no special chars',
        required = True,
        dest = 'wafer_name',
    )
    parser.add_argument(
        '-c',
        '--chipName',
        metavar = 'NAME',
        type = str,
        help = 'Name of the chip - no special chars',
        required = True,
        dest = 'chip_name',
    )
    parser.add_argument(
        '-t',
        '--commentStr',
        metavar = 'NAME',
        type = str,
        help = 'Comment string - no special chars',
        required = True,
        dest = 'comment_str',
    )
    parser.add_argument(
        '-a',
        '--do_pixel_id_check',
        help = 'Do the I2C Pixel Address test',
        action = 'store_true',
        dest = 'do_pixel_id_check',
    )
    parser.add_argument(
        '-i',
        '--do_i2c_check',
        help = 'Do the I2C test',
        action = 'store_true',
        dest = 'do_i2c_check',
    )
    parser.add_argument(
        '-b',
        '--doBaseline',
        help = 'Do the baseline measurement, required in order to take data with QInj',
        action = 'store_true',
        dest = 'do_baseline',
    )
    parser.add_argument(
        '-q',
        '--doQInj',
        help = 'Do the data taking with QInj, it is necessary to do the baseline in order to do QInj',
        action = 'store_true',
        dest = 'do_qinj',
    )
    parser.add_argument(
        '-f',
        '--doOffline',
        help = 'Do offline translation',
        action = 'store_true',
        dest = 'do_offline',
    )
    parser.add_argument(
        '--row',
        metavar = 'ROW',
        type = int,
        help = 'Row index of the pixel to be scanned. Default: 0',
        default = 0,
        dest = 'row',
    )
    parser.add_argument(
        '--col',
        metavar = 'COL',
        type = int,
        help = 'Col index of the pixel to be scanned. Default: 0',
        default = 0,
        dest = 'col',
    )

    args = parser.parse_args()

    if args.row > 15 or args.row < 0:
        raise RuntimeError("The pixel row must be within the range 0 to 15")
    if args.col > 15 or args.col < 0:
        raise RuntimeError("The pixel column must be within the range 0 to 15")

    def signal_handler(sig, frame):
        print("Exiting gracefully")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    run_ProbeStation(
        wafer_name = args.wafer_name,
        chip_name = args.chip_name,
        comment_str = args.comment_str,
        do_pixel_id_check = args.do_pixel_id_check,
        do_i2c_check = args.do_i2c_check,
        do_baseline = args.do_baseline,
        do_qinj = args.do_qinj,
        do_offline = args.do_offline,
        row = args.row,
        col = args.col,
    )

if __name__ == "__main__":
    main()
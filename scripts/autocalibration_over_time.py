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
import os, sys
import datetime
from tqdm import tqdm
import pandas
import logging
import signal
import sqlite3
import i2c_gui
import i2c_gui.chips
from i2c_gui.usb_iss_helper import USB_ISS_Helper
from i2c_gui.chips.etroc2_chip import register_decoding
from pathlib import Path

def run_auto_calibration(
    chip_name: str,
    run_str: str,
    comment_str: str,
    port = "/dev/ttyACM2",
    chip_address = 0x60,
    ws_address = None,
    disable_all_pixels: bool = False,
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
    history_file = data_dir / 'BaselineHistory_TID_Jan2024_CERN.sqlite'

    if disable_all_pixels:

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
        TH_offset_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "TH_offset")
        DAC_handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", "DAC")

        row_indexer_handle,_,_ = chip.get_indexer("row")
        column_indexer_handle,_,_ = chip.get_indexer("column")
        broadcast_handle,_,_ = chip.get_indexer("broadcast")

        column_indexer_handle.set(0)
        row_indexer_handle.set(0)

        chip.read_all_block("ETROC2", "Pixel Config")
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

        broadcast_handle.set(True)
        chip.write_all_block("ETROC2", "Pixel Config")

        broadcast_ok = True
        for this_row in range(16):
            for this_col in range(16):
                column_indexer_handle.set(this_col)
                row_indexer_handle.set(this_row)

                chip.read_all_block("ETROC2", "Pixel Config")

                if int(disDataReadout_handle.get(), 0) != int(disDataReadout, 0):
                    broadcast_ok = False
                    break
                if int(QInjEn_handle.get(), 0) != int(QInjEn, 0):
                    broadcast_ok = False
                    break
                if int(disTrigPath_handle.get(), 0) != int(disTrigPath, 0):
                    broadcast_ok = False
                    break
                if int(upperTOATrig_handle.get(), 0) != int(upperTOA, 0):
                    broadcast_ok = False
                    break
                if int(lowerTOATrig_handle.get(), 0) != int(lowerTOA, 0):
                    broadcast_ok = False
                    break
                if int(upperTOTTrig_handle.get(), 0) != int(upperTOT, 0):
                    broadcast_ok = False
                    break
                if int(lowerTOTTrig_handle.get(), 0) != int(lowerTOT, 0):
                    broadcast_ok = False
                    break
                if int(upperCalTrig_handle.get(), 0) != int(upperCal, 0):
                    broadcast_ok = False
                    break
                if int(lowerCalTrig_handle.get(), 0) != int(lowerCal, 0):
                    broadcast_ok = False
                    break
                if int(upperTOA_handle.get(), 0) != int(upperTOA, 0):
                    broadcast_ok = False
                    break
                if int(lowerTOA_handle.get(), 0) != int(lowerTOA, 0):
                    broadcast_ok = False
                    break
                if int(upperTOT_handle.get(), 0) != int(upperTOT, 0):
                    broadcast_ok = False
                    break
                if int(lowerTOT_handle.get(), 0) != int(lowerTOT, 0):
                    broadcast_ok = False
                    break
                if int(upperCal_handle.get(), 0) != int(upperCal, 0):
                    broadcast_ok = False
                    break
                if int(lowerCal_handle.get(), 0) != int(lowerCal, 0):
                    broadcast_ok = False
                    break
                if int(enable_TDC_handle.get(), 0) != int(enable_TDC, 0):
                    broadcast_ok = False
                    break
            if not broadcast_ok:
                break

        if not broadcast_ok:
            print("Broadcast failed! \n Will manually disable pixels")
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

    row_indexer_handle,_,_ = chip.get_indexer("row")
    column_indexer_handle,_,_ = chip.get_indexer("column")

    data = {
        'row': [],
        'col': [],
        'baseline': [],
        'noise_width': [],
        'timestamp': [],
        'chip_name': [],
        'note': [],
    }

    for this_row in range(16):
        for this_col in range(16):

            row_indexer_handle.set(this_row)
            column_indexer_handle.set(this_col)

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
            chip.read_all_block("ETROC2", "Pixel Config")

            # Disable TDC
            enable_TDC_handle.set("0")

            # Enable THCal clock and buffer, disable bypass
            CLKEn_THCal_handle.set("1")
            BufEn_THCal_handle.set("1")
            Bypass_THCal_handle.set("0")
            TH_offset_handle.set(hex(0x0a))

            # Send changes to chip
            chip.write_all_block("ETROC2", "Pixel Config")
            time.sleep(0.1)

            # Reset the calibration block (active low)
            RSTn_THCal_handle.set("0")
            chip.write_decoded_value("ETROC2", "Pixel Config", "RSTn_THCal")
            time.sleep(0.1)
            RSTn_THCal_handle.set("1")
            chip.write_decoded_value("ETROC2", "Pixel Config", "RSTn_THCal")
            time.sleep(0.1)

            # Start and Stop the calibration, (25ns x 2**15 ~ 800 us, ACCumulator max is 2**15)
            ScanStart_THCal_handle.set("1")
            chip.write_decoded_value("ETROC2", "Pixel Config", "ScanStart_THCal")
            time.sleep(0.1)
            ScanStart_THCal_handle.set("0")
            chip.write_decoded_value("ETROC2", "Pixel Config", "ScanStart_THCal")
            time.sleep(0.1)

            # Wait for the calibration to be done correctly
            retry_counter = 0
            chip.read_all_block("ETROC2", "Pixel Status")
            print("Scan Done Register: ", ScanDone_handle.get())
            while ScanDone_handle.get() != "1":
                time.sleep(0.01)
                chip.read_all_block("ETROC2", "Pixel Status")
                retry_counter += 1
                if retry_counter == 5 and ScanDone_handle.get() != "1":
                    print(f"!!!ERROR!!! Scan not done for row {this_row}, col {this_col}!!!")
                    break

            data['row'].append(this_row)
            data['col'].append(this_col)
            data['baseline'].append(int(BL_handle.get(), 0))
            data['noise_width'].append(int(NW_handle.get(), 0))
            data['timestamp'].append(datetime.datetime.now())
            data['chip_name'].append(chip_name)

            note_for_df = ''
            if comment_str == '':
                note_for_df = run_str
            else:
                note_for_df = f'{run_str}_{comment_str}'
            data['note'].append(note_for_df)

            # Enable TDC
            enable_TDC_handle.set("1")

            # Disable THCal clock and buffer, enable bypass
            CLKEn_THCal_handle.set("0")
            BufEn_THCal_handle.set("0")
            Bypass_THCal_handle.set("1")
            DAC_handle.set(hex(0x3ff))

            # Send changes to chip
            chip.write_all_block("ETROC2", "Pixel Config")

    BL_df = pandas.DataFrame(data=data)

    with sqlite3.connect(history_file) as sqlconn:
        BL_df.to_sql('baselines', sqlconn, if_exists='append', index=False)

    # Disconnect chip
    conn.disconnect()

def main():
    import argparse

    parser = argparse.ArgumentParser(
                    prog='Make baseline history',
                    description='Control them!',
                    #epilog='Text at the bottom of help'
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
        '-d',
        '--disable_all_pixels',
        help = 'disable_all_pixels',
        action = 'store_true',
        dest = 'disable_all_pixels',
    )
    parser.add_argument(
        '--interval_time',
        metavar = 'TIME',
        type = int,
        help = 'interval between automatlic calibration in seconds',
        required = True,
        dest = 'interval_time',
    )
    parser.add_argument(
        '--global_time',
        metavar = 'TIME',
        type = str,
        help = 'global run time for automatic calibration, eg. 1h, 20m, 30s',
        required = True,
        dest = 'global_time',
    )

    args = parser.parse_args()

    def signal_handler(sig, frame):
        print("Exiting gracefully")
        sys.exit(0)

    total_time = -1
    if 'h' in args.global_time:
        total_time = int(args.global_time.split('h')[0]) * 60 * 60
    elif 'm' in args.global_time:
        total_time = int(args.global_time.split('m')[0]) * 60
    elif 's' in args.global_time:
        total_time = int(args.global_time.split('s')[0])
    else:
        print('Please specify the unit of time (h or m or s)')
        sys.exit(0)

    start_time = time.time()
    count = 0

    while True:
        run_str = f"Run{count}"
        signal.signal(signal.SIGINT, signal_handler)

        run_auto_calibration(
            chip_name = args.chip_name,
            comment_str = args.comment_str,
            run_str = run_str,
            disable_all_pixels = args.disable_all_pixels,
        )
        end_time = time.time()

        if (end_time - start_time > total_time):
            print('Exiting because of time limit')
            sys.exit(0)

        count += 1
        print(f'Sleeping in {args.interval_time}s')
        time.sleep(args.interval_time)

if __name__ == "__main__":
    main()
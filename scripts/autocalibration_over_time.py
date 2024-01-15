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

class Chip_Auto_Cal_Helper:
    def __init__(
        self,
        history_filename: str,
        data_dir: Path = Path('../ETROC-Data/'),
        ):
        # TODO: What if data_dir does not exist?
        # TODO: There is probably a smarter way to handle the file name
        # TODO: In fact, the best approch would be to put these steps outside
        # the class and the class only receives one path variable with the
        # full path to the history file
        self._data_dir = data_dir
        self._history_file_path = data_dir / (history_filename + ".sqlite")

    def run_auto_calibration(
        self,
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
        log_level=logging.WARN
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

        row_indexer_handle,_,_ = chip.get_indexer("row")
        column_indexer_handle,_,_ = chip.get_indexer("column")
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

        data = {
            'row': [],
            'col': [],
            'baseline': [],
            'noise_width': [],
            'timestamp': [],
        }

        note_for_df = ''
        if comment_str == '':
            note_for_df = run_str
        else:
            note_for_df = f'{run_str}_{comment_str}'

        for this_row in tqdm(range(16)):
            for this_col in range(16):

                row_indexer_handle.set(this_row)
                column_indexer_handle.set(this_col)
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
                # print("Scan Done Register: ", ScanDone_handle.get())
                while ScanDone_handle.get() != "1":
                    time.sleep(0.01)
                    chip.read_all_block("ETROC2", "Pixel Status")
                    retry_counter += 1
                    if retry_counter == 5 and ScanDone_handle.get() != "1":
                        print(f"!!!ERROR!!! Scan not done for row {this_row}, col {this_col}!!!")
                        break

                # Disable THCal clock and buffer, enable bypass
                CLKEn_THCal_handle.set("0")
                BufEn_THCal_handle.set("0")
                Bypass_THCal_handle.set("1")
                DAC_handle.set(hex(0x3ff))

                # Send changes to chip
                chip.write_all_block("ETROC2", "Pixel Config")

                data['row'].append(this_row)
                data['col'].append(this_col)
                data['baseline'].append(int(BL_handle.get(), 0))
                data['noise_width'].append(int(NW_handle.get(), 0))
                data['timestamp'].append(datetime.datetime.now())

        BL_df = pandas.DataFrame(data=data)
        BL_df['chip_name'] = chip_name
        BL_df['note'] = note_for_df

        with sqlite3.connect(self._history_file_path) as sqlconn:
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

    cal_helper = Chip_Auto_Cal_Helper(
        history_filename = "BaselineHistory_TID_Jan2024_CERN"
    )

    while True:
        run_str = f"Run{count}"
        signal.signal(signal.SIGINT, signal_handler)

        cal_helper.run_auto_calibration(
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
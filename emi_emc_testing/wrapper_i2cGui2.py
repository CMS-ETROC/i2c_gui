import numpy as np
import pandas as pd

import i2c_gui2
import logging
import datetime
import time

from pathlib import Path
from tqdm import tqdm
from mpl_toolkits.axes_grid1 import make_axes_locatable

import hist
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mplhep as hep
hep.style.use('CMS')

GREEN = '\033[32m'  # ANSI code for green text
RED   = "\033[31m"  # ANSI code for red text
RESET = '\033[0m'   # ANSI code to reset text formatting

class i2c_connection():
    _chips = None

    def __init__(self, port, chip_addresses, ws_addresses, chip_names, clock = 100):
        self.chip_addresses = chip_addresses
        self.ws_addresses = ws_addresses
        self.chip_names = chip_names

        self.fc_clk_delay = {chip_address: 1 for chip_address in self.chip_addresses}
        self.fc_data_delay = {chip_address: 1 for chip_address in self.chip_addresses}

        ## Logger
        log_level = 50
        # logging.basicConfig(format='%(asctime)s - %(levelname)s:%(name)s:%(message)s', stream=sys.stdout, force=True, level=log_level)
        logger = logging.getLogger("Script_Logger")
        logger.setLevel(log_level)
        logger.propagate = False
        self.chip_logger = logging.getLogger("Chip_Logger")
        self.chip_logger.setLevel(log_level)
        self.chip_logger.propagate = False
        self.i2c_logger = logging.getLogger("I2C_Log")
        self.i2c_logger.setLevel(log_level)
        self.i2c_logger.propagate = False
        if not logger.handlers:
            logger.addHandler(logging.NullHandler())
        if not self.chip_logger.handlers:
            self.chip_logger.addHandler(logging.NullHandler())
        if not self.i2c_logger.handlers:
            self.i2c_logger.addHandler(logging.NullHandler())
        self.conn = i2c_gui2.USB_ISS_Helper(port, clock, dummy_connect = False)

        self.BL_df = {}
        for chip_address in chip_addresses:
            self.BL_df[chip_address] = []

    def config_chips(self,
                     do_pixel_check: bool = False,
                     do_basic_peripheral_register_check: bool = False,
                     do_set_chip_peripherals: bool = True,
                     do_disable_all_pixels: bool = False,
                     do_auto_calibration: bool = False,
                     do_disable_and_calibration: bool = False,
                     do_prepare_ws_testing: bool = False,
                     ):

        for chip_address, chip_name, ws_address in zip(self.chip_addresses, self.chip_names, self.ws_addresses):

            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address, ws_address)

            if( do_pixel_check ): self.pixel_check(chip_address, chip)
            if( do_basic_peripheral_register_check ): self.basic_peripheral_register_check(chip_address, chip)
            if( do_set_chip_peripherals ): self.set_chip_peripherals(chip_address, chip)
            if( do_disable_all_pixels ): self.disable_all_pixels(chip_address, chip)
            if( do_auto_calibration ): self.auto_calibration(chip_address, chip_name, chip)
            if ( do_disable_and_calibration ):
                self.disable_all_pixels(chip_address, chip)
                self.auto_calibration(chip_address, chip_name, chip)
            if( do_prepare_ws_testing ): self.prepare_ws_testing(chip_address, ws_address, chip)

    #def __del__(self):
    #    del self.conn


    #--------------------------------------------------------------------------#
    ## Function to get cached chip objects
    def get_chip_i2c_connection(self, chip_address, ws_address=None):
        if self._chips is None:
            self._chips = {}
        if chip_address not in self._chips:
            self._chips[chip_address] = i2c_gui2.ETROC2_Chip(chip_address, ws_address, self.conn, self.chip_logger)
        return self._chips[chip_address]


    #--------------------------------------------------------------------------#
    def get_bl_nw_map(self):
        return self.BL_df


    #--------------------------------------------------------------------------#
    def auto_cal_single_pixel(self, chip_address: list[int], row: int, col: int, bl_nw_output: dict,
                              chip: i2c_gui2.ETROC2_Chip=None, verbose: bool = False):

        if(chip == None and chip_address != None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        elif(chip == None and chip_address == None):
            print("Need chip address to make a new chip in disable pixel!")
            return

        chip.row = row
        chip.col = col

        chip.read_all_block("ETROC2", "Pixel Config")

        # Disable TDC
        chip.set_decoded_value("ETROC2", "Pixel Config", "enable_TDC", 0)
        # Enable THCal clock and buffer, disable bypass
        chip.set_decoded_value("ETROC2", "Pixel Config", "CLKEn_THCal", 1)
        chip.set_decoded_value("ETROC2", "Pixel Config", "BufEn_THCal", 1)
        chip.set_decoded_value("ETROC2", "Pixel Config", "Bypass_THCal", 0)

        # Send changes to chip
        chip.write_all_block("ETROC2", "Pixel Config")

        # Reset the calibration block (active low)
        chip.set_decoded_value("ETROC2", "Pixel Config", "RSTn_THCal", 0)
        chip.write_decoded_value("ETROC2", "Pixel Config", "RSTn_THCal")
        chip.set_decoded_value("ETROC2", "Pixel Config", "RSTn_THCal", 1)
        chip.write_decoded_value("ETROC2", "Pixel Config", "RSTn_THCal")

        # Start and Stop the calibration, (25ns x 2**15 ~ 800 us, ACCumulator max is 2**15)
        chip.set_decoded_value("ETROC2", "Pixel Config", "ScanStart_THCal", 1)
        chip.write_decoded_value("ETROC2", "Pixel Config", "ScanStart_THCal")
        chip.set_decoded_value("ETROC2", "Pixel Config", "ScanStart_THCal", 0)
        chip.write_decoded_value("ETROC2", "Pixel Config", "ScanStart_THCal")

        # Wait for the calibration to be done correctly
        retry_counter = 0
        chip.read_decoded_value("ETROC2", "Pixel Status", "ScanDone")
        while chip.get_decoded_value("ETROC2", "Pixel Status", "ScanDone") != 1:
            time.sleep(0.01)
            chip.read_decoded_value("ETROC2", "Pixel Status", "ScanDone")
            retry_counter += 1
            if retry_counter == 100 and chip.get_decoded_value("ETROC2", "Pixel Status", "ScanDone") != 1:
                print(f"Retry counter reaches at 100! // Auto_Calibration Scan has failed for row {row}, col {col}!!")
                break

        chip.read_all_block("ETROC2", "Pixel Status")

        # Save outputs
        bl_nw_output['row'].append(row)
        bl_nw_output['col'].append(col)
        bl_nw_output['baseline'].append(chip.get_decoded_value("ETROC2", "Pixel Status", "BL"))
        bl_nw_output['noise_width'].append(chip.get_decoded_value("ETROC2", "Pixel Status", "NW"))
        bl_nw_output['timestamp'].append(datetime.datetime.now())

        # Disable TDC
        chip.set_decoded_value("ETROC2", "Pixel Config", "enable_TDC", 0)
        # Disable THCal clock and buffer
        chip.set_decoded_value("ETROC2", "Pixel Config", "CLKEn_THCal", 0)
        chip.set_decoded_value("ETROC2", "Pixel Config", "BufEn_THCal", 0)
        # Enable bypass and set the BL to the DAC
        chip.set_decoded_value("ETROC2", "Pixel Config", "Bypass_THCal", 1)
        chip.set_decoded_value("ETROC2", "Pixel Config", "DAC", 0x3ff)

        # Send changes to chip
        chip.write_all_block("ETROC2", "Pixel Config")

        if(verbose): print(f"Auto calibration done (enTDC=0 + DAC=1023) for pixel ({row},{col}) on chip {hex(chip_address)}, BL={bl_nw_output['baseline'][-1]}, NW={bl_nw_output['noise_width'][-1]}")

    #--------------------------------------------------------------------------#
    def config_TDC_window_ranges_in_memory(self, chip: i2c_gui2.ETROC2_Chip, window_dict: dict = None):

        if window_dict is None:
            window = {
                "upperTOATrig": 0x3ff,
                "lowerTOATrig": 0x000,
                "upperTOTTrig": 0x1ff,
                "lowerTOTTrig": 0x000,
                "upperCalTrig": 0x3ff,
                "lowerCalTrig": 0x000,
                "upperTOA": 0x3ff,
                "lowerTOA": 0x000,
                "upperTOT": 0x1ff,
                "lowerTOT": 0x000,
                "upperCal": 0x3ff,
                "lowerCal": 0x000,
            }

        else:
            window = window_dict

        for key, value in window.items():
            chip.set_decoded_value("ETROC2", "Pixel Config", key, value)

    #--------------------------------------------------------------------------#
    def config_single_pixel(
            self, row: int, col: int,
            chip_address = None,
            Qsel: int = None,
            QInjEn: bool = False,
            Bypass_THCal: bool = True,
            power_mode: str = "low",
            chip: i2c_gui2.ETROC2_Chip=None,
            verbose: bool = False,
        ):

        valid_power_modes = ['low', '010', '101', 'high']

        if power_mode not in valid_power_modes:
            power_mode = "low"
        if(chip == None and chip_address != None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)
        elif(chip == None and chip_address == None):
            print("Need chip address to make a new chip in disable pixel!")
            return

        chip.row = row
        chip.col = col
        chip.read_all_block("ETROC2", "Pixel Config")

        pixel_config_dict = {
            'disDataReadout': 0,
            'QInjEn': 1 if QInjEn else 0,
            'disTrigPath': 0,
            'L1Adelay': 0x01f5,
            'Bypass_THCal': 1 if Bypass_THCal else 0,
            'TH_offset': 0x14,
            'QSel': Qsel if Qsel is not None else 0x1e,
            'DAC': 0x3ff,
            'enable_TDC': 1,
            'IBSel': 0b111,
        }

        self.config_TDC_window_ranges_in_memory(chip=chip)

        if power_mode == "high":
            pixel_config_dict['IBSel'] = 0b000
        elif power_mode == "010":
            pixel_config_dict['IBSel'] = 0b010
        elif power_mode == "101":
            pixel_config_dict['IBSel'] = 0b101
        elif power_mode == "low":
            pixel_config_dict['IBSel'] = 0b111

        for key, value in pixel_config_dict.items():
            chip.set_decoded_value("ETROC2", "Pixel Config", key, value)
        chip.write_all_block("ETROC2", "Pixel Config")

        if(verbose): print(f"Enabled pixel ({row},{col}) for chip: {hex(chip_address)}")

    #--------------------------------------------------------------------------#
    def config_single_pixel_offset(self, chip_address, row: int, col: int, offset: int = 20, chip: i2c_gui2.ETROC2_Chip = None, verbose = False):

        if(chip == None and chip_address != None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        elif(chip == None and chip_address == None):
            print("Need chip address to make a new chip in disable pixel!")
            return

        tmp_df = self.BL_df[chip_address]
        bl =  tmp_df.loc[(tmp_df['row'] == row) & (tmp_df['col'] == col)]['baseline'].values[0]

        chip.row = row
        chip.col = col

        chip.read_decoded_value("ETROC2", "Pixel Config", "DAC")
        old_DAC = chip.get_decoded_value("ETROC2", "Pixel Config", "DAC")

        chip.set_decoded_value("ETROC2", "Pixel Config", "DAC", bl+offset)
        chip.write_decoded_value("ETROC2", "Pixel Config", "DAC")
        new_DAC = chip.get_decoded_value("ETROC2", "Pixel Config", "DAC")

        if verbose:
            print(f'Old DAC value: {old_DAC} is changed to New DAC value: {new_DAC} with offset {offset} for pixel ({row},{col}) (BL={bl}) for chip: {hex(chip_address)}')


    #--------------------------------------------------------------------------#
    ## Power Mode Functions
    def config_power_mode(self, chip_address: int, scan_list: list[tuple], power_mode: str = 'low', verbose: bool = False):

        valid_power_modes = ['low', '010', '101', 'high']

        if power_mode not in valid_power_modes:
            power_mode = "low"

        chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        IBSel = 0b111

        if power_mode == "high":
            IBSel = 0b000
        elif power_mode == "010":
            IBSel = 0b010
        elif power_mode == "101":
            IBSel = 0b101
        elif power_mode == "low":
            IBSel = 0b111

        for row, col in scan_list:
            chip.row = row
            chip.col = col

            chip.set_decoded_value("ETROC2", "Pixel Config", "IBSel", IBSel)
            chip.write_decoded_value("ETROC2", "Pixel Config", "IBSel")

            if(verbose):
                print(f"Set pixel ({row},{col}) to power mode: {IBSel}")


    #--------------------------------------------------------------------------#
    def config_fc_data_delay(self, chip_address: int, fc_clk_delay: int, fc_data_delay: int):

        if fc_clk_delay > 1 or fc_clk_delay < 0:
            raise ValueError('fc_clk_delay value must be 0 or 1')

        if fc_data_delay > 1 or fc_data_delay < 0:
            raise ValueError('fc_data_delay value must be 0 or 1')

        self.fc_clk_delay[chip_address] = fc_clk_delay
        self.fc_data_delay[chip_address] = fc_data_delay

        chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        chip.read_register("ETROC2", "Peripheral Config", "PeriCfg18")

        chip.set_decoded_value("ETROC2", "Peripheral Config", "fcClkDelayEn", fc_clk_delay)
        chip.set_decoded_value("ETROC2", "Peripheral Config", "fcDataDelayEn", fc_data_delay)

        chip.write_register("ETROC2", "Peripheral Config", "PeriCfg18")

        print(f"FC delays has been changed for the chip: {hex(chip_address)}")


    #--------------------------------------------------------------------------#
    ## Library of basic config functions
    # Function 0
    def pixel_check(self, chip_address, chip: i2c_gui2.ETROC2_Chip=None):

        pixel_flag_fail = False
        try:
            if chip == None:
                chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

            for row in range(16):
                for col in range(16):
                    chip.row = row
                    chip.col = col

                    chip.read_decoded_value("ETROC2", "Pixel Status", 'PixelID')
                    fetched_row = chip.get_decoded_value("ETROC2", "Pixel Status", 'PixelID-Row')
                    fetched_col = chip.get_decoded_value("ETROC2", "Pixel Status", 'PixelID-Col')

                    if row != fetched_row or col != fetched_col:
                        print(chip_address, f"Pixel ({row}, {col}) returned ({fetched_row}, {fetched_col}), failed consistency check!")
                        pixel_flag_fail = True

            if not pixel_flag_fail:
                # print(f"Passed pixel check for chip: {hex(chip_address)}")
                return True
            return False

        except Exception as e:
            print(RED+f"An error occurred in pixel_check: {e}"+RESET)
            return False

    #--------------------------------------------------------------------------#
    # Function 1
    def basic_peripheral_register_check(self, chip_address, chip: i2c_gui2.ETROC2_Chip = None):

        try:
            if(chip==None):
                chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

            peri_flag_fail = False
            peripheralRegisterKeys = [i for i in range(32)]

            # Initial read
            chip.read_all_block("ETROC2", "Peripheral Config")

            for peripheralRegisterKey in peripheralRegisterKeys:
                # Fetch the register
                data_PeriCfgX = chip["ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}"]

                # Make the flipped bits
                data_modified_PeriCfgX = data_PeriCfgX ^ 0xff

                # Set the register with the value
                chip["ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}"] = data_modified_PeriCfgX
                chip.write_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")  # Implicit read after write

                # Perform second read to verify the persistence of the change
                data_new_1_PeriCfgX = chip["ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}"]
                chip.read_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
                data_new_2_PeriCfgX = chip["ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}"]

                # Undo the change to recover the original register value, and check for consistency
                chip["ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}"] = data_PeriCfgX
                chip.write_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
                data_recover_PeriCfgX = chip["ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}"]

                # Handle what we learned from the tests
                # print(f"PeriCfg{peripheralRegisterKey:2}", data_bin_PeriCfgX, "To", data_bin_new_1_PeriCfgX,  "To", data_bin_new_2_PeriCfgX, "To", data_bin_recover_PeriCfgX)
                if(data_new_1_PeriCfgX!=data_new_2_PeriCfgX or data_new_2_PeriCfgX!=data_modified_PeriCfgX or data_recover_PeriCfgX!=data_PeriCfgX):
                    print(f"{chip_address}, PeriCfg{peripheralRegisterKey:2}", "FAILURE")
                    peri_flag_fail = True

            # Delete created components
            del peripheralRegisterKeys

            if(not peri_flag_fail):
                # print(f"Passed peripheral write check for chip: {hex(chip_address)}")
                return True
            return False

        except Exception as e:
            print(RED+f"An error occurred in basic_peripheral_register_check: {e}"+RESET)
            return False

    #--------------------------------------------------------------------------#
    # Function 2
    def set_chip_peripherals(self, chip_address, chip: i2c_gui2.ETROC2_Chip = None):
        try:
            if(chip == None):
                chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

            chip.read_all_block("ETROC2", "Peripheral Config")

            chip.set_decoded_value("ETROC2", "Peripheral Config", "EFuse_Prog", 0x00017f0f)           # chip ID
            chip.set_decoded_value("ETROC2", "Peripheral Config", "singlePort", 1)           # Set data output to right port only
            chip.set_decoded_value("ETROC2", "Peripheral Config", "serRateLeft", 0b00)          # Set Data Rates to 320 mbps
            chip.set_decoded_value("ETROC2", "Peripheral Config", "serRateRight", 0b00)         # ^^
            chip.set_decoded_value("ETROC2", "Peripheral Config", "onChipL1AConf", 0b00)        # Switches off the onboard L1A
            chip.set_decoded_value("ETROC2", "Peripheral Config", "PLL_ENABLEPLL", 1)        # "Enable PLL mode, active high. Debugging use only."
            chip.set_decoded_value("ETROC2", "Peripheral Config", "chargeInjectionDelay", 0x0a) # User tunable delay of Qinj pulse
            chip.set_decoded_value("ETROC2", "Peripheral Config", "triggerGranularity", 0x01)   # only for trigger bit
            chip.set_decoded_value("ETROC2", "Peripheral Config", "fcClkDelayEn", self.fc_clk_delay[chip_address])
            chip.set_decoded_value("ETROC2", "Peripheral Config", "fcDataDelayEn", self.fc_data_delay[chip_address])

            chip.write_all_block("ETROC2", "Peripheral Config")

            # print(f"Peripherals set for chip: {hex(chip_address)}")

        except Exception as e:
            print(RED+f"An error occurred in set_chip_peripherals: {e}"+RESET)

    #--------------------------------------------------------------------------#
    # Function 3
    def disable_all_pixels(self, chip_address, power_mode = 'low', chip: i2c_gui2.ETROC2_Chip = None):

        if(chip==None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        chip.row = 0
        chip.col = 0
        chip.read_all_block("ETROC2", "Pixel Config")

        IBSel = 0b111

        if power_mode == "high":
            IBSel = 0b000
        elif power_mode == "010":
            IBSel = 0b010
        elif power_mode == "101":
            IBSel = 0b101
        elif power_mode == "low":
            IBSel = 0b111

        # Define pixel configuration settings
        pixel_config = {
            "disDataReadout": 1,
            "QInjEn": 0,
            "disTrigPath": 1,
            "upperTOATrig": 0x000,
            "lowerTOATrig": 0x000,
            "upperTOTTrig": 0x1ff,
            "lowerTOTTrig": 0x1ff,
            "upperCalTrig": 0x3ff,
            "lowerCalTrig": 0x3ff,
            "upperTOA": 0x000,
            "lowerTOA": 0x000,
            "upperTOT": 0x1ff,
            "lowerTOT": 0x1ff,
            "upperCal": 0x3ff,
            "lowerCal": 0x3ff,
            "enable_TDC": 0,
            "IBSel": IBSel,  # Low power mode
            "Bypass_THCal": 1,  # Bypass Mode
            "TH_offset": 0x3f,  # Max Offset
            "DAC": 0x3ff,  # Max DAC
        }

        # Set pixel configuration values on the chip
        for key, value in pixel_config.items():
            chip.set_decoded_value("ETROC2", "Pixel Config", key, value)

        chip.broadcast = True
        chip.write_all_block("ETROC2", "Pixel Config")
        chip.broadcast = False

        # try:
        #     chip.broadcast = True
        #     chip.write_all_block("ETROC2", "Pixel Config")
        #     chip.broadcast = False
        #     print(f"Disabled pixels (Bypass, TH-3f DAC-3ff) for chip: {hex(chip_address)}")

        #     # Verify broadcast
        #     print('Verifying Broadcast results')
        #     for row in tqdm(range(16), desc="Checking broadcast for row", position=0):
        #         for col in range(16):
        #             chip.row = row
        #             chip.col = col

        #             chip.read_all_block("ETROC2", "Pixel Config")

        #             for key, value in pixel_config.items():
        #                 if chip.get_decoded_value("ETROC2", "Pixel Config", key) != value:
        #                     raise RuntimeError("Failed to verify broadcast results")

        # except RuntimeError as err:
        #     ### Broadcast failed
        #     print(err)
        #     print("Broadcast failed! Will manually disable pixels\n")
        #     for row in tqdm(range(16), desc="Disabling row", position=0):
        #         for col in range(16):
        #             chip.row = row
        #             chip.col = col

        #             chip.read_all_block("ETROC2", "Pixel Config")

        #             for key, value in pixel_config.items():
        #                 chip.set_decoded_value("ETROC2", "Pixel Config", key, value)

        #             chip.write_all_block("ETROC2", "Pixel Config")

        #     print(f"Disabled pixels (Bypass, TH-3f DAC-3ff) for chip: {hex(chip_address)}")


    #--------------------------------------------------------------------------#
    # Function 4
    def auto_calibration(self, chip_address, chip_name, chip: i2c_gui2.ETROC2_Chip = None, ver_on: bool = False):

        if(chip == None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        bl_nw_dict = {
            'row': [],
            'col': [],
            'baseline': [],
            'noise_width': [],
            'timestamp': [],
        }

        # Loop for threshold calibration
        for row in tqdm(range(16), desc="Calibrating row", position=0):
            for col in range(16):
                self.auto_cal_single_pixel(chip_address=chip_address, row=row, col=col, bl_nw_output=bl_nw_dict, chip=chip, verbose=ver_on)

        bl_nw_df = pd.DataFrame(data = bl_nw_dict)
        bl_nw_df['chip_name'] = chip_name

        self.BL_df[chip_address] = bl_nw_df
        del bl_nw_dict, bl_nw_df

        print(f"Auto calibration finished for chip: {hex(chip_address)}")

    def auto_calibration_select_pixels(self, chip_address, chip_name, chip: i2c_gui2.ETROC2_Chip = None, ver_on: bool = False, pixels=[]):
        if(chip == None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)
        bl_nw_dict = {
            'row': [],
            'col': [],
            'baseline': [],
            'noise_width': [],
            'timestamp': [],
        }
        for row,col in tqdm(pixels, desc="Calibrating pixels", position=0):
            self.auto_cal_single_pixel(chip_address=chip_address, row=row, col=col, bl_nw_output=bl_nw_dict, chip=chip, verbose=ver_on)
        bl_nw_df = pd.DataFrame(data = bl_nw_dict)
        bl_nw_df['chip_name'] = chip_name
        self.BL_df[chip_address] = bl_nw_df
        del bl_nw_dict, bl_nw_df

    #--------------------------------------------------------------------------#
    def make_BL_NW_2D_maps(self, input_df: pd.DataFrame, given_chip_name: str, note: str, save_path, timestamp):
        ## Make BL and NW 2D map
        fig = plt.figure(dpi=200, figsize=(20,10))
        gs = fig.add_gridspec(1,2)
        ax0 = fig.add_subplot(gs[0,0])
        ax0.set_title(f"{given_chip_name}: BL (DAC LSB)\n{note}", size=17, loc="right")
        img0 = ax0.imshow(input_df.baseline, interpolation='none', vmin=input_df.baseline.to_numpy().reshape(-1).min(), vmax=input_df.baseline.to_numpy().reshape(-1).max())
        ax0.set_aspect("equal")
        ax0.invert_xaxis()
        ax0.invert_yaxis()
        plt.xticks(range(16), range(16), rotation="vertical")
        plt.yticks(range(16), range(16))
        hep.cms.text(loc=0, ax=ax0, fontsize=17, text="ETL ETROC")
        divider = make_axes_locatable(ax0)
        cax = divider.append_axes('right', size="5%", pad=0.05)
        fig.colorbar(img0, cax=cax, orientation="vertical")

        ax1 = fig.add_subplot(gs[0,1])
        ax1.set_title(f"{given_chip_name}: NW (DAC LSB)\n{note}", size=17, loc="right")
        img1 = ax1.imshow(input_df.noise_width, interpolation='none', vmin=0, vmax=16)
        ax1.set_aspect("equal")
        ax1.invert_xaxis()
        ax1.invert_yaxis()
        plt.xticks(range(16), range(16), rotation="vertical")
        plt.yticks(range(16), range(16))
        hep.cms.text(loc=0, ax=ax1, fontsize=17, text="ETL ETROC")
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right', size="5%", pad=0.05)
        fig.colorbar(img1, cax=cax, orientation="vertical")

        bl_threshold = 0.55 * (input_df.baseline.values.max() - input_df.baseline.values.min()) + input_df.baseline.values.min()

        for col in range(16):
            for row in range(16):

                bl_value = int(input_df.baseline[col][row])
                nw_value = int(input_df.noise_width[col][row])
                bl_text_color = 'black' if bl_value > bl_threshold else 'white'
                nw_text_color = 'black' if nw_value > 9 else 'white'

                ax0.text(col,row, bl_value, c=bl_text_color, size=10, rotation=45, fontweight="bold", ha="center", va="center")
                ax1.text(col,row, nw_value, c=nw_text_color, size=11, rotation=45, fontweight="bold", ha="center", va="center")

        plt.tight_layout()
        fig.savefig(save_path / f'{given_chip_name}_BL_NW_2D_map_{timestamp}.png')

        del fig


    def make_BL_NW_1D_hists(self, input_df: pd.DataFrame, given_chip_name: str, note: str, save_path, timestamp):
        fig, axes = plt.subplots(1, 2, figsize=(20, 10))
        hep.cms.text(loc=0, ax=axes[0], fontsize=17, text="ETL ETROC")
        axes[0].set_title(f"{given_chip_name}: BL (DAC LSB)\n{note}", size=17, loc="right")
        bl_array = input_df['baseline'].to_numpy().flatten()
        bl_hist = hist.Hist(hist.axis.Regular(128, 0, 1024, name='bl', label='BL [DAC]'))
        bl_hist.fill(bl_array)
        mean, std = bl_array.mean(), bl_array.std()
        bl_hist.plot1d(ax=axes[0], yerr=False, label=f'Mean: {mean:.2f}, Std: {std:.2f}')
        axes[0].legend()

        hep.cms.text(loc=0, ax=axes[1], fontsize=17, text="ETL ETROC")
        axes[1].set_title(f"{given_chip_name}: NW (DAC LSB)\n{note}", size=17, loc="right")
        nw_hist = hist.Hist(hist.axis.Regular(16, 0, 16, name='nw', label='NW [DAC]'))
        nw_array = input_df['noise_width'].to_numpy().flatten()
        nw_hist.fill(nw_array)
        mean, std = nw_array.mean(), nw_array.std()
        nw_hist.plot1d(ax=axes[1], yerr=False, label=f'Mean: {mean:.2f}, Std: {std:.2f}')
        axes[1].xaxis.set_major_locator(ticker.MultipleLocator(1))
        axes[1].xaxis.set_minor_locator(ticker.NullLocator())
        axes[1].legend()

        plt.tight_layout()
        fig.savefig(save_path / f'{given_chip_name}_BL_NW_1D_hist_{timestamp}.png')

        del fig, axes


    #--------------------------------------------------------------------------#
    def save_baselines(
            self,
            hist_dir: str = "../ETROC-History",
            save_notes: str = "",
        ):

        import sqlite3

        save_mother_path = Path(hist_dir)
        save_mother_path.mkdir(exist_ok=True, parents=True)
        outfile = save_mother_path / 'BaselineHistory.sqlite'

        fig_outdir = save_mother_path / 'baseline_figures'
        fig_outdir.mkdir(exist_ok=True, parents=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

        for idx, chip_address in enumerate(self.chip_addresses):

            current_df = self.BL_df[chip_address]
            pivot_df = current_df.pivot(index=['row'], columns=['col'], values=['baseline', 'noise_width'])

            ### Save baseline into SQL
            current_df.loc[:, "save_notes"] = save_notes
            with sqlite3.connect(outfile) as sqlconn:
                current_df.to_sql('baselines', sqlconn, if_exists='append', index=False)

            self.make_BL_NW_2D_maps(pivot_df, self.chip_names[idx], save_notes, fig_outdir, timestamp)
            self.make_BL_NW_1D_hists(current_df, self.chip_names[idx], save_notes, fig_outdir, timestamp)


    #--------------------------------------------------------------------------#
    def enable_select_pixels_in_chips(
            self,
            pixel_list: list[tuple],
            Qsel: int = None,
            QInjEn: bool = True,
            Bypass_THCal: bool = True,
            power_mode: str = "low",
            verbose: bool = False,
        ):
            valid_power_modes = ['low', '010', '101', 'high']

            if power_mode not in valid_power_modes:
                power_mode = "low"

            for chip_address in self.chip_addresses:

                chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

                for row, col in tqdm(pixel_list, desc="Enabling pixels"):
                    self.config_single_pixel(row=row, col=col, chip_address=chip_address, Qsel=Qsel, QInjEn=QInjEn,
                                             Bypass_THCal=Bypass_THCal, power_mode=power_mode, chip=chip, verbose=verbose)


    def set_chip_offsets(self, chip_address, pixel_list: list[tuple] = None, offset: int = 20, chip: i2c_gui2.ETROC2_Chip=None, verbose=False):

        if(chip == None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        if pixel_list is None:
            raise ValueError('Please specify the pixel of interests in the input argument')

        for row,col in pixel_list:
            self.config_single_pixel_offset(chip_address=chip_address, row=row, col=col, offset=offset, chip=chip, verbose=verbose)

        # print(f"Offset set to {hex(offset)} for chip: {hex(chip_address)}")


    def set_chip_offsets_broadcast(self, chip_address, offset: int = 20, chip: i2c_gui2.ETROC2_Chip = None):

        if(chip==None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        chip.row = 0
        chip.col = 0

        chip.read_decoded_value("ETROC2", "Pixel Config", "TH_offset")
        chip.set_decoded_value("ETROC2", "Pixel Config", "TH_offset", offset)

        try:
            chip.broadcast = True
            chip.write_decoded_value("ETROC2", "Pixel Config", "TH_offset")
            chip.broadcast = False

            print('Verifying Broadcast results')
            for row in tqdm(range(16), desc="Checking broadcast for row", position=0):
                for col in range(16):
                    chip.row = row
                    chip.col = col

                    chip.read_decoded_value("ETROC2", "Pixel Config", "TH_offset")
                    if chip.get_decoded_value("ETROC2", "Pixel Config", "TH_offset") != offset:
                        raise RuntimeError("Failed to verify broadcast results")

        except RuntimeError as err:
            print(err)
            col_list, row_list = np.meshgrid(np.arange(16),np.arange(16))
            scan_list = list(zip(row_list.flatten(),col_list.flatten()))
            for row,col in scan_list:
                self.config_single_pixel_offset(chip_address=chip_address, row=row, col=col, offset=offset, chip=chip)

        print(f"Offset set to {hex(offset)} for chip: {hex(chip_address)}")

    #--------------------------------------------------------------------------#
    ## Chip Calibration Util Functions
    def onchipL1A(self, chip_address, chip: i2c_gui2.ETROC2_Chip = None, comm = '00'):

        if(chip == None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        chip.read_decoded_value("ETROC2", "Peripheral Config", 'onChipL1AConf')
        chip.set_decoded_value("ETROC2", "Peripheral Config", 'onChipL1AConf', int(comm, base=2))
        chip.write_decoded_value("ETROC2", "Peripheral Config", 'onChipL1AConf')

        print(f"OnChipL1A action {comm} done for chip: {hex(chip_address)}")

    def asyAlignFastcommand(self, chip_address, chip: i2c_gui2.ETROC2_Chip = None):

        if(chip == None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        chip.read_decoded_value("ETROC2", "Peripheral Config", 'asyAlignFastcommand')
        chip.set_decoded_value("ETROC2", "Peripheral Config", 'asyAlignFastcommand', 1)
        chip.write_decoded_value("ETROC2", "Peripheral Config", 'asyAlignFastcommand')
        time.sleep(0.1)
        chip.set_decoded_value("ETROC2", "Peripheral Config", 'asyAlignFastcommand', 0)
        chip.write_decoded_value("ETROC2", "Peripheral Config", 'asyAlignFastcommand')

        # print(f"asyAlignFastcommand action done for chip: {hex(chip_address)}")

    def asyResetGlobalReadout(self, chip_address, chip: i2c_gui2.ETROC2_Chip = None):

        if(chip == None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        chip.read_decoded_value("ETROC2", "Peripheral Config", 'asyResetGlobalReadout')
        chip.set_decoded_value("ETROC2", "Peripheral Config", 'asyResetGlobalReadout', 0)
        chip.write_decoded_value("ETROC2", "Peripheral Config", 'asyResetGlobalReadout')
        time.sleep(0.1)
        chip.set_decoded_value("ETROC2", "Peripheral Config", 'asyResetGlobalReadout', 1)
        chip.write_decoded_value("ETROC2", "Peripheral Config", 'asyResetGlobalReadout')

        # print(f"Reset Global Readout done for chip: {hex(chip_address)}")

    def calibratePLL(self, chip_address, chip: i2c_gui2.ETROC2_Chip = None):

        if(chip == None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        ### PLL Reset
        chip.read_decoded_value("ETROC2", "Peripheral Config", 'asyPLLReset')
        chip.set_decoded_value("ETROC2", "Peripheral Config", 'asyPLLReset', 0)
        chip.write_decoded_value("ETROC2", "Peripheral Config", 'asyPLLReset')
        time.sleep(0.1)
        chip.set_decoded_value("ETROC2", "Peripheral Config", 'asyPLLReset', 1)
        chip.write_decoded_value("ETROC2", "Peripheral Config", 'asyPLLReset')

        ### asyStartCalibration
        chip.read_decoded_value("ETROC2", "Peripheral Config", 'asyStartCalibration')
        chip.set_decoded_value("ETROC2", "Peripheral Config", 'asyStartCalibration', 0)
        chip.write_decoded_value("ETROC2", "Peripheral Config", 'asyStartCalibration')
        time.sleep(0.1)
        chip.set_decoded_value("ETROC2", "Peripheral Config", 'asyStartCalibration', 1)
        chip.write_decoded_value("ETROC2", "Peripheral Config", 'asyStartCalibration')

        # print(f"PLL Calibrated for chip: {hex(chip_address)}")


    #--------------------------------------------------------------------------#
    def i2c_dumping(
        self,
        chip_address: int,
        ws_address: int,
        outdir: Path,
        chip_name: str,
        fname: str,
        full: bool,
    ):
        chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address, ws_address)
        start_time = time.time()

        if full:
            chip.read_all()
        else:
            chip.read_all_efficient()

        end_time = time.time()
        chip.save_config(outdir / f"{chip_name}_{fname}{'_full' if full else ''}.pckl")

        print("--- %s seconds ---" % (end_time - start_time))

    def i2c_loading(
        self,
        chip_address: int,
        ws_address: int,
        outdir: Path,
        chip_name: str,
        fname: str,
        full: bool,
    ):
        chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address, ws_address)
        chip.load_config(outdir / f"{chip_name}_{fname}{'_full' if full else ''}.pckl")

        start_time = time.time()

        if full:
            chip.write_all()
        else:
            chip.write_all_efficient()

        end_time = time.time()

        print("--- %s seconds ---" % (end_time - start_time))

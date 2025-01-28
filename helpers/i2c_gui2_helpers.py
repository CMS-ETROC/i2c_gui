import i2c_gui2
import logging
import datetime
import time

import numpy as np
import pandas as pd

from tqdm import tqdm

class i2c_connection():
    _chips = None

    def __init__(self, port, chip_addresses, ws_addresses, chip_names, clock = 100):
        self.chip_addresses = chip_addresses
        self.ws_addresses = ws_addresses
        self.chip_names = chip_names
        # 2-tuple of binary numbers represented as strings ("0","1")
        # Here "0" is the "fcClkDelayEn" and "1" is the fcDataDelayEn
        ## Logger
        log_level=30
        logging.basicConfig(format='%(asctime)s - %(levelname)s:%(name)s:%(message)s')
        logger = logging.getLogger("Script_Logger")
        self.chip_logger = logging.getLogger("Chip_Logger")
        self.conn = i2c_gui2.USB_ISS_Helper(port, clock, dummy_connect = False)
        logger.setLevel(log_level)

        self.BL_df = {}
        for chip_address in chip_addresses:
            self.BL_df[chip_address] = []

    # func_string is an 8-bit binary number, LSB->MSB is function 0->7
    # "0" means don't call the corr function, and vice-versa
    def config_chips(self,
                     do_pixel_check: bool = False,
                     do_basic_peripheral_register_check: bool = False,
                     do_set_chip_peripherals: bool = False,
                     do_disable_all_pixels: bool = False,
                     do_auto_calibration: bool = False,

                     func_string = '00000000'):

        for chip_address, chip_name, ws_address in zip(self.chip_addresses, self.chip_names, self.ws_addresses):

            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address, ws_address)

            if( do_pixel_check ): self.pixel_check(chip_address, chip)
            if( do_basic_peripheral_register_check ): self.basic_peripheral_register_check(chip_address, chip)
            if( do_set_chip_peripherals ): self.set_chip_peripherals(chip_address, chip)
            if( do_disable_all_pixels ): self.disable_all_pixels(chip_address, chip, check_broadcast=True)
            if( do_auto_calibration ): self.auto_calibration(chip_address, chip_name, chip)
            if(int(func_string[-6])):
                if( do_disable_all_pixels ):
                    self.auto_calibration_and_disable(chip_address, chip_name, chip, check_broadcast=True)
                else:
                    self.auto_calibration_and_disable(chip_address, chip_name, chip, check_broadcast=False)
            if(int(func_string[-7])): self.set_chip_offsets(chip_address, offset=20, chip=chip)
            if(int(func_string[-8])): self.prepare_ws_testing(chip_address, ws_address, chip)

    def __del__(self):
        del self.conn


    #--------------------------------------------------------------------------#
    ## Function to get cached chip objects
    def get_chip_i2c_connection(self, chip_address, ws_address=None):
        if self._chips is None:
            self._chips = {}

        if chip_address not in self._chips:
            self._chips[chip_address] = i2c_gui2.ETROC2_Chip(chip_address, ws_address, self.conn, self.chip_logger)

        # logger.setLevel(log_level)
        return self._chips[chip_address]

    #--------------------------------------------------------------------------#
    def auto_cal_single_pixel(self, chip_address: list[int], row: int, col: int, bl_nw_output: dict,
                              chip: i2c_gui2.ETROC2_Chip=None, verbose: bool = False):

        if(chip == None and chip_address != None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        elif(chip == None and chip_address == None):
            print("Need chip address to make a new chip in disable pixel!")
            return

        chip.set_indexer('row', row)
        chip.set_indexer('column', col)

        chip.read_all_block("ETROC2", "Pixel Config")

        # Disable TDC
        chip.set_decoded_value("ETROC2", "Pixel Config", "enable_TDC", 0)
        # Enable THCal clock and buffer, disable bypass
        chip.set_decoded_value("ETROC2", "Pixel Config", "CLKEn_THCal", 1)
        chip.set_decoded_value("ETROC2", "Pixel Config", "BufEn_THCal", 1)
        chip.set_decoded_value("ETROC2", "Pixel Config", "Bypass_THCal", 0)
        # chip.set_decoded_value("ETROC2", "Pixel Config", "TH_offset", 0x0a)

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
        chip.read_all_block("ETROC2", "Pixel Status")
        while chip.get_decoded_value("ETROC2", "Pixel Status", "ScanDone") != 1:
            time.sleep(0.01)
            chip.read_all_block("ETROC2", "Pixel Status")
            retry_counter += 1
            if retry_counter == 5 and chip.get_decoded_value("ETROC2", "Pixel Status", "ScanDone") != 1:
                print(f"Retry counter reaches at 5! // Auto_Calibration Scan has failed for row {row}, col {col}!!")
                break

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

        if(verbose): print(f"Auto calibration done (enTDC=0 + DAC=1023) for pixel ({row},{col}) on chip: {hex(chip_address)}")




    #--------------------------------------------------------------------------#
    ## Library of basic config functions
    # Function 0
    def pixel_check(self, chip_address, chip: i2c_gui2.ETROC2_Chip=None):

        pixel_flag_fail = False

        if chip == None:
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        for row in range(16):
            for col in range(16):
                chip.set_indexer('row', row)
                chip.set_indexer('column', col)

                fetched_row = chip.get_decoded_value("ETROC2", "Pixel Status", 'PixelID-Row')
                fetched_col = chip.get_decoded_value("ETROC2", "Pixel Status", 'PixelID-Col')

                if row != fetched_row or col != fetched_col:
                    print(chip_address, f"Pixel ({row},{col}) returned ({fetched_row}{fetched_col}), failed consistency check!")
                    pixel_flag_fail = True

        if not pixel_flag_fail:
            print(f"Passed pixel check for chip: {hex(chip_address)}")

    #--------------------------------------------------------------------------#
    # Function 1
    def basic_peripheral_register_check(self, chip_address, chip: i2c_gui2.ETROC2_Chip = None):

        if(chip==None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        peri_flag_fail = False
        peripheralRegisterKeys = [i for i in range(32)]

        # Initial read
        chip.read_all_block("ETROC2", "Peripheral Config")

        for peripheralRegisterKey in peripheralRegisterKeys:
            # Fetch the register
            data_PeriCfgX = chip.get_decoded_value("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
            # Make the flipped bits
            data_modified_PeriCfgX = data_PeriCfgX ^ 0xff

            # Set the register with the value
            chip.set_decoded_value("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}", data_modified_PeriCfgX)
            chip.write_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}", readback_check=True)  # Implicit read after write

            # Perform second read to verify the persistence of the change
            data_new_1_PeriCfgX = chip.get_decoded_value("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
            chip.read_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")
            data_new_2_PeriCfgX = chip.get_decoded_value("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")

            # Undo the change to recover the original register value, and check for consistency
            chip.set_decoded_value("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}", data_PeriCfgX)
            chip.write_register("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}", readback_check=True)
            data_recover_PeriCfgX = chip.get_decoded_value("ETROC2", "Peripheral Config", f"PeriCfg{peripheralRegisterKey}")

            # Handle what we learned from the tests
            # print(f"PeriCfg{peripheralRegisterKey:2}", data_bin_PeriCfgX, "To", data_bin_new_1_PeriCfgX,  "To", data_bin_new_2_PeriCfgX, "To", data_bin_recover_PeriCfgX)
            if(data_new_1_PeriCfgX!=data_new_2_PeriCfgX or data_new_2_PeriCfgX!=data_modified_PeriCfgX or data_recover_PeriCfgX!=data_PeriCfgX):
                print(f"{chip_address}, PeriCfg{peripheralRegisterKey:2}", "FAILURE")
                peri_flag_fail = True

        if(not peri_flag_fail):
            print(f"Passed peripheral write check for chip: {hex(chip_address)}")

        # Delete created components
        del peripheralRegisterKeys


    #--------------------------------------------------------------------------#
    # Function 2
    def set_chip_peripherals(self, chip_address, chip: i2c_gui2.ETROC2_Chip = None):

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
        chip.set_decoded_value("ETROC2", "Peripheral Config", "fcClkDelayEn", 1)
        chip.set_decoded_value("ETROC2", "Peripheral Config", "fcDataDelayEn", 1)

        chip.write_all_block("ETROC2", "Peripheral Config")

        print(f"Peripherals set for chip: {hex(chip_address)}")


    #--------------------------------------------------------------------------#
    # Function 3
    def disable_all_pixels(self, chip_address, chip: i2c_gui2.ETROC2_Chip = None):

        if(chip==None):
            chip: i2c_gui2.ETROC2_Chip = self.get_chip_i2c_connection(chip_address)

        chip.set_indexer('row', 0)
        chip.set_indexer('column', 0)
        chip.read_all_block("ETROC2", "Pixel Config")

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
            "IBSel": 0,  # High power mode
            "Bypass_THCal": 1,  # Bypass Mode
            "TH_offset": 0x3f,  # Max Offset
            "DAC": 0x3ff,  # Max DAC
        }

        # Set pixel configuration values on the chip
        for key, value in pixel_config.items():
            chip.set_decoded_value("ETROC2", "Pixel Config", key, value)

        chip.set_indexer('broadcast', 1)
        chip.write_all_block("ETROC2", "Pixel Config")
        chip.set_indexer('broadcast', 0)
        print(f"Disabled pixels (Bypass, TH-3f DAC-3ff) for chip: {hex(chip_address)}")

        # Verify broadcast
        print('Verifying Broadcast results')
        broadcast_ok = True
        for row in tqdm(range(16), desc="Checking broadcast for row", position=0):
            for col in range(16):
                chip.set_indexer('row', row)
                chip.set_indexer('column', col)

                chip.read_all_block("ETROC2", "Pixel Config")

                for key, value in pixel_config.items():
                    if chip.get_decoded_value("ETROC2", "Pixel Config", key) != value:
                        broadcast_ok = False
                        break
                if not broadcast_ok:
                    break
            if not broadcast_ok:
                break

        # Handle broadcast failure
        if not broadcast_ok:
            print("Broadcast failed! \n Will manually disable pixels")
            for row in tqdm(range(16), desc="Disabling row", position=0):
                for col in range(16):
                    chip.set_indexer('row', row)
                    chip.set_indexer('column', col)

                    chip.read_all_block("ETROC2", "Pixel Config")

                    for key, value in pixel_config.items():
                        chip.set_decoded_value("ETROC2", "Pixel Config", key, value)

                    chip.write_all_block("ETROC2", "Pixel Config")

            print(f"Disabled pixels (Bypass, TH-3f DAC-3ff) for chip: {hex(chip_address)}")


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
import wrapper_i2cGui2
import argparse
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def run_i2c(i2c_port, chip_addresses, ws_addresses, chip_names, output_path):

    try:
        i2c_conn = wrapper_i2cGui2.i2c_connection(i2c_port, chip_addresses, ws_addresses, chip_names)
    except:
        raise RuntimeError("Failed to create I2C GUI Conn Object. Please reconnect the cable to SB-ISS module")

    try:
        for chip_address in chip_addresses[:]:
            i2c_conn.calibratePLL(chip_address, chip=None)
        for chip_address in chip_addresses[:]:
            i2c_conn.asyResetGlobalReadout(chip_address, chip=None)
            i2c_conn.asyAlignFastcommand(chip_address, chip=None)
        logger.info("SUCCESS: PLL and FC calibration")
    except Exception as e:
        raise RuntimeError(f"An error, {e}, occured during first pll/fc calibration")

    for chip_address, chip_name, ws_address in zip(chip_addresses, chip_names, ws_addresses):
        chip = i2c_conn.get_chip_i2c_connection(chip_address, ws_address)

        # Pixel ID Check
        # pixel_check_result = i2c_conn.pixel_check(chip_address, chip)
        # if pixel_check_result:
        #     logger.info("SUCCESS: Pixel ID Check")
        # else:
        #     logger.error("FAILURE: Pixel ID Check")

        # # Peripheral Register Check
        # peri_reg_result = i2c_conn.basic_peripheral_register_check(chip_address, chip)
        # if peri_reg_result:
        #     logger.info("SUCCESS: Peri Reg Check")
        # else:
        #     logger.error("FAILURE: Peri Reg Check")

        i2c_conn.set_chip_peripherals(chip_address, chip)
        i2c_conn.disable_all_pixels(chip_address, 'high', chip)

        pixels_of_interest = [(r, c) for r in range(16) for c in range(16)]

        i2c_conn.auto_calibration_select_pixels(chip_address, chip_name, chip, pixels=pixels_of_interest)
        now = datetime.now().isoformat(sep=' ', timespec='seconds')
        i2c_conn.save_baselines(hist_dir=output_path, save_notes=f'{now}')

        bl_mw_map = i2c_conn.get_bl_nw_map()
        logger.info("\n%s", bl_mw_map[chip_address][['row', 'col', 'baseline', 'noise_width']].head(10))

    pixel_for_test = [(2, 2), (2, 10), (10, 2), (10, 10), (5, 5), (5, 13), (13, 5), (13, 13)]
    logger.info("Enable pixels for S-curve and qinj testing")
    logger.info("Testing Pixels: %s", pixel_for_test)
    i2c_conn.enable_select_pixels_in_chips(pixel_for_test, Qsel=30, QInjEn=True, Bypass_THCal=True, power_mode='high', verbose=False)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
            prog='PlaceHolder',
            description='PlaceHolder',
    )

    parser.register('type', 'hex', lambda s: int(s, 16))

    parser.add_argument(
        '--boardName',
        metavar = 'NAME',
        type = str,
        help = 'Any name representing your DUT',
        required = True,
        dest = 'boardName',
    )

    parser.add_argument(
        '--port',
        metavar = 'PORT',
        type = str,
        help = 'port including path to your i2c device',
        default = '/dev/ttyACM0',
        dest = 'port',
    )

    parser.add_argument(
        '--outDir',
        metavar = 'DIR',
        type = str,
        help = 'path to the output directory to store outputs',
        default = '/home/daq/ETROC2/ETROC-History/EMI_EMC',
        dest = 'outDir',
    )

    parser.add_argument(
        '--address',
        metavar = 'ADDR',
        type='hex',
        help = 'main I2C address of the ETROC chip',
        default = 0x60,
        dest = 'address',
    )

    parser.add_argument(
        '--wsAddress',
        metavar = 'ADDR',
        type='hex',
        help = 'I2C address of the waveform sampler of the ETROC chip',
        default = 0x40,
        dest = 'address',
    )

    args = parser.parse_args()

    i2c_port = args.port
    chip_addresses = [args.address]
    ws_addresses = [args.wsAddress]
    chip_names = [f"{args.boardName}"]
    output_path = f"{args.outDir}/{args.boardName}"

    run_i2c(i2c_port, chip_addresses, ws_addresses, chip_names, output_path)

from wafer_probing import *
import argparse
import logging
import sys

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
        i2c_conn = i2c_connection(i2c_port, chip_addresses, ws_addresses, chip_names)
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

    pixels_of_interest = [(2, 2), (2, 10), (10, 2), (10, 10), (5, 5), (5, 13), (13, 5), (13, 13)]
    for chip_address, chip_name, ws_address in zip(chip_addresses, chip_names, ws_addresses):
        chip = i2c_conn.get_chip_i2c_connection(chip_address, ws_address)
        
        # Pixel ID Check
        pixel_check_result = i2c_conn.pixel_check(chip_address, chip)
        if pixel_check_result:
            logger.info("SUCCESS: Pixel ID Check")
        else:
            logger.error("FAILURE: Pixel ID Check")
        
        # Peripheral Register Check
        peri_reg_result = i2c_conn.basic_peripheral_register_check(chip_address, chip)
        if peri_reg_result:
            logger.info("SUCCESS: Peri Reg Check")
        else:
            logger.error("FAILURE: Peri Reg Check")
        
        i2c_conn.set_chip_peripherals(chip_address, chip)
        i2c_conn.disable_all_pixels(chip_address, 'high', chip)

        # if do_full_chip:
        #     col_list, row_list = np.meshgrid(np.arange(16),np.arange(16))
        #     pixels_of_interest = list(zip(row_list.flatten(),col_list.flatten()))
        # else:
        #     pixels_of_interest = [(2, 2), (2, 10), (10, 2), (10, 10), (5, 5), (5, 13), (13, 5), (13, 13)]

        i2c_conn.auto_calibration_select_pixels(chip_address, chip_name, chip, pixels=pixels_of_interest)
        now = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
        i2c_conn.save_baselines(hist_dir=output_path, save_notes=f'{now}', maps=False)

        bl_mw_map = i2c_conn.get_bl_nw_map()
        print(bl_mw_map[chip_address][['row', 'col', 'baseline', 'noise_width']].head(10))

    # i2c_conn.enable_select_pixels_in_chips(pixels_of_interest, Qsel=30, QInjEn=True, Bypass_THCal=True, power_mode=power_mode, verbose=False)

    # for chip_address in chip_addresses:
    #     chip = i2c_conn.get_chip_i2c_connection(chip_address)
    #     i2c_conn.set_chip_offsets(chip_address, pixel_list=pixels_of_interest, offset=20, chip=chip, verbose=False)
    # for chip_address in chip_addresses:
    #     bl_mw_map = i2c_conn.get_bl_nw_map()
    #     print(bl_mw_map[chip_address][['row','col','baseline','noise_width','chip_name']])

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
            prog='PlaceHolder',
            description='PlaceHolder',
    )

    parser.add_argument(
        '--dieName',
        metavar = 'NAME',
        type = str,
        help = 'Example: die<number>_RxCy',
        required = True,
        dest = 'dieName',
    )
    
    parser.add_argument(
        '--waferName',
        metavar = 'WAFER',
        type = str,
        help = 'Example: Wafer_<batch_name>_<wafer_number>',
        required = True,
        dest = 'waferName',
    )


    args = parser.parse_args()

    i2c_port = "/dev/ttyACM0"
    chip_addresses = [0x60]
    ws_addresses = [0x40]
    chip_names = [f"{args.dieName}"]
    output_path = f"/home/daq/ETROC2/ETROC-History/CERN_Feb2026_Wafer/{args.waferName}/{args.dieName}"

    run_i2c(i2c_port, chip_addresses, ws_addresses, chip_names, output_path)

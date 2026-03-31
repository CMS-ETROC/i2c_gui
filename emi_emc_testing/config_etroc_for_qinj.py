import yaml
import argparse
import new_wrapper_i2cGui2
import load_bl_history
import plotter

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def config_for_qinj(
        config_path,
        history_note,
        do_checks: bool = False,
        load_histroy: bool = False,
):
    # Load the external YAML data
    cfg = load_config(config_path)

    # Extract lists for the wrapper
    chip_addrs = [c['addr'] for c in cfg['chips']]
    ws_addrs = [c['ws_addr'] for c in cfg['chips']]
    names = [c['name'] for c in cfg['chips']]

    try:
        i2c_conn = new_wrapper_i2cGui2.i2c_connection(cfg['port'], chip_addresses=chip_addrs, ws_addresses=ws_addrs, chip_names=names)
    except Exception as e:
        raise RuntimeError(f"Failed to create I2C GUI Conn Object: {e}. Please reconnect the cable to USB-ISS module")

    ### PLL & FC calibration
    i2c_conn.batch_PLL_FC_calibration()

    if do_checks:
        i2c_conn.batch_pixel_check()
        i2c_conn.batch_peripheral_check()

    ### Config basic
    i2c_conn.batch_disable_all_chips(cfg['power_mode'])
    i2c_conn.batch_set_chip_peripherals()

    ### Run OR Load Calibration
    if load_histroy:
        historical_dfs = load_bl_history.interactive_load_baselines(cfg['output_path'], names)

        # Inject the loaded DataFrames directly into the wrapper's memory
        for addr, chip_name in zip(chip_addrs, names):
            print(historical_dfs[chip_name])
            # if not historical_dfs[chip_name].empty:
            #     i2c_conn.BL_df[addr] = historical_dfs[chip_name]
            # else:
            #     raise RuntimeError(f"Cannot proceed: Missing historical baseline data for {chip_name}")

    else:
        pass
        # pixels_of_interest = [(r, c) for r in range(16) for c in range(16)]
        # i2c_conn.batch_auto_calibrate_chip(pixels_of_interest)

        # ### Save calibration results
        # for _, df in i2c_conn.BL_df.items():
        #     plotter.save_baselines(df, hist_dir=cfg['output_path'], save_notes=history_note)

    ### Config pixels for qinj
    # pixels_for_qinj = [(2, 2), (2, 10), (10, 2), (10, 10), (5, 5), (5, 13), (13, 5), (13, 13)]
    # i2c_conn.batch_enable_pixels(pixels_for_qinj, Qsel=cfg['qsel'], offset=cfg['offset'])

    # ### Print Invalid FC, good case: counter didn't change!
    # i2c_conn.batch_check_invalid_fc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ETROC2 YAML-based Config Tool')

    parser.add_argument(
        '--config',
        type = str,
        required = True,
        help = 'Path to YAML config',
        dest = 'config',
    )

    parser.add_argument(
        '--note',
        type = str,
        required = True,
        help = 'Unique note to select BL/NW history',
        dest = 'note',
    )

    parser.add_argument(
        '--doChecks',
        action = 'store_true',
        help = 'If the I2C checks should be performed',
        dest = 'doChecks',
    )

    parser.add_argument(
        '--load-history',
        action='store_true',
        help='Skip auto-calibration and choose a baseline from history',
        dest='load_history'
    )

    args = parser.parse_args()
    config_for_qinj(args.config, args.note, do_checks=args.doChecks, load_histroy=args.load_history)
import time
import argparse
import socket
import yaml

from src import new_wrapper_i2cGui2
from src import cmd_interpret

DEFAULT_CONFIG = {
    "firmware": "0001",
    "polarity": 0x4023,
    "timestamp": 0x0000,
    "active_channel": 0x0001,
    "prescale_factor": 2048,
    "counter_duration": 0x0000,
    "triggerbit_delay": 0x1800,
    "fc_delays": 0x0000,
    "data_delays_01": 0x0000,
    "data_delays_23": 0x0000,
    "num_fifo_read": 65536,
    "clear_fifo": 1,
    "reset_counter": 1,
    "fast_command_memo": "Start Triggerbit"
}

# -----------------------
def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# -----------------------
def _send_fc_sequence(input_socket, reg12_val: int, reg10_val: int, reg9_val: int) -> None:
    """Helper to send a standard Fast Command hardware sequence."""
    cmd_interpret.write_config_reg_decoded(input_socket, "register_12", reg12_val)
    cmd_interpret.write_config_reg_decoded(input_socket, "register_10", reg10_val, DEFAULT_CONFIG['prescale_factor'])
    cmd_interpret.write_config_reg_decoded(input_socket, "register_9", reg9_val)
    cmd_interpret.write_pulse_reg_decoded(input_socket, "fc_init")
    time.sleep(0.01)

# -----------------------
def _execute_fc_command(base_reg12: int, cmd_offset: int, base_val: int, loops: int, uniform: bool, do_loop: bool) -> None:
    """Helper to handle the initial command and its optional repeating loop."""
    reg12_val = base_reg12 + cmd_offset

    # 1. Send the initial base command
    _send_fc_sequence(reg12_val, base_val, base_val)

    # 2. Execute the loop if requested
    if do_loop and loops > 0:
        interval = (3000 // 16) // loops if uniform else 1
        for i in range(loops):
            step_val = base_val + (interval * i * 0x010) if uniform else base_val + (i * 0x010)
            _send_fc_sequence(reg12_val, step_val, step_val)

# -----------------------
def configure_memo_FC(input_socket, memo=None) -> None:
    memo_str = memo if memo is not None else DEFAULT_CONFIG['fast_command_memo']
    words = memo_str.split(' ')

    # 1. Parse all flags into a clean dictionary
    flags = {
        "QInj": "QInj" in words,
        "repeatedQInj": any("repeatedQInj" in w for w in words),
        "L1A": "L1A" in words,
        "L1ARange": "L1ARange" in words,
        "BCR": "BCR" in words,
        "Triggerbit": "Triggerbit" in words,
        "Start": "Start" in words,
        "uniform": "uniform" in words,
    }

    # 2. Extract loop count safely
    qinj_loop = 1
    for word in words:
        if "repeatedQInj=" in word:
            try:
                qinj_loop = int(word.split('=')[1])
            except Exception as e:
                break

    # 3. Determine base register 12 value
    base_reg12 = 0x0070 if flags["Triggerbit"] else 0x0030

    # --- Hardware Execution Sequence ---

    if flags["Start"]:
        cmd_interpret.write_config_reg_decoded(input_socket, "register_11", 0x0deb)
        time.sleep(0.01)

    # IDLE (Always executed based on original code flow)
    _send_fc_sequence(base_reg12, 0x000, 0x0deb)

    if flags["BCR"]:
        _send_fc_sequence(base_reg12 + 0x2, 0x000, 0x000)

    if flags["QInj"]:
        _execute_fc_command(base_reg12, 0x5, 0x005, qinj_loop, flags["uniform"], flags["repeatedQInj"])

    if flags["L1A"]:
        _execute_fc_command(base_reg12, 0x6, 0x1fd, qinj_loop, flags["uniform"], flags["L1ARange"])

    # Final signal start
    cmd_interpret.write_pulse_reg_decoded(input_socket, "fc_signal_start")
    time.sleep(0.01)

# -----------------------
def launch(input_socket):
    initial_registers = ["active_channel", "timestamp", "triggerbit_delay", "polarity", "counter_duration", "fc_delays", "data_delays_01", "data_delays_23"]
    for reg_name in initial_registers:
        cmd_interpret.write_config_reg_decoded(input_socket, reg_name, DEFAULT_CONFIG.get(reg_name))

    # Write special-case register
    cmd_interpret.write_config_reg_decoded(input_socket, "register_10", 0x000, DEFAULT_CONFIG['prescale_factor'])

    if DEFAULT_CONFIG['clear_fifo']:
        cmd_interpret.write_pulse_reg_decoded(input_socket, "clear_fifo")
        time.sleep(2.1)

    configure_memo_FC()

# -----------------------
def get_32bit(input_socket, high_reg_idx, low_reg_idx):
    """Helper to combine two 16-bit registers into one 32-bit integer."""
    high = cmd_interpret.read_status_reg(input_socket, high_reg_idx)
    low = cmd_interpret.read_status_reg(input_socket, low_reg_idx)
    return (high << 16) | low

# -----------------------
def pixel_turnon_points(input_socket):

    master_results = {}

    for addr in chip_addrs:
        master_results[addr] = {}
        df = i2c_conn.BL_df[addr]

        for row, col in pixels_for_scan:
            row_data = df.loc[(df['row'] == row) & (df['col'] == col)]
            a = 0
            b = int(row_data['baseline'].values[0] + 3 * row_data['noise_width'].values[0])

            trace = {
                'refresh_counter': [],
                'L1A_enabled': [],
                'data_counter': [],
                'header_counter': [],
                'trigger_counter': [],
                'dac': [],
            }

            while b - a > 1:
                dac_val = int((a + b) // 2)

                # Set the DAC to the value being scanned
                i2c_conn.set_dac(addr, row, col, dac_val)
                configure_memo_FC(input_socket, memo="Start Triggerbit QInj L1A")

                # 2. Optimized Polling (Only read the status bit)
                timeout_start = time.monotonic()
                while cmd_interpret.read_status_reg(input_socket, 7) < 1:
                    if time.monotonic() - timeout_start > 1: # 1 second safety timeout
                        print(f"Timeout waiting for FPGA at DAC {dac_val}")
                        break
                    time.sleep(0.01)

                # --- Start of Reading Logic ---
                # 1. Initial configuration read
                # Read reg 8 and check the 11th bit (0x400 = 2^10, which is the 11th bit position)
                reg8 = cmd_interpret.read_config_reg(input_socket, 8)
                en_L1A = (reg8 >> 10) & 1

                # 2. Initial status read
                data_counter      = get_32bit(4, 3)
                header_counter    = get_32bit(6, 5)
                refresh_counter   = cmd_interpret.read_status_reg(input_socket, 7)
                trigger_counter   = get_32bit(9, 8)

                trace["refresh_counter"].append(refresh_counter)
                trace["L1A_enabled"].append(bool(en_L1A))
                trace["data_counter"].append(data_counter)
                trace["header_counter"].append(header_counter)
                trace["trigger_counter"].append(trigger_counter)
                trace["dac"].append(dac_val)

                # Binary search logic
                if trigger_counter > 0:
                    b = dac_val
                else:
                    a = dac_val

                configure_memo_FC(input_socket, memo="Triggerbit")

            master_results[addr][f"R{row}_C{col}"] = {
                "turn_on_dac": a,
                "scan_data": trace
            }

    return master_results


def trigger_bit_noisescan(input_socket):

    master_results = {}

    for addr in chip_addrs:
        df = i2c_conn.BL_df[addr]
        master_results[addr] = {}

        for row, col in pixels_for_scan:
            row_data = df.loc[(df['row'] == row) & (df['col'] == col)]
            bl = row_data['baseline'].values[0]

            i2c_conn.config_single_pixel(addr, row, col, Qsel=5, QInjEn=False)

            scan_range = range(bl-10, bl+10, 1)
            trace = {
                'refresh_counter': [],
                'L1A_enabled': [],
                'data_counter': [],
                'header_counter': [],
                'trigger_counter': [],
                'dac': [],
            }

            for threshold in scan_range:

                i2c_conn.set_dac(addr, row, col, threshold)
                configure_memo_FC(input_socket, memo="Start Triggerbit L1A")

                # 2. Optimized Polling (Only read the status bit)
                timeout_start = time.monotonic()
                while cmd_interpret.read_status_reg(input_socket, 7) < 1:
                    if time.monotonic() - timeout_start > 1: # 1 second safety timeout
                        print(f"Timeout waiting for FPGA at DAC {threshold}")
                        break
                    time.sleep(0.01)

                # --- Start of Reading Logic ---
                # 1. Initial configuration read
                # Read reg 8 and check the 11th bit (0x400 = 2^10, which is the 11th bit position)
                reg8 = cmd_interpret.read_config_reg(input_socket, 8)
                en_L1A = (reg8 >> 10) & 1

                # 2. Initial status read
                data_counter      = get_32bit(4, 3)
                header_counter    = get_32bit(6, 5)
                refresh_counter   = cmd_interpret.read_status_reg(input_socket, 7)
                trigger_counter   = get_32bit(9, 8)

                trace["refresh_counter"].append(refresh_counter)
                trace["L1A_enabled"].append(bool(en_L1A))
                trace["data_counter"].append(data_counter)
                trace["header_counter"].append(header_counter)
                trace["trigger_counter"].append(trigger_counter)
                trace["dac"].append(threshold)

                configure_memo_FC(input_socket, memo="Triggerbit")

            master_results[addr][f"R{row}_C{col}"] = {
                "scan_data": trace
            }

    return master_results

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
            prog='PlaceHolder',
            description='PlaceHolder',
    )

    parser.register('type', 'hex', lambda s: int(s, 16))

    parser.add_argument(
        '--config',
        metavar = 'NAME',
        type = str,
        help = 'path to yaml config file',
        required = True,
        dest = 'config',
    )

    args = parser.parse_args()

    # Load the external YAML data
    cfg = load_config(args.config)

    # Extract lists for the wrapper
    chip_addrs = [c['addr'] for c in cfg['chips']]
    ws_addrs = [c['ws_addr'] for c in cfg['chips']]
    names = [c['name'] for c in cfg['chips']]

    try:
        i2c_conn = new_wrapper_i2cGui2.i2c_connection(cfg['port'], chip_addresses=chip_addrs, ws_addresses=ws_addrs, chip_names=names)
    except Exception as e:
        raise RuntimeError(f"Failed to create I2C GUI Conn Object: {e}. Please reconnect the cable to USB-ISS module")

    # pixels_for_scan = [(2, 2), (2, 10), (10, 2), (10, 10), (5, 5), (5, 13), (13, 5), (13, 13)]
    pixels_for_scan = [(2, 2)]

    ### PLL & FC calibration
    i2c_conn.batch_PLL_FC_calibration()

    ### Config basic
    i2c_conn.batch_disable_all_chips(cfg['power_mode'])
    i2c_conn.batch_set_chip_peripherals()

    ### Run calibration
    i2c_conn.batch_auto_calibrate_chip(pixels_for_scan)

    ### Config pixels for qinj
    i2c_conn.batch_enable_pixels(pixels_for_scan, Qsel=30)

    # Establish FPGA Socket Connection
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((cfg['fpga_ip'], cfg['fpga_port']))
        launch(sock)
        scanned_data1 = pixel_turnon_points(sock)

        ### Preparation for next task
        i2c_conn.batch_disable_all_chips(cfg['power_mode'])
        scanned_data2 = trigger_bit_noisescan(sock)
#############################################################################
# zlib License
#
# (C) 2023 Zach Flowers, Murtaza Safdari <musafdar@cern.ch>, Jongho Lee
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

# Imports
import matplotlib.pyplot as plt
import i2c_gui
import i2c_gui.chips
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os, sys
import multiprocessing
import datetime
from pathlib import Path
import subprocess
import sqlite3
from notebooks.notebook_helpers import *
sys.path.insert(1, f'/home/{os.getlogin()}/ETROC2/ETROC_DAQ')
import run_script
import importlib
importlib.reload(run_script)
import signal
import pandas as pd
import time 

def push_history_to_git(
        input_df: pd.DataFrame,
        note: str,
        git_repo: str,
    ):
    # Store BL, NW dataframe for later use
    new_columns = {
        'note': f'{note}',
    }

    if not os.path.exists(f'/home/{os.getlogin()}/ETROC2/{git_repo}'):
        os.system(f'git clone git@github.com:CMS-ETROC/{git_repo}.git /home/{os.getlogin()}/ETROC2/{git_repo}')

    for col in new_columns:
        input_df[col] = new_columns[col]

    outdir = git_repo
    outfile = outdir / 'BaselineHistory.sqlite'

    init_cmd = [
        'cd ' + str(outdir.resolve()),
        'git stash -u',
        'git pull',
    ]
    end_cmd = [
        'cd ' + str(outdir.resolve()),
        'git add BaselineHistory.sqlite',
        'git commit -m "Added new history entry"',
        'git push',
        'git stash pop',
        'git stash clear',
    ]
    init_cmd = [x + '\n' for x in init_cmd]
    end_cmd  = [x + '\n' for x in end_cmd]

    p = subprocess.Popen(
        '/bin/bash',
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        )

    for cmd in init_cmd:
        p.stdin.write(cmd + "\n")
    p.stdin.close()
    p.wait()
    print(p.stdout.read())

    with sqlite3.connect(outfile) as sqlconn:
        input_df.to_sql('baselines', sqlconn, if_exists='append', index=False)

    p = subprocess.Popen(
        '/bin/bash',
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        )

    for cmd in end_cmd:
        p.stdin.write(cmd + "\n")
    p.stdin.close()
    p.wait()

    p.stdin.close()
    print(p.stdout.read())

def func_daq(
        chip_names,
        run_str,
        extra_str,
        directory: Path,
        fpga_ip = "192.168.2.3",
        delay: int = 485,
        run_time: int = 120,
        extra_margin_time: int = 100,
    ):

    print('DAQ Start:', datetime.datetime.now())
    ## Making directory to save main_process.out files
    # currentPath = Path('.')
    # main_pro_dir = currentPath / 'main_process_cosmic'
    # main_pro_dir.mkdir(exist_ok=True)

    outdir_name = f'{run_str}_'+'_'.join(chip_names)+f'_{extra_str}'
    outdir = directory / outdir_name
    outdir.mkdir(exist_ok=False)

    trigger_bit_delay = int('100111'+format(delay, '010b'), base=2)
    parser = run_script.getOptionParser()
    (options, args) = parser.parse_args(args=f"-f --useIPC --reset_all_till_trigger_linked --hostname {fpga_ip} -t {run_time+extra_margin_time} -o {outdir_name} -v -w -s 0x0000 -p 0x000f -d {trigger_bit_delay} -a 0x00bb --counter_duration 0x0001 --compressed_translation -l 100000 --compressed_binary".split())
    IPC_queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=run_script.main_process, args=(IPC_queue, options, f'main_process_cosmic'))
    process.start()

    IPC_queue.put('memoFC Start Triggerbit BCR')
    while not IPC_queue.empty():
        pass
    time.sleep(run_time)
    IPC_queue.put('stop DAQ')
    IPC_queue.put('memoFC Triggerbit')
    while not IPC_queue.empty():
        pass
    IPC_queue.put('allow threads to exit')
    process.join()
    print('DAQ End:', datetime.datetime.now())

    del IPC_queue, process, parser

def func_fpga_data(
        chip_names,
        fpga_ip = "192.168.2.3",
        time_limit: int = 3,
        th_offset: int = 0x0f,
    ):

    parser = run_script.getOptionParser()

    ## One time to create output file
    rootdir = Path('../ETROC-Data')
    todaydir = rootdir / (datetime.date.today().isoformat() + '_Array_Test_Results')
    outdir_name = '_'.join(chip_names)+'_FPGA_data'
    outdir = todaydir / outdir_name

    if not outdir.is_dir():
        (options, args) = parser.parse_args(args=f"--useIPC --hostname {fpga_ip} -o {outdir_name} -v -w --reset_till_trigger_linked --counter_duration 0x0001 --fpga_data_time_limit {time_limit} --fpga_data --nodaq --DAC_Val {th_offset}".split())
        IPC_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=run_script.main_process, args=(IPC_queue, options, f'main_process_fpga_data'))
        process.start()
        process.join()

    (options, args) = parser.parse_args(args=f"--useIPC --hostname {fpga_ip} -o {outdir_name} -v --reset_till_trigger_linked --counter_duration 0x0001 --fpga_data_time_limit {time_limit} --fpga_data --nodaq --DAC_Val {th_offset}".split())
    IPC_queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=run_script.main_process, args=(IPC_queue, options, f'main_process_fpga_data'))
    process.start()
    process.join()

    del IPC_queue, process, parser

def run_daq(
        chip_names: list,
        chip_addresses: list,
        run_str: str,
        extra_str: str,
        i2c_port: str = "/dev/ttyACM0",
        fpga_ip: str = "192.168.2.3",
        th_offset: int = 0x18,
        run_time: int = 120,
        do_infiniteLoop: bool = False,
        do_TDC: bool = False,
        do_Counter: bool = False,
        do_fullAutoCal: bool = False,
        do_saveHistory: bool = False,
    ):
    # It is very important to correctly set the chip name, this value is stored with the data
    chip_fignames = f'{run_str}_'+'_'.join(chip_names)+f'_{extra_str}'

    # 'The port name the USB-ISS module is connected to. Default: COM3'
    port = i2c_port
    # ws_addresses = [None, None, None]

    # i2c_gui.__no_connect__ = False  # Set to fake connecting to an ETROC2 device
    # i2c_gui.__no_connect_type__ = "echo"  # for actually testing readback
    # #i2c_gui.__no_connect_type__ = "check"  # default behaviour

    data_rootdir = Path('../ETROC-Data')
    data_outdir = data_rootdir / (datetime.date.today().isoformat() + '_Array_Test_Results')
    data_outdir.mkdir(exist_ok=True)

    fig_outdir = Path('../ETROC-figures')
    fig_outdir = fig_outdir / (datetime.date.today().isoformat() + '_Array_Test_Results')
    fig_outdir.mkdir(exist_ok=True)
    fig_path = str(fig_outdir)

    # Make i2c_connection class object
    # i2c_conn = self, port, chip_addresses, chip_names, chip_fc_delays
    i2c_conn = i2c_connection(port,chip_addresses,chip_names,[("1","1"), ("1","1"), ("1","1")])

    # Config chips
    ### Key is (Disable Pixels, Auto Cal, Chip Peripherals, Basic Peri Reg Check, Pixel Check)
    # 0 - 0 - (disable & auto_cal all pixels) - (auto_TH_CAL) - (disable default all pixels) - (set basic peripherals) - (peripheral reg check) -  (pixel ID check)
    i2c_conn.config_chips('00001111')

    if do_fullAutoCal:
        i2c_conn.config_chips('00100000')
        ## Visualize the learned Baselines (BL) and Noise Widths (NW)
        ## Note that the NW represents the full width on either side of the BL
        frames = []
        for chip_address, chip_name in zip(chip_addresses,chip_names):
            BL_map_THCal,NW_map_THCal, BL_df = i2c_conn.get_auto_cal_maps(chip_address)
            frames.append(BL_df)
            fig = plt.figure(dpi=200, figsize=(10,10))
            gs = fig.add_gridspec(1,2)

            ax0 = fig.add_subplot(gs[0,0])
            ax0.set_title(f"{chip_name}: BL (DAC LSB)")
            img0 = ax0.imshow(BL_map_THCal, interpolation='none')
            ax0.set_aspect("equal")
            ax0.invert_xaxis()
            ax0.invert_yaxis()
            plt.xticks(range(16), range(16), rotation="vertical")
            plt.yticks(range(16), range(16))
            divider = make_axes_locatable(ax0)
            cax = divider.append_axes('right', size="5%", pad=0.05)
            fig.colorbar(img0, cax=cax, orientation="vertical")

            ax1 = fig.add_subplot(gs[0,1])
            ax1.set_title(f"{chip_name}: NW (DAC LSB)")
            img1 = ax1.imshow(NW_map_THCal, interpolation='none')
            ax1.set_aspect("equal")
            ax1.invert_xaxis()
            ax1.invert_yaxis()
            plt.xticks(range(16), range(16), rotation="vertical")
            plt.yticks(range(16), range(16))
            divider = make_axes_locatable(ax1)
            cax = divider.append_axes('right', size="5%", pad=0.05)
            fig.colorbar(img1, cax=cax, orientation="vertical")

            for x in range(16):
                for y in range(16):
                    ax0.text(x,y,f"{BL_map_THCal.T[x,y]:.0f}", c="white", size=5, rotation=45, fontweight="bold", ha="center", va="center")
                    ax1.text(x,y,f"{NW_map_THCal.T[x,y]:.0f}", c="white", size=5, rotation=45, fontweight="bold", ha="center", va="center")
            plt.savefig(fig_path+"/BL_NW_"+chip_name+"_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")+".png")

        full_BL_df = pd.concat(frames)
        if do_saveHistory:
            push_history_to_git(full_BL_df, f'{run_str}_{extra_str}', 'ETROC-History-Cosmic')

        col_list, row_list = np.meshgrid(np.arange(16), np.arange(16))
        scan_list = list(zip(row_list.flatten(), col_list.flatten()))

    else:
        # Define pixels of interest
        row_list = [14, 14, 14, 14]
        col_list = [6, 7, 8, 9]
        scan_list = list(zip(row_list, col_list))
        print(scan_list)
        
        tmp_data = []
        for chip_address, chip_name in zip(chip_addresses, chip_names):
            for row, col in scan_list:
                i2c_conn.auto_cal_pixel(chip_name=chip_name, row=row, col=col, verbose=False, chip_address=chip_address, chip=None, data=tmp_data, row_indexer_handle=None, column_indexer_handle=None)
        BL_df = pandas.DataFrame(data = tmp_data)
        if do_saveHistory:
            push_history_to_git(BL_df, f'{run_str}_{extra_str}', 'ETROC-History-Cosmic')

    ### Enable pixels of Interest
    i2c_conn.enable_select_pixels_in_chips(scan_list)

    offset = th_offset
    for chip_address in chip_addresses[:]:
        chip = i2c_conn.get_chip_i2c_connection(chip_address)
        row_indexer_handle,_,_ = chip.get_indexer("row")
        column_indexer_handle,_,_ = chip.get_indexer("column")
        for row, col in scan_list:
            print(f"Operating on chip {hex(chip_address)} Pixel ({row},{col})")
            column_indexer_handle.set(col)
            row_indexer_handle.set(row)    
            i2c_conn.pixel_decoded_register_write("TH_offset", format(offset, '06b'), chip)
            i2c_conn.pixel_decoded_register_write("QInjEn", "0", chip)
        del chip, row_indexer_handle, column_indexer_handle

    # Calibrate PLL
    for chip_address in chip_addresses[:]:
        i2c_conn.calibratePLL(chip_address, chip=None)

    # Calibrate FC
    for chip_address in chip_addresses[:]:
        i2c_conn.asyResetGlobalReadout(chip_address, chip=None)
        i2c_conn.asyAlignFastcommand(chip_address, chip=None)

    plzDelDir = data_outdir / 'PlzDelete_Board013_NoLinkCheck'
    if not plzDelDir.is_dir():
        print('\nOne time DAQ run for checking LED lights')
        # Run One Time DAQ to Set FPGA Firmware
        parser = run_script.getOptionParser()
        (options, args) = parser.parse_args(args=f"-f --useIPC --hostname {fpga_ip} -t 20 -o PlzDelete_Board013_NoLinkCheck -v -w -s 0x000c -p 0x000f -d 0xb800 -a 0x00bb --clear_fifo".split())
        IPC_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=run_script.main_process, args=(IPC_queue, options, f'main_process_Start_LEDs_Board013_NoLinkCheck'))
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
    
    if not do_infiniteLoop:
        # hold for keyboard input when infinite loop is off
        input("Are LEDs looking okay? Press the Enter key to continue: ")

    if do_TDC:
        func_daq(
            chip_names = chip_names,
            run_str = run_str,
            extra_str = extra_str,
            directory = data_outdir,
            fpga_ip = fpga_ip,
            delay = 485,
            run_time = run_time,
            extra_margin_time = 30,
        )
    elif do_Counter:
        func_fpga_data(
            chip_names = chip_names,
            fpga_ip = fpga_ip,   
        )
    else:
        print('Run mode is not specify. Exit the script and disconnect I2C.')

    # Disconnect I2C Device
    del i2c_conn


def main():
    import argparse

    parser = argparse.ArgumentParser(
                    prog='Cosmic run!',
                    description='Control them!',
                    #epilog='Text at the bottom of help'
                    )

    parser.add_argument(
        '-s',
        '--extraStr',
        metavar = 'NAME',
        type = str,
        help = 'Extra string - no special chars',
        required = True,
        dest = 'extra_str',
    )
    parser.add_argument(
        '-t',
        '--runTime',
        metavar = 'TIME',
        type = int,
        help = 'DAQ running time in second',
        required = True,
        dest = 'daq_run_time',
    )
    parser.add_argument(
        '-l',
        '--infiniteLoop',
        help = 'Do infinite loop',
        action = 'store_true',
        dest = 'infinite_loop',
    )
    parser.add_argument(
        '--runTDC',
        help = 'Take TDC data while running DAQ',
        action = 'store_true',
        dest = 'run_TDC',
    )
    parser.add_argument(
        '--runCounter',
        help = 'Take FPGA data while running DAQ',
        action = 'store_true',
        dest = 'run_Counter',
    )
    parser.add_argument(
        '--fullAutoCal',
        help = 'Run autocalibration for all 256 pixels',
        action = 'store_true',
        dest = 'fullAutoCal',
    )
    parser.add_argument(
        '--saveHistory',
        help = 'Save BL and NW as a history and push to git repo',
        action = 'store_true',
        dest = 'saveHistory',
    )
    parser.add_argument(
        '-b0',
        '--board0_name',
        metavar = 'NAME',
        help = "Name of the ETROC board installed in channel 0 (FMCRX1)",
        dest = 'board0_name',
        required = True,
        type = str,
    )
    parser.add_argument(
        '-b1',
        '--board1_name',
        metavar = 'NAME',
        help = "Name of the ETROC board installed in channel 1 (FMCRX2)",
        dest = 'board1_name',
        default = None,
        type = str,
    )
    parser.add_argument(
        '-b2',
        '--board2_name',
        metavar = 'NAME',
        help = "Name of the ETROC board installed in channel 2 (FMCRX3)",
        dest = 'board2_name',
        default = None,
        type = str,
    )
    parser.add_argument(
        '-b3',
        '--board3_name',
        metavar = 'NAME',
        help = "Name of the ETROC board installed in channel 3 (FMCRX4)",
        dest = 'board3_name',
        default = None,
        type = str,
    )
    parser.add_argument(
        '--board0_i2c',
        metavar = 'I2C_ADDRESS',
        help = "I2C address of the ETROC board installed in channel 0 (FMCRX1)",
        dest = 'board0_i2c',
        required = True,
        type = int,
    )
    parser.add_argument(
        '--board1_i2c',
        metavar = 'I2C_ADDRESS',
        help = "I2C address of the ETROC board installed in channel 1 (FMCRX2)",
        dest = 'board1_i2c',
        default = None,
        type = int,
    )
    parser.add_argument(
        '--board2_i2c',
        metavar = 'I2C_ADDRESS',
        help = "I2C address of the ETROC board installed in channel 2 (FMCRX3)",
        dest = 'board2_i2c',
        default = None,
        type = int,
    )
    parser.add_argument(
        '--board3_i2c',
        metavar = 'I2C_ADDRESS',
        help = "I2C address of the ETROC board installed in channel 3 (FMCRX4)",
        dest = 'board3_i2c',
        default = None,
        type = int,
    )
    args = parser.parse_args()
    start_time = time.time()

    full_chip_names = [args.board0_name, args.board1_name, args.board2_name, args.board3_name]
    full_chip_addresses = [args.board0_i2c, args.board1_i2c, args.board2_i2c, args.board3_i2c]

    chip_names = list(filter(lambda item: item is not None, full_chip_names))
    chip_addresses = list(filter(lambda item: item is not None, full_chip_addresses))

    count = 0
    while True:
        run_str = f"Run{count}"

        if (args.infinite_loop) and (args.daq_run_time > 7200) and (args.run_TDC):
            print("User set daq running time too long while enabling infinite loop option!")
            print("Maximum running time should be 7200s!")
            break

        def signal_handler(sig, frame):
            print("Exiting gracefully")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        run_daq(
            chip_names = chip_names,
            chip_addresses = chip_addresses,
            run_str = run_str,
            extra_str = args.extra_str,
            i2c_port = "/dev/ttyACM2",
            fpga_ip = "192.168.2.3",
            th_offset = 0x0f,
            run_time = args.daq_run_time,
            do_infiniteLoop = args.infinite_loop,
            do_TDC = args.run_TDC,
            do_Counter = args.run_Counter,
            do_fullAutoCal =  args.fullAutoCal,
            do_saveHistory = args.saveHistory,
        )
        
        end_time = time.time()
        if (args.infinite_loop) and (args.run_Counter) and (end_time - start_time > args.daq_run_time):
            break

        count += 1
        if not args.infinite_loop:
            break

if __name__ == "__main__":
    main()
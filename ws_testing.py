#############################################################################
# zlib License
#
# (C) 2023 Cristóvão Beirão da Cruz e Silva <cbeiraod@cern.ch>
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

#############################################################################
# Modified for ETROC2 I2C testing in jupyter notebooks, Murtaza Safdari
#############################################################################

## Imports
import matplotlib.pyplot as plt
import logging
import i2c_gui
import i2c_gui.chips
from i2c_gui.usb_iss_helper import USB_ISS_Helper
from i2c_gui.fpga_eth_helper import FPGA_ETH_Helper
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import time
from tqdm import tqdm
from i2c_gui.chips.etroc2_chip import register_decoding
import os, sys
import multiprocessing
import datetime
from pathlib import Path
import pandas as pd
sys.path.insert(1, f'/home/{os.getlogin()}/ETROC2/ETROC_DAQ')
import run_script
import importlib
importlib.reload(run_script)

# Set defaults
### It is very important to correctly set the chip name, this value is stored with the data
chip_name = "01E2_#48"

# 'The port name the USB-ISS module is connected to. Default: COM3'
port = "/dev/ttyACM0"
# I2C addresses for the pixel block and WS
chip_address = 0x60
ws_address = 0x40

i2c_gui.__no_connect__ = False  # Set to fake connecting to an ETROC2 device
i2c_gui.__no_connect_type__ = "echo"  # for actually testing readback
#i2c_gui.__no_connect_type__ = "check"  # default behaviour

# Start logger and connect
## Logger
log_level=30
logging.basicConfig(format='%(asctime)s - %(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("Script_Logger")
Script_Helper = i2c_gui.ScriptHelper(logger)

## USB ISS connection
conn = i2c_gui.Connection_Controller(Script_Helper)
conn.connection_type = "USB-ISS"
conn.handle: USB_ISS_Helper
conn.handle.port = port
conn.handle.clk = 100

conn.connect()

chip = i2c_gui.chips.ETROC2_Chip(parent=Script_Helper, i2c_controller=conn)
chip.config_i2c_address(chip_address)
chip.config_waveform_sampler_i2c_address(ws_address)  # Not needed if you do not access WS registers
logger.setLevel(log_level)


# Useful Functions to streamline register reading and writing

def pixel_decoded_register_write(decodedRegisterName, data_to_write):
    bit_depth = register_decoding["ETROC2"]["Register Blocks"]["Pixel Config"][decodedRegisterName]["bits"]
    handle = chip.get_decoded_indexed_var("ETROC2", "Pixel Config", decodedRegisterName)
    chip.read_decoded_value("ETROC2", "Pixel Config", decodedRegisterName)
    if len(data_to_write)!=bit_depth: print("Binary data_to_write is of incorrect length for",decodedRegisterName, "with bit depth", bit_depth)
    data_hex_modified = hex(int(data_to_write, base=2))
    if(bit_depth>1): handle.set(data_hex_modified)
    elif(bit_depth==1): handle.set(data_to_write)
    else: print(decodedRegisterName, "!!!ERROR!!! Bit depth <1, how did we get here...")
    chip.write_decoded_value("ETROC2", "Pixel Config", decodedRegisterName)

def pixel_decoded_register_read(decodedRegisterName, key, need_int=False):
    handle = chip.get_decoded_indexed_var("ETROC2", f"Pixel {key}", decodedRegisterName)
    chip.read_decoded_value("ETROC2", f"Pixel {key}", decodedRegisterName)
    if(need_int): return int(handle.get(), base=16)
    else: return handle.get()

def peripheral_decoded_register_write(decodedRegisterName, data_to_write):
    bit_depth = register_decoding["ETROC2"]["Register Blocks"]["Peripheral Config"][decodedRegisterName]["bits"]
    handle = chip.get_decoded_display_var("ETROC2", "Peripheral Config", decodedRegisterName)
    chip.read_decoded_value("ETROC2", "Peripheral Config", decodedRegisterName)
    if len(data_to_write)!=bit_depth: print("Binary data_to_write is of incorrect length for",decodedRegisterName, "with bit depth", bit_depth)
    data_hex_modified = hex(int(data_to_write, base=2))
    if(bit_depth>1): handle.set(data_hex_modified)
    elif(bit_depth==1): handle.set(data_to_write)
    else: print(decodedRegisterName, "!!!ERROR!!! Bit depth <1, how did we get here...")
    chip.write_decoded_value("ETROC2", "Peripheral Config", decodedRegisterName)

def peripheral_decoded_register_read(decodedRegisterName, key, need_int=False):
    handle = chip.get_decoded_display_var("ETROC2", f"Peripheral {key}", decodedRegisterName)
    chip.read_decoded_value("ETROC2", f"Peripheral {key}", decodedRegisterName)
    if(need_int): return int(handle.get(), base=16)
    else: return handle.get()

def ws_decoded_register_write(decodedRegisterName, data_to_write):
    bit_depth = register_decoding["Waveform Sampler"]["Register Blocks"]["Config"][decodedRegisterName]["bits"]
    handle = chip.get_decoded_display_var("Waveform Sampler", "Config", decodedRegisterName)
    chip.read_decoded_value("Waveform Sampler", "Config", decodedRegisterName)
    if len(data_to_write)!=bit_depth: print("Binary data_to_write is of incorrect length for",decodedRegisterName, "with bit depth", bit_depth)
    data_hex_modified = hex(int(data_to_write, base=2))
    if(bit_depth>1): handle.set(data_hex_modified)
    elif(bit_depth==1): handle.set(data_to_write)
    else: print(decodedRegisterName, "!!!ERROR!!! Bit depth <1, how did we get here...")
    chip.write_decoded_value("Waveform Sampler", "Config", decodedRegisterName)

def ws_decoded_config_read(decodedRegisterName, need_int=False):
    handle = chip.get_decoded_display_var("Waveform Sampler", f"Config", decodedRegisterName)
    chip.read_decoded_value("Waveform Sampler", f"Config", decodedRegisterName)
    if(need_int): return int(handle.get(), base=16)
    else: return handle.get()

def ws_decoded_status_read(decodedRegisterName, need_int=False):
    handle = chip.get_decoded_display_var("Waveform Sampler", f"Status", decodedRegisterName)
    chip.read_decoded_value("Waveform Sampler", f"Status", decodedRegisterName)
    if(need_int): return int(handle.get(), base=16)
    else: return handle.get()


# Check if any pixels are broken
### If a pixel returns a COL and ROW number that inconsistent with the pixel that we are addressing, then it is broken

Failure_map = np.zeros((16,16))
row_indexer_handle,_,_ = chip.get_indexer("row")  # Returns 3 parameters: handle, min, max
column_indexer_handle,_,_ = chip.get_indexer("column")
for row in range(16):
    for col in range(16):
        column_indexer_handle.set(col)
        row_indexer_handle.set(row)
        fetched_row = pixel_decoded_register_read("PixelID-Row", "Status", need_int=True)
        fetched_col = pixel_decoded_register_read("PixelID-Col", "Status", need_int=True)
        if(row!=fetched_row or col!=fetched_col):
            print("Fail!", row, col, fetched_row, fetched_col)
            Failure_map[15-row,15-col] = 1

# Set the basic peripheral registers
peripheral_decoded_register_write("EFuse_Prog", format(0x00017f0f, '032b'))     # chip ID
peripheral_decoded_register_write("singlePort", '1')                            # Set data output to right port only
peripheral_decoded_register_write("serRateLeft", '00')                          # Set Data Rates to 320 mbps
peripheral_decoded_register_write("serRateRight", '00')                         # ^^
peripheral_decoded_register_write("onChipL1AConf", '00')                        # Switches off the onboard L1A
peripheral_decoded_register_write("PLL_ENABLEPLL", '1')                         # "Enable PLL mode, active high. Debugging use only."
peripheral_decoded_register_write("chargeInjectionDelay", format(0x0a, '05b'))  # User tunable delay of Qinj pulse
peripheral_decoded_register_write("triggerGranularity", format(0x00, '03b'))    # only for trigger bit

# Perform Auto-calibration on WS pixel (Row0, Col14)
# Reset the maps
baseLine = 0
noiseWidth = 0

row_indexer_handle,_,_ = chip.get_indexer("row")  # Returns 3 parameters: handle, min, max
column_indexer_handle,_,_ = chip.get_indexer("column")
row = 0
col = 14
column_indexer_handle.set(col)
row_indexer_handle.set(row)
# Enable THCal clock and buffer, disable bypass
pixel_decoded_register_write("CLKEn_THCal", "1")
pixel_decoded_register_write("BufEn_THCal", "1")
pixel_decoded_register_write("Bypass_THCal", "0")
pixel_decoded_register_write("TH_offset", format(0x07, '06b'))
# Reset the calibration block (active low)
pixel_decoded_register_write("RSTn_THCal", "0")
pixel_decoded_register_write("RSTn_THCal", "1")
# Start and Stop the calibration, (25ns x 2**15 ~ 800 us, ACCumulator max is 2**15)
pixel_decoded_register_write("ScanStart_THCal", "1")
pixel_decoded_register_write("ScanStart_THCal", "0")
# Check the calibration done correctly
if(pixel_decoded_register_read("ScanDone", "Status")!="1"): print("!!!ERROR!!! Scan not done!!!")
baseLine = pixel_decoded_register_read("BL", "Status", need_int=True)
noiseWidth = pixel_decoded_register_read("NW", "Status", need_int=True)
# Disable clock and buffer before charge injection 
pixel_decoded_register_write("CLKEn_THCal", "0") 
pixel_decoded_register_write("BufEn_THCal", "0")
# Set Charge Inj Q to 15 fC
pixel_decoded_register_write("QSel", format(0x0e, '05b'))

### Print BL and NW from automatic calibration
print(f"BL: {baseLine}, NW: {noiseWidth}")

### Disable all pixel readouts before doing anything
row_indexer_handle,_,_ = chip.get_indexer("row")
column_indexer_handle,_,_ = chip.get_indexer("column")
column_indexer_handle.set(0)
row_indexer_handle.set(0)

broadcast_handle,_,_ = chip.get_indexer("broadcast")
broadcast_handle.set(True)
pixel_decoded_register_write("disDataReadout", "1")
broadcast_handle.set(True)
pixel_decoded_register_write("QInjEn", "0")
broadcast_handle.set(True)
pixel_decoded_register_write("disTrigPath", "1")

### WS and pixel initialization
# If you want, you can change the pixel row and column numbers
row_indexer_handle,_,_ = chip.get_indexer("row")  # Returns 3 parameters: handle, min, max
column_indexer_handle,_,_ = chip.get_indexer("column")
row = 0
col = 14
print(f"Enabling Pixel ({row},{col})")
column_indexer_handle.set(col)
row_indexer_handle.set(row)
pixel_decoded_register_write("Bypass_THCal", "0")      
pixel_decoded_register_write("TH_offset", format(0x0c, '06b'))  # Offset used to add to the auto BL for real triggering
pixel_decoded_register_write("QSel", format(0x1e, '05b'))       # Ensure we inject 30 fC of charge  
pixel_decoded_register_write("QInjEn", "1")                     # ENable charge injection for the selected pixel
pixel_decoded_register_write("RFSel", format(0x00, '02b'))      # Set Largest feedback resistance -> maximum gain 


regOut1F_handle = chip.get_display_var("Waveform Sampler", "Config", "regOut1F")
regOut1F_handle.set("0x22")
chip.write_register("Waveform Sampler", "Config", "regOut1F")
regOut1F_handle.set("0x0b")
chip.write_register("Waveform Sampler", "Config", "regOut1F")

# ws_decoded_register_write("mem_rstn", "0")                      # 0: reset memory
# ws_decoded_register_write("clk_gen_rstn", "0")                  # 0: reset clock generation
# ws_decoded_register_write("sel1", "0")                          # 0: Bypass mode, 1: VGA mode
ws_decoded_register_write("DDT", format(0, '016b'))             # Time Skew Calibration set to 0
ws_decoded_register_write("CTRL", format(0x2, '02b'))           # CTRL default = 0x10 for regOut0D

chip.read_all_address_space("Waveform Sampler") # Read all registers of WS
rd_addr_handle = chip.get_decoded_display_var("Waveform Sampler", "Config", "rd_addr")
dout_handle = chip.get_decoded_display_var("Waveform Sampler", "Status", "dout")

### Run DAQ to send ws fc
time_per_pixel = 30
dead_time_per_pixel = 5
total_scan_time = time_per_pixel + dead_time_per_pixel
outname = 'ws_test'

today = datetime.date.today()
todaystr = "../ETROC-Data/" + today.isoformat() + "_Array_Test_Results/"
base_dir = Path(todaystr)
base_dir.mkdir(exist_ok=True) 

parser = run_script.getOptionParser() 
(options, args) = parser.parse_args(args=f"-f --useIPC --hostname 192.168.2.3 -t {int(total_scan_time)} -o {outname} -v -w -s 0x000C -p 0x000f --compressed_translation  --clear_fifo".split())
IPC_queue = multiprocessing.Queue()
process = multiprocessing.Process(target=run_script.main_process, args=(IPC_queue, options, f'main_process'))
process.start()

IPC_queue.put('start onetime ws')
while not IPC_queue.empty():
    pass

time.sleep(time_per_pixel)
IPC_queue.put('stop ws')

time.sleep(1)
IPC_queue.put('stop DAQ')
while not IPC_queue.empty():
    pass

IPC_queue.put('allow threads to exit')
process.join()

### Read from WS memory
ws_decoded_register_write("rd_en_I2C", "1")

# For loop to read data from WS
max_steps = 1024
lastUpdateTime = time.time_ns()
base_data = []
coeff = 0.04/5*8.5  # This number comes from the example script in the manual
time_coeff = 1/2.56  # 2.56 GHz WS frequency

for time_idx in tqdm(range(max_steps)):
    rd_addr_handle.set(hex(time_idx))
    chip.write_decoded_value("Waveform Sampler", "Config", "rd_addr")
    chip.read_decoded_value("Waveform Sampler", "Status", "dout")
    data = dout_handle.get()

    #if time_idx == 1:
    #    data = hex_0fill(int(data, 0) + 8192, 14)

    binary_data = bin(int(data, 0))[2:].zfill(14)  # because dout is 14 bits long
    Dout_S1 = int('0b'+binary_data[1:7], 0)
    Dout_S2 = int(binary_data[ 7]) * 24 + \
                int(binary_data[ 8]) * 16 + \
                int(binary_data[ 9]) * 10 + \
                int(binary_data[10]) *  6 + \
                int(binary_data[11]) *  4 + \
                int(binary_data[12]) *  2 + \
                int(binary_data[13])

    base_data.append(
        {
            "Time Index": time_idx,
            "Data": int(data, 0),
            "Raw Data": bin(int(data, 0))[2:].zfill(14),
            "pointer": int(binary_data[0]),
            "Dout_S1": Dout_S1,
            "Dout_S2": Dout_S2,
            "Dout": Dout_S1*coeff + Dout_S2,
        }
    )

df = pd.DataFrame(base_data)

pointer_idx = df["pointer"].loc[df["pointer"] != 0].index
if len(pointer_idx) != 0:
    pointer_idx = pointer_idx[0]
    new_idx = list(set(range(len(df))).difference(range(pointer_idx+1))) + list(range(pointer_idx+1))
    df = df.iloc[new_idx].reset_index(drop = True)
    df["Time Index"] = df.index

df["Time [ns]"] = df["Time Index"] * time_coeff
df.set_index('Time Index', inplace=True)

# Disable reading data from WS:
ws_decoded_register_write("rd_en_I2C", "0")

outdir = Path('../ETROC-Data')
outdir = outdir / (datetime.date.today().isoformat() + '_Array_Test_Results')
outdir.mkdir(exist_ok=True)
outfile = outdir / ("rawdataWS_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + ".csv")
df.to_csv(outfile, index=False)

fig, ax = plt.subplots()
ax.plot(df['Time [ns]'], df['Dout'])
plt.show()
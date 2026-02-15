import subprocess
import time
import sys
import argparse
from pathlib import Path

# --- Configuration ---
# Please update these values before running the script
mother_dir = "CERN_Feb2026_Wafer"
wafer_name = "Wafer_N62C72_02G4_AfterUBM_Bump"
CONFIG_FILE = "20260209-CERN-Wafer.yaml"

# --- Script settings ---
PYTHON_EXECUTABLE = sys.executable # Use the same python that runs this script
SCRIPT_TO_RUN = "read_current_v2.py"


def generate_toml_config(die_name, wafer_name, toml_path, toml_filename):
    """Generates a TOML configuration file from a template with dynamic values."""
    print(f"--- Generating TOML config file: {toml_filename} ---")

    toml_content = f"""[satellites.ETROC2ClassicWafer]

[satellites.ETROC2ClassicWafer.One]
fast_command_memo = "Start QInj L1A Triggerbit BCR"
polarity = 0x4123
active_channel = 0x0001
timestamp = 0x0000

# fc_delays        = 0b0000000000100100 # register 4
data_delays_01   = 0b0000000000010100 # register 5
# data_delays_23   = 0b0000111100000000 # register 6
# counter_duration = 0b0000000000000000 # register 7

i2c_port = "/dev/ttyACM0"
chip_addresses = [0x60]
ws_addresses = [0x40]
chip_names = ["{die_name}"]
output_path = "/home/daq/ETROC2/ETROC-Data/{mother_dir}/{wafer_name}/{die_name}"
do_full_chip = true 
power_mode = "high"

[satellites.ETROC2Receiver]

[satellites.ETROC2Receiver.One]
output_path = "/home/daq/ETROC2/ETROC-Data/{mother_dir}/{wafer_name}/{die_name}"
translate = 1
compressed_binary = 0
skip_fillers = 1
"""

    try:
        with open(Path(toml_path) / toml_filename, "w") as f:
            f.write(toml_content)
        print(f"--- Successfully generated TOML config for {die_name}. ---")
        return True
    except IOError as e:
        print(f"--- ERROR: Could not write TOML file '{toml_filename}': {e} ---")
        return False
    except ImportError:
        print("--- ERROR: The 'toml' library is not installed. ---")
        print("--- Please install it by running: pip install toml ---")
        return False


def run_command(command, show_output=True):
    """Executes a command and waits for it to complete.
    
    Args:
        command: List of command arguments
        show_output: If True, display output in real-time. If False, capture it.
    """
    try:
        print(f"--- Running command: {' '.join(command)} ---")
        if show_output:
            # Use shell to filter out libgpib messages but show everything else
            cmd_str = ' '.join(command) + ' 2>&1 | grep -v "^libgpib:"'
            subprocess.run(cmd_str, shell=True, check=True)
        else:
            # Capture output for later display (e.g., on error)
            subprocess.run(command, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"--- ERROR executing command: {' '.join(command)} ---")
        print(f"--- Return Code: {e.returncode} ---")
        if not show_output:
            print(f"--- STDOUT: ---\n{e.stdout}")
            print(f"--- STDERR: ---\n{e.stderr}")
        return False
    except FileNotFoundError:
        print(f"--- ERROR: The script '{command[1]}' was not found. ---")
        print("--- Please ensure it is in the same directory or in your system's PATH. ---")
        return False


def main(args):
    """Main function to orchestrate the testing process."""
    print("Starting automated wafer testing process...")

    OUTPUT_PATH = f"/home/daq/ETROC2/ETROC-History/{mother_dir}/{wafer_name}/{args.dieName}"  # IMPORTANT: Change this to your desired output directory
    Path(OUTPUT_PATH).mkdir(exist_ok=True, parents=True)

    # 1. Prepare paths and generate the TOML configuration file
    if not generate_toml_config(args.dieName, wafer_name, '/home/daq/ETROC2', 'testslowwafer.toml'):
        print("--- Halting execution due to TOML generation failure. ---")
        sys.exit(1) # Exit the script if config can't be created

    # 1. Start power-on and logging process in the background.
    # This assumes read_current_v2.py can handle both flags in one call.
    start_and_log_command = [
        PYTHON_EXECUTABLE,
        SCRIPT_TO_RUN,
        "-c", CONFIG_FILE,
        "--turn-on",
        "--log",
        "-i", "1",
        "-o", OUTPUT_PATH,
        "-f", "power.sqlite",
    ]
    print(f"--- Starting power-on and logging: {' '.join(start_and_log_command)} ---")
    # Popen starts the process without blocking, allowing us to manage it
    active_process = subprocess.Popen(start_and_log_command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    
    print("\n--- Power-on and logging started. Press CTRL+C to stop logging and proceed with shutdown. ---")

    # 2. Wait for keyboard interrupt to stop logging
    try:
        # wait() blocks until the process finishes on its own,
        # or until this script is interrupted by the user (e.g., with Ctrl+C).
        start_time = time.time()
        last_print_time = start_time
        #first_10_sec_script_run = False  # Flag to ensure script runs only once
        #
        while active_process.poll() is None:  # While process is still running
            current_time = time.time()
            elapsed_time = current_time - start_time
        #    
        #    # Exit the loop after given seconds
        #    if elapsed_time >= args.runTime:
        #        print(f"\n--- {args.runTime} seconds elapsed. Stopping logging automatically... ---")
        #        break
        #    
        #    # Run another script after first 10 seconds
        #    if elapsed_time >= 10 and not first_10_sec_script_run:
        #        print("--- 10 seconds elapsed. Running additional script... ---")
        #        # CONFIGURE THIS: Change to your script name and arguments
        #        additional_script_command = [
        #            PYTHON_EXECUTABLE,
        #            "run_i2c.py",  # Change this to your script
        #            "--dieName", f"{args.dieName}",
        #            "--waferName", f"{wafer_name}",
        #        ]
        #        if run_command(additional_script_command):
        #            print("--- Additional script completed successfully. ---")
        #        else:
        #            print("--- Additional script failed. ---")
        #        first_10_sec_script_run = True
        #    
            # Print every 10 seconds
            if current_time - last_print_time >= 10:
                print(f"{int(elapsed_time)} seconds passed")
                last_print_time = current_time
        #    
        #    time.sleep(0.5)  # Sleep briefly to avoid busy waiting
            
    except KeyboardInterrupt:
        print("\n--- Keyboard interrupt received. Stopping the process... ---")
    except Exception as e:
        # Catch other potential exceptions from wait()
        print(f"\n--- An unexpected error occurred while waiting for the process: {e} ---")


    # 3. Terminate the process
    # This will run after the process finishes naturally or after a KeyboardInterrupt
    print("--- Terminating process (if still running)... ---")
    active_process.terminate()

    # Wait a moment to ensure the process has terminated and capture any final output
    try:
        stdout, stderr = active_process.communicate(timeout=5)
        print("--- Process stopped. ---")
        if stdout:
            print(f"--- Logging STDOUT: ---\n{stdout}")
        #if stderr:
        #    print(f"--- Logging STDERR: ---\n{stderr}")

    except subprocess.TimeoutExpired:
        print("--- Process did not terminate gracefully. Forcing kill. ---")
        active_process.kill()

    print("") # Newline for readability

    # 4. Wait for 1 second
    print(f"Waiting for 0.5 second(s)...")
    time.sleep(0.5)

    # 5. Turn off power supplies
    turn_off_command = [
        PYTHON_EXECUTABLE,
        SCRIPT_TO_RUN,
        "-c", CONFIG_FILE,
        "--turn-off",
        "--no_reset_inst"
    ]
    if not run_command(turn_off_command):
        print("Failed to turn off power supplies. Please check manually.")
    
    print("Automated process complete.")


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
        '--runTime',
        metavar = 'TIME',
        type = int,
        help = 'maximum run time in seconds',
        default = 25,
        dest = 'runTime',
    )

    args = parser.parse_args()
    main(args)

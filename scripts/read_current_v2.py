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

import pyvisa
import time
from threading import Timer
import signal
import sys
import datetime
import pandas
import sqlite3
from pathlib import Path
from log_action import log_action_v2

# This class from stackoverflow Q 474528
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

class DeviceMeasurements():
    _power_supplies = {}
    _channels = {}

    _rt = None

    def __init__(
            self,
            outdir: Path,
            interval: int,
            baudrate: int = 9600,
            write_termination: str = None,
            read_termination: str = None,
                 ):
        self._rm = pyvisa.ResourceManager()
        self._interval = interval
        self._outdir = outdir
        self._baudrate = baudrate
        self._write_termination = write_termination
        self._read_termination = read_termination

        if self._interval < 3:
            self._interval = 3

    def add_instrument(self, name: str, manufacturer: str, model: str, serial: str, config: dict[str, str] = {}):
        self._power_supplies[name] = {
            "manufacturer": manufacturer,
            "model": model,
            "serial": serial,
            "config": config,
            "resource": None,
            "handle": None,
        }

    def add_channel(self, name: str, channel: int, alias: str, config: dict[str, str] = {}):
        if name not in self._power_supplies:
            raise RuntimeError(f"A power supply with the name {name} does not exist")

        if name not in self._channels:
            self._channels[name] = {}

        if channel in self._channels[name]:
            raise RuntimeError(f"You are defining the channel {channel} for power supply {name} twice")

        self._channels[name][channel] = {
            "alias": alias,
            "config": config,
            "Vset": None,
            "Ilimit": None,
            "on": False,
        }

    # TODO: Currently this code is specific for the CERN type of power supply, other types should be implemented here somehow
    def set_channel_voltage(self, name: str, channel: int, voltage: float):
        self._channels[name][channel]["Vset"] = voltage
        if self._channels[name][channel]["on"]:
            self._power_supplies[name]["handle"].write(f"V{channel} {voltage}")

    # TODO: Currently this code is specific for the CERN type of power supply, other types should be implemented here somehow
    def set_channel_current_limit(self, name: str, channel: int, current: float):
        self._channels[name][channel]["Ilimit"] = current
        if self._channels[name][channel]["on"]:
            self._power_supplies[name]["handle"].write(f"I{channel} {current}")

    def find_devices(self):
        resources = self._rm.list_resources()

        for resource in resources:
            #if 'ASRL/dev/ttyS' in resource.split('::')[0]:
            #    continue
            #if '/dev/ttyUSB' in resource.split('::')[0]:
            #    continue
            with self._rm.open_resource(resource) as instrument:
                try:
                    instrument.baud_rate = self._baudrate
                    instrument.timeout = 2000
                    instrument.write_termination = self._write_termination
                    instrument.read_termination = self._read_termination
                    idn: str = instrument.query('*IDN?')
                    print(idn)
                    # idn format: <company name>, <model number>, <serial number>, <firmware revision>
                    idn_info = idn.split(",")
                    idn_info = [inf.strip() for inf in idn_info]

                    for supply in self._power_supplies:
                        if idn_info[0] == self._power_supplies[supply]["manufacturer"] and idn_info[1] == self._power_supplies[supply]["model"] and idn_info[2] == self._power_supplies[supply]["serial"]:
                            self._power_supplies[supply]["resource"] = resource
                            break
                except:
                    print(f"Could not connect to resource: {resource}")
                    print("  Perhaps the device is not VISA compatible")
                    continue

        for supply in self._power_supplies:
            if self._power_supplies[supply]["resource"] is None:
                raise RuntimeError(f"Unable to find the power supply for {supply}")

        # This loop separate from above because of the lock
        for supply in self._power_supplies:
            self._power_supplies[supply]["handle"] = self._rm.open_resource(self._power_supplies[supply]["resource"])
            self._power_supplies[supply]["handle"].baud_rate = self._baudrate
            self._power_supplies[supply]["handle"].timeout = 5000
            self._power_supplies[supply]["handle"].write_termination = self._write_termination
            self._power_supplies[supply]["handle"].read_termination = self._read_termination

            for channel in self._channels[supply]:
                # TODO: Currently this code is specific for the CERN type of power supply, other types should be implemented here somehow
                state = self._power_supplies[supply]["handle"].query(f"OP{channel}?")
                if state == "0":
                    self._channels[supply][channel]['on'] = False
                elif state == "1":
                    self._channels[supply][channel]['on'] = True
                else:
                    raise RuntimeError(f"An impossible state was found for {supply} channel {channel}: \"{state}\"")

            self._power_supplies[supply]["handle"].query("IFLOCK")  # Lock the device
            self._power_supplies[supply]["handle"].query("IFLOCK")  # Lock the device

    def turn_on(self):
        for supply in self._power_supplies:
            for channel in self._channels[supply]:
                self._channels[supply][channel]['on'] = True

                voltage = self._channels[supply][channel]["Vset"]
                if voltage is None:
                    voltage = self._channels[supply][channel]["config"]["Vset"]
                    if voltage is None:
                        voltage = 0
                self.set_channel_voltage(supply, channel, voltage)

                current = self._channels[supply][channel]["Ilimit"]
                if current is None:
                    current = self._channels[supply][channel]["config"]["Ilimit"]
                    if current is None:
                        current = 0.01
                self.set_channel_current_limit(supply, channel, current)

                if 'IRange' not in self._channels[supply][channel]["config"] or self._channels[supply][channel]["config"]["IRange"] == "Low":
                    self._power_supplies[supply]["handle"].write(f"IRANGE{channel} 1")
                elif self._channels[supply][channel]["config"]["IRange"] == "High":
                    self._power_supplies[supply]["handle"].write(f"IRANGE{channel} 0")
                else:  # TODO: Move the exception to another function (the add channel for instance), to avoid exceptions during config
                    raise RuntimeError(f'Unknown IRange option: {self._channels[supply][channel]["config"]["IRange"]}')

            self._power_supplies[supply]["handle"].write("*CLS")

            for channel in self._channels[supply]:
                self._power_supplies[supply]["handle"].write(f"OP{channel} 1")
                self.log_action("Power", "On", f"{supply} {channel}")

    def start_log(self):
        time.sleep(0.5)
        self._rt = RepeatedTimer(self._interval, self.log_measurement)
        self.log_action("Power", "Logging", "Start")

    def stop_log(self):
        if self._rt is not None:
            self._rt.stop()
            self._rt = None
            self.log_action("Power", "Logging", "Stop")

    def turn_off(self):
        for supply in self._power_supplies:
            for channel in self._channels[supply]:
                self._channels[supply][channel]['on'] = False
                self._power_supplies[supply]["handle"].write(f"OP{channel} 0")
                self.log_action("Power", "Off", f"{supply} {channel}")

    def release_devices(self):
        for supply in self._power_supplies:
            self._power_supplies[supply]["handle"].query("IFUNLOCK")  # Lock the device

    def log_action(self, action_system: str, action_type: str, action_message: str):
        log_action_v2(self._outdir, action_system, action_type, action_message)
        #data = {
        #    'timestamp': [datetime.datetime.now().isoformat(sep=' ')],
        #    'type': [action_type],
        #    'action': [action],
        #}
        #df = pandas.DataFrame(data)

        #outfile = self._outdir / 'PowerHistory_v2.sqlite'
        #with sqlite3.connect(outfile) as sqlconn:
        #    df.to_sql('actions', sqlconn, if_exists='append', index=False)

    def log_measurement(self):
        measurement = self.do_measurement()

        df = pandas.DataFrame(measurement)

        outfile = self._outdir / 'PowerHistory_v2.sqlite'
        with sqlite3.connect(outfile) as sqlconn:
            df.to_sql('power_v2', sqlconn, if_exists='append', index=False)

    def do_measurement(self):
        measurement = {
            'timestamp': [],
            'V': [],
            'I': [],
            'Instrument': [],
            'Channel': [],
            'channel_id': [],
            # 'instrument_id': [],  # TODO: add a database for the instruments too, so we can track what was used where and when
        }

        for supply in self._power_supplies:
            for channel in self._channels[supply]:
                V = self._power_supplies[supply]["handle"].query(f"V{channel}O?")
                I = self._power_supplies[supply]["handle"].query(f"I{channel}O?")
                time = datetime.datetime.now().isoformat(sep=' ')

                channel_name = self._channels[supply][channel]["alias"]
                if channel_name is None:
                    channel_name = f"Channel{channel}"

                measurement["timestamp"] += [time]
                measurement["V"] += [V]
                measurement["I"] += [I]
                measurement["Instrument"] += [supply]
                measurement["Channel"] += [channel_name]
                measurement["channel_id"] += [channel]

        return measurement

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
                    prog='Read Current',
                    description='Control them!\nBy default, this script will take no action apart from finding and attempting to connect to the configured power supplies. Use the --turn-on --log --turn-off options to control what actions the script takes',
                    #epilog='Text at the bottom of help'
                    )

    parser.add_argument(
        '-l',
        '--list',
        action = 'store_true',
        help = 'List the SCPI resources and then exit',
        dest = 'list',
    )
    parser.add_argument(
        '-r',
        '--baudrate',
        type = int,
        help = 'The baud rate to connect to the instruments. All instruments must have the same baud rate. Default: 9600',
        dest = 'baudrate',
        default = 9600,
    )
    parser.add_argument(
        '-i',
        '--measurement-interval',
        type = int,
        help = 'The interval in seconds between measurements. Default: 5',
        dest = 'measurement_interval',
        default = 5,
    )
    parser.add_argument(
        '-o',
        '--output-directory',
        type = Path,
        help = 'The directory where the log file is saved to. Default: ./',
        dest = 'output_directory',
        default = Path("./"),
    )
    parser.add_argument(
        '--write-termination',
        type = str,
        help = "The termination characters used for writing. CR -> Carriage Return; LF -> Line Feed",
        dest = 'write_termination',
        #default = None,
        default = "LF",  # For CERN power supplies
        choices = [None, "CR", "LF", "CRLF", "LFCR"],
    )
    parser.add_argument(
        '--read-termination',
        type = str,
        help = "The termination characters used for reading. CR -> Carriage Return; LF -> Line Feed",
        dest = 'read_termination',
        #default = None,
        default = "CRLF",  # For CERN power supplies
        choices = [None, "CR", "LF", "CRLF", "LFCR"],
    )
    parser.add_argument(
        '--turn-on',
        action = 'store_true',
        help = 'Turn on the power supplies',
        dest = 'turn_on',
    )
    parser.add_argument(
        '--log',
        action = 'store_true',
        help = 'Log the power supplies\' measurements. The process will not exit on its own, use Ctrl+C to exit',
        dest = 'log',
    )
    parser.add_argument(
        '--turn-off',
        action = 'store_true',
        help = 'Turn off the power supplies',
        dest = 'turn_off',
    )

    args = parser.parse_args()

    if args.write_termination == "CR":
        write_termination = "\r"
    elif args.write_termination == "LF":
        write_termination = "\n"
    elif args.write_termination == "CRLF":
        write_termination = "\r\n"
    elif args.write_termination == "LFCR":
        write_termination = "\n\r"
    else:
        write_termination = None

    if args.read_termination == "CR":
        read_termination = "\r"
    elif args.read_termination == "LF":
        read_termination = "\n"
    elif args.read_termination == "CRLF":
        read_termination = "\r\n"
    elif args.read_termination == "LFCR":
        read_termination = "\n\r"
    else:
        read_termination = None

    # Defaults for CERN power supplies. i.e. THURLBY THANDAR  PL303QMD-P
    #write_termination = '\n'
    #read_termination = '\r\n'

    if args.list:
        rm = pyvisa.ResourceManager()
        resource_list = rm.list_resources()

        print(resource_list)

        for resource in resource_list:
            print(resource)

            with rm.open_resource(resource) as instrument:
                try:
                    # TODO: Need a more intelligent way in order to not force all instruments to have the same requirements
                    instrument.baud_rate = args.baudrate
                    instrument.timeout = 2000
                    instrument.write_termination = write_termination
                    instrument.read_termination = read_termination
                    idn: str = instrument.query('*IDN?')
                    print(idn)
                except:
                    continue
    else:
        device_meas = DeviceMeasurements(
                                        outdir = Path(args.output_directory),
                                        #outdir = Path('/run/media/daq/T7/'),
                                        interval = args.measurement_interval,
                                        baudrate = args.baudrate,
                                        write_termination = write_termination,
                                        read_termination = read_termination,
                                         )

        # TODO: Parse instruments and channels from a config file so that the code does not change from setup to setup, there would be a config file for each setup
        device_meas.add_instrument("Power", "THURLBY THANDAR", "PL303QMD-P", "506013")  # TID Top
        device_meas.add_instrument("WS Power", "THURLBY THANDAR", "PL303QMD-P", "425044")  # TID Bottom

        device_meas.add_channel("Power", 1, "Analog", config = {
                                                                "Vset": 1.2 + 0.04,
                                                                "Ilimit": 0.5,
                                                                "IRange": "Low",  # Alternative "High"
                                                                }
        )
        device_meas.add_channel("Power", 2, "Digital", config = {
                                                                "Vset": 1.2 + 0.09,
                                                                "Ilimit": 0.4,
                                                                "IRange": "Low",  # Alternative "High"
                                                                }
        )
        device_meas.add_channel("WS Power", 1, "Analog", config = {
                                                                "Vset": 1.2 + 0.01,
                                                                "Ilimit": 0.03,
                                                                "IRange": "Low",  # Alternative "High"
                                                                }
        )
        device_meas.add_channel("WS Power", 2, "Digital", config = {
                                                                "Vset": 1.2 + 0.01,
                                                                "Ilimit": 0.1,
                                                                "IRange": "Low",  # Alternative "High"
                                                                }
        )

        device_meas.find_devices()

        if args.turn_on:
            device_meas.turn_on()

        if args.log:
            def signal_handler(sig, frame):
                print("Exiting gracefully")

                device_meas.stop_log()
                if args.turn_off:
                    device_meas.turn_off()
                device_meas.release_devices()

                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)

            device_meas.start_log()

            signal.pause()
        else:
            if args.turn_off:
                device_meas.turn_off()

        device_meas.release_devices()

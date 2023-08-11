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
    _power_supply_resource = None
    _power_supply_instrument = None
    _vref_resource = None
    _vref_instrument = None
    _rt = None

    _power_V1_set = 1.2 + 0.022
    _power_V2_set = 1.2 + 0.05
    _power_I1_limit = 0.5
    _power_I2_limit = 0.4

    _vref_V1_set = 1.0
    _vref_V2_set = 0.0
    _vref_I1_limit = 0.01
    _vref_I2_limit = 0.0

    def __init__(self, outdir: Path, interval: int):
        self._rm = pyvisa.ResourceManager()
        self._interval = interval
        self._outdir = outdir

        if self._interval < 3:
            self._interval = 3

    def find_devices(self):
        resources = self._rm.list_resources()

        for resource in resources:
            if 'ASRL/dev/ttyS' in resource.split('::')[0]:
                continue
            with self._rm.open_resource(resource) as instrument:
                try:
                    instrument.baud_rate = 9600
                    instrument.timeout = 2000
                    instrument.write_termination = '\n'
                    instrument.read_termination = '\r\n'
                    idn = instrument.query('*IDN?')
                    print(idn)
                    if "THURLBY THANDAR" in idn and "PL303QMD-P" in idn and "506013" in idn:
                        self._power_supply_resource = resource
                    if "THURLBY THANDAR" in idn and "PL303QMD-P" in idn and "565123" in idn:
                        self._vref_resource = resource
                except:
                    continue

        if self._power_supply_resource is None:
            raise RuntimeError("Unable to find the power supply")

    def turn_on(self, do_log = True):
        if self._power_supply_resource is not None:
            self._power_supply_instrument = self._rm.open_resource(self._power_supply_resource)

            self._power_supply_instrument.baud_rate = 9600
            self._power_supply_instrument.timeout = 5000
            self._power_supply_instrument.write_termination = '\n'
            self._power_supply_instrument.read_termination = '\r\n'

            self._power_supply_instrument.query("IFLOCK")  # Lock the device

            self._power_supply_instrument.write(f"V1 {self._power_V1_set}")  # V1 is Analog supply
            self._power_supply_instrument.write(f"V2 {self._power_V2_set}")  # V2 is Digital supply
            self._power_supply_instrument.write(f"I1 {self._power_I1_limit}")
            self._power_supply_instrument.write(f"I2 {self._power_I2_limit}")

            self._power_supply_instrument.write("IRANGE1 1")  # Set both supplies to the lower current range for better resolution
            self._power_supply_instrument.write("IRANGE2 1")

            self._power_supply_instrument.write("*CLS")

            self._power_supply_instrument.write("OPALL 1")  # Turn both supplies on

        if self._vref_resource is not None:
            self._vref_instrument = self._rm.open_resource(self._vref_resource)

            self._vref_instrument.baud_rate = 9600
            self._vref_instrument.timeout = 5000
            self._vref_instrument.write_termination = '\n'
            self._vref_instrument.read_termination = '\r\n'

            self._vref_instrument.query("IFLOCK")  # Lock the device

            self._vref_instrument.write(f"V1 {self._vref_V1_set}")  # V1 is VRef
            self._vref_instrument.write(f"V2 {self._vref_V2_set}")  # V2 is ...
            self._vref_instrument.write(f"I1 {self._vref_I1_limit}")
            self._vref_instrument.write(f"I2 {self._vref_I2_limit}")

            self._vref_instrument.write("IRANGE1 1")  # Set both supplies to the lower current range for better resolution
            self._vref_instrument.write("IRANGE2 1")

            self._vref_instrument.write("*CLS")

            self._vref_instrument.write("OPALL 1")  # Turn both supplies on

        if do_log:
            time.sleep(0.5)
            self._rt = RepeatedTimer(self._interval, self.log_measurement)


    def turn_off(self):
        if self._rt is not None:
            self._rt.stop()
            self._rt = None

        if self._power_supply_instrument is not None:
            self._power_supply_instrument.write("OPALL 0")  # Turn both supplies on

            self._power_supply_instrument.query("IFUNLOCK")  # Release the lock

        if self._vref_instrument is not None:
            self._vref_instrument.write("OPALL 0")  # Turn both supplies on

            self._vref_instrument.query("IFUNLOCK")  # Release the lock

    def log_measurement(self):
        measurement = self.do_measurement()

        df = pandas.DataFrame(measurement)

        outfile = self._outdir / 'PowerHistory.sqlite'
        with sqlite3.connect(outfile) as sqlconn:
            df.to_sql('power', sqlconn, if_exists='append', index=False)

    def do_measurement(self):
        measurement = {
            'timestamp': [],
            'V1': [],
            'I1': [],
            'V2': [],
            'I2': [],
            'Instrument': [],
        }

        if self._power_supply_instrument is not None:
            V1 = self._power_supply_instrument.query("V1O?")
            I1 = self._power_supply_instrument.query("I1O?")
            V2 = self._power_supply_instrument.query("V2O?")
            I2 = self._power_supply_instrument.query("I2O?")
            time = datetime.datetime.now().isoformat(sep=' ')

            measurement["timestamp"] += [time]
            measurement["V1"] += [V1]
            measurement["I1"] += [I1]
            measurement["V2"] += [V2]
            measurement["I2"] += [I2]
            measurement["Instrument"] += ['Power']

        if self._vref_instrument is not None:
            VRef1 = self._vref_instrument.query("V1O?")
            IRef1 = self._vref_instrument.query("I1O?")
            VRef2 = self._vref_instrument.query("V2O?")
            IRef2 = self._vref_instrument.query("I2O?")
            timeRef = datetime.datetime.now().isoformat(sep=' ')

            measurement["timestamp"] += [time]
            measurement["V1"] += [V1]
            measurement["I1"] += [I1]
            measurement["V2"] += [V2]
            measurement["I2"] += [I2]
            measurement["Instrument"] += ['VRef']

        return measurement


delay_time = 5

device_meas = DeviceMeasurements(outdir=Path('.'), interval=delay_time)

device_meas.find_devices()
device_meas.turn_on()

def signal_handler(sig, frame):
    print("Exiting gracefully")

    device_meas.turn_off()

    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

signal.pause()

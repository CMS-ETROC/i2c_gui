import time
import argparse

from constellation.core.controller import ScriptableController
from constellation.core.controller_configuration import load_config
from constellation.core.protocol.cscp1 import SatelliteState

def run_daq(args):

    ## Settings
    group_name = args.group
    config_file_path = args.config

    # Create controller
    ctrl = ScriptableController(group_name)
    constellation = ctrl.constellation

    # Load configuration
    cfg = load_config(config_file_path)

    #for sat in constellation.satellites.values():
    #    print(sat.get_name())

    # Wait until all satellites are connected
    ctrl.await_satellites(["EtrocWaveform.One"])

    # Initialize and launch the Constellation with the configuration read from a file
    constellation.initialize(cfg)
    ctrl.await_state(SatelliteState.INIT)
    constellation.launch()
    ctrl.await_state(SatelliteState.ORBIT)

    # Start the run
    constellation.start(args.outDir)
    ctrl.await_state(SatelliteState.RUN)

    time.sleep(args.daq_time)

    # Stop the run and await ORBIT state of all satellites
    constellation.stop()
    ctrl.await_state(SatelliteState.ORBIT)

    constellation.land()
    ctrl.await_state(SatelliteState.INIT)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
            prog='PlaceHolder',
            description='PlaceHolder',
    )

    parser.register('type', 'hex', lambda s: int(s, 16))

    parser.add_argument(
        '--group',
        metavar = 'NAME',
        type = str,
        help = 'SAME group name with satellite',
        required = True,
        dest = 'group',
    )

    parser.add_argument(
        '--config',
        metavar = 'NAME',
        type = str,
        help = 'path to constellation TOML config file',
        required = True,
        dest = 'config',
    )

    parser.add_argument(
        '--outDir',
        metavar = 'DIR',
        type = str,
        help = 'Name of the output directory',
        required = True,
        dest = 'outDir',
    )

    parser.add_argument(
        '--daq_time',
        metavar = 'NUM',
        type= int,
        help = 'DAQ time in seconds',
        default = 60,
        dest = 'daq_time',
    )

    args = parser.parse_args()

    run_daq(args)

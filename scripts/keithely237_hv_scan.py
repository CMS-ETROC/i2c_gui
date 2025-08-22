import asyncio, time, argparse
import pandas as pd

# Devices
from prologix_gpib_async import AsyncPrologixGpibEthernetController
from pathlib import Path

testmode = False
hybrid = 'hpk'

async def main(args):

    if testmode:
        voltage = range(10, 40, 10)
        measurement_time = 5
    else:
        voltage = range(10, 280, 10)
        measurement_time = 60

    if hybrid == 'hpk':
        current_limit = -1E-6
        digit = -1e9
    elif hybrid == 'fbk':
        current_limit = -1E-4
        digit = -1e6
    else:
        exit()

    current = []

    try:
        async with AsyncPrologixGpibEthernetController("192.168.2.40", pad=22) as gpib_device:
            version = await gpib_device.version()
            print("Controller version:", version)

            await gpib_device.write(b'U1X') ## Print Error state
            print(await gpib_device.read())

            await gpib_device.write(b'U0X') ## Print Model number and firmware revision
            print(await gpib_device.read())

            ## B: Bias
            ## B(level),(range),(delay)
            ## level: voltage
            ## range: 4: 1100V mode
            ## delay: 0: no delay
            await gpib_device.write(b"B-5.0,4,0X") ## B(Voltage level),(range 4: 1100V mode),(delay)
            await gpib_device.write(b"N1X") ## Turn on output

            for ivol in voltage:
                command_string = f"B-{ivol},4,0X"
                command_bytes = command_string.encode('ascii')
                await gpib_device.write(command_bytes)
                time.sleep(0.5)

                await gpib_device.write(b"G4,2,0X")
                output = await gpib_device.read()
                formatted_output = float(output.rstrip().decode('ascii'))

                if formatted_output < current_limit:
                    current.append(formatted_output)
                    break
                else:
                    time.sleep(measurement_time)
                    await gpib_device.write(b"G4,2,0X")
                    output = await gpib_device.read()
                    formatted_output = float(output.rstrip().decode('ascii'))
                    current.append(formatted_output)

            ## G: Get output
            ## G(items),(format),(lines)
            ## items: 1: source value, 4: Measure value
            ## format: 2: ASCII data, no prefix or suffix
            ## lines: 0: One line of dc data per talk
            #await gpib_device.write(b"G1,2,0X") ## "-0015.0E+00\r\n", output format = 2
            #output = await gpib_device.read()
            #print(float(output.rstrip().decode('ascii'))) ## Remove \r\n characters and convert byte_string to float
            #time.sleep(0.5)

            #await gpib_device.write(b"G4,2,0X") ## "-0.03671E-09\r\n", output format = 2
            #output = await gpib_device.read()
            #print(float(output.rstrip().decode('ascii'))) ## Remove \r\n characters and convert byte_string to float
            #time.sleep(0.5)

            await gpib_device.write(b"N0X") ## Turn off output
            await gpib_device.write(b"B-5.0,4,0X") ## B(Voltage level),(range 4: 1100V mode),(delay)

            voltage = voltage[:len(current)]

            tmp_dict = {
                'HV': voltage,
                'current': current,
            }

            df = pd.DataFrame(tmp_dict)
            df['current'] = df['current'] * digit
            df = df.round({'HV': 1, 'current': 2})

            outdir = Path('../../IVscan')
            outdir.mkdir(exist_ok=True)
            df.to_csv(outdir / args.output, index=False)

    except (ConnectionError, ConnectionRefusedError):
        print("Could not connect to remote target. Is the device connected?")

parser = argparse.ArgumentParser(
        prog='Control Keithely 237',
        description='Remote control script for Keithely 237 source meter',
)

parser.add_argument(
    '-o',
    '--output',
    help = 'output file name',
    dest = 'output',
)

args = parser.parse_args()

asyncio.run(main(args))

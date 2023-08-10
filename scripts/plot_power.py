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

from pathlib import Path
import sqlite3
import pandas
import datetime
import matplotlib.pyplot as plt

def plot_power(
        hours: int,
        file: Path,
    ):
    with sqlite3.connect(file) as sqlite3_connection:
        data_df = pandas.read_sql('SELECT * FROM power', sqlite3_connection, index_col=None)

        data_df['timestamp'] = pandas.to_datetime(data_df['timestamp'], infer_datetime_format=True, format='mixed')

        tmp_df = data_df.loc[data_df['timestamp'] > datetime.datetime.now() - datetime.timedelta(hours=hours)]

        instruments = data_df['Instrument'].unique()

        for instrument in instruments:
            figure, axis = plt.subplots(
                nrows=2,
                ncols=2,
                sharex='col',
                #sharey='row',
            )

            this_df = tmp_df.loc[tmp_df['Instrument'] == instrument].copy()

            if instrument == "Power":
                V1_str = 'V Analog [V]'
                V2_str = 'V Digital [V]'
                I1_str = 'I Analog [A]'
                I2_str = 'I Digital [A]'
            else:
                V1_str = 'V1 [V]'
                V2_str = 'V2 [V]'
                I1_str = 'I1 [A]'
                I2_str = 'I2 [A]'
            this_df[V1_str]  = (this_df['V1'].str.replace('V','')).astype(float)
            this_df[V2_str] = (this_df['V2'].str.replace('V','')).astype(float)
            this_df[I1_str]  = (this_df['I1'].str.replace('A','')).astype(float)
            this_df[I2_str] = (this_df['I2'].str.replace('A','')).astype(float)

            figure.suptitle(f'Voltage and Current plots for instrument {instrument}')

            this_df.plot(
                x = 'timestamp',
                y = V1_str,
                kind = 'scatter',
                ax=axis[0, 0],
                #kind = 'line',
            )
            this_df.plot(
                x = 'timestamp',
                y = I1_str,
                kind = 'scatter',
                ax=axis[1, 0],
                #kind = 'line',
            )

            this_df.plot(
                x = 'timestamp',
                y = V2_str,
                kind = 'scatter',
                ax=axis[0, 1],
                #kind = 'line',
            )
            this_df.plot(
                x = 'timestamp',
                y = I2_str,
                kind = 'scatter',
                ax=axis[1, 1],
                #kind = 'line',
            )

            plt.show()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
                    prog='TID measurements',
                    description='Control them!',
                    #epilog='Text at the bottom of help'
                    )
    
    parser.add_argument(
        '-t',
        '--hours',
        metavar = 'HOURS',
        type = int,
        help = 'Hours to go back and plot. Default: 24',
        default = 24,
        dest = 'hours',
    )
    parser.add_argument(
        '-f',
        '--file',
        metavar = 'PATH',
        type = Path,
        help = 'sqlite file with the power data',
        required = True,
        dest = 'file',
    )

    args = parser.parse_args()

    plot_power(args.hours, args.file)
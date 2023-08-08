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

        data_df['V Analog [V]']  = (data_df['V1'].str.replace('V','')).astype(float)
        data_df['V Digital [V]'] = (data_df['V2'].str.replace('V','')).astype(float)
        data_df['I Analog [A]']  = (data_df['I1'].str.replace('A','')).astype(float)
        data_df['I Digital [A]'] = (data_df['I2'].str.replace('A','')).astype(float)

        tmp_df = data_df.loc[data_df['timestamp'] > datetime.datetime.now() - datetime.timedelta(hours=hours)]

        figure, axis = plt.subplots(
            nrows=2,
            ncols=2,
            sharex='col',
            #sharey='row',
        )

        tmp_df.plot(
            x = 'timestamp',
            y = 'V Analog [V]',
            kind = 'scatter',
            ax=axis[0, 0],
            #kind = 'line',
        )
        tmp_df.plot(
            x = 'timestamp',
            y = 'I Analog [A]',
            kind = 'scatter',
            ax=axis[1, 0],
            #kind = 'line',
        )

        tmp_df.plot(
            x = 'timestamp',
            y = 'V Digital [V]',
            kind = 'scatter',
            ax=axis[0, 1],
            #kind = 'line',
        )
        tmp_df.plot(
            x = 'timestamp',
            y = 'I Digital [A]',
            kind = 'scatter',
            ax=axis[1, 1],
            #kind = 'line',
        )

        plt.show()

        print(len(data_df))
        print(len(tmp_df))

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
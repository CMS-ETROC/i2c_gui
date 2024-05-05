import matplotlib.pyplot as plt
import json
import pandas as pd

senseV = []
current = []
terminalV = []
#columns = ['U0','U1','U2','U3','U5','U6','U7','time']
columns = ['U0','U1','U2','U3','U4','U5','U6','U7']

def plotting(inputfile = 'out.json'):

    with open(inputfile, 'r') as f:
        lines = f.readlines()
        
        for line in lines:
            dicc = json.loads(line)
            
            values = [float(val[:-2]) for val in dicc["Measured Sense Voltage"]]
            senseV.append(values+[dicc["timestamp"]])
            values = [float(val[:-3]) for val in dicc["Measured Current"]]
            current.append(values+[dicc["timestamp"]])
            values = [float(val[:-2]) for val in dicc["Measured Terminal Voltage"]]
            terminalV.append(values+[dicc["timestamp"]])
    
    # Crear dataframes
    senseV_data = pd.DataFrame(senseV)
    senseV_data.columns = columns
    current_data = pd.DataFrame(current)
    current_data.columns = columns
    terminalV_data = pd.DataFrame(terminalV)
    terminalV_data.columns = columns
    
    # Plotting
    fig, axes = plt.subplots(len(columns),1, figsize=(10,6*len(ids)))
    plt.grid(True)
    plt_index = 0
    for col in columns:
        axes[plt_index].plot(senseV_data["time"], senseV_data[col], marker='o', linestyle='-')
        axes[plt_index].title(f'Values vs Time ({col})')
        axes[plt_index].xlabel('Time')
        axes[plt_index].ylabel(f'{col} [uA]')
        axes[plt_index].xticks(rotation=45)
        axes[plt_index].tight_layout()
        plt_index += 1
    #plt.savefig("fig.png")

if __name__=='__main__':
    parser = argparse.ArgumentParser(
                    prog='HV Plotter',
                    description='Plot output of DESY TB21 NI Crate HV',
                    )

    parser.add_argument(
        '-i',
        '--input-file',
        type = str,
        help = 'The name of the json file with HV vals. Default: out.json',
        dest = 'input_file',
        default = 'out.json',
    )
    #parser.add_argument(
    #    '-d',
    #    '--output-directory',
    #    type = Path,
    #    help = 'Path to where the json file should be stored. Default: ./',
    #    dest = 'output_directory',
    #    default = Path("./"),
    #)

    #parser.add_argument(
    #    '-t',
    #    '--time-limit',
    #    type = int,
    #    help = 'Amount of time to log for. Default: 5',
    #    dest = 'time_limit',
    #    default = 5,
    #)

    args = parser.parse_args()

    inputfile = args.input_file

    print('------------------- Plotting ---------------------')
    print(f'Inputfile is {inputfile}.')

    plotting(inputfile)

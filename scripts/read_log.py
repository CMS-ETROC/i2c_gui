import matplotlib.pyplot as plt
import json
import pandas as pd

senseV = []
current = []
terminalV = []
columns = ['U1','U2','U3','U4','U6','time']

# Leer el archivo JSON
with open('NICrate_runtest.json', 'r') as f:
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

# Plotear
plt.figure(figsize=(10, 6))
plt.plot(senseV_data["time"], senseV_data["U6"], marker='o', linestyle='-')
plt.title('Values vs Time (U6)')
plt.xlabel('Time')
plt.ylabel('Value')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("fig.png")

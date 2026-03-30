# This directory has scripts for EMI/EMC testing

The user only tested this with python version 3.13.1. Python 3.13.1 can be installed via [pyenv](https://github.com/pyenv/pyenv).

## Installation

Starting from your base directory. First clone git repos in the following:

- Clone i2c package


```git clone git@github.com:CMS-ETROC/i2c_gui.git -b i2c_gui_2 --depth=1```

- Clone ETROC DAQ based on constellation


```git clone git@github.com:CMS-ETROC/Constellation.git -b ETROC2v2 --depth=1```

- Clone KC705 firmware (The user must be a member of CMS-ETROC git organization)
```
git clone git@github.com:CMS-ETROC/ETROC2TestFirmware.git -b SEU2025 --depth=5
cd ETROC2TestFirmware
git checkout a620653
cd ../
```

- Assuming that the user is using pyenv environment.


`pyenv shell 3.13.1`

- Either the user can use venv environment.


`python -m venv venv`
`source venv/bin/activate`

- Install python packages via pip


`pip install -r i2c_gui/emi_emc_testing/emirequirements.txt`

- Install Constellation via pip
```
cd Constellation
pip install "ConstellationDAQ[cli]" -e .
```

## Preparation
You need to open three terminals. One for running scripts, the other terminals for constellation Satellites. Also, all terminals must load the same python environment.

- Tab 1 (EtrocTransmitter Satellite)
```
cd Constellation
SatelliteEtrocTransmitter -g <group_name> -n One
```

- Tab 2 (EtrocReceiver Satellite)
```
cd Constellation
SatelliteEtrocReceiver -g <group_name> -n One
```

- Tab 3


`cd i2c_gui/emi_emc_testing`

## Update config
Use your preferred tool to change the parameters in qinj_external_trig.toml

## Run
While both satellites are online, you run scripts in Tab 3.

- To run i2c


`python run_i2c.py -h`

- To run constellation


`python run_constellation -h`
# This directory has scripts for EMI/EMC testing

This framework only tested with python version 3.13.1. Python 3.13.1 can be installed via [pyenv](https://github.com/pyenv/pyenv).
However, if python version >= 3.11, the framework should work.

## Installation

Starting from your base directory. First clone git repos in the following:

### - Clone i2c package
```
git clone git@github.com:CMS-ETROC/i2c_gui.git -b i2c_gui_2 --depth=1
```

### - Clone ETROC DAQ based on constellation
```
git clone git@github.com:CMS-ETROC/Constellation.git -b ETROC2v2 --depth=1
```

### - Clone KC705 firmware (The user must be a member of CMS-ETROC git organization)
```
git clone git@github.com:CMS-ETROC/ETROC2TestFirmware.git -b SEU2025 --depth=5
```

### Set pyenv or venv enviornment
#### To install python version and actiave for shell
```
pyenv install 3.13.1
pyenv shell 3.13.1
```

#### To install and activate python venv
```
python -m venv venv
source venv/bin/activate
```
### - Install python packages via pip
```
pip install -r i2c_gui/emi_emc_testing/requirements.txt
```

### - Install Constellation via pip
```
cd Constellation
pip install "ConstellationDAQ[cli]" -e .
```

## Update configs
There are two different format of config files can be found in "configs" directory. yaml files is for run script, toml files are for constellation satellite. Please use your preferred editor to update the config.

## How to run Charge injection
You need to open three terminals. One for running scripts, the other terminals for constellation Satellites. Also, all terminals must load the same python environment.

### - Tab 1 (EtrocTransmitter Satellite)
```
cd Constellation
SatelliteEtrocTransmitter -g <group_name> -n One
```

### - Tab 2 (EtrocReceiver Satellite)
```
cd Constellation
SatelliteEtrocReceiver -g <group_name> -n One
```

### - Tab 3
```
cd i2c_gui/emi_emc_testing
python config_etroc_for_qinj.py --config <path to yaml> --note <unique note for BL and NW history> (--load-history)
python run_qinj_constellation.py --group <group_name> --config <path to toml> --outDir <output directory name> --daq_time <daq run time in seconds>
```

### - Tab 4 (Optional)
In case, the user have an issue that not seeing charge injection LED lights on KC705, the user can debug the system by the following command
```
Controller -g <group name> -c <path to toml>
```
The command will open IPython console then
```
constellation.initialize(cfg)
constellation.launch()
constellation.EtrocTransmitter.set_data_phase_channel_delay([value, channel])
constellation.EtrocTransmitter.set_fc_phase_channel_delay([value, channel])
```
Once you find the right delay, you can copy and paste the register values into toml files.

## How to run Waveform Sampler
You need to open two terminals. One for running scripts, the other terminal for constellation Satellites. Also, all terminals must load the same python environment. I2C library is merged into a waveform satellite, so all the i2c configuration is also in toml file. Note that **reading waveform sampler data via i2c is slow, it takes about 12 seconds for each waveform!** So please give enough time to collect waveform, also for some reason, it is not guaranteed that every waveform has a charge injection pulse.

### - Tab 1 (EtrocWaveform Satellite)
```
cd Constellation
SatelliteEtrocWaveform -g <group_name> -n One
```

### - Tab 2
```
cd i2c_gui/emi_emc_testing
python run_qinj_constellation.py --group <group_name> --config <path to toml> --outDir <output directory name> --daq_time <daq run time in seconds>
```
# ITA 2026 April Logbook

Campaign started on 6th April 2026, Jordi arrived at ITA and did the initial setup.

On 7th of April 2026, actual campaign started.
Initial setup took some time to set up, in particular to have the steering scripts calling the I2C/DAQ scripts running inside a docker and integrated with the GUI.

## First runs - Baseline & QInjTEST

* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $28\.\mu A$

### Baseline + Noise width
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260407_VDDA_TEST01

Initial test run was configured to inject all noise at a constant current of $10\.mA$ [Measured in RMS] with the following frequencies:
- $0.1\.MHz$
- $0.2\.MHz$
- $0.3\.MHz$
- $0.4\.MHz$
- $0.5\.MHz$
- $0.6\.MHz$
- $0.7\.MHz$
- $0.8\.MHz$
- $0.9\.MHz$
- $1.0\.MHz$
- $1.5\.MHz$
- $2.0\.MHz$
- $3.0\.MHz$
- $4.0\.MHz$
- $5.0\.MHz$
- $7.0\.MHz$
- $10\.MHz$
- $12\.MHz$
- $15\.MHz$
- $17\.MHz$
- $20\.MHz$
- $22\.MHz$
- $25\.MHz$
- $27\.MHz$
- $30\.MHz$
- $40\.MHz$
- $50\.MHz$
Exception of frequency 0, with current 0, serves as the reference.

Something happened towards the end of the run, where the injected current monitoring registered up to $300\.mA$ of injected current and both the ETROC and USB-ISS latched up, requiring a powr cycle to recover.


### QInj
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260407_VDDA_TEST01_QInj

In a second step, using same injected noise parameters, we perform a QInj data taking for each point with offset 10, using the baselines measured before any noise was injected. Trigger is configured in the "fixed trigger mode", i.e. the L1A FC is sent automatically a fixed number of bunch crossings after the QInj FC. Also stopped quite ealrly due to unspecified issue with DAQ

## Second Run

Adjusted power levels with respect to first run.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $28\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260407_VDDA_Overnight

For this run, we adjusted the power level with respect to the first run, we set the following values:
- 0.1: $20\.mA$
- 0.2: $20\.mA$
- 0.3: $20\.mA$
- 0.4: $5\.mA$
- 0.5: $5\.mA$
- 0.6: $5\.mA$
- 0.7: $5\.mA$
- 0.8: $5\.mA$
- 0.9: $5\.mA$
- 1.0: $20\.mA$
- 1.5: $20\.mA$
- 2.0: $20\.mA$
- 3.0: $20\.mA$
- 4.0: $20\.mA$
- 5.0: $20\.mA$
- 7.0: $20\.mA$
- 10: $20\.mA$
- 12: $20\.mA$
- 15: $20\.mA$
- 17: $20\.mA$
- 20: $20\.mA$
- 22: $20\.mA$
- 25: $20\.mA$
- 27: $20\.mA$
- 30: $20\.mA$
- 40: $20\.mA$
- 50: $20\.mA$

## Third Run

Attempted to set up an overnight run scanning both frequency and multiple power levels.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260407_VDDA_Overnight

Due to an issue with the power amplifier/monitor, only the first few points (~4) are good, i.e. $100\.kHz$ at [$1$, $3$, $5$, $30$] $mA$.

## Fourth Run

Retrying QInj, same settings as first run (i.e. same frequency list an $10\.mA$). With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_10mA

First attempt ran well, but a few frequency points are missing because ETROC communication failed:
- $0.8\.MHz$
- $0.9\.MHz$
- $1.0\.MHz$
- $1.5\.MHz$
- $2.0\.MHz$
- $10\.MHz$
- $12\.MHz$
- $22\.MHz$

## Fifth run

Repeating QInj, same settings as first run but reduced power ($5 mA$). With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_5mA

Ran well, but a few frequency points are missing because ETROC communication failed:
- $1.0\.MHz$
- $1.5\.MHz$
- $2.0\.MHz$
- $3.0\.MHz$
- $30\.MHz$
- $40\.MHz$

## Sixth run

Repeating QInj, same settings as first run but reduced power ($3 mA$). With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_3mA

Ran well, no frequency points are missing due to ETROC communication failures

## Seventh run

Repeating QInj, same settings as first run but increased power ($20 mA$). With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_20mA

Ran well, but a few frequency points are missing due to ETROC communication failures
- $15\.MHz$
- $17\.MHz$

## Eighth run

Repeating QInj, same settings as first run but different power settings power, trying to fill in the failures from previous QInj runs. With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_several (later moved into the respective directories for the respective power level)

Ran well, but a few frequency points are still missing due to ETROC communication failures, mostly at $10 mA$:
- $5\.mA$; $2\.MHz$
- $10\.mA$; $0.9\.MHz$
- $10\.mA$; $1.0\.MHz$
- $10\.mA$; $1.5\.MHz$
- $10\.mA$; $2.0\.MHz$
- $10\.mA$; $10\.MHz$
- $10\.mA$; $12\.MHz$
- $10\.mA$; $22\.MHz$

## Ninth run

Repeating QInj, same settings as first run but different power settings power, trying to fill in the failures from previous QInj run. With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_several (later moved into the respective directories for the respective power level)

Ran well, but a few frequency points are still missing due to ETROC communication failures, only at $10 mA$:
- $10\.mA$; $2.0\.MHz$
- $10\.mA$; $10\.MHz$
- $10\.mA$; $12\.MHz$
- $10\.mA$; $22\.MHz$

## Tenth run

Repeating QInj, same settings as first run but different power settings power, trying to fill in the failures from previous QInj run. With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_several (later moved into the respective directories for the respective power level)

Ran well, but a few frequency points are still missing due to ETROC communication failures, only at $10 mA$:
- $10\.mA$; $10\.MHz$
- $10\.mA$; $12\.MHz$
- $10\.mA$; $22\.MHz$

## Eleventh run

Repeating QInj, same settings as first run but different power settings power, trying to fill in the failures from previous QInj run. With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_several (later moved into the respective directories for the respective power level)

Ran well, but a few frequency points are still missing due to ETROC communication failures, only at $10 mA$:
- $10\.mA$; $12\.MHz$

## Twelfth run

Repeating QInj, same settings as first run but different power settings power, trying to fill in the failures from previous QInj run. With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_several (later moved into the respective directories for the respective power level)

Ran well, no frequency points are missing due to ETROC communication failures

## Thirteenth run

Repeating Baseline+noisewidth scan, but this time do the full thing at once.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_BLNW/

$50\.MHz$ at $10\.mA$ failed very frequently. We were not able to run it. Tried to do $20\.mA$ directly, since it worked before but even then did not work this time. Maybe due to higher temperature? The LGAD current is higher, which seems to imply a higher temperature.

## Fourteenth Run

Performing QInj, in self trigger with QInj disabled, same frequency list as before but with $3\.mA$.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_Noise/noise_offset8_st_3mA

All frequencies without issue except $50\.MHz$, which failed

## Fifteenth Run

Performing QInj, in self trigger with QInj disabled, same frequency list as before but with $5\.mA$.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_Noise/noise_offset8_st_5mA

Some issues with frequencies:
- $0.5\.MHz$
- $0.6\.MHz$
- $0.9\.MHz$
- $3\.MHz$
- $4\.MHz$
- $5\.MHz$
- $7\.MHz$
- $10\.MHz$
- $12\.MHz$
- $15\.MHz$
- $25\.MHz$
- $50\.MHz$
- Check carefully later, we may have missed some other frequencies with issues

## Sixteenth Run

Performing QInj, in self trigger with QInj disabled, same frequency list as before but with $10\.mA$.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\.V$
  * VDDA : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_Noise/noise_offset8_st_10mA

Some issues with frequencies:
- $0.8\.MHz$
- $4\.MHz$
- $5\.MHz$
- $30\.MHz$

## Seventeenth Run

Changed to VDDD noise injection, setting up an overnight baeline+Noise width run.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDA + VDDWSD + VDDWSA : $1.2\.V$
  * VDDD : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $32\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDD_BLNW/

Full "double" scan finished without issue.
Used the regular frequencies and for injected current we had the following list:
- $3\.mA$
- $4\.mA$
- $5\.mA$
- $6\.mA$
- $7\.mA$
- $8\.mA$
- $9\.mA$

## Eighteenth Run

Still VDDD noise injection, now performing QInj with fixed trigger
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDA + VDDWSD + VDDWSA : $1.2\.V$
  * VDDD : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $27\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260409_VDDD_QInj/qinj_fixed_3mA

Scanning normal frequencies. Some issues with frequencies:
- $0.1\.MHz$
- $0.2\.MHz$
- $7\.MHz$
- $10\.MHz$
- $12\.MHz$
- $15\.MHz$
- $17\.MHz$
- $20\.MHz$
- $22\.MHz$
- $40\.MHz$
- $50\.MHz$


## Nineteenth Run

Still VDDD noise injection, now performing QInj with fixed trigger
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDA + VDDWSD + VDDWSA : $1.2\.V$
  * VDDD : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $27\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260409_VDDD_QInj/qinj_fixed_5mA

Scanning normal frequencies. It appears all frequencies worked.

## Twentieth Run

Still VDDD noise injection, now performing noise with self trigger (no QInj)
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDA + VDDWSD + VDDWSA : $1.2\.V$
  * VDDD : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $28\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260409_VDDD_Noise/noise_offset7_st_3mA

Scanning normal frequencies.

Appears to be no data... configuration issue?

## Twenty First Run

Still VDDD noise injection, back to baseline+noise width, but higher current ($15\.mA$).
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDA + VDDWSD + VDDWSA : $1.2\.V$
  * VDDD : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $28\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260409_VDDD_BLNW/

Scanning normal frequencies expanded with $60\.MHz$, $70\.MHz$, $80\.MHz$ and removing $0.4\.MHz$ to $0.8\.MHz$ frequencies.

From $40\.MHz$ forward, the system failed and I2C communication was lost.

## Twenty Second Run

Still VDDD noise injection, doing baseline+noise width, with current ($10\.mA$).
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDA + VDDWSD + VDDWSA : $1.2\.V$
  * VDDD : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $28\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260409_VDDD_BLNW/

Reduced set of frequencies:
- $40\.MHz$
- $50\.MHz$
- $60\.MHz$
- $70\.MHz$
- $80\.MHz$

## Twenty Third Run

Still VDDD noise injection, doing baseline+noise width, with current ($12\.mA$).
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDA + VDDWSD + VDDWSA : $1.2\.V$
  * VDDD : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $28\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260409_VDDD_BLNW/

Reduced set of frequencies:
- $40\.MHz$
- $50\.MHz$
- $60\.MHz$
- $70\.MHz$
- $80\.MHz$

## Twenty Fourth Run

Still VDDD noise injection, doing baseline+noise width, with current ($20\.mA$).
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDA + VDDWSD + VDDWSA : $1.2\.V$
  * VDDD : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $28\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260409_VDDD_BLNW/

Scanning normal frequencies, but removing $0.4\.MHz$ to $0.8\.MHz$ and $40\.MHz$ and $50\.MHz$ frequencies.

Suggest to repeat frequencies:
- $10\.MHz$
- $15\.MHz$
- $20\.MHz$
- $27\.MHz$

## Twenty Fifth Run

Still VDDD noise injection, doing baseline+noise width, with current ($30\.mA$).
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDA + VDDWSD + VDDWSA : $1.2\.V$
  * VDDD : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $28\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260409_VDDD_BLNW/

Scanning reduced set of frequencies to find limits:
- $0.1\.MHz$
- $0.2\.MHz$
- $0.3\.MHz$
- $0.9\.MHz$
- $1\.MHz$
- $5\.MHz$
- $10\.MHz$
- $15\.MHz$
- $20\.MHz$
- $25\.MHz$
- $30\.MHz$

$30\.MHz$ failed?

## Twenty Sixth Run

Still VDDD noise injection, doing baseline+noise width, with current ($40\.mA$).
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDA + VDDWSD + VDDWSA : $1.2\.V$
  * VDDD : $1.2\.V$ with noise injected
  * VRef : External $1\.V$
* HV:
  * Bias Voltage: $200\.V$
  * Leakage Current: $28\.\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260409_VDDD_BLNW/

Scanning reduced set of frequencies to find limits:
- $0.1\.MHz$
- $0.2\.MHz$
- $0.3\.MHz$
- $0.9\.MHz$
- $1\.MHz$
- $5\.MHz$
- $10\.MHz$
- $15\.MHz$
- $20\.MHz$
- $25\.MHz$
- $30\.MHz$


# Help - Tip&Tricks

## Docker Setup
[TODO]

## Docker
Jordi configured all the code to run inside docker, mkaes setup and portability a bit easier, but adds a layer of indirection to run commands.

We are using docker compose to help manage the docker commands, if not, some commands become very long.
There is a docker compose config file, where a lot of details are defined.
The "home" directory for docker and docker compose is `/home/electricos/ETROC2_NoiseCampaign`.
The docker compose config file can be found in this directory as `docker-compose.yml`.

To run the docker container and put terminal inside the container (if we close/exit this, the container is closed, so keep this running for however long is needed to run the tests):
`docker compose run --rm noise`

Inside docker go to the data directory which is the host /home/electricos/ETROC2_NoiseCampaign mounted to /data:
`cd /data`

Inside data directory, we can run the regular commands, scripts (from Jordi) which are reorganised from Jongho run scripts.
To run baseline autocalibration, normally from the specific subdirectory: `python ../scripts/etroc2-sc.py --config et20p1_Pair5.yaml --do-checks autocal --save-note [note]`
To run QInj/noise:
 - Make sure baselines have been acquired first
 - Then configure pixels for QInj: `python ../scripts/etroc2-sc.py --config et20p1_Pair5.yaml --do-checks qinj --qinj-en`
 - Or configure pixels for noise: `python ../scripts/etroc2-sc.py --config et20p1_Pair5.yaml --do-checks qinj --no-qinj-en`
 - Then run DAQ data taking: `python ../scripts/etroc2-daq.py --group [gname] --config qinj_external_trig.toml --outdir [DIR]`

From another terminal, to open a connection to the container:
`docker exec -it [container_name] /bin/bash`

To get container name, try tab completion, if not works, use the command:
`docker ps`

## Constellation

With a terminal to the docker container, run the satellites (receiver/trnasmitter).
`SatelliteEtrocReceiver -g [gname] -n K2`
`SatelliteEtrocTransmitter -g [gname] -n K2`

gname should match, here we hard code in some places gname to `IFCA`

## Quick Analysis Scripts

Inside docker container, inside the data storage (/data/*) run the analysis scripts:
- Baseline analysis: `../scripts/plot_bl_noise.py [folder] [board_name] --output-dir [dir]`
- QInj analysis: `../scripts/plot_daq_observables.py [folder] --output-dir [dir]`

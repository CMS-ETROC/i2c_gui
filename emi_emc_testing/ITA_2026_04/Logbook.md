# ITA 2026 April Logbook

Campaign started on 6th April 2026, Jordi arrived at ITA and did the initial setup.

On 7th of April 2026, actual campaign started.
Initial setup took some time to set up, in particular to have the steering scripts calling the I2C/DAQ scripts running inside a docker and integrated with the GUI.

## First runs - TEST

* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260407_VDDA_TEST01

Initial test run was configured to inject all noise at a constant current of $10\,mA$ [RMS?] with the following frequencies:
- 0.1
- 0.2
- 0.3
- 0.4
- 0.5
- 0.6
- 0.7
- 0.8
- 0.9
- 1.0
- 1.5
- 2.0
- 3.0
- 4.0
- 5.0
- 7.0
- 10
- 12
- 15
- 17
- 20
- 22
- 25
- 27
- 30
- 40
- 50
Exception of frequency 0, with current 0, serves as the reference.

Something happened towards the end of the run, where the injected current monitoring registered up to $300\,mA$ of injected current and both the ETROC and USB-ISS latched up, requiring a powr cycle to recover.


### QInj
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260407_VDDA_TEST01_QInj

In a second step, using same injected noise parameters, we perform a QInj data taking for each point with offset 10, using the baselines measured before any noise was injected. Trigger is configured in the "fixed trigger mode", i.e. the L1A FC is sent automatically a fixed number of bunch crossings after the QInj FC. Also stopped quite ealrly due to unspecified issue with DAQ

## Second Run

Adjusted power levels with respect to first run.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260407_VDDA_Overnight

For this run, we adjusted the power level [RMS?] with respect to the first run, we set the following values:
- 0.1: $20 mA$
- 0.2: $20 mA$
- 0.3: $20 mA$
- 0.4: $5 mA$
- 0.5: $5 mA$
- 0.6: $5 mA$
- 0.7: $5 mA$
- 0.8: $5 mA$
- 0.9: $5 mA$
- 1.0: $20 mA$
- 1.5: $20 mA$
- 2.0: $20 mA$
- 3.0: $20 mA$
- 4.0: $20 mA$
- 5.0: $20 mA$
- 7.0: $20 mA$
- 10: $20 mA$
- 12: $20 mA$
- 15: $20 mA$
- 17: $20 mA$
- 20: $20 mA$
- 22: $20 mA$
- 25: $20 mA$
- 27: $20 mA$
- 30: $20 mA$
- 40: $20 mA$
- 50: $20 mA$

## Third Run

Attempted to set up an overnight run scanning both frequency and multiple power levels.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260407_VDDA_Overnight

Due to an issue with the power amplifier/monitor, only the first few points (~4) are good, i.e. 100 kHz at [1, 3, 5, 30] mA.

## Fourth Run

Retrying QInj, same settings as first run (i.e. same frequency list an $10\,mA$). With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_10mA

First attempt ran well, but a few frequency points are missing because ETROC communication failed:
- 0.8
- 0.9
- 1.0
- 1.5
- 2.0
- 10
- 12
- 22

## Fifth run

Repeating QInj, same settings as first run but reduced power ($5 mA$). With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_5mA

Ran well, but a few frequency points are missing because ETROC communication failed:

- 1.0
- 1.5
- 2.0
- 3.0
- 30
- 40

## Sixth run

Repeating QInj, same settings as first run but reduced power ($3 mA$). With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_3mA

Ran well, no frequency points are missing due to ETROC communication failures

## Seventh run

Repeating QInj, same settings as first run but increased power ($20 mA$). With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_20mA

Ran well, but a few frequency points are missing due to ETROC communication failures

- 15
- 17

## Eighth run

Repeating QInj, same settings as first run but different power settings power, trying to fill in the failures from previous QInj runs. With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_several (later moved into the respective directories for the respective power level)

Ran well, but a few frequency points are still missing due to ETROC communication failures, mostly at $10 mA$:

- $5 mA$; $2 MHz$
- $10 mA$; $0.9 MHz$
- $10 mA$; $1.0 MHz$
- $10 mA$; $1.5 MHz$
- $10 mA$; $2.0 MHz$
- $10 mA$; $10 MHz$
- $10 mA$; $12 MHz$
- $10 mA$; $22 MHz$

## Ninth run

Repeating QInj, same settings as first run but different power settings power, trying to fill in the failures from previous QInj run. With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_several (later moved into the respective directories for the respective power level)

Ran well, but a few frequency points are still missing due to ETROC communication failures, only at $10 mA$:

- $10 mA$; $2.0 MHz$
- $10 mA$; $10 MHz$
- $10 mA$; $12 MHz$
- $10 mA$; $22 MHz$

## Tenth run

Repeating QInj, same settings as first run but different power settings power, trying to fill in the failures from previous QInj run. With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_several (later moved into the respective directories for the respective power level)

Ran well, but a few frequency points are still missing due to ETROC communication failures, only at $10 mA$:

- $10 mA$; $10 MHz$
- $10 mA$; $12 MHz$
- $10 mA$; $22 MHz$

## Eleventh run

Repeating QInj, same settings as first run but different power settings power, trying to fill in the failures from previous QInj run. With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_several (later moved into the respective directories for the respective power level)

Ran well, but a few frequency points are still missing due to ETROC communication failures, only at $10 mA$:

- $10 mA$; $12 MHz$

## Twelfth run

Repeating QInj, same settings as first run but different power settings power, trying to fill in the failures from previous QInj run. With fixed trigger.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_QInj/qinj_fixed_several (later moved into the respective directories for the respective power level)

Ran well, no frequency points are still missing due to ETROC communication failures

## Thirteenth run

Repeating Baseline+noisewidth scan, but this time do the full thing at once.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_BLNW/

$50 MHz$ at $10 mA$ failed very frequently. We were not able to run it. Tried to do $20 mA$ directly, since it worked before and then tried to complete with $7 mA$.

## Fourteenth Run

Performing QInj, in self trigger with QInj disabled, same frequency list as before but with $3\,mA$.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_Noise/noise_offset8_st_3mA

All frequencies without issue except $50 MHz$, which failed

## Fifteenth Run

Performing QInj, in self trigger with QInj disabled, same frequency list as before but with $5\,mA$.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_Noise/noise_offset8_st_5mA

Some issues with frequencies:
- 0.5
- 0.6
- 0.9
- 3
- 4
- 5
- 7
- 10
- 12
- 15
- 25
- 50
- other - check carefully later

## Sixteenth Run

Performing QInj, in self trigger with QInj disabled, same frequency list as before but with $10\,mA$.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDD + VDDWSD + VDDWSA : $1.2\,V$
  * VDDA : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDA_Noise/noise_offset8_st_10mA

Some issues with frequencies:
- 0.8
- 4
- 5
- 30

## Seventeenth Run

Changed to VDDD noise injection, setting up an overnight baeline+Noise width run.
* ETROC Board: Pair 5 (from Jordi)
* Power supplies:
  * VDDA + VDDWSD + VDDWSA : $1.2\,V$
  * VDDD : $1.2\,V$ with noise injected
  * VRef : External $1\,V$
* HV:
  * Bias Voltage: $200\,V$
  * Leakage Current: $28\,\mu A$
* Storage directory: /home/electricos/ETROC2_NoiseCampaign/20260408_VDDD_BLNW/

Full scan finished without issue. Used the regular frequencies and for injected current, we had the following list:
- $3 mA$
- $4 mA$
- $5 mA$
- $6 mA$
- $7 mA$
- $8 mA$
- $9 mA$
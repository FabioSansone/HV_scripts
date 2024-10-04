# HV scripts

Scripts to command the HV and FEB boards of the Hyper-Kamiokande mPMTs detectors

## FEB_firmware

- The HK.. files ending in .hex are the FEB microcontroller firmwares, the latest one to use is HKL031V4A.hex, to program the FEB use reprogram_FEBs.py. Use
```sh
reprogram_FEBs.py --help
```
for help on the script.

## Scripts

- rc_utils and hv_utils are the libraries needed by all the other scripts to control the runcontrol and the high-voltage
- the not python scripts are to use within the HV and RC shells
- All the other scripts are python based:
    - ACQ_nexys.py is the acquisition script, it istantiate a class acquisitor, that acquires data and ooutputs a .csv file
    - CRC32.py is the library that has the function to calculate and check the CRC bits in the data
    - allTurnON.py turns on all 19 FEBs 4 every second to make sure that the power supply is not overloaded, which would shut down the board
    - set_address.py is used to set the modbus address to all the FEBs, since after the programming all of them have address 20
    - thresholdscanLED.py and thresholdscanSC.py are the script used for the thresholdscan of a single PMT (single channel = SC) 

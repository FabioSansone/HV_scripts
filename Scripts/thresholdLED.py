import serial
import sys
import time
import csv
import numpy as np
from ACQ_nexys import acquisitor
sys.path.append('/home/rock/Tscan_PMT/hv_utils')
sys.path.append('/home/rock/Tscan_PMT/rc_utils')
from ListaCMD import RunControl
from hvmodbus import HVModbus

def main():
    RC = RunControl()
    FEB = HVModbus()
    try:
        FEB.open(serial='/dev/ttyUSB0', addr=1)
        print('FEB connessa.')
    except serial.SerialException:
        print('Seriale non trovata di HV.')
        sys.exit()
    
    thresholds = [10, 15, 20, 25, 30, 35, 40, 50, 100, 150, 200, 250, 300]

    try:
        FEB.setVoltageSet(1210)
        print(f'Voltage set to {1210}')
    except AttributeError:
        print('FEB non trovata')
        sys.exit()

    FEB.powerOn()
    stateON = 1
    print('RampUP voltage')
    while stateON != 0:
        Febdata = FEB.readMonRegisters()
        print(f'{Febdata["V"]} V, {Febdata["I"]} uA')
        stateON = int(Febdata['status'])
        time.sleep(1)

    for threshold in thresholds:
        
        FEB.setThreshold(threshold)

        RC.Port.Send_CMD(0x9, 0XF)
        time.sleep(1)
        RC.Port.Send_CMD(0x9, 0x0)
        time.sleep(0.25)

        ac = acquisitor(MaxEvent=50000, port='/dev/ttyUSB3', filename=f'thNOLED_{threshold}')
        ac.connect()
        ac.nexysACQ()
        
    FEB.powerOff()
    stateON = 0
    print('RampDOWN voltage')
    while stateON != 1:
        Febdata = FEB.readMonRegisters()
        print(f'{Febdata["V"]} V, {Febdata["I"]} uA')
        stateON = int(Febdata['status'])
        time.sleep(1)

if __name__ == '__main__':
    main()

import serial
import sys
import time
import csv
import numpy as np
sys.path.append('/home/rock/Tscan_PMT/hv_utils')
sys.path.append('/home/rock/Tscan_PMT/rc_utils')
from ListaCMD import RunControl
from hvmodbus import HVModbus

def do_threshold(Vset, namefile):
    RC = RunControl()
    FEB = HVModbus()
    try:
        FEB.open(serial='/dev/ttyUSB0', addr=1)
        print('FEB connessa.')
    except serial.SerialException:
        print('Seriale non trovata di HV.')
        sys.exit()
    discr = FEB.readCalibRegisters()
    print(f'Discr set to {round(discr[2])}')

    file = open(namefile, 'w')
    writer = csv.writer(file)
    writer.writerow(['Vset', 'Threshold', 'Rate'])
    file.close()

    for voltage in Vset:
        try:
            FEB.setVoltageSet(voltage)
            print(f'Voltage set to {voltage}')
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

        for i in range(1, 300):
            try:
                FEB.setThreshold(i)
            except AttributeError:
                print('FEB non trovata.')
                sys.exit()
                rate = 0
            for j in range(1000):
                rate = int(RC.Port.Send_CMD(0xE))
                with open(namefile, 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow([voltage, i, rate])
                time.sleep(1)
                print(f'Threshold a {i}, misura {j} --> ratemeter: {rate}')

    FEB.powerOff()
    stateON = 0
    print('RampDOWN voltage')
    while stateON != 1:
        Febdata = FEB.readMonRegisters()
        print(f'{Febdata["V"]} V, {Febdata["I"]} uA')
        stateON = int(Febdata['status'])
        time.sleep(1)


if __name__ == '__main__':
    do_threshold([1210], 'tscan_taketaNOLED.csv')

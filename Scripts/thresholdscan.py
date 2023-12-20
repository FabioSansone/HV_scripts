import allTurnON
import serial
import sys
import mmap
import argparse
from hvmodbus import HVModbus
import time
import csv
import numpy as np

def do_threshold(Vset, namefile, FEB, regs, address):
    try:
        FEB.openFEB(serial='/dev/ttyPS2', addr=address)
    except serial.SerialException:
        print('Seriale non trovata.')
        sys.exit()
    discr = FEB.readCalibRegisters()
    print(f'Discr set to {discr[2]}')
    allTurnON.do_write(0, 2**(address-1), regs)  # chip-select
    file = open(namefile, 'w')
    writer = csv.writer(file)
    writer.writerow(['Vset', 'Threshold', 'Rate'])
    file.close()
    for i in range(500):
        try:
            FEB.setThreshold(i)
        except AttributeError:
            print(F'FEB non trovata.')
            sys.exit()

        rate_array = []
        for j in range(10):
            rate_array.append(allTurnON.do_read(address + 19, regs))
            time.sleep(1)
        file = open(namefile, 'a')
        writer = csv.writer(file)
        writer.writerow([Vset, i, np.mean(rate_array)])
        file.close()
        print(f'Threshold set to {i}mV --> ratemeter: {np.mean(rate_array)}')

def turn_on_HV_all(boards, Vset):
    currentstate = []
    stateON = [0] * 19
    for FEB, i in zip(boards, range(1, 20)):
        try:
            FEB.openFEB(serial='/dev/ttyPS2', addr=i)
        except serial.SerialException:
            print('Seriale non trovata.')
            sys.exit()
        FEB.setVoltageSet(int(Vset))
        FEB.powerOn()
        print(f'HV {i} turned on')
        time.sleep(0.5)
    while currentstate != stateON:
        print('mPMT ramp-up')
        currentstate = []
        for FEB, i in zip(boards, range(1, 20)):
            try:
                FEB.openFEB(serial='/dev/ttyPS2', addr=i)
            except serial.SerialException:
                sys.exit(-1)
            Febdata = FEB.readMonRegisters()
            currentstate.append(int(Febdata['status']))
        time.sleep(0.5)
    print('All HV on!')

def turn_off_HV_all(boards, exception=20):
    currentstate = []
    stateOFF = [1] * 19
    for FEB, i in zip(boards, range(1, 20)):
        if i != exception:
            try:
                FEB.openFEB(serial='/dev/ttyPS2', addr=i)
            except serial.SerialException:
                print('Seriale non trovata.')
                sys.exit()
            FEB.powerOff()
            print(f'HV {i} turned off')
        else:
            continue
        time.sleep(0.5)
    while currentstate != stateOFF:
        print('mPMT ramp-down')
        currentstate = []
        for FEB, i in zip(boards, range(1, 20)):
            if i != exception:
                try:
                    FEB.openFEB(serial='/dev/ttyPS2', addr=i)
                except serial.SerialException:
                    sys.exit(-1)
                Febdata = FEB.readMonRegisters()
                currentstate.append(int(Febdata['status']))
            else:
                currentstate.append(1)
        time.sleep(0.5)
    print('All HV off!')

def turn_on_HV_sc(FEB, address, Vset):
    stateON = 1
    currentstate = 0
    try:
        FEB.openFEB(serial='/dev/ttyPS2', addr=address)
    except serial.SerialException:
        print('Seriale non trovata.')
        sys.exit()
    FEB.setVoltageSet(int(Vset))
    FEB.powerOn()
    print(f'FEB {address} turned on')
    while currentstate != stateON:
        print('mPMT ramp-up')
        Febdata = FEB.readMonRegisters()
        currentstate = int(Febdata['status'])

def main():
    yn = ' '
    #
    #Parse script arguments
    #
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--numberFEB',  help='FEB addres that will perform the thresholdscan')
    parser.add_argument('-f', '--filename',  help='Output filename')
    parser.add_argument('-v', '--vset', help='Voltage for thresholdscan')
    parser.add_argument('-d', '--datanum', help='Number of data to take starting from 0')
    parser_args = parser.parse_args()   
    #
    #Open run control DMA
    #
    try:
        fid = open('/dev/uio0', 'r+b', 0)
    except:
        print('E: UIO device /dev/uio0 not found')
        sys.exit(-1)
    regs = mmap.mmap(fid.fileno(), 0x10000)
    #
    #Tun ON alla FEBs
    #
    allTurnON.turnmPMTon(regs)
    time.sleep(0.5)
    #
    #Crete with FEBs
    #
    FEB1 = HVModbus()
    FEB2 = HVModbus()
    FEB3 = HVModbus()
    FEB4 = HVModbus()
    FEB5 = HVModbus()
    FEB6 = HVModbus()
    FEB7 = HVModbus()
    FEB8 = HVModbus()
    FEB9 = HVModbus()
    FEB10 = HVModbus()
    FEB11 = HVModbus()
    FEB12 = HVModbus()
    FEB13 = HVModbus()
    FEB14 = HVModbus()
    FEB15 = HVModbus()
    FEB16 = HVModbus()
    FEB17 = HVModbus()
    FEB18 = HVModbus()
    FEB19 = HVModbus()
    boards = [FEB1, FEB2, FEB3, FEB4, FEB5, FEB6, FEB7, FEB8, FEB9, FEB10, FEB11, FEB12, FEB13, FEB14, FEB15, FEB16, FEB17, FEB18, FEB19]
    #
    #Ask if turn all PMTs on
    #
    while (yn != 'Y') | (yn  != 'N'):
        yn = input('Do you want to turn on ALL the PMTs (Y/N)?').capitalize()
        if yn == 'Y':
            turn_on_HV_all(boards, int(parser_args.vset))
            break
        elif yn == 'N':
            turn_off_HV_all(boards, exception=int(parser_args.numberFEB))
            turn_on_HV_sc(boards[int(parser_args.numberFEB) - 1], int(parser_args.numberFEB), int(parser_args.vset))
            break
    #
    #Start thresholdscan
    #
    do_threshold(int(parser_args.vset), parser_args.filename, boards[int(parser_args.numberFEB) - 1], regs, int(parser_args.numberFEB))
    #
    #Set CS off
    #
    allTurnON.do_write(0, 0, regs)
    #
    #Turn HV off
    #
    turn_off_HV_all(boards, except=20)

if __name__ == '__main__':
    main()

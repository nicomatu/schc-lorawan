### SCHC Packet transmission through LoRaWAN message                    BLOCK [3]/[7]

'''
##        Receives a SCHC Packet and sends it through a LoRaWAN uplink message
##
##        The SCHC Packets are passed to a LoRaWAN end-device through a serial interface to be
##        sent to the corresponding gateway via the LoRaWAN link. As a hardware requirement
##        (RN2903), the SCHC Packets are sent in hexadecimal format.
##
##        The command used for this purpose is 'mac tx <type> <portno> <data>', where:
##
##              -  <type>   refers to whether the message requires an ACK (confirmed) or not
##                          (unconfirmed). It must be one of these two strings: 'cnf' or 'uncnf'
##                          
##              - <portno>  is the device's port number used, a decimal number between 1 and 223
##                          
##              -  <data>   is the data to be sent in hexadecimal format.
##                          Here it carries the SCHC Packet.
##
##        LoRaWAN stands for Long-Range Wide Area Network, an LPWAN technology. The layer 2
##        protocol is LoRaWAN protocol. This design is compliant with the LoRa specification
##        version 1.0.2.
##
##        The maximum size for the packets is dependent on the LoRaWAN protocol's Data Rate,
##        which is variable. The maximum size will be explicitly established here.
##
##        SCHC is a compression and fragnentation mechanism for IPv6 packets [RFC 8200] over
##        Low Power Wide Area Network (LPWAN) [RFC 8376] technologies. It is currently under
##        development by the Internet Engineering Task Force (IETF).
##
##
##            -Code by Nicolás Maturana
##
##            -October 2018
##            -mail: nico.matu.a@gmail.com
#'''

## Import statements

import time
#import sys as system
import serial, time
import serial.tools
import serial.tools.list_ports

from bitstring import Bits as bits, BitArray as bar, BitStream as bst, ConstBitStream as conbst


comports = [comport.device for comport in serial.tools.list_ports.comports()]
print(comports)

complen = len(comports)


#############
'''
for x in comports:
    print(x)
    if 'ACM' in x:
        targetcomport = x
        print('if condition met')
        break
    else:
        print("Device not connected")
        raise SystemExit(0)
        print('Didn\'t exit')
        break
#'''
##############

targetcomport = comports[complen-1]

print("Target comport: " + targetcomport)


## Serial interface

ser = serial.Serial(
	port = targetcomport,
	baudrate = 57600,
	timeout = 3,
        write_timeout = 3
        )

## Correct hex format

pad = bits(len(schcP)%8)      # padding bits  -   lora need an integer number of bytes

loradata = ( schcP + pad ).hex

## Defaults

txtype = 'cnf '         # message requires an ACK from server
portno = '1 '          # device's port number, not to confuse with channel

## Join gateway

#cmd = 'mac join abp'

## Input command

cmd = 'mac tx ' + txtype + portno + loradata


#exit variables
exit = False

## Initalize datarate fix

dr = None

setdr = bytes(("mac set dr 3\r\n").encode('ascii'))     # set datarate to DR = 3 (command)
getdr = bytes(("mac get dr\r\n").encode('ascii'))       # get datarate (command)


## Start transmission

#'''
while not exit:
    try:
        #fix datarate
        ser.write(getdr)
        dr = ser.read(3).rstrip()
        print("dr = " + dr)
        #check datarate
        while dr not in {"3","4"}:
            #ser.flushInput()
            print(ser.read(20))
            ser.write(setdr)
            print(ser.read(20))
            ser.write(getdr)
            print("in bytes = " + str(ser.in_waiting))
            dr = ser.read(3).rstrip()
            print("dr = " + dr)
            time.sleep(1)
                
        outdataCRLF = bytes((cmd + '\r\n').encode('ascii'))

        out = outdataCRLF

        if ser.in_waiting > 0:
            print('in buffer bytes: ' + str(ser.in_waiting))
            indata = ser.read(100).rstrip()
            print(indata)
        if ser.out_waiting > 0:
            print('out buffer bytes: ' + str(ser.out_waiting))

        print('Sending command "' + str(cmd) + '"')

        ser.write(out)
        #print('out buffer bytes: ' + str(ser.out_waiting))
        
        time.sleep(0.5)     #wait first answer

        #print('out buffer bytes: ' + str(ser.out_waiting))
        wait = False
        printwait = True
        
        while ser.in_waiting > 0 or wait:
            while wait:
                if printwait:
                    print("Waiting for response...")
                    printwait = False
                try:
                    if ser.in_waiting > 0:
                        printwait = True
                        break
                except KeyboardInterrupt:
                    break
            time.sleep(0.1)
            print('in buffer bytes: ' + str(ser.in_waiting))
            indata = ser.read(100).rstrip()
            print(indata)
            wait = False
            #time.sleep(3)

            if ("busy" in indata) or (indata == "ok"):
                wait = True
            
            #print('out buffer bytes: ' + str(ser.out_waiting))

##        indata = ser.read(100).rstrip()
##        print(indata)



    except KeyboardInterrupt:
        loop = False
        exit = True
        print("\nLoop stopped\n")

#'''
print("Ending Program")
'''
#'''


















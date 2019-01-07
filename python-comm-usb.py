### Interactive message interface for LoRaWAN end-device (Microchip RN2903)

#basic serial write-read routine

print("Empezando")

import time
import sys as system
import serial, time
import serial.tools
import serial.tools.list_ports
#from cominit import cominit

comports = [comport.device for comport in serial.tools.list_ports.comports()]
print(comports)

complen = len(comports)
#return

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

'''
#'''
targetcomport = comports[complen-1]

print("Target comport: " + targetcomport)

ser = serial.Serial(
	port = targetcomport,
	baudrate = 57600,
	timeout = 3,
        write_timeout = 3
        )

##  Command list -initialization

try:
    if init not in {0, 1, True, False}:
        raise NameError
    else:
        print("init = " + str(type(init)) + "  " + str(init))
except NameError:
    while True:
            try:
                init=input("Inicializar? 1=sí / 0=no\n")
                if init not in {0, 1, True, False}:
                    print("init debe pertenecer a {0, 1, True, False}")
                    continue
                else:
                    break
            except NameError:
                print("init debe pertenecer a {0, 1, True, False}")
                continue

if init in {0, 1, True, False}:
    if init in {1, True}:
        #try:
        print("init= " + str(init) + "\nInicializando...")
        execfile("cominit.py")
        #except NameError:
    else:
        print("init= " + str(init) + "\nContinuando sin inicializar.")
else:
    print("Algo extraño ocurrió")


#cmd = 'sys get hweui'

'''
## For Python 3


outdata = bytes(command,'ascii')
outdataCRLF = bytes(command + '<CR><LF>','ascii')

outdataCR = bytes(command + '<CR>','ascii')
outdataLF = bytes(command + '<LF>','ascii')
'''

incomplete = False
loop = False
exit = False

response2group = ("mac tx", "mac join")

## Comenzar rutina de comandos

while not exit:
    # chequear último comando
    while not loop:
        try:
            if incomplete:
                print("Command was incomplete, some parameters missing. Try again.")
        except NameError:
            incomplete = False
        try:
            cmd
            #print("cmd = " + str(cmd))
        except NameError:
            cmd = None
        try:
            print("\nLast Command was \'" + str(cmd) \
                + "\'.\nInput new cmd or double-enter to execute same")
            aux = system.stdin.readlines(1)[0]    #stdin is list type
            aux = aux.rstrip()
            if aux == 'None':
                print("cmd is empty")
                continue
            elif aux == 'loop':
                loop = True
                break
            elif aux == 'print':
                var = raw_input("Input variable to print\n")
                if var == '':
                    continue
                print(var + " = "); print(eval(var))
                continue
            elif aux == 'exec':
                var = raw_input("Input expression to execute\n")
                if var == '':
                    continue
                exec(var)
                continue
            elif aux == 'exit':
                raise #system.exit(0)
            elif aux == '' :
                if str(cmd) == 'None' or str(cmd) == '':
                    continue
                elif cmd == 'print':
                    var = raw_input("Input variable to print\n")
                    if var == '':
                        continue
                    print(var + " = "); print(eval(var))
                    continue
                elif cmd == 'exec':
                    var = raw_input("Input expression to execute\n")
                    if var == '':
                        continue
                    exec(var)
                    continue
                else:
                    break
            
            #print("type aux =" + str(type(aux)))
            cmd = eval(aux)                  #str(input("input new cmd\n"))
            if type(cmd) == bool:
                raise SyntaxError
            #print("type cmd= " + str(type(cmd)))       #debug
            print("new cmd= " + str(cmd))
            break
        except NameError:
            print("Command not recognized")
            continue
        except SyntaxError:
            try:
                cmd = aux
                print("new cmd= " + str(cmd))
                break
            except:
                print("cmd=aux failed. Something happened.")
        except KeyboardInterrupt:
            print("Program terminated by user.")
            exit=True
            break
                #raise StopIteration

##        except: BLOQUEA interrupción de la shell con ctrl+c
##            print("Something else happened.")

    #'''
    if exit:
        break

    if loop:
        time.sleep(1)
    else:
        pass

    try:
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
        
        time.sleep(0.8)     #wait first answer

        #print('out buffer bytes: ' + str(ser.out_waiting))
        wait = False
        printwait = True
        incomplete = True
        while ser.in_waiting > 0 or wait:
            incomplete = False
            tries = 0
            while wait:
                try:
                    if printwait:
                        print("Waiting for response...")
                        printwait = False
                    if ser.in_waiting > 0:
                        break
                    time.sleep(1)
                    tries += 1
                    if tries >= 20:
                        print("Timeout: No response")
                        break
                except KeyboardInterrupt:
                    break
            time.sleep(0.1)
            print('in buffer bytes: ' + str(ser.in_waiting))
            indata = ser.read(ser.in_waiting).rstrip()
            print(indata)
            wait = False
            printwait = True

            response = any( cmd.startswith(z) for z in response2group )
            if ("busy" in indata) or (indata == "ok" and response):
                wait = True
            
            #print('out buffer bytes: ' + str(ser.out_waiting))

##        indata = ser.read(100).rstrip()
##        print(indata)



    except KeyboardInterrupt:
        loop = False
        print("\nLoop stopped\n")

print("Ending Program")
'''
#'''










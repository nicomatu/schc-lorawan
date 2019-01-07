### COMANDOS NODO LORAWAN MICROCHIP

#def cominit(init=1):

#print("init_cominit= " + str(init))
'''
if not(init):
    
    print("init=0, retornando sin inicializar defaults")

    return
'''

print("Ejecutando cominit.py")

#defaults

defkey = '0000'
#global mode, txtype, portno, sendmsg, deva
mode ='lora'
txtype = 'uncnf'
portno = '1'
sendmsg = 'no message'
freq = '915000000'

#cmd keywords

lora = 'lora'
cnf='cnf'
uncnf='uncnf'
tx = 'tx'
rx = 'rx'
save = 'save'


#cmd blocks
sys = 'sys '
mac = 'mac '
rad = 'radio '

g = 'get '
s = 'set '

sg = sys + g
ss = sys + s

mg = mac + g
ms = mac + s

rg = rad + g
rs = rad + s

#keys keywords
deva = 'devaddr '       # ABP
deve = 'deveui '        # OTAA
ape = 'appeui '         # OTAA
nsk = 'nwkskey '        # ABP
ask = 'appskey '        # ABP
apk = 'appkey '         # OTAA

#keys
keys = {
    'devaddr': defkey,
#deveui = defkey
#appeui = defkey
#nwkskey = defkey
#appskey = defkey
    'appkey' : defkey
        }


#sys get
sgver = sg + 'ver'
sgvdd = sg + 'vdd'
sghw = sg + 'hweui'

'''
#mac set
try
    msdeva = ms + deva + devaddr
    except 
msdeve = ms + deve + deveui
msape = ms + ape + appeui
msnsk = ms + nsk + nwkskey
msask = ms + ask + appskey
msapk = ms + apk + appkey
'''
    
#mac get
mgdeva = (mg + deva).rstrip()
mgdeve = (mg + deve).rstrip()
mgape = (mg + ape).rstrip()

mgstat = mg + 'status'

#mac
mres = mac + 'reset'
mtx = mac + 'tx ' + txtype + ' ' + portno + ' ' + sendmsg
mja = mac + 'join abp'
mjo = mac + 'join otaa'
msave = mac + 'save'
mp = mac + 'pause'

#radio
#rws = rad + 'rx' + rxwinsize
#rtx = rad + 'tx' + data
rcw = rad + 'cw'

#radio set
rsmod = rs + 'mod ' + mode
rsfreq = rs + 'freq ' + str(freq)

#radio get
rgmod = rg + 'mod'
rgfreq = rg + 'freq'


#Seleccionar comando

try:
    print("Comando cmd= " + str(cmd))
except NameError:
    while True:
        try:
            print("default command?\n")
            aux = system.stdin.readlines(1)[0]    #stdin is list type
            aux = aux.rstrip()
            cmd = eval(aux)
            print("Comando cmd= " + str(cmd))
            break
        except NameError:
            print("Comando no reconocido")
            continue
        except SyntaxError:
            try:
                cmd = aux
                print("new cmd= " + str(cmd))
                break
            except:
                print("cmd=aux failed. Something happened.")
init = False

print("Fin cominit.py")



########################## FIN #######################



### SCHC Decompression for received SCHC Packets                        BLOCK [6]/[7]

'''             ######## EDIT INTRO ##############################
##        Receives IPv6 standard-header + dummy payload packets and applies SCHC Compression
##
##        The SCHC Packets (compressed IPv6 packets) are sent through a LoRaWAN link. In this
##        case it is an uplink: from end-device to gateway. As a hardware requirement (RN2903),
##        the SCHC Packets are sent in hexadecimal format.
##
##        SCHC is a compression and fragnentation mechanism for IPv6 packets [RFC 8200] over
##        Low Power Wide Area Network (LPWAN) [RFC 8376] technologies. It is currently under
##        development by the Internet Engineering Task Force (IETF).
##
##        This implementation considers IPv6 packets with only the standard 40-byte header plus
##        a payload. No support for extension headers is given.
##
##        The system is intended for IPv6 packet transmission within a Long-Range Wide Area
##        Network (LoRaWAN). The layer 2 protocol is LoRaWAN protocol. This design is compliant
##        with the LoRa specification version 1.0.2.
##
##        The maximum size for the packets is dependent on the LoRaWAN protocol's Data Rate,
##        which is variable. The maximum size will be explicitly established here.
##
##        This SCHC implementation only considers compression/decompression. Fragmentation will
##        not be supported, therefore the maximum packet size limitation.
##
##
##            -Code by Nicolás Maturana
##
##            -October 2018
##            -mail: nico.matu.a@gmail.com
#'''            '''######## EDIT INTRO ##############################'''

# Packet structure

#               | IPv6 Packet  | = | Fixed Header [40 bytes] |   Payload   |
#
# Bit position                     0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 |
#                                  |       |               |                                       |    
#  Field size   |  [40 bytes]  |   |  [4]  |      [8]      |                 [20]                  |
#   [# bits]    | Fixed Header | = |Version| Traffic Class |              Flow Label               |
#                                  |-------+---------------+-------+---------------+---------------|
#                                  |             [16]              |      [8]      |      [8]      | 
#                                  |         Payload Length        |  Next Header  |   Hop Limit   |
#                                  |-------------------------------+---------------+---------------| 
#                                  |                                                               |  
#                                  |                             [128]                             |
#                                  |                        Source Address                         |
#                                  |                                                               |
#                                  |---------------------------------------------------------------| 
#                                  |                                                               |
#                                  |                             [128]                             |
#                                  |                      Destination Address                      |
#                                  |                                                               |
#                                  +---------------------------------------------------------------+

## Resulting SCHC Packet structure
##
##    +--- ... --+------- ... -------+------------------+
##    |  Rule ID |Compression Residue|  packet payload  |
##    +--- ... --+------- ... -------+------------------+
##    |                              |
##    |--------Compressed Header-----|
##

## Rules concept    -   (a Rule is a list of Field Descriptions)                                                           
##
##      Acronyms:                 /----------------------------\
##                                |           Rule N           |
##      FID: Field ID            /----------------------------\|
##      FL:  Field Length        |           Rule i           ||    Field Descriptions (FD)
##      FP:  Field Position     /----------------------------\||              |
##            (occurence)       |  (FID)    Rule 1           |||              |
##      TV:  Target Value       |+-------+--+--+--+--+--+---+|||              |    *they refer to
##      MO:  Matching Operator  ||Field 1|FL|FP|DI|TV|MO|CDA||||<-------------+     the fields of 
##      CDA: Compression/       |+-------+--+--+--+--+--+---+|||              |     the header(s)
##           Decompression      ||Field 2|FL|FP|DI|TV|MO|CDA||||<-------------+
##           Action             |+-------+--+--+--+--+--+---+|||              |
##                              ||...    |..|..|..|..|..|...||||              |
##                              |+-------+--+--+--+--+--+---+||/              |
##      *FV: Field Value        ||Field N|FL|FP|DI|TV|MO|CDA|||<--------------+
##                              |+-------+--+--+--+--+--+---+|/
##                              |                            |
##                              \----------------------------/
##

## Matching Operator (MO)
##
##   /--------------------+----------------------------------------------\  +--not-sent (expected TV)
##   |  Name              | Meaning                                      |  |
##   |                    |                                              |  | +--not-sent (fixed-known)
##   +--------------------+----------------------------------------------+  | |
##   |equal               |True if FV = TV                               |>-+ +--value-sent
##   |                    |                                              |    |       (impredictable)
##   |ignore              |Result is always True.                        |>---+
##   |                    |                                              |    +--send LSB ( first part      
##   |MSB(x)              |True if the x MSBs of FV = TV in the Rule.    |       is constant, second 
##   |                    |The x is the number of bits compared.         |      part is impredictable )
##   |                    |                                              |      
##   |                    | *If the FL is described as variable, the     |>-+--send LSB ( known set of
##   |                    | length must be a multiple of its unit.       |  |     values, common start )
##   |                    | For example, if the unit of the variable     |  |
##   |                    | length is in bytes, x must be multiple of 8. |  +--not-sent ( known value,
##   |                    |                                              |                unique start )
##   |match-mapping       |True if FV = TV[i] for some index i.          |
##   |                    |                                              |>--send index ( always a 
##   |                    | *TV is an indexed list of values.            |         member of known set )
##   |                    | The index is sent instead of the FV.         |
##   \--------------------+----------------------------------------------/
##

## Compression-Decompression Actions (CDA)
##
##   /--------------------+-------------+----------------------------\
##   |  Action     (!)    | Compression | Decompression              |
##   |                    |             |                            |
##   +--------------------+-------------+----------------------------+
##   |not-sent            |elided       |use value stored in context |  equal / ignore / MSB(x) 
##   |value-sent          |send         |build from received value   |  ignore / equal?
##   |mapping-sent        |send index   |value from index on a table |  match-mapping
##   |LSB                 |send LSB     |TV, received value          |  ignore / MSB(x)
##   |compute-length      |elided       |compute length              |  ignore
##   |compute-checksum    |elided       |compute UDP checksum        |  ignore
##   |DevIID              |elided       |build IID from L2 Dev addr  |  ignore
##   |AppIID              |elided       |build IID from L2 App addr  |  ignore
##   \--------------------+-------------+----------------------------/
##

## Course of events:
##      
##    1. Communication side is identified
##    2. Rules are initialized
##    3. A SCHC Packet is received (from payload retriever)
##    4. Rule IDs are read and applicable Rules are identified
##    5. Applicable Rules are scanned for:
##            -Direction (DI)
##            -Field Position (FP)
##            -Compression/Decompression Action (CDA)
##
##    6. Fields are reconstructed using Target Value (TV) and Compression Residue
##    7. At all times Rule order is followed, and also FD order inside each Rule
##    8. Any computations are left to be done after reconstruction
##    9. If the special no-compression Rule is found, the leading Rule ID is removed
##       and the remaining data corresponds to the original IPv6 packet (plus padding)
##   10. Any padding bits that may be present are removed using the PL information
##
##    *NOTE:
##
##    As this implementation does not include Fragmentation, no Reassembly is performed
##    prior to Decompression. A complete SCHC Packet is always assumed.
##
##

## Import statements

from math import log, ceil
from bitarray import bitarray as ba
from bitstring import Bits as bits, BitArray as bar, BitStream as bst, ConstBitStream as conbst
from collections import OrderedDict as ordic

#from copy import deepcopy as dcopy     #if dict.copy() causes multi-reference

## Communication context

side = 'gateway'     # default for this implementation. Other option is 'end-device'.
#did = DevIID           # device identifier, used for downlink compression

if side == 'gateway':
    di = 'up'
else:
    di = 'dw'
        

## Defaults

dpl = 40
dsa = bits('0b01')
dsa = dsa*64
dda = bits('0b10')*64

udp = 17
nonh = 59
tcp = 6

## Initialize rules

rn = rulesNumber  = 4 
fn = fieldsNumber = 8   # lines per Rule, 8 fields in IPv6 header

rb = ruleBits = int(ceil(log(rn,2)))     # bits needed to represent Rule IDs

rules = []              # empty list + .append method to avoid multi-reference
                        # we want a list of rn=(4) lists of fn=(8) elements

## Common case

hfid = headerFID = ["v","tc","fl","pl","nh","hl","sa","da"]
hfl = headerFieldLength = [4, 8, 20, 16, 8, 8, 128, 128]        # all lengths are known
#hfp = headerFieldPosition = [1]*7                              # one occurence per field
#hdi = headerDirection = "up"                                   # only uplink
htv = headerTargetValue = [6, 0, 0, dpl, udp, 200, [dsa[0:16].uint], [dda[0:16].uint]]
hmo = headerMatchingOperator = ["equal"]*3 + ["ignore"] + ["equal"]*2 + ["mmap"]*2 
hcda = headerCompDecompAct = ["not-s"]*3 + ["val-s"] + ["not-s"]*2 + ["index"]*2

#*NOTE: TVs CAN NOT be based on ANY packet-to-send field, they are fixed and must be known
# (included in a static shared Rule) by both ends beforehand

field_items = iter([

        ("FID", "v"),       # identifies header field 
        ("FL" ,  4),        # length of the field
        ("FP" ,  1),        # position of the field occurence within the header
        ("DI" , "up"),      # direction of communication  up/dw/bi
        ("TV" ,  6),        # value used for comparison with FV
        ("MO" , "ignore"),  # method of comparison
        ("CDA", "not-s"),   # action taken if Rule is selected

    ])

fields = ordic(field_items)

for i in range(rn):
    rules.append([])            # add rules as (independent) lists
    for h in range(fn):
        rules[i].append(fields.copy())
pass
#print(rules)


## Define rules

#apply common case      -DI/FP are NOT modified; 

count = 0        
for x in rules:
    print(count)
    count +=1
    for i in range(fn):
        x[i]["FID"] = hfid[i]
        x[i]["FL"] = hfl[i]
        x[i]["TV"] = htv[i]
        if x is rules[0]:       # rule 0 assumes fully-known context
            print(x[i])
            continue
        else:
            x[i]["MO"] = hmo[i]
            x[i]["CDA"] = hcda[i]
        print(x[i])
pass
print "\n"

#easy header field indexes

V  = 0
TC = 1          
FL = 2
PL = 3
NH = 4
HL = 5
SA = 6
DA = 7

#rule 0     *ideal* = all context is fully known

#known:     v - tc - fl - pl - nh - hl - sa - da
#fromset:
#unknown:   

rules[0][PL].update(TV= dpl , MO='equal', CDA='not-s')      # default payload size
rules[0][NH].update(TV= nonh, MO='equal', CDA='not-s')      # not UDP
rules[0][HL].update(TV= 200 , MO='equal', CDA='not-s')
rules[0][SA].update(TV= dsa[0:16].uint , MO='equal', CDA='not-s')      # default source address
rules[0][DA].update(TV= dda[0:16].uint , MO='equal', CDA='not-s')      # default destin address

#rule 1     -ready == common case

#known:     v - tc - fl - nh - hl 
#fromset:   sa - da
#unknown:   pl 

#rule 2     -allow unknown addresses + unknown hop limits + known set of next headers

#known:     v - tc - fl
#fromset:   nh
#unknown:   pl - hl - sa - da

rules[2][NH].update(TV= [udp,nonh,tcp], MO='mmap',   CDA='index')
rules[2][HL].update(TV= 200           , MO='ignore', CDA='val-s')
rules[2][SA].update(TV= dsa[0:16].uint, MO='ignore', CDA='val-s')
rules[2][DA].update(TV= dda[0:16].uint, MO='ignore', CDA='val-s')

#rule 3     -no compression possible

for x in rules[3]:
    x["DI"] = 'dw'        # force failure


####
countt = 0        
for x in rules:
    print(countt)
    countt +=1
    for i in range(fn):
        print x[i]
print "\n"

###############################

###<RECEIVE SCHC PACKET schcP>

schcrx = bits('0x' + loradata)

## Initialize packet reader

pr = 0          # allowed values: [rid offset]  +  4-12-32-48-56-64-192-320
#               #   --->  6-14-34-50-58-66-194-322 

## Identify decompression Rule

decrid = schcrx[0:rb]        #read the first 'rb' bits from SCHC Packet
pr += rb                    #update reader
decrule = decrid.uint       # rule number, valid since rule 0 exists

#print(decrid == rid)        # check if identified rule matches rule selected in compression

dechdr = bits()                 # prepare decompressed header - an empty list
decfds = [None]*8            # separate decompressed header fields - a list with 8 values (8 fields)

start= 0


## Apply Rule

for fd in rules[decrule]:
    #check direction
    if fd["DI"]!="bi" and fd["DI"]!=di:            
        continue                            # if DI not in message direction, skip FD
    elif fd["FP"]!=dfp:                     # else check FP
        continue                            # if rule's FP doesn't match the field's, skip FD
    else:                                   # else apply CDA
        #
        fid = fd["FID"]             # one of        ["v","tc","fl","pl","nh","hl","sa","da"]
        print(fid)
        hf = eval(fid.upper())      # turns into    ["V","TC","FL","PL","NH","HL","SA","DA"] -> indexes
        decflen = fd["FL"]          # obtain field length
        print("FL = " + str(decflen))
        #
        #check CDA
        if fd["CDA"]=='not-s':
            #not-sent, build from TV   *fixed-known
            decfds[hf] = bits(uint=fd["TV"], length = decflen)#bin(fd["TV"]))        # convert TV to bits, interpreted as uint
            continue                                # field ready, go to next FD
        elif fd["CDA"]=='val-s':
            #value-sent, build from received SCHC Packet --> need to know the length = FL
            #      ##if not int (variable length feld) --> check sent length    
            #decflen = fd["FL"]
            decfds[hf] = schcrx[pr:pr+decflen]    # read FL number of bits, start from curr pos
            pr += decflen                         #update reader
            print(str(decflen) + " bits read\n pr is now = " + str(pr))
            #compresvals.append(fv.uint)
            #compres+=fv                 # add FV to comp-residue    *impredictable
            continue                    # field ready, go to next FD
        elif fd["CDA"]=='index':
            indlen = len(fd["TV"]).bit_length()      # bits used to encode index
            decindex = schcrx[pr:pr+indlen].uint     # read index bits, interpret as uint
            pr += indlen                             #update reader
            print(str(indlen) + " bits read\n pr is now = " + str(pr))
            decfds[hf] = bits(uint=fd["TV"][decindex], length = decflen)         # add TV[index] as bits to dec fields
            continue                            # field ready, go to next FD
        elif fd["CDA"]=='LSB':
            decflen = fd["FL"] - len(fd["TV"])    # LSBs = FL - MSBs omitted (TV length), 
            #                                       # TV must be a bitstring
            decfds[hf] = schcrx[pr:pr+decflen]    # read LSBs number of bits, start from curr pos
            pr += decflen                         #update reader
            print(str(decflen) + " bits read\n pr is now = " + str(pr))
            continue                # field ready, go to next FD

        #elif DevIID,AppIID

        #elif compute

        else:
            print("Something failed")
            break
    print(decfds[hf] == packet[start:decflen])
    start += decflen
    
#end for

for z in decfds:
    dechdr += z      #build complete header


## Add payload - drop padding bits

pdbits = decfds[PL].uint*8
readpd = schcrx[pr:pr+pdbits]

pr += pdbits                         #update reader

## Build full decompressed packet

decpacket = dechdr + readpd


#debug 

P = packet = ip6



## Verify

print("Decompressed packet = original packet???")

result = decpacket == packet

print(result)
















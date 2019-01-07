### Static Context Header Compression (SCHC) for IPv6 packets           BLOCK [2]/[7]

'''
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
#'''

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
##    3. An IPv6 packet is received (from generator)
##    4. Rules are scanned according to:
##            -Direction (DI)
##            -Field Position (FP)
##            -Target Value (TV), through Matching Operator (MO)
##            -If all MO results are valid (True), Rule is selected
##            -Otherwise, the next Rule is scanned
##            
##    5. If no elligible Rule is found, packet MUST be sent without compression
##    6. If the LPWAN technology Word is greater than a bit, apply Padding as needed
##       Padding bits are added at the end of the payload (done in sender script)
##
##    *NOTE:
##
##    When no applicable Rule is found, SCHC SHOULD apply the Fragmentation scheme.
##    As this implementation does not include Fragmentation, maximum packet size is
##    checked for in the generator block, so that no uncompressed packet will exceed
##    the link's maximum message size.
##
##

## Import statements

from math import log, ceil
from bitarray import bitarray as ba
from bitstring import Bits as bits, BitArray as bar, BitStream as bst, ConstBitStream as conbst
from collections import OrderedDict as ordic

#from copy import deepcopy as dcopy     #if dict.copy() causes multi-reference

## Communication context

side = 'end-device'     # default for this implementation. Other option is 'gateway'.
#did = DevIID           # device identifier, used for downlink compression

if side == 'end-device':
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
htv = headerTargetValue = [6, 0, 0, dpl, udp, 200, [dsa.uint], [dda.uint]]
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

    #APPLY FRAGMENTATION

####
countt = 0        
for x in rules:
    print(countt)
    countt +=1
    for i in range(fn):
        print x[i]
print "\n"

## Select SCHC Rule

rid = ruleID    = bits()         #empty, no rule selected yet

###<RECEIVE PACKET P>

P = packet = ip6

## SCHC algorithm

# Parse packet



# Run through rules

currule = 0
compresvals = []        # compression residue values
compres = bits()        # compression residue as a bit chain
compresfds = []
include = False
dfp = 1
#fpset = set()
selrules = []           # selected rules list
print("debugging")

print "breakpoint"

for x in rules:
    for fd in x:
        #check direction
        if fd["DI"]!="bi" and fd["DI"]!=di:            
            continue                            # if DI not in message direction, skip FD
        elif fd["FP"]!=dfp:                     # else check FP
            continue                            # if rule's FP doesn't match the field's, skip FD
        else:                                   # else check MO
            include = True
            fid = fd["FID"]
            fv = eval(fid)#[0:16]
            if fd["MO"]=='ignore':
                #check CDA
                if fd["CDA"]=='not-s':
                    #not-sent, no compression residue   *fixed-known
                    continue
                elif fd["CDA"]=='val-s':
                    compresvals.append(fv.uint)
                    compres+=fv                 # add FV to comp-residue    *impredictable
                    compresfds.append(fid)
                    continue                    # rule applies to FD, check next
                else:  # fd["CDA"]=='LSB'
                    compresvals.append(lsb(x, fv.uint))     # ( bits and int as arguments, careful )
                    compres += fv           # add x LSBs from fv to comp-residue    *const-impr
                    compresfds.append(fid)
                    continue                # rule applies to FD, check next
            elif fd["MO"]=='equal':
                if fd["TV"]==fv.uint:
                    #not-sent, no comp-residue      *expected
                    continue                        # rule applies to FD, check next
                else:
                    compresvals = []            # rule failed, clean comp-residue
                    compres = bits()
                    compresfds = []
                    include = False
                    break                       # rule does not apply, go to next rule
            elif fd["MO"]=='MSB(x)':
                if msb(x, fv, fd["TV"]):                # bits and int as arguments, careful
                    #check CDA
                    if fd["CDA"]=='not-s':
                        #not-sent, no comp-residue       *known, unique start
                        continue                        # rule applies to FD, check next
                    else:  # fd["CDA"]=='LSB'
                        compresvals.append(lsb(x, fv.uint))  # ( bits and int as arguments, careful )
                        compres += fv       # add x LSBs from fv to comp-residue    *com-start
                        compresfds.append(fid)
                        continue            # rule applies to FD, check next
                else:
                    compresvals = []            # rule failed, clean comp-residue
                    compres = bits()
                    compresfds = []
                    include = False
                    break                       # rule does not apply, go to next rule
            elif fd["MO"]=='mmap':
                if fv.uint in fd["TV"]:
                    index = fd["TV"].index(fv.uint)
                    compresvals.append(index)       # add index of TV[i] = FV to comp-residue
                    compres += bits(uint=index, length=len(fd["TV"]).bit_length())#compres += bits(bin(index))
                    compresfds.append(fid + " as index = " + str(index))
                    continue                        # rule applies to FD, check next
                else:
                    compresvals = []            # rule failed, clean comp-residue
                    compres = bits()
                    compresfds = []
                    include = False
                    break                       # rule does not apply, go to next rule
            else:
                print("Something unexpected happened")
                break
    if include:
        selrules.append(currule)                # add Rule ID to selected rules
        rid += bits(uint=currule, length=rb)    # add rule to Rule ID bit chain
        include = False
    else:
        include = True
    currule +=1                         # prepare next rule

print selrules, rid
print compresvals, compres, compresfds


comphdr = compheader = rid + compres
schcP = SCHCPacket = rid + compres + pd





















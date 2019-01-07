### IPv6 dummy packet Generator                                         BLOCK [1]/[7]

'''
##        Generates IPv6 standard-header + dummy payload packets
##       
##        The packets will be passed to a Static Context Header Compression (SCHC) Compressor
##        block (sender side).
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

## Import statements

from random import choice, randrange

import bitarray 
#from bitarray import *
from bitarray import bitarray as ba

import bitstring
from bitstring import Bits as bits, BitArray as bar, BitStream as bst, ConstBitStream as conbst

   
# Parameters

mps = maxPacketSize = 100       # bytes
hs  = headerSize    = 40        # bytes
pds = payloadSize   = mps - hs  # bytes

##dataRateMode = 0        # for payload size dependency

# Constants and fixed values

#known:     v - tc - fl
#fromset:   nh
#unknown:   pl - hl - sa - da

###<SHOULD CHOOSE RULE 2>

v   = version       = bits(ba('0110'))          # 4   bits, value = 6
tc  = trafficClass  = bits(uint=0, length=8)    # 8   bits, value = 0
fl  = flowLabel     = bits(uint=0, length=20)   # 20  bits, value = 0
pl  = payloadLength = bits(uint=pds, length=16) # 16  bits, value = payload size in bytes
nh  = nextHeader    = bits(uint=17, length=8)   # 8   bits, value = 17 = udp
hl  = hopLimit      = bits(uint=randrange(20,255), length=8)    # 8   bits, value = random
sa  = sourceAddress = bits(ba(128))             # 128 bits, value = random
da  = destinationAddress = bits(ba(128))        # 128 bits, value = random
pd  = payload       = bits(ba(pds * 8))         # bits, value = random

print "v: ",v, v.length
print "tc: ",tc, tc.length
print "fl: ",fl, fl.length
print "pl: ",pl, pl.int, pl.length
print "sa: ",sa, sa.length
print "da: ",da, da.length


#######

##<MODIFY TO CHOOSE OTHER RULES>

# Constants and fixed values

#known:     v - tc - fl
#fromset:   nh
#unknown:   pl - hl - sa - da

#######



hfds = headerFields = [v, tc, fl, pl, nh, hl, sa, da,]
hdr = header    = v + tc + fl + pl + nh + hl + sa + da
pfds = packetFields = [v, tc, fl, pl, nh, hl, sa, da, pd]
ip6 = ipv6Packet    = bits(v + tc + fl + pl + nh + hl + sa + da + pd)
bs  = bitSize       = ip6.length
print ip6;''' print ip6.bin; '''
print bs, bs/8

# Visual format

k = 32
lines = [None]*bs
print "bs = ",bs
print len(lines)
print "\n"

hexlines = [None]*10
binlines = [None]*10
for i in range (0, 10):
    hexlines[i] = ip6[(i)*k:(i+1)*k].hex
    binlines[i] = ip6[(i)*k:(i+1)*k].bin

for i in range (0, 10):
    print hexlines[i]
    
print "\n"

for i in range (0, 10):
    print binlines[i]



























### SCHC over LoRaWAN runstack


## Run IPv6 packet generator

execfile("packet-gen.py")

print("IPv6 packet successfully created")

## Run SCHC compressor

execfile("schc_comp.py")

print("SCHC compression successfully completed. SCHC Packet created.")

## Run device sender script

execfile("lorawan-message-up.py")



print("Runstack script finished")

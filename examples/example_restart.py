import BloonsAI
import struct

addr_dict = BloonsAI.initialize_restart()

for key, value in addr_dict.items():
    print(key, ": ", value)

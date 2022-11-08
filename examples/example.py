import BloonsAI
import struct

mydict = BloonsAI.initialize()
for key in mydict:
    print(key, ": ", mydict[key])

money = BloonsAI.get_value_double(mydict["cash"], 8)
print("Retrieved Money: ", money)
print("Retrieved Health: ", BloonsAI.get_value_double(mydict["health"], 8))
print("Retrieved Towers: ", BloonsAI.get_value_double(mydict["tower_count"], 4))
print("Retrieved Round: ", BloonsAI.get_value_double(mydict["round"], 4))
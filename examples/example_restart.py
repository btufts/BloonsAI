import BloonsAI

mydict = BloonsAI.initialize_restart(100.0, 2.0)

for key, value in mydict.items():
    print(key, ": ", value)

# print("Retrieved Money: ", BloonsAI.get_value(mydict["cash"], 8))
# print("Retrieved Health: ", BloonsAI.get_value(mydict["health"], 8))
# print("Retrieved Towers: ", BloonsAI.get_value(mydict["tower_count"], 4))
# print("Retrieved Round: ", BloonsAI.get_value(mydict["round"], 8))

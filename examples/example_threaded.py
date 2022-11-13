import BloonsAI

# 3 parameter is verbosity, it affects how many print statments there are in the function
# Will likely make this value 0 during actual training or testing AI
mydict = BloonsAI.initialize_threaded(100.0, 2.0, 5)

for key, value in mydict.items():
    print(key, ": ", value)

print("Retrieved Money: ", BloonsAI.get_value(mydict["cash"], 8))
print("Retrieved Health: ", BloonsAI.get_value(mydict["health"], 8))
print("Retrieved Towers: ", BloonsAI.get_value(mydict["tower_count"], 4))
print("Retrieved Round: ", BloonsAI.get_value(mydict["round"], 8))

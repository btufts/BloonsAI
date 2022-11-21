import json
import csv
import os
import sys

genetics_file = os.path.join(sys.path[0], "src", "AI", "utils", "genetics.json")
generation_info_file = os.path.join(sys.path[0], "src", "AI", "utils", "generation_info.csv")


# read_genetics and save_genetics:
# https://www.geeksforgeeks.org/reading-and-writing-json-to-a-file-in-python/
# csv:
# https://stackoverflow.com/questions/3348460/csv-file-written-with-python-has-blank-lines-between-each-row


def read_genetics():
    with open(genetics_file, 'r') as openfile:
        json_object = json.load(openfile)
    for gene in json_object:
        for action in gene:
            action[2] = (action[2][0], action[2][1])
    #print(json_object)
    return json_object


def save_genetics(genetics1, genetics2):
    genetics = [genetics1, genetics2]
    json_object = json.dumps(genetics, indent=4)
    with open(genetics_file, "w") as outfile:
        outfile.write(json_object)


def create_gen_info_file():
    # Overwrites file with header
    save_gen_info("generation_num", "game_round", "game_time", "game_round2", "game_time2", flag='w')


def save_gen_info(generation_num, game_round, game_time, game_round2, game_time2, avg_round, avg_towers, avg_upgrades, highest, lowest, flag='a'):
    with open(generation_info_file, flag, newline='') as file:
        writer = csv.writer(file)
        writer.writerow([generation_num, game_round, game_time, game_round2, game_time2, avg_round, avg_towers, avg_upgrades, highest, lowest])


def get_generation_num():
    with open(generation_info_file, 'r', newline='') as file:
        last_gen_num = int(file.readlines()[-1].split(',')[0])
    return last_gen_num

def get_best_scores():
    with open(generation_info_file, 'r', newline='') as file:
        last_line = file.readlines()[-1].split(',')
    return float(last_line[1]), float(last_line[2]), float(last_line[3]), float(last_line[4])


# create_gen_info_file()

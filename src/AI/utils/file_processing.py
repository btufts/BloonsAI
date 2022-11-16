import json
import csv

genetics_file = "genetics.json"
generation_info_file = "generation_info.csv"

# read_genetics and save_genetics:
# https://www.geeksforgeeks.org/reading-and-writing-json-to-a-file-in-python/
# csv:
# https://stackoverflow.com/questions/3348460/csv-file-written-with-python-has-blank-lines-between-each-row


def read_genetics():
    with open(genetics_file, 'r') as openfile:
        json_object = json.load(openfile)
    return json_object


def save_genetics(genetics1, genetics2):
    genetics = [genetics1, genetics2]
    json_object = json.dumps(genetics, indent=4)
    with open(genetics_file, "w") as outfile:
        outfile.write(json_object)


def create_gen_info_file():
    # Overwrites file with header
    save_gen_info("generation_num", "game_round", "game_time", flag='w')


def save_gen_info(generation_num, game_round, game_time, flag='a'):
    with open(generation_info_file, flag, newline='') as file:
        writer = csv.writer(file)
        writer.writerow([generation_num, game_round, game_time])


def get_generation_num():
    with open(generation_info_file, 'r', newline='') as file:
        last_gen_num = int(file.readlines()[-1][0])
    return last_gen_num


# create_gen_info_file()

import time
import random
import time
import sys
from BTD6Game import Game
import pyautogui as pg

# Genetic setup
# place_tower = ["place_tower", "dart_monkey", (205, 500)]
# upgrade_tower = ["upgrade", path, monkey_to_upgrade]

def load_genetics():
    """
    Use the stored csv to load in the most recent best genetics
    :return: a dictionary of the best genetics
    """
    return {}

home = (559, 825)
exit = (50, 1022)
quit = (1147, 738)
steam_play = (600, 648)
start_game = (953, 988)
play_game = (831, 934)
monkey_meadow = (527, 250)
meadow_easy = (621, 427)
meadow_standard = (633, 592)
restart_button = (819, 803)
confirm_restart_button = (1136, 720)

def full_restart_game():
    pg.click(home)
    time.sleep(5)
    pg.click(exit)
    time.sleep(3)
    pg.click(quit)
    time.sleep(10)
    pg.click(steam_play)
    time.sleep(35)
    pg.click(start_game)
    time.sleep(5)
    pg.click(play_game)
    time.sleep(5)
    pg.click(monkey_meadow)
    time.sleep(5)
    pg.click(meadow_easy)
    time.sleep(5)
    pg.click(meadow_standard)
    time.sleep(5)

def restart_game():
    pg.click(restart_button)
    time.sleep(1)
    pg.click(confirm_restart_button)

def create_grid():
    grid = []
    for j in range(80, 1000, 68):
        for i in range(0, 1600, 80):
            pos = (i, j)
            grid.append(pos)
    return grid

def main():

    if len(sys.argv) < 2:
        print("Please pass in difficulty:")
        print("E: Easy, M: Medium, H: Hard, C: Chimps")
        print("Followed by Y or N to use cache")
        exit()

    difficulty = {
        "E": {
            "lives": 200.0,
            "start_round": 0,
            "max_round": 40,
            "base": "easybase",
            "bottom": "easybottom",
            "middle": "easymiddle",
            "top": "easytop"
        },
        "M":{
            "lives": 150.0,
            "start_round": 0,
            "max_round": 60,
            "base": "mediumbase",
            "bottom": "mediumbottom",
            "middle": "mediummiddle",
            "top": "mediumtop"
        },
        "H": {
            "lives": 100.0,
            "start_round": 2,
            "max_round": 80,
            "base": "hardbase",
            "bottom": "hardbottom",
            "middle": "hardmiddle",
            "top": "hardtop"
        },
        "C": {
            "lives": 1.0,
            "start_round": 2,
            "max_round": 100,
            "base": "hardbase",
            "bottom": "hardbottom",
            "middle": "hardmiddle",
            "top": "hardtop"
        },
    }

    if sys.argv[1] not in difficulty.keys():
        print("Invalid Difficulty")
        print("E: Easy, M: Medium, H: Hard, C: Chimps")
        print("Followed by Y or N to load genetics")

    load = False

    if len(sys.argv) > 2 and sys.argv[2] == "Y":
        load = True

    time.sleep(2)

    base_genes = [
        ["place_tower", "ninja_monkey", (627, 503)],
        ["place_tower", "bomb_shooter", (627, 503)],
        ["place_tower", "dart_monkey", (627, 503)],
        # ["place_tower", "ninja_monkey", (630, 402)],
        # ["place_tower", "bomb_shooter", (630, 402)],
        # ["place_tower", "dart_monkey", (630, 402)],
        # ["place_tower", "ninja_monkey", (900, 600)],
        # ["place_tower", "bomb_shooter", (300, 300)],
        # ["place_tower", "dart_monkey", (400, 400)]
    ]

    if load:
        cur_genes = load_genetics()
    else:
        cur_genes = base_genes


    while True:
        best_games = []
        # Go through all current individuals and run game
        for gene in cur_genes:
            print("<============Beginning New Game============>")
            new_game = Game([gene], difficulty[sys.argv[1]], False)
            round, length, game_genes = new_game.run_game()
            print("Round: ", round, " - Time: ", length)
            best_games.append([round, length, game_genes])
            restart_game()

        exit()

        # Get the best individual
        first_best = None
        first_best_scores = [0, 0]
        second_best = None
        second_best_scores = [0, 0]
        for each in best_games:
            num_rounds = each[0]
            time_game = each[1]
            if num_rounds > first_best_scores[0]:
                first_best = each[2]
                first_best_scores = [each[0], each[1]]
            elif num_rounds == first_best_scores[0]:
                if time_game > first_best_scores[1]:
                    first_best = each[2]
                    first_best_scores = [each[0], each[1]]
            elif num_rounds > second_best_scores[0]:
                second_best = each[2]
                second_best_scores = [each[0], each[1]]
            elif num_rounds == second_best_scores[0]:
                if time_game > second_best_scores[1]:
                    second_best = each[2]
                    second_best_scores = [each[0], each[1]]
                


        # Mutate that individual into 4 other types?

        # Reset cur_genes



if __name__=="__main__":
    main()
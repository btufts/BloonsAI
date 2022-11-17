# Entry file to train the AI

import time
import sys
from .BTD6Game import Game
import pyautogui as pg
import src.AI.utils.util as util
import src.AI.utils.file_processing as fp

# Genetic setup
# place_tower = ["place_tower", "dart_monkey", (205, 500)]
# upgrade_tower = ["upgrade", path, monkey_to_upgrade]

# Move this to util maybe?
def load_genetics():
    """
    Use the stored csv to load in the most recent best genetics
    :return: a dictionary of the best genetics
    """
    return {}


def full_restart_game():
    pg.click(util.home)
    time.sleep(5)
    pg.click(exit)
    time.sleep(3)
    pg.click(quit)
    time.sleep(10)
    pg.click(util.steam_play)
    time.sleep(35)
    pg.click(util.start_game)
    time.sleep(5)
    pg.click(util.play_game)
    time.sleep(5)
    pg.click(util.monkey_meadow)
    time.sleep(5)
    pg.click(util.meadow_easy)
    time.sleep(5)
    pg.click(util.meadow_standard)
    time.sleep(5)

def restart_game():
    pg.click(util.restart_button)
    time.sleep(1)
    pg.click(util.confirm_restart_button)

def create_grid():
    grid = []
    for j in range(80, 1000, 68):
        for i in range(0, 1600, 80):
            pos = (i, j)
            grid.append(pos)
    return grid

def train():

    difficulty_selection = input("Please enter difficulty (E: Easy, M: Medium, H: Hard, C: Chimps): ")
    while difficulty_selection not in ['E', 'M', 'H', 'C']:
        print("Invalid Difficulty")
        print("E: Easy, M: Medium, H: Hard, C: Chimps")
        difficulty_selection = input("Please enter difficulty (E: Easy, M: Medium, H: Hard, C: Chimps): ")
        
    preload = input("Load data from file? ")
    while preload not in ['Y', 'N']:
        print("Invalid Value")
        print("Y for load, N for not load")
        preload = input("Load data from file? ")
    
    difficulty = {}
    match difficulty_selection:
        case 'E':
            difficulty = {
                "lives": 200.0,
                "start_round": 0,
                "max_round": 40,
                "base": "easybase",
                "bottom": "easybottom",
                "middle": "easymiddle",
                "top": "easytop"
            }
        case 'M':
            difficulty = {
                "lives": 150.0,
                "start_round": 0,
                "max_round": 60,
                "base": "mediumbase",
                "bottom": "mediumbottom",
                "middle": "mediummiddle",
                "top": "mediumtop"
            }
        case 'H':
            difficulty = {
                "lives": 100.0,
                "start_round": 2,
                "max_round": 80,
                "base": "hardbase",
                "bottom": "hardbottom",
                "middle": "hardmiddle",
                "top": "hardtop"
            }
        case 'C':
            difficulty = {
                "lives": 1.0,
                "start_round": 2,
                "max_round": 100,
                "base": "hardbase",
                "bottom": "hardbottom",
                "middle": "hardmiddle",
                "top": "hardtop"
            }

    load = False
    match preload:
        case 'Y':
            load = True
        case _:
            load = False

    time.sleep(2)

    base_genes = [
        [["place_tower", "ninja_monkey", (627, 503)]],
        [["place_tower", "bomb_shooter", (627, 503)]],
        [["place_tower", "dart_monkey", (627, 503)]],
        # ["place_tower", "ninja_monkey", (630, 402)],
        # ["place_tower", "bomb_shooter", (630, 402)],
        # ["place_tower", "dart_monkey", (630, 402)],
        # ["place_tower", "ninja_monkey", (900, 600)],
        # ["place_tower", "bomb_shooter", (300, 300)],
        # ["place_tower", "dart_monkey", (400, 400)]
    ]

    if load:
        cur_genes = fp.read_genetics()
        generation_num = fp.get_generation_num()
    else:
        cur_genes = base_genes
        generation_num = 0


    while True:

        # create offspring here

        best_games = []
        generation_num += 1
        # Go through all current individuals and run game
        for gene in cur_genes:
            print("<============Beginning New Game============>")
            new_game = Game(gene, difficulty, False)
            round, length, game_genes = new_game.run_game()
            print("Round: ", round, " - Time: ", length)
            best_games.append([round, length, game_genes])
            restart_game()

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
        fp.save_genetics(first_best, second_best)
        fp.save_gen_info(generation_num, first_best_scores[0], first_best_scores[1])

        exit()
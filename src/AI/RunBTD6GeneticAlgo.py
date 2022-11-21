# Entry file to train the AI

import time
from .BTD6Game import Game
import pyautogui as pg
import src.AI.utils.util as util
import src.AI.utils.file_processing as fp
import random
import math

# Genetic setup
# place_hero = ["place_hero", (x, y)]
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

def create_grid():
    grid = []
    for j in range(80, 1000, 68):
        for i in range(0, 1600, 80):
            pos = (i, j)
            grid.append(pos)
    return grid

def get_grid_num(grid, loc):
    shortest = math.dist(grid[0], loc)
    shortest_index = 0
    for i in range(1, len(grid)):
        dist = math.dist(grid[i], loc)
        if dist < shortest:
            shortest = dist
            shortest_index = i
    return shortest_index

def update_monkey_loc(avg_round, best_games):
    # Will call file reading function to get monkey data
    monkey_locations = {}
    grid = util.setup_grid()
    for game in best_games:
        actions = game[2]
        game_round = game[0]
        for act in actions:
            if act[0] == "upgrade":
                continue
            grid_num = get_grid_num(grid, act[2])
            monkey_locations[act[1]] = monkey_locations[act[1]][grid_num] + (game_round - avg_round)
            if monkey_locations[act[1]][grid_num] < 1: 
                monkey_locations[act[1]][grid_num] = 1
    # Call function to write monkey_locations back to file


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

    while True:
        try:
            learning_rate = float(input("What learning rate? "))
        except ValueError:
            print("Invalid float value")
        else:
            if(learning_rate >= 0 and learning_rate <= 1):
                break
            else:
                print("Invalid Learning rate (0 <= a <= 1)")

    while True:
        try:
            gens = int(input("How many generations? "))
        except ValueError:
            print("Invalid number of generations")
        else:
            break
            
    
    
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
                "top": "easytop",
                "round": 0
            }
        case 'M':
            difficulty = {
                "lives": 150.0,
                "start_round": 0,
                "max_round": 60,
                "base": "mediumbase",
                "bottom": "mediumbottom",
                "middle": "mediummiddle",
                "top": "mediumtop",
                "round": 0
            }
        case 'H':
            difficulty = {
                "lives": 100.0,
                "start_round": 2,
                "max_round": 80,
                "base": "hardbase",
                "bottom": "hardbottom",
                "middle": "hardmiddle",
                "top": "hardtop",
                "round": 2
            }
        case 'C':
            difficulty = {
                "lives": 1.0,
                "start_round": 2,
                "max_round": 100,
                "base": "hardbase",
                "bottom": "hardbottom",
                "middle": "hardmiddle",
                "top": "hardtop",
                "round": 6
            }

    load = False
    match preload:
        case 'Y':
            load = True
        case _:
            load = False

    time.sleep(2)

    base_genes = [
        [["place_hero", (627, 503)]],
        [["place_hero", (300, 600)]],
        [["place_hero", (700, 303)]],
    ]

    
    for _ in range(gens):

        if load:
            cur_genes = fp.read_genetics()
            generation_num = fp.get_generation_num()
        else:
            cur_genes = base_genes
            generation_num = 0

        # create offspring here
        if len(cur_genes[0]) >=2 and len(cur_genes[1]) >=2:
            for _ in range(4):
                split = random.randint(1, min(len(cur_genes[0]), len(cur_genes[1]))-1)
                game1 = list(cur_genes[0])
                game2 = list(cur_genes[1])
                game1_half1 = game1[:split]
                game1_half2 = game1[split:]
                game2_half1 = game2[:split]
                game2_half2 = game2[split:]
                game1_half1.extend(game2_half2)
                game2_half1.extend(game1_half2)
                cur_genes.append(game1_half1)
                cur_genes.append(game2_half1)

            cur_genes.append(list(cur_genes[0])[:random.randint(math.floor(len(cur_genes[0])/2), len(cur_genes[0])-1)])
            cur_genes.append(list(cur_genes[1])[:random.randint(math.floor(len(cur_genes[1])/2), len(cur_genes[1])-1)])
            cur_genes.append(list(cur_genes[0])[:random.randint(1, math.ceil(len(cur_genes[0])/2))])
            cur_genes.append(list(cur_genes[1])[:random.randint(1, math.ceil(len(cur_genes[1])/2))])
            cur_genes.append(["place_hero", (627, 503)])
            cur_genes.append(["place_hero", (700, 303)])

        for each in cur_genes:
            print(each)

        best_scores = fp.get_best_scores()
        first_best = cur_genes[0]
        first_best_scores = [best_scores[0], best_scores[1]]
        second_best = cur_genes[1]
        second_best_scores = [best_scores[2], best_scores[3]]

        best_games = []
        generation_num += 1
        # Go through all current individuals and run game
        ind = 1
        total_rounds = 0
        for gene in cur_genes:
            print("<============Beginning Game ", ind,"============>")
            print(gene)
            new_game = Game(gene, difficulty, False, learning_rate)
            while(new_game is None):
                util.full_restart(difficulty)
                new_game = Game(gene, difficulty, False, learning_rate)
            round, length, game_genes, towers, upgrades = new_game.run_game()
            total_rounds += round
            print("Round: ", round, " - Time: ", length)
            best_games.append([round, length, game_genes, towers, upgrades])
            util.restart_game()
            ind+=1

        avg_round = total_rounds/len(cur_genes)
        update_monkey_loc(avg_round, best_games)
        
        # Get the best individual
        total_towers = 0
        total_upgrades = 0
        highest = 0
        lowest = 1000
        for each in best_games:
            num_rounds = each[0]
            time_game = each[1]
            total_rounds += num_rounds
            total_towers += each[3]
            total_upgrades += each[4]
            highest = max(highest, num_rounds)
            lowest = min(lowest, num_rounds)
            if num_rounds > first_best_scores[0]:
                second_best = first_best
                second_best_scores = [first_best_scores[0], first_best_scores[1]]
                first_best = each[2]
                first_best_scores = [each[0], each[1]]
            elif num_rounds == first_best_scores[0]:
                if time_game > first_best_scores[1]:
                    second_best = first_best
                    second_best_scores = [first_best_scores[0], first_best_scores[1]]
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
        fp.save_gen_info(generation_num, first_best_scores[0], first_best_scores[1], second_best_scores[0], second_best_scores[1], total_rounds/len(best_games), total_towers/len(best_games), total_upgrades/len(best_games), highest, lowest)
        util.full_restart(difficulty)
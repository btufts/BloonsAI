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
    monkey_locations = fp.read_grid_vals()
    grid = util.setup_grid()
    for game in best_games:
        actions = game[2]
        game_round = game[0]
        for act in actions:
            if act[0] == "upgrade":
                continue
            grid_num = get_grid_num(grid, act[2])
            monkey_locations[act[1]][grid_num] = monkey_locations[act[1]][grid_num] + (game_round - avg_round)
            if monkey_locations[act[1]][grid_num] < 1: 
                monkey_locations[act[1]][grid_num] = 1
    fp.write_grid_vals(monkey_locations)


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
        [["place_hero", "hero_monkey", (627, 503)]],
        [["place_hero", "hero_monkey", (300, 600)]],
        [["place_hero", "hero_monkey", (700, 303)]],
    ]

    
    for _ in range(gens):

        print("<============ START GENERATION ============>")

        if load:
            cur_genes = fp.read_genetics()
            generation_num = fp.get_generation_num()
            grid_vals = util.normalize(fp.read_grid_vals())
        else:
            cur_genes = base_genes
            generation_num = 0
            grid_vals = util.instantiate_grid_vals()
            fp.write_grid_vals(grid_vals)
            grid_vals = util.normalize(grid_vals)

        print("<============ PARENT 1 ============>")
        print(cur_genes[0])
        print("<============ PARENT 2 ============>")
        print(cur_genes[1])
        print("<============ BEST SCORES ============>")
        print(fp.get_best_scores())

        # create offspring here
        if len(cur_genes[0]) >=2 and len(cur_genes[1]) >=2:
            for i in range(2):
                split = random.randint(1, min(len(cur_genes[0]), len(cur_genes[1]))-1)
                game1 = cur_genes[0].copy()
                game2 = cur_genes[1].copy()
                game1_half1 = game1[:split]
                game1_half2 = game1[split:]
                game2_half1 = game2[:split]
                game2_half2 = game2[split:]
                game1_half1.extend(game2_half2)
                game2_half1.extend(game1_half2)
                if i == 1:
                    first_act = game1_half1[0]
                    second_act = game2_half1[0]
                    game1_half1.pop(0)
                    game2_half1.pop(0)
                    random.shuffle(game1_half1)
                    random.shuffle(game2_half1)
                    game1_half1.insert(0, first_act)
                    game2_half1.insert(0, second_act)
                cur_genes.append(game1_half1)
                cur_genes.append(game2_half1)
            
            for _ in range(2):
                game = []
                for i in range(min(len(cur_genes[0]), len(cur_genes[1]))):
                    c = random.choice([0,1])
                    game.append(cur_genes[c][i])
                cur_genes.append(game)

            for _ in range(2):
                game = cur_genes[0].copy()
                first_act = game[0]
                game.pop(0)
                random.shuffle(game)
                game.insert(0, first_act)
                cur_genes.append(game)
                

            cur_genes.append(list(cur_genes[0])[:random.randint(math.floor(len(cur_genes[0])/2), len(cur_genes[0])-1)])
            cur_genes.append(list(cur_genes[1])[:random.randint(math.floor(len(cur_genes[1])/2), len(cur_genes[1])-1)])
            cur_genes.append(list(cur_genes[0])[:random.randint(1, math.ceil(len(cur_genes[0])/2))])
            cur_genes.append([["place_hero", "hero_monkey", (300, 600)]])
            cur_genes.append([["place_hero", "hero_monkey", (627, 503)]])
            cur_genes.append([["place_hero", "hero_monkey", (700, 303)]])


        print("<============ ALL GAMES ============>")
        for each in cur_genes:
            print(each)

        first_best = None
        first_best_scores = [0, 0]
        second_best = None
        second_best_scores = [0, 0]

        if generation_num > 0:
            best_scores = fp.get_best_scores()
            first_best = cur_genes[0].copy()
            first_best_scores = [best_scores[0], best_scores[1]]
            second_best = cur_genes[1].copy()
            second_best_scores = [best_scores[2], best_scores[3]]

        best_games = []
        generation_num += 1
        # Go through all current individuals and run game
        ind = 1
        total_rounds = 0
        for gene in cur_genes:
            print("<============ START GAME ", ind,"============>")
            print(gene)
            new_game = Game(gene, difficulty, False, learning_rate, grid_vals)
            while(new_game is None):
                util.full_restart(difficulty)
                new_game = Game(gene, difficulty, False, learning_rate, grid_vals)
            round, length, game_genes, towers, upgrades = new_game.run_game()
            total_rounds += round
            print("<============ GAME STATS ============>")
            print("Round: ", round, " - Time: ", length)
            print("<============ GAME ACTIONS ============>")
            print(game_genes)
            print("<============ ENG GAME ", ind, "============>")
            best_games.append([round, length, game_genes, towers, upgrades])
            if ind % 4 == 0:
                print("Restarting")
                util.full_restart(difficulty)
            else:
                util.restart_game()
            ind+=1

        avg_round = total_rounds/len(cur_genes)
        update_monkey_loc(avg_round, best_games)
        
        # Get the best individual
        print("<============ ALL GAMES ============>")
        for i in range(len(best_games)):
            print("<============ GAME ", i, "============>")
            print(best_games[i])
        total_towers = 0
        total_upgrades = 0
        highest = 0
        lowest = 1000
        best_round = fp.read_best_round()
        for each in best_games:
            num_rounds = each[0]
            time_game = each[1]
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

        print("<============ BEST GAME ============>")
        print(first_best)
        print(first_best_scores)
        print("<============ BEST GAME 2 ============>")
        print(second_best)
        print(second_best_scores)

        if first_best_scores[0] > best_round:
            fp.write_best_game(first_best_scores[0], first_best)
        load = True
        fp.save_genetics(first_best, second_best)
        fp.save_gen_info(generation_num, first_best_scores[0], first_best_scores[1], second_best_scores[0], second_best_scores[1], total_rounds/len(best_games), total_towers/len(best_games), total_upgrades/len(best_games), highest, lowest)

        print("<============ END GENERATION ============>")
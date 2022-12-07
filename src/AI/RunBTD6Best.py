import time
from .BTD6Game import Game
import pyautogui as pg
import src.AI.utils.util as util
import src.AI.utils.file_processing as fp
import random
import math


def test():
    difficulty_selection = input("Please enter difficulty (E: Easy, M: Medium, H: Hard, C: Chimps): ")
    while difficulty_selection not in ['E', 'M', 'H', 'C']:
        print("Invalid Difficulty")
        print("E: Easy, M: Medium, H: Hard, C: Chimps")
        difficulty_selection = input("Please enter difficulty (E: Easy, M: Medium, H: Hard, C: Chimps): ")

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

    gene = fp.read_genetics()[0]
    grid_vals = util.normalize(fp.read_grid_vals())
    new_game = Game(gene, difficulty, False, 0, grid_vals)
    while(new_game is None):
        util.full_restart(difficulty)
        new_game = Game(gene, difficulty, False, 0, grid_vals)
    new_game.run_game()


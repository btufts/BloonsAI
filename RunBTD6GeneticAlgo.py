import time

from BTD6Game import Game
import pyautogui as pg

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

def restart_game():
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

def create_grid():
    grid = []
    for j in range(80, 1000, 68):
        for i in range(0, 1600, 80):
            pos = (i, j)
            grid.append(pos)
    return grid

load = False
base_genes = {}

if load:
    cur_genes = load_genetics()
else:
    cur_genes = base_genes

while True:

    # Go through all current individuals and run game
    for each in cur_genes:
        new_game = Game(each)
        new_game.run_game()

    # Get the best individual

    # Mutate that individual into 4 other types?

    # Reset cur_genes

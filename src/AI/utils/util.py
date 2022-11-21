# Utility functions and variables

import pyautogui as pg
from src.AI.utils.TowerData import tower_data
import time
import BloonsAI

# If the tower is placed at greater than or equal to 835 in the X direction, then the upgrade path will
# appear on the left side of the screen. If X is less than 835, then the upgrade will be on the right
middle_division = 835

moves = ["place_tower", "upgrade"]
towers = ["dart_monkey", "bomb_shooter", "ninja_monkey", 
        "monkey_ace", "wizard_monkey", "sniper_monkey", 
        "tack_shooter", "boomerang_monkey", "ice_monkey",
        "glue_gunner", "mortar_monkey"]

upgrade_paths = {
    "right_top": (1551, 516),
    "right_middle": (1551, 641),
    "right_bottom": (1551, 784),
    "right_close": (1620, 76),
    "left_top": (330, 491),
    "left_middle": (330, 638),
    "left_bottom": (330, 782),
    "left_close": (397, 80)
}

place_tower_random = ["tower", "location", "both"]
upgrade_tower_random = ["path", "location"]

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

def full_restart(difficulty_coords):
    BloonsAI.kill()
    time.sleep(3)
    pg.click(371, 425)
    time.sleep(20)
    pg.click(957, 986)
    time.sleep(10)
    pg.click(838, 930)
    time.sleep(3)
    pg.click(541, 249)
    time.sleep(3)
    pg.click(1278, 397) #Difficulty Coords
    time.sleep(3)
    pg.click(629, 579) # Game Type coords
    time.sleep(3)
    pg.click(1130, 723) # Overwrite saved game
    time.sleep(3)

def start_freeplay():
    time.sleep(2)
    pg.click(959, 901) # Ok on win
    time.sleep(2)
    pg.click(1215, 838) # Click freeplay
    time.sleep(2)
    pg.click(953, 749) # Ok on directions to freeplay
    time.sleep(2)

def restart_game():
    time.sleep(2)
    pg.click(restart_button)
    time.sleep(1)
    pg.click(confirm_restart_button)

def scroll(down):
    if down:
        pg.moveTo(1822, 935)
        pg.mouseDown()
        pg.moveTo(1822, 179, 0.2)
        pg.mouseUp()
    else:
        pg.moveTo(1822, 179)
        pg.mouseDown()
        pg.moveTo(1822, 1080, 0.2)
        pg.mouseUp()

def place_tower(tower_type, location):
    if tower_data[tower_type]["scroll"]:
        scroll(True)
        time.sleep(0.2)
    pg.click(tower_data[tower_type]["location"])
    pg.moveTo(location)
    pg.click()
    time.sleep(0.1)
    if tower_data[tower_type]["scroll"]:
        scroll(False)
    time.sleep(0.2)

def upgrade_monkey(location, path):
    if location[0] >= middle_division:
        side = "left"
    else:
        side = "right"
    path = side + "_" + path
    pg.click(location)
    time.sleep(0.1)
    pg.click(upgrade_paths[path])
    time.sleep(0.1)
    pg.click(upgrade_paths[side+"_close"])

def setup_grid():
    grid = []
    for j in range(80, 1000, 68):
        for i in range(0, 1600, 80):
            grid.append((i, j))
    return grid
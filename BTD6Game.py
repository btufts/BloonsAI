import time
from TowerData import tower_data
import pyautogui as pg
import BloonsAI


def scroll(down):
    if down:
        pg.mouseDown(1822, 935)
        pg.moveTo(1822, 179, 0.2)
        pg.mouseUp()
    else:
        pg.mouseDown(1822, 179)
        pg.moveTo(1822, 1080, 0.2)
        pg.mouseUp()


def place_tower(tower_type, location):
    pg.click(tower_data[tower_type]["location"])
    pg.moveTo(location)
    pg.click()
    time.sleep(0.5)

def upgrade_monkey(location, path, monkey):
    pass

class Game:
    state = {
        "lives": 200,
        "money": 650,
        "towers": 0,
        "round": 0
    }

    # If the tower is placed at greater than or equal to 835 in the X direction, then the upgrade path will
    # appear on the left side of the screen. If X is less than 835, then the upgrade will be on the right
    middle_division = 835

    start_button = (1828, 993)

    top_left_corner = (21, 13)
    bottom_right_corner = (1559, 954)

    tower_data = tower_data

    towers = {}

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

    # Dictionary of locations to place towers
    placement_grid = {}

    def __init__(self, genetics):
        self.genetics = genetics
        self.mydict = BloonsAI.initialize()

    def update_state(self):
        self.state["money"] = BloonsAI.get_value(self.mydict["cash"], 8)
        self.state["lives"] = BloonsAI.get_value(self.mydict["health"], 8)
        self.state["towers"] = BloonsAI.get_value(self.mydict["tower_count"], 4)
        self.state["round"] = BloonsAI.get_value(self.mydict["round"], 4)

    def start_round(self):
        pg.click(self.start_button)

    def save_genetics(self):
        pass

    def run_game(self):
        while self.state["lives"] > 0:
            self.update_state()
    
    def place_tower(self, monkey, location):
        num_towers = self.state["towers"]
        place_tower(monkey, location)
        time.sleep(0.25)
        self.update_state()
        if self.state["towers"] == num_towers + 1:
            return True
        else:
            return False

class Monkey:
    rank = [0, 0, 0]

    def __init__(self, location, monkey_type):
        self.location = location
        self.monkey_type = monkey_type
    
    def update_rank(self, path):
        if path == "top":
            self.rank[0] += 1
        elif path == "middle":
            self.rank[1] += 1
        elif path == "bottom":
            self.rank[2] += 1
    

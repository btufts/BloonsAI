import time
from TowerData import tower_data
import pyautogui as pg
import BloonsAI
import random

# If the tower is placed at greater than or equal to 835 in the X direction, then the upgrade path will
# appear on the left side of the screen. If X is less than 835, then the upgrade will be on the right
middle_division = 835

moves = ["place_tower", "upgrade"]
towers = ["dart_monkey", "bomb_shooter", "ninja_monkey"]

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

class Game:
    state = {
        "lives": 200,
        "money": 650,
        "towers": 0,
        "round": 0
    }

    # Location of play next round button
    start_button = (1828, 993)

    top_left_corner = (21, 13)
    bottom_right_corner = (1559, 954)

    # Data on cost and location of towers to put down
    tower_data = tower_data

    # List of towers on screen
    towers = []

    # Round counter to know when to start next round
    round = 0

    # List of actions
    action_list = []

    def __init__(self, genetics):
        self.genetics = genetics
        self.mydict = BloonsAI.initialize_restart()
        self.grid = setup_grid()

    def update_state(self):
        self.state["money"] = BloonsAI.get_value(self.mydict["cash"], 8)
        self.state["lives"] = BloonsAI.get_value(self.mydict["health"], 8)
        self.state["towers"] = BloonsAI.get_value(self.mydict["tower_count"], 4)
        self.state["round"] = BloonsAI.get_value(self.mydict["round"], 8)

    def start_round(self):
        pg.click(self.start_button)

    def save_genetics(self):
        pass

    def run_game(self):
        self.perform_action(self.genetics[0])
        self.start_round()
        start_time = time.time()
        action = 1
        num_actions = len(self.genetics)
        while self.state["lives"] > 0:
            if self.state["round"] > self.round:
                self.start_round()
                self.round += 1
            if action < num_actions:
                next_action = self.genetics[action]
                self.update_state()
                if self.check_cash(next_action) < self.state["money"]:
                    self.perform_action(next_action)
                    action += 1
            else:
                next_act = self.generate_action()
                self.genetics.append(next_act)
                num_actions += 1
        end_time = time.time()
        length = end_time - start_time
        self.save_genetics()
        return self.state["round"], length, self.action_list
                
    def generate_action(self):
        if len(self.towers) == 0:
            first_act = "place_tower"
        else:
            first_act = random.sample(moves, 1)[0]
        if first_act == "place_tower":
            tower_to_place = random.sample(towers, 1)[0]
            location_to_place = random.sample(self.grid, 1)[0]
            act = [first_act, tower_to_place, location_to_place]
            return act
        else:
            tower_to_upgrade = random.sample(self.towers, 1)[0]
            index_of_tower = self.towers.index(tower_to_upgrade)
            available = tower_to_upgrade.available
            if len(available) == 0:
                for i in range(len(self.towers)):
                    tower_to_upgrade = self.towers[(index_of_tower+i)%len(self.towers)]
                    available = tower_to_upgrade.available
                    if len(available) > 0:
                        break
                if len(available) == 0:
                    tower_to_place = random.sample(towers, 1)[0]
                    location_to_place = random.sample(self.grid, 1)[0]
                    act = ["place_tower", tower_to_place, location_to_place]
                    return act
            path_to_upgrade = random.sample(available, 1)[0]
            act = [first_act, path_to_upgrade, self.towers.index(tower_to_upgrade)]
            return act


    def perform_action(self, action):
        if action[0] == "place_tower":
            loc = self.place_tower(action[1], action[2], 0)
            cur_monkey = Monkey(loc, action[1])
            self.towers.append(cur_monkey)
            act = ["place_tower", action[1], loc]
        else:
            monkey_to_upgrade = self.towers[action[2]]
            path = action[1]
            upgrade_monkey(monkey_to_upgrade.location, path)
            monkey_to_upgrade.update_rank(path)
            act = action
        self.action_list.append(act)

    
    def place_tower(self, monkey, location, repeated):
        self.update_state()
        time.sleep(0.1)
        num_towers = self.state["towers"]
        place_tower(monkey, location)
        time.sleep(0.25)
        self.update_state()
        if self.state["towers"] == num_towers + 1:
            return location
        else:
            if repeated > 9:
                x = random.randint(0, self.bottom_right_corner[0])
                y = random.randint(0, self.bottom_right_corner[1])
                return self.place_tower(monkey, (x, y), 0)
            offset = random.randrange(-1, 1) * 20
            new_X = location[0] + offset
            new_Y = location[1] + offset
            if new_X <= 0:
                new_X += new_X + random.randrange(10, 100)
            if new_X >= self.bottom_right_corner[0]:
                new_X -= random.randrange(25, 200)
            if new_Y <= 0:
                new_Y += new_Y + random.randrange(10, 100)
            if new_Y >= self.bottom_right_corner[1]:
                new_Y -= random.randrange(25, 200)
            new_loc = (new_X, new_Y)
            return self.place_tower(monkey, new_loc, repeated+1)
    
    def check_cash(self, action):
        if action[0] == "place_tower":
            return self.tower_data[action[1]]["base"]
        else:
            tower_upgrading = self.towers[action[2]]
            monkey_name = tower_upgrading.monkey_type
            path = action[1]
            cur_path_level = tower_upgrading.get_path_level(path)
            return self.tower_data[monkey_name][path][cur_path_level+1]

class Monkey:
    top = 0
    middle = 0
    bottom = 0

    available = ["top", "middle", "bottom"]

    def __init__(self, location, monkey_type):
        self.location = location
        self.monkey_type = monkey_type
    
    def update_rank(self, path):
        if path == "top":
            self.top += 1
            if self.top == 5:
                if "top" in self.available:
                    self.available.remove("top")
            if self.top == 1:
                if self.bottom > 0:
                    if "middle" in self.available:
                        self.available.remove("middle")
                elif self.middle > 0:
                    if "bottom" in self.available:
                        self.available.remove("bottom")
            if self.top == 2:
                if self.bottom > 2 or self.middle > 2:
                    if "top" in self.available:
                        self.available.remove("top")
            if self.top == 3:
                if self.bottom == 2:
                    if "bottom" in self.available:
                        self.available.remove("bottom")
                elif self.middle == 2:
                    if "middle" in self.available:
                        self.available.remove("middle")
        elif path == "middle":
            self.middle += 1
            if self.middle == 5:
                if "middle" in self.available:
                    self.available.remove("middle")
            if self.middle == 1:
                if self.bottom > 0:
                    if "top" in self.available:
                        self.available.remove("top")
                elif self.top > 0:
                    if "bottom" in self.available:
                        self.available.remove("bottom")
            if self.middle == 2:
                if self.bottom > 2 or self.top > 2:
                    if "middle" in self.available:
                        self.available.remove("middle")
            if self.middle == 3:
                if self.bottom == 2:
                    if "bottom" in self.available:
                        self.available.remove("bottom")
                elif self.top == 2:
                    if "top" in self.available:
                        self.available.remove("top")
        elif path == "bottom":
            self.bottom += 1
            if self.bottom == 5:
                if "bottom" in self.available:
                    self.available.remove("bottom")
            if self.bottom == 1:
                if self.middle > 0:
                    if "top" in self.available:
                        self.available.remove("top")
                elif self.top > 0:
                    if "middle" in self.available:
                        self.available.remove("middle")
            if self.bottom == 2:
                if self.middle > 2 or self.top > 2:
                    if "bottom" in self.available:
                        self.available.remove("bottom")
            if self.bottom == 3:
                if self.middle == 2:
                    if "middle" in self.available:
                        self.available.remove("middle")
                elif self.top == 2:
                    if "top" in self.available:
                        self.available.remove("top")

    def get_path_level(self, path):
        if path == "top":
            return self.top
        elif path == "middle":
            return self.middle
        else:
            return self.bottom
    

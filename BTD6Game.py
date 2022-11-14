import time
from TowerData import tower_data
import pyautogui as pg
import BloonsAI
import random
import math
import numpy as np

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
    
    #########################################################
    ################ SHARED BY ALL INSTANCES ################
    #########################################################

    # Location of play next round button
    start_button = (1828, 993)
    top_left_corner = (21, 13)
    bottom_right_corner = (1559, 954)

    # Data on cost and location of towers to put down
    tower_data = tower_data


    def __init__(self, genetics, difficulty, cache):
        self.genetics = genetics
        self.state = {
            "lives": difficulty["lives"],
            "money": 650,
            "towers": 0,
            "round": difficulty["start_round"],
            "max_round": difficulty["max_round"]
        }

        self.grid = setup_grid()
        self.diff = difficulty
        self.towers = []
        self.action_list = []
        self.max_spend = 1000
        self.action_ratio = [.4, .6]
        self.round = 0

        if cache:
            self.mydict = BloonsAI.initialize()
        else:
            search_time = time.time()
            self.mydict = BloonsAI.initialize_threaded(difficulty["lives"], float(difficulty["start_round"]), 0)
            search_end_time = time.time()
            print("Init Time: ", search_end_time-search_time)
        

    def update_state(self):
        self.state["money"] = BloonsAI.get_value(self.mydict["cash"], 8)
        self.state["lives"] = BloonsAI.get_value(self.mydict["health"], 8)
        self.state["towers"] = BloonsAI.get_value(self.mydict["tower_count"], 4)
        self.state["round"] = BloonsAI.get_value(self.mydict["round"], 8)

    def start_round(self):
        pg.click(self.start_button)

    def save_genetics(self):
        print("<================ GENETICS ================>")
        print(self.action_list)
        print("<============= END OF GENETICS =============>")

    def update_ratio(self):
        prob = round((math.erf(2*((self.round/100)-.5))+1)/5, 2)
        self.action_ratio = [.4-prob, .6+prob]

    def update_max_spend(self):
        if self.round >= 50:
            self.max_spend = 999999999
        else:
            self.max_spend = 1000*math.exp(self.round/15)+200

    def run_game(self):
        self.perform_action(self.genetics[0])
        self.start_round()
        time.sleep(1)
        self.start_round()
        start_time = time.time()
        action = 1
        num_actions = len(self.genetics)
        #and self.state["max_round"] > self.state["round"] !!! Not sure how round ending work? >? or >=? hm !!!
        while self.state["lives"] > 0 and self.state["round"] < self.state["max_round"]:
            if action < num_actions:
                next_action = self.genetics[action]
                self.update_state()
                print("<========== CURRENT TOWER LIST ==========>")
                for tower in self.towers:
                    print("Tower: ", tower)
                print(self.state["money"], " - ", next_action, " - ", 
                        self.check_cash(next_action), " - ", self.action_ratio[0], "/", 
                        self.action_ratio[1])
                if next_action[0] == "upgrade":
                        print("Tower to upgrade: ", self.towers[next_action[2]])
                while self.check_cash(next_action) > self.state["money"] and self.state["lives"] > 0 and self.state["round"] < self.state["max_round"]:
                    self.update_state()
                    print(self.state["money"], " - ", next_action, " - ", 
                        self.check_cash(next_action), " - ", self.action_ratio[0], "/", 
                        self.action_ratio[1])
                    if next_action[0] == "upgrade":
                        print("Tower to upgrade: ", self.towers[next_action[2]])
                    if self.state["round"] > self.round:
                        self.start_round()
                        self.round += 1
                        self.update_ratio()
                        self.update_max_spend()
                    else:
                        time.sleep(0.5)
                print("Performing Action: ", (next_action))
                if self.perform_action(next_action):
                    action += 1
            else:
                print("Generating Action")
                next_act = self.generate_action()
                self.genetics.append(next_act)
                num_actions += 1
            time.sleep(0.2)
        end_time = time.time()
        length = end_time - start_time
        self.save_genetics()
        return self.state["round"], length, self.action_list
                
    def generate_action(self):
        if len(self.towers) == 0:
            first_act = "place_tower"
        else:
            #first_act = random.sample(moves, 1)[0]
            first_act = np.random.choice(moves, 1, p=self.action_ratio)[0]
        if first_act == "place_tower":
            tower_to_place = random.sample(towers, 1)[0]
            location_to_place = random.sample(self.grid, 1)[0]
            act = [first_act, tower_to_place, location_to_place]
            return act
        else:
            print("TOWER LIST: ", self.towers)
            towers_to_upgrade = list(self.towers)
            random.shuffle(towers_to_upgrade)
            print("TOWER LIST AFTER SHUFFLE: ", self.towers)
            for i in range(len(towers_to_upgrade)):
                available = list(towers_to_upgrade[i].available)
                random.shuffle(available)                                        
                for j in range(len(available)):
                    act = [first_act, available[j], self.towers.index(towers_to_upgrade[i])]
                    if(self.check_cash(act) <= self.max_spend):
                        return act
            tower_to_place = random.sample(towers, 1)[0]
            location_to_place = random.sample(self.grid, 1)[0]
            act = ["place_tower", tower_to_place, location_to_place]
            return act

    def perform_action(self, action):
        if action[0] == "place_tower":
            status, loc = self.place_tower(action[1], action[2])
            if not status:
                # Failed to place monkey
                x = random.randint(0, self.bottom_right_corner[0])
                y = random.randint(0, self.bottom_right_corner[1])
                action[2] = (x, y)
                return False
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
        return True

    def place_tower(self, monkey, location):
        self.update_state()
        time.sleep(0.1)
        num_towers = self.state["towers"]
        for i in range(9):
            place_tower(monkey, location)
            time.sleep(0.5)
            self.update_state()
            if self.state["towers"] == num_towers+1:
                return True, location
            else:
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
                location = (new_X, new_Y)
        return False, (0, 0)
    
    def check_cash(self, action):
        if action[0] == "place_tower":
            return self.tower_data[action[1]][self.diff["base"]]
        else:
            tower_upgrading = self.towers[action[2]]
            monkey_name = tower_upgrading.monkey_type
            path = action[1]
            cur_path_level = tower_upgrading.get_path_level(path)
            return self.tower_data[monkey_name][self.diff[path]][cur_path_level+1]

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

    def __str__(self):
        return "% s: % s - % s/% s/% s" % (self.monkey_type, self.top, self.middle, self.bottom, self.location)
    

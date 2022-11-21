# Game class to play the game

import time
from src.AI.utils.TowerData import tower_data
import pyautogui as pg
import BloonsAI
import random
import math
import numpy as np
import src.AI.utils.util as util
from src.AI.Monkey import Monkey

class Game:
    
    #########################################################
    ################ SHARED BY ALL INSTANCES ################
    #########################################################

    # Location of play next round button
    start_button = (1828, 993)
    top_left_corner = (21, 13)
    bottom_right_corner = (1559, 954)
    hero = (1710, 219)

    def __new__(cls, genetics, difficulty, cache, alpha):
        game = super(Game, cls).__new__(cls) 
        search_time = time.time()
        game.mydict = BloonsAI.initialize_threaded(difficulty["lives"], float(difficulty["start_round"]), 0)
        search_end_time = time.time()
        print("Init Time: ", search_end_time-search_time)
        if len(game.mydict) == 0:
            return None
        return game

    def __init__(self, genetics, difficulty, cache, alpha):
        self.genetics = genetics.copy()
        self.state = {
            "lives": difficulty["lives"],
            "money": 650,
            "towers": 0,
            "round": difficulty["start_round"],
            "max_round": difficulty["max_round"]
        }
        self.alpha = alpha

        self.grid = util.setup_grid()
        self.diff = difficulty
        # (x,y): Monkey
        self.towers = {}
        self.upgrades = 0
        # ["place_tower", "{tower}", (x,y)]
        # ["upgrade", "{branch}", (x,y)]
        self.action_list = []
        self.max_spend = 1000
        self.action_ratio = [.35, .65]
        self.round = difficulty["round"]
        self.round_timer = 0

        # if cache:
        #     self.mydict = BloonsAI.initialize()
        # else:
        #     search_time = time.time()
        #     self.mydict = BloonsAI.initialize_threaded(difficulty["lives"], float(difficulty["start_round"]), 0)
        #     #self.mydict = BloonsAI.initialize_restart(difficulty["lives"], float(difficulty["start_round"]))
        #     search_end_time = time.time()
        #     print("Init Time: ", search_end_time-search_time)
            
        
    def update_state(self):
        self.state["money"] = BloonsAI.get_value(self.mydict["cash"], 8)
        self.state["lives"] = BloonsAI.get_value(self.mydict["health"], 8)
        self.state["towers"] = BloonsAI.get_value(self.mydict["tower_count"], 4)
        self.state["round"] = BloonsAI.get_value(self.mydict["round"], 8)

    def start_round(self):
        self.round_timer = time.time()
        pg.click(self.start_button)

    def retry_start_round(self):
        time.sleep(1)
        pg.click(826, 946)
        time.sleep(1)
        pg.click(812, 13)
        time.sleep(1)
        self.round_timer = time.time()
        pg.click(self.start_button)

    def save_genetics(self):
        print("<================ GENETICS ================>")
        print(self.action_list)
        print("<============= END OF GENETICS =============>")

    def update_ratio(self):
        prob = round((math.erf(5*((self.round/100)-.2))+1)/8, 2)
        self.action_ratio = [.35-prob, .65+prob]

    def update_max_spend(self):
        if self.round >= 50:
            self.max_spend = 999999999
        else:
            self.max_spend = 1000*math.exp(self.round/15)+200

    def run_game(self):
        while((len(self.genetics) > 0 and self.genetics[0][0] == "upgrade") or (len(self.genetics) > 0 and self.check_cash(self.genetics[0]) > self.state["money"])):
            self.genetics.pop(0)
        if(len(self.genetics) == 0):
            first_action = self.generate_action()
            self.genetics.append(first_action)
        self.perform_action(self.genetics[0])
        self.start_round()
        time.sleep(1)
        self.start_round()
        start_time = time.time()
        action = 1
        num_actions = len(self.genetics)
        while self.state["lives"] > 0:
            if self.state["round"] == self.state["max_round"]:
                util.start_freeplay()
            if action < num_actions:
                next_action = self.genetics[action]
                self.update_state()
                print("<========== CURRENT TOWER LIST ==========>")
                for tower in self.towers:
                    print("Tower: ", tower)
                if next_action[0] == "upgrade":
                    possible = self.verify_upgrade(next_action)
                    if not possible:
                        new_action = self.fix_upgrade(next_action)
                        if not new_action:
                            self.genetics.remove(next_action)
                            num_actions -= 1
                            continue
                        else:
                            next_action = new_action
                print(self.state["money"], " - ", next_action, " - ", 
                        self.check_cash(next_action), " - ", self.action_ratio[0], "/", 
                        self.action_ratio[1])
                if next_action[0] == "upgrade":
                        print("Tower to upgrade: ", self.towers[next_action[2]])
                while self.check_cash(next_action) > self.state["money"] and self.state["lives"] > 0:
                    if self.state["round"] == self.state["max_round"]:
                        util.start_freeplay()
                    self.update_state()
                    print(self.state["money"], " - ", next_action, " - ", 
                        self.check_cash(next_action), " - ", self.action_ratio[0], "/", 
                        self.action_ratio[1])
                    if next_action[0] == "upgrade":
                        print("Tower to upgrade: ", self.towers[next_action[2]])
                    if self.state["round"] > self.round:
                        self.round += 1
                        self.update_ratio()
                        self.update_max_spend()
                        self.start_round()
                        time.sleep(0.2)
                    else:
                        if time.time() - self.round_timer >= 300:
                            self.retry_start_round()
                        time.sleep(0.5)
                print("Performing Action: ", (next_action))
                if self.perform_action(next_action):
                    action += 1
                    while action < num_actions and self.genetics[action][0] == "upgrade" and not self.verify_upgrade(self.genetics[action]):
                        new_action = self.fix_upgrade(self.genetics[action])
                        if not new_action:
                            self.genetics.remove(self.genetics[action])
                            num_actions -= 1
                        else:
                            self.genetics[action] = new_action

                    if action < num_actions:
                        potential_next_act = self.genetics[action]
                        rand_num = random.random()
                        if rand_num <= self.alpha:
                            print("MUTATION OCCURRED")
                            print("OLD ACTION: " + str(potential_next_act))
                            new_action = self.perform_mutation(potential_next_act)
                            print("NEW ACTION: " + str(new_action))
                            self.genetics[action] = new_action
                    time.sleep(0.2)
            else:
                print("Generating Action")
                next_act = self.generate_action()
                self.genetics.append(next_act)
                num_actions += 1
            time.sleep(0.2)
        end_time = time.time()
        length = end_time - start_time
        self.save_genetics()
        return self.state["round"], length, self.action_list, len(self.towers), self.upgrades
                
    def generate_action(self):
        if len(self.towers) == 0:
            first_act = "place_tower"
        else:
            first_act = np.random.choice(util.moves, 1, p=self.action_ratio)[0]
        if first_act == "place_tower":
            tower_to_place = random.sample(util.towers, 1)[0]
            location_to_place = random.sample(self.grid, 1)[0]
            act = [first_act, tower_to_place, location_to_place]
            return act
        else:
            print("TOWER LIST: ")
            for key, value in self.towers.items():
                print(key, ": ", value)
            towers_to_upgrade = list(self.towers.keys())
            random.shuffle(towers_to_upgrade)
            for i in range(len(towers_to_upgrade)):
                available = list(self.towers[towers_to_upgrade[i]].available.copy())
                random.shuffle(available)                                        
                for j in range(len(available)):
                    act = [first_act, available[j], towers_to_upgrade[i]]
                    if(self.check_cash(act) <= self.max_spend):
                        return act
            tower_to_place = random.sample(util.towers, 1)[0]
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
            self.towers[loc] = cur_monkey
            act = ["place_tower", action[1], loc]
        else:
            self.upgrades += 1
            monkey_to_upgrade = self.towers[action[2]]
            path = action[1]
            util.upgrade_monkey(monkey_to_upgrade.location, path)
            monkey_to_upgrade.update_rank(path)
            act = action
        self.action_list.append(act)
        return True

    def place_tower(self, monkey, location):
        self.update_state()
        time.sleep(0.1)
        num_towers = self.state["towers"]
        for _ in range(9):
            # TODO: doesn't work
            if self.state["lives"] <= 0:
                break
            elif self.state["round"] == self.state["max_round"]:
                util.start_freeplay
            util.place_tower(monkey, location)
            time.sleep(0.25)
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
            return tower_data[action[1]][self.diff["base"]]
        else:
            tower_upgrading = self.towers[action[2]]
            monkey_name = tower_upgrading.monkey_type
            path = action[1]
            cur_path_level = tower_upgrading.get_path_level(path)
            return tower_data[monkey_name][self.diff[path]][cur_path_level+1]
    
    def perform_mutation(self, action):
        if action[0] == "place_tower":
            update = random.sample(util.place_tower_random, 1)[0]
            if update == "tower":
                action[1] = random.sample(util.towers, 1)[0]
            elif update == "location":
                action[2] = random.sample(self.grid, 1)[0]
            else:
                action[1] = random.sample(util.towers, 1)[0]
                action[2] = random.sample(self.grid, 1)[0]
            return action
        else:
            upgrade = random.sample(util.upgrade_tower_random, 1)[0]
            if upgrade == "path":
                tower = self.towers.get(action[2])
                available_actions = tower.available.copy()
                if action[1] in available_actions and len(available_actions) > 1:
                    available_actions.remove(action[1])
                random.shuffle(available_actions)
                temp = action[1]
                for act in available_actions:
                    action[1] = act
                    if self.check_cash(action) <= self.max_spend:
                        return action
                action[1] = temp

            if len(self.towers) > 1:
                possible_locs = list(self.towers.keys())
                if action[2] in possible_locs:
                    possible_locs.remove(action[2])
                random.shuffle(possible_locs)
                for loc in possible_locs:
                    action[2] = loc
                    tower = self.towers[loc]
                    available_actions = tower.available.copy()
                    random.shuffle(available_actions)
                    for act in available_actions:
                        action[1] = act
                        if self.check_cash(action) <= self.max_spend:
                            return action
            return action
    
    def verify_upgrade(self, action):
        if self.towers.get(action[2]):
            tower = self.towers.get(action[2])
            available_actions = tower.available.copy()
            if action[1] in available_actions and self.check_cash(action) <= self.max_spend:
                return True
        return False
    
    def fix_upgrade(self, action):
        if self.towers.get(action[2]) is not None:
            tower = self.towers.get(action[2])
            available_actions = tower.available.copy()
            random.shuffle(available_actions)
            for act in available_actions:
                action[1] = act
                if self.check_cash(action) <= self.max_spend:
                    return action
        locations = list(self.towers.keys())
        best_loc = {}
        best_dist = []
        for each in locations:
            dist = math.dist(each, action[2])
            best_loc[dist] = each
            best_dist.append(dist)
        best_dist.sort()
        for each2 in best_dist:
            tower_to_upgrade = self.towers.get(best_loc.get(each2))
            action[2] = best_loc.get(each2)
            available_actions = tower_to_upgrade.available.copy()
            random.shuffle(available_actions)
            for act in available_actions:
                action[1] = act
                if self.check_cash(action) <= self.max_spend:
                    return action
        return False


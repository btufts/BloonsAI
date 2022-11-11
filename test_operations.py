import BTD6Game
import pyautogui
import random
import time

time.sleep(5)

grid = []

action = ["place_tower", "dart_monkey", (400, 500)]

new_game = BTD6Game.Game([action])

round, time, genes = new_game.run_game()
print("Round: " + str(round))
print("Time: " + str(time))
print(genes)

# print(new_game.state["round"])
# new_game.start_round()
# new_game.perform_action(new_game.generate_action())
# print(new_game.generate_action())
# print(new_game.generate_action())
# time.sleep(60)
# new_game.update_state()
# print(new_game.state["round"])

# action = ["place_tower", "dart_monkey", new_game.grid[random.randint(0, len(new_game.grid)-1)]]

# new_game.perform_action(action)

# action2 = ["upgrade", "top", 0]

# new_game.perform_action(action2)

# monkey = BTD6Game.Monkey((0,0), "dart_monkey")
# monkey2 = BTD6Game.Monkey((0,0), "ninja_monkey")
# new_game.towers.append(monkey)
# new_game.towers.append(monkey2)

# monkey.update_rank("top")
# monkey.update_rank("bottom")
# monkey.update_rank("bottom")
# monkey.update_rank("bottom")
# monkey.update_rank("top")

# monkey2.update_rank("middle")

# print(monkey.available)
# print(monkey.top, monkey.middle, monkey.bottom)

# print(new_game.check_cash(["place_tower", "dart_monkey", (0,0)]))
# print(new_game.check_cash(["place_tower", "bomb_shooter", (0,0)]))
# print(new_game.check_cash(["place_tower", "ninja_monkey", (0,0)]))
# print(new_game.check_cash(["upgrade", "top", 0]))
# print(new_game.check_cash(["upgrade", "middle", 0]))
# print(new_game.check_cash(["upgrade", "bottom", 0]))
# print(new_game.check_cash(["upgrade", "top", 1]))
# print(new_game.check_cash(["upgrade", "middle", 1]))
# print(new_game.check_cash(["upgrade", "bottom", 1]))
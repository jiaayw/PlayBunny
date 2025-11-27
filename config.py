# coding:utf-8

# -----World Setting------
graphic_file = 'resources/world_level3.txt'
grid_width = 50   # pixels of a single grid
wall_color = '#D3CAB4'
wall_img = "resources/wall.png"
hunter_color = '#000000'
hunter_img = "resources/hunter.gif"
rabbit_color = "#FF60C7"
rabbit_img = "resources/rabbit.gif" 
carrot_color = '#DAA72A'
carrot_img = "resources/carrot.gif"
speed = 50  # animal speed is 10m/s, the max value supposed to be less than 1000.


# -----Learning Parameters---
alpha = 0.2    # learning rate
gamma = 0.9    # importance of next action
epsilon = 0.1  # exploration chance


# ------Reward and Punishment----
EAT_CARROT = 50
CAUGHT_BY_HUNTER = -100
MOVE_REWARD = -1

# determine how many directions can agent moves.
directions = 4  # you may change it to 4: up,down,left and right.


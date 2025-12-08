# world settings
graphic_file = 'resources/world_level3.txt'
grid_width = 50  
wall_color = '#D3CAB4'
wall_img = "resources/wall.png"
hunter_color = '#000000'
hunter_img = "resources/hunter.gif"
rabbit_color = "#FF60C7"
rabbit_img = "resources/rabbit.gif" 
carrot_color = '#DAA72A'
carrot_img = "resources/carrot.gif"
# the max value supposed to be less than 1000.
speed = 50  


# learning parameter
# learning rate
alpha = 0.2
# importance of next action    
gamma = 0.9  
# exploration chance  
epsilon = 0.1  


# parameters for reward function
EAT_CARROT = 50
CAUGHT_BY_HUNTER = -100
MOVE_REWARD = -1

# determine how many directions can agent moves
# we also considered 8 but hunmanhunter can only move in 4 directions
directions = 4  


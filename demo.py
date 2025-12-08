import tkinter as tk
import importlib
import datetime
import os
import glob
import random 
import setup
import config as cfg
import agents 
from metrics_viz import TrainingMetrics

importlib.reload(setup)
importlib.reload(cfg)
importlib.reload(agents)

from agents import Rabbit, Carrot, Hunter, pick_random_location

# global flag
# 0 = stop, 2 = Level 2, 3 = Level 3, 4 = Level 4
TRIGGER_NEXT_LEVEL = 0 

def get_latest_brain():
    directory = "resources/brain"
    if not os.path.exists(directory): return None
    list_of_files = glob.glob(f'{directory}/*.pkl') 
    if not list_of_files: return None
    return max(list_of_files, key=os.path.getctime)

def get_random_brain_file():
    """Selects a random brain file for Level 4."""
    directory = "resources/brain"
    if not os.path.exists(directory): return None
    list_of_files = glob.glob(f'{directory}/*.pkl') 
    if not list_of_files: return None
    return random.choice(list_of_files)

def save_progress():
    """Saves brain, data, and plots."""
    print("Saving current session...")
    directory = "resources/brain"
    if not os.path.exists(directory): os.makedirs(directory)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{directory}/rabbit_brain_{timestamp}.pkl"
    
    if rabbit and hasattr(rabbit, 'ai'):
        rabbit.ai.save_brain(filename)
    
    if metrics:
        metrics.save_data_to_file("resources/data")
        metrics.plot(save_dir="resources/play")

class HumanHunter(Hunter):
    def __init__(self, filename):
        super().__init__(filename)
        self.cell = None
        self.color = cfg.hunter_color
        self.image_file = "resources/hunter.gif"
        self.hunterWin = 0
        self.next_move = None

    def set_move(self, direction_index):
        self.next_move = direction_index

    def update(self):
        if self.next_move is not None:
            self.go_direction(self.next_move)
            self.next_move = None
            
            # Check for collision
            for agent in self.cell.agents:
                if isinstance(agent, Rabbit):
                    print(f'Hunter caught rabbit! ({self.hunterWin + 1}/10)')
                    self.hunterWin += 1
                    agent.hunterWin += 1 
                    
                    if metrics:
                        metrics.update_step(cfg.CAUGHT_BY_HUNTER) 
                        metrics.record_outcome('died')
                    
                    if self.hunterWin >= 10:
                        self.handle_level_progression()
                        return

                    self.reset_positions(agent)
                    break

    def handle_level_progression(self):
        global TRIGGER_NEXT_LEVEL
        current_title = self.world.display.title
        
        # Level 1 to Level 2
        if "Level 1" in current_title:
            print("\n>>> LEVEL 1 CLEARED! ADVANCING TO LEVEL 2... <<<\n")
            save_progress()
            TRIGGER_NEXT_LEVEL = 2
            self.world.display.root.destroy()
            
        # Level 2 to Level 3
        elif "Level 2" in current_title:
            print("\n>>> LEVEL 2 CLEARED! UNLOCKING BOSS MODE (LEVEL 3)... <<<\n")
            save_progress()
            TRIGGER_NEXT_LEVEL = 3
            self.world.display.root.destroy()

        # Level 3 to Level 4
        elif "Level 3" in current_title:
            print("\n>>> LEVEL 3 CLEARED! ENTERING CHAOS MODE (LEVEL 4)... <<<\n")
            save_progress()
            TRIGGER_NEXT_LEVEL = 4
            self.world.display.root.destroy()
        
        # Level to Finish
        elif "Level 4" in current_title:
            print("\n>>> LEVEL 4 CLEARED! YOU ARE THE ULTIMATE HUNTER! <<<\n")
            save_progress()
            TRIGGER_NEXT_LEVEL = 0
            self.world.display.root.destroy()
        
        else:
            print("Round cleared!")
            self.reset_positions(self.cell.agents[0])

    def reset_positions(self, rabbit_agent):
        self.cell = pick_random_location(self.world)
        rabbit_agent.cell = pick_random_location(self.world)
        rabbit_agent.lastState = None
        rabbit_agent.lastAction = None
        rabbit_agent.skip_turn = True
        self.world.display.redraw()

world = None
hunter = None
rabbit = None
carrot = None
metrics = None

def key_press(event):
    key = event.keysym
    direction_map = {'Up': 0, 'Right': 1, 'Down': 2, 'Left': 3}
    if key in direction_map and hunter:
        hunter.set_move(direction_map[key])
    if world and world.display.root:
        world.display.root.after(1, game_step)

def game_step():
    if world:
        world.update(rabbit.rabbitWin, hunter.hunterWin)

def on_close():
    print("Ending simulation...")
    # If user closes window manually, do not trigger next level
    global TRIGGER_NEXT_LEVEL
    TRIGGER_NEXT_LEVEL = 0 
    save_progress() 
    if world and world.display.root:
        try:
            world.display.root.destroy()
        except:
            pass

def run_game(brain_file, map_file, title_msg):
    global world, hunter, rabbit, carrot, metrics
    
    if not os.path.exists(map_file):
        print(f"Error: Map file {map_file} missing.")
        return

    metrics = TrainingMetrics()
    world = setup.World(filename=map_file, directions=4)
    
    rabbit = Rabbit(brain_file=brain_file, metrics=metrics)
    if brain_file:
        print(f"Brain loaded ({brain_file}): Disabling random exploration (epsilon = 0).")
        rabbit.ai.epsilon = 0
    
    hunter = HumanHunter(filename=map_file)
    carrot = Carrot()
    
    world.add_agent(hunter, cell=pick_random_location(world))
    world.add_agent(rabbit, cell=pick_random_location(world))
    world.add_agent(carrot, cell=pick_random_location(world))
    
    world.display.activate()
    world.display.speed = cfg.speed
    world.display.set_title(title_msg)
    
    world.display.root.bind('<Up>', key_press)
    world.display.root.bind('<Down>', key_press)
    world.display.root.bind('<Left>', key_press)
    world.display.root.bind('<Right>', key_press)
    world.display.root.protocol("WM_DELETE_WINDOW", on_close)

    print(f"Started: {title_msg}")
    world.display.root.mainloop()

if __name__ == '__main__':
    L2_BRAIN = "resources/brain/smart_level2.pkl" 
    L3_BRAIN = "resources/brain/smart_level3.pkl"
    NORMAL_MAP = "resources/world.txt"
    HARD_MAP = "resources/world_level3.txt"

    fallback_brain = get_latest_brain()

    while True:
        TRIGGER_NEXT_LEVEL = 0
        
        print("\n--- MAIN MENU ---")
        print("1. Start Campaign (Level 1 -> 4)")
        print("2. Jump to Level 2")
        print("3. Jump to Level 3")
        print("Q. Quit")
        choice = input("Select Option: ").strip().upper()

        if choice == 'Q':
            break

        current_state = 0
        
        if choice == '1':
            current_state = 1
        elif choice == '2':
            current_state = 2
        elif choice == '3':
            current_state = 3
        else:
            print("Invalid choice.")
            continue

        while current_state > 0:
            
            # Level 1: Fresh Brain, Normal Map
            if current_state == 1:
                print("\n--- LEVEL 1: FRESH BRAIN ---")
                print("Objective: Catch 10 times to unlock Level 2.")
                run_game(None, NORMAL_MAP, "Level 1 - Catch 10 times")
                
                if TRIGGER_NEXT_LEVEL == 2:
                    current_state = 2 
                    TRIGGER_NEXT_LEVEL = 0
                else:
                    current_state = 0 

            # Level 2: Smart Brain, Normal Map
            elif current_state == 2:
                brain_to_use = L2_BRAIN if os.path.exists(L2_BRAIN) else fallback_brain
                print(f"\n--- LEVEL 2: SMART BRAIN ({brain_to_use}) ---")
                print("Objective: Catch 10 times to unlock Level 3.")
                run_game(brain_to_use, NORMAL_MAP, "Level 2 - Catch 10 times")

                if TRIGGER_NEXT_LEVEL == 3:
                    current_state = 3 
                    TRIGGER_NEXT_LEVEL = 0
                else:
                    current_state = 0 

            # Level 3: Boss Brain, Hard Map
            elif current_state == 3:
                brain_to_use = L3_BRAIN if os.path.exists(L3_BRAIN) else fallback_brain
                print(f"\n--- LEVEL 3: BOSS MAZE ({brain_to_use}) ---")
                print("Objective: Catch 10 times to unlock Level 4.")
                run_game(brain_to_use, HARD_MAP, "Level 3 - BOSS MAZE")
                
                if TRIGGER_NEXT_LEVEL == 4:
                    current_state = 4
                    TRIGGER_NEXT_LEVEL = 0
                else:
                    current_state = 0

            # Level 4: Random Brain, Hard Map
            elif current_state == 4:
                random_brain = get_random_brain_file()
                print(f"\n--- LEVEL 4: CHAOS MODE (Random Brain: {random_brain}) ---")
                print("Objective: Final Challenge.")
                run_game(random_brain, HARD_MAP, "Level 4 - Random Brain Challenge")
                
                current_state = 0

        print("Returning to Main Menu...")
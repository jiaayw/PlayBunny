# interactive_demo.py
import tkinter as tk
import importlib
import datetime
import os
import glob
import setup
import config as cfg
from metrics_viz import TrainingMetrics

# Import Shared Logic
from agents import Rabbit, Carrot, pick_random_location

importlib.reload(setup)
importlib.reload(cfg)

# --- Global Flag for Level 3 Transition ---
TRIGGER_LEVEL_3 = False

# --- Helpers ---
def get_latest_brain():
    directory = "resources/brain"
    if not os.path.exists(directory): return None
    list_of_files = glob.glob(f'{directory}/*.pkl') 
    if not list_of_files: return None
    return max(list_of_files, key=os.path.getctime)

# --- NEW: Centralized Save Function ---
def save_progress():
    """Saves brain, data, and plots. Called on close OR transition."""
    print("Saving current session...")
    
    # 1. Save Brain
    directory = "resources/brain"
    if not os.path.exists(directory): os.makedirs(directory)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{directory}/rabbit_brain_{timestamp}.pkl"
    
    if rabbit and hasattr(rabbit, 'ai'):
        rabbit.ai.save_brain(filename)
    
    # 2. Save Metrics (Data & Plots)
    if metrics:
        metrics.save_data_to_file("resources/data")
        metrics.plot(save_dir="resources/play")

class HumanHunter(setup.Agent):
    def __init__(self, filename):
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
                    print('Hunter caught rabbit!')
                    self.hunterWin += 1
                    
                    # Update Rabbit stats for visual title
                    agent.hunterWin += 1 
                    
                    # Metrics
                    metrics.update_step(cfg.CAUGHT_BY_HUNTER) 
                    metrics.record_outcome('died')
                    
                    # --- 3. AUTO-GO TO LEVEL 3 ---
                    if self.hunterWin >= 10 and "level3" not in self.world.filename:
                        print("\n>>> LEVEL 3 UNLOCKED! ENTERING BOSS MODE... <<<\n")
                        
                        # FIX: Save Level 2 progress before switching!
                        save_progress()
                        
                        global TRIGGER_LEVEL_3
                        TRIGGER_LEVEL_3 = True
                        self.world.display.root.destroy()
                        return

                    self.reset_positions(agent)
                    break

    def reset_positions(self, rabbit_agent):
        self.cell = pick_random_location(self.world)
        rabbit_agent.cell = pick_random_location(self.world)
        rabbit_agent.lastState = None
        rabbit_agent.lastAction = None
        rabbit_agent.skip_turn = True
        self.world.display.redraw()

# --- Globals ---
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
    save_progress() # Use the helper function
    
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
    # --- CONFIG ---
    CUSTOM_BRAIN_FILE = "resources/brain/rabbit_brain_20251123-152318.pkl" 
    # --------------

    smart_brain = CUSTOM_BRAIN_FILE
    if smart_brain is None or not os.path.exists(smart_brain):
        smart_brain = get_latest_brain()

    while True:
        TRIGGER_LEVEL_3 = False
        
        print("\n--- MAIN MENU ---")
        print("1. Level 1 (Fresh Brain)")
        print("2. Level 2 (Smart Brain)")
        print("Q. Quit")
        choice = input("Select Level: ").strip().upper()

        if choice == 'Q':
            break

        selected_brain = None
        if choice == '2':
            selected_brain = smart_brain
            if not selected_brain:
                print("No smart brain found. Using Fresh.")
        
        run_game(selected_brain, 'resources/world.txt', f"Level {choice}")

        if TRIGGER_LEVEL_3:
            hard_map = "resources/world_level3.txt"
            run_game(smart_brain, hard_map, "LEVEL 3")
            print("Returning to Menu...")
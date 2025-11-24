# escapeBunny.py
import setup
import config as cfg
import importlib
import os
import datetime
import time
from metrics_viz import TrainingMetrics

# Import optimized agents
from agents import Rabbit, Hunter, Carrot, pick_random_location

importlib.reload(setup)
importlib.reload(cfg)

if __name__ == '__main__':
    LOAD_FILE = None

    # --- 1. PERFORMANCE SETTING ---
    RENDER = True

    # 1. Setup Metrics
    metrics = TrainingMetrics()

    # 2. Setup Agents
    rabbit = Rabbit(brain_file=LOAD_FILE, metrics=metrics)
    hunter = Hunter(filename='resources/world.txt')
    carrot = Carrot()
    
    # 3. Setup World
    world = setup.World(filename='resources/world.txt', directions=4)
    world.add_agent(rabbit, cell=pick_random_location(world))
    world.add_agent(carrot, cell=pick_random_location(world))
    world.add_agent(hunter, cell=pick_random_location(world))

    if RENDER:
        world.display.activate()
        world.display.speed = cfg.speed

    print(f"Training started. Render Mode: {RENDER}")
    print("Press 'Ctrl + C' in the terminal to stop and save.")

    # --- ADDED: Step counter for logging ---
    total_steps = 0 

    try:
        while True:
            world.update(rabbit.rabbitWin, rabbit.hunterWin)
            
            if RENDER:
                if hasattr(world, "display") and not world.display.activated:
                    print("Display deactivated.")
                    break
            else:
                time.sleep(0.01)
                # --- VISUALIZE PROCESS IN CONSOLE ---
                total_steps += 1
                # Print progress every 1000 steps so you know it's working
                if total_steps % 100 == 0:
                    print(f"Training... Step: {total_steps} | Carrots: {rabbit.rabbitWin} | Deaths: {rabbit.hunterWin}")

    except KeyboardInterrupt:
        # This runs when you press Ctrl+C
        print("\n\nStopping training...")

    # Save Logic
    print("Saving progress...")
    directory = "resources/brain"
    if not os.path.exists(directory): os.makedirs(directory)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{directory}/rabbit_brain_{timestamp}.pkl"
    
    if hasattr(rabbit, 'ai'):
        rabbit.ai.save_brain(filename)

    metrics.save_data_to_file("resources/data")
    metrics.plot(save_dir="resources/train")
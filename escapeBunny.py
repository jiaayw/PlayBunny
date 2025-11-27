# escapeBunny.py
import setup
import config as cfg
import importlib
import os
import datetime
from metrics_viz import TrainingMetrics
import time

# Import optimized agents
from agents import Rabbit, Hunter, Carrot, pick_random_location

importlib.reload(setup)
importlib.reload(cfg)

if __name__ == '__main__':
    LOAD_FILE = None

    # --- 1. PERFORMANCE SETTING ---
    # Set to False to train at max speed (Invisible).
    # Set to True to watch the game (Normal speed).
    RENDER = True

    # 1. Setup Metrics
    metrics = TrainingMetrics()

    # 2. Setup Agents (Pass metrics to Rabbit)
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

    total_steps = 0
    try:
        while True:
            world.update(rabbit.rabbitWin, rabbit.hunterWin)
        
            if RENDER:
                if hasattr(world, "display") and not world.display.activated:
                    print("Display deactivated.")
                    break
            else:
                # Stop after specific number of steps if invisible
                # (e.g., stop after 5000 episodes or manually via Ctrl+C)
                # For now, we rely on Ctrl+C to stop in console
                time.sleep(0.008)
                total_steps += 1
                # Print progress every 100 steps (more frequent since we slowed it down)
                if total_steps % 500 == 0:
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
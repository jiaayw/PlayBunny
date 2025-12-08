import matplotlib.pyplot as plt
import os
import numpy as np
import json
import datetime

class TrainingMetrics:
    """
    Track how 'smart' the rabbit becomes over time.

    We log:
    1. Rolling Success Rate (Last 50 Games):
    Example: In the last 50 lives, did it eat carrot or die?
    Goal: This line should go up (from 0% to 50%+) as it learns.
    2. Steps Per Carrot (Efficiency):
    How many steps did it take to find the carrot?
    Goal: This line should go down. A smart rabbit takes the shortest path.
    Note: If it takes 500 steps to find one carrot, it's just wandering randomly.
    3. Total Reward per Episode:
    The sum of all points (Movement -1, Carrot +50, Death -100) in one life.
    Goal: Should trend upwards from negative to positive.
    """

    def __init__(self, log_every=1):
        self.log_every = log_every
        self.episodes = []        
        self.episode_rewards = [] 
        self.outcomes = []        # 1 = Carrot, 0 = Died
        self.steps_to_carrot = [] 
        
        self.current_life_reward = 0
        self.current_life_steps = 0

        # Style settings
        plt.style.use('ggplot') 

    def update_step(self, reward):
        self.current_life_reward += reward
        self.current_life_steps += 1

    def record_outcome(self, outcome_type):
        if outcome_type == 'carrot':
            self.outcomes.append(1)
            self.steps_to_carrot.append(self.current_life_steps)
            self.current_life_steps = 0 
        elif outcome_type == 'died':
            self.outcomes.append(0)
            self.episodes.append(len(self.episodes) + 1)
            self.episode_rewards.append(self.current_life_reward)
            self.current_life_reward = 0
            self.current_life_steps = 0

    def save_data_to_file(self, directory="resources/data"):
        """Saves raw metrics data to JSON files."""
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        
        data = {
            "outcomes": self.outcomes,
            "episode_rewards": self.episode_rewards,
            "steps_to_carrot": self.steps_to_carrot
        }
        
        filename = f"{directory}/metrics_{timestamp}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Raw data saved to: {filename}")
        except Exception as e:
            print(f"Error saving data: {e}")

    def _save_plot(self, data, title, ylabel, color, filename, window=50, fill=False):
        if not data: return

        plt.figure(figsize=(10, 6), dpi=100)
        
        # plot raw data faintly
        plt.plot(data, color=color, alpha=0.25, linewidth=1, label='Raw')
        
        # plot smoothed trend
        if len(data) >= window:
            
            smooth = np.convolve(data, np.ones(window)/window, mode='valid')
            x_axis = range(window - 1, len(data))
            plt.plot(x_axis, smooth, color=color, linewidth=2.5, label=f'Trend ({window} avg)')
            
            if fill:
                plt.fill_between(x_axis, smooth, color=color, alpha=0.1)

        plt.title(title, fontsize=14, fontweight='bold', color='#333333')
        plt.xlabel("Episodes", fontsize=11)
        plt.ylabel(ylabel, fontsize=11)
        plt.legend(frameon=True, facecolor='white', framealpha=0.8)
        plt.tight_layout()
        
        plt.savefig(filename)
        plt.close()
        print(f"Plot saved: {filename}")

    def plot(self, save_dir=None):
        if save_dir is not None:
            os.makedirs(save_dir, exist_ok=True)

        if self.outcomes:
            # Calculate rolling success rate
            window = 50
            rates = []
            for i in range(len(self.outcomes)):
                start = max(0, i - window)
                chunk = self.outcomes[start:i+1]
                rates.append(sum(chunk) / len(chunk))
            
            # For success rate, we calculate 'rates' manually above to be same length as outcomes,
            # so we use a small window=1 for smoothing or just rely on the calculation above.
            # To keep it simple and use the smoothing visualizer:
            self._save_plot(rates, "Success Rate (Survival + Carrot)", "Rate (0.0 - 1.0)", 
                            '#2ecc71', os.path.join(save_dir, "1_success_rate.png"), window=10, fill=True)

        if self.steps_to_carrot:
            self._save_plot(self.steps_to_carrot, "Efficiency (Steps to find Carrot)", "Steps", 
                            '#3498db', os.path.join(save_dir, "2_efficiency.png"), window=20)

        if self.episode_rewards:
            self._save_plot(self.episode_rewards, "Cumulative Reward per Episode", "Total Score", 
                            '#9b59b6', os.path.join(save_dir, "3_total_rewards.png"), window=20, fill=True)
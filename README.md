# Play Bunny: Reinforcement Learning Game

A grid-based survival game where an AI Rabbit learns to survive and eat carrots while being chased by a Hunter. This project demonstrates **Tabular Q-Learning** in a discrete 2D environment, featuring an adversary using **A* Pathfinding**.

## Game Modes

### 1. Training Mode (AI vs AI)
*   **Script:** `escapeBunny.py`
*   **Description:** The Rabbit plays against an A* Hunter thousands of times to learn strategies.
*   **Headless Mode:** Can run without graphics (`RENDER = False`) for ultra-fast training.
*   **Output:** Saves the learned "Brain" (Q-Table) to `resources/brain/` and training metrics to `resources/train/`.

### 2. Interactive Demo (Human vs AI)
*   **Script:** `interactive_demo.py`
*   **Description:** You play as the Hunter! Use arrow keys to catch the AI Rabbit.
*   **Levels:**
    *   **Level 1:** Play against a "Fresh" (Dumb) Rabbit.
    *   **Level 2:** Play against a "Smart" Rabbit (loads a trained brain).
    *   **Level 3 (Boss Mode):** Unlocked by catching the rabbit 10 times. Features a harder maze map.

## Installation & Setup

### Prerequisites
*   Python 3.x
*   `tkinter` (Usually included with Python)
*   `matplotlib` (For generating metric plots)
*   `numpy`

##  How to Run

### To Train the AI
1.  Open `escapeBunny.py`.
2.  Adjust settings if desired (e.g., set `RENDER = True` to watch, or `False` for fast training).
3.  Run the script:
    ```bash
    python escapeBunny.py
    ```
4.  The Q-Table is saved automatically upon closing the window (or interrupting the script).

### To Play the Game
1.  Run the demo script:
    ```bash
    python interactive_demo.py
    ```
2.  Follow the on-screen menu:
    *   Press **1** for Level 1 (Easy).
    *   Press **2** for Level 2 (Hard - uses trained brain).
3.  **Controls:** Use **Arrow Keys** ⬆️⬇️⬅️➡️ to move the Hunter.
4.  **Objective:** Catch the rabbit! If you catch it 10 times, you unlock the secret Boss Level.

## Technical Details

### The Agent (Rabbit)
*   **Algorithm:** Tabular Q-Learning.
*   **State Space:**
    1.  **Surroundings:** Walls in the 8 neighboring cells.
    2.  **Hunter Radar:** Relative direction of the Hunter (-1, 0, 1).
    3.  **Carrot Radar:** Relative direction of the Carrot (-1, 0, 1).
*   **Actions:** Move Up, Down, Left, Right.
*   **Rewards:**
    *   Move: `-1` (Penalty for wasting time)
    *   Eat Carrot: `+50`
    *   Caught by Hunter: `-100`

### The Adversary (Hunter)
*   Uses **A* (A-Star) Pathfinding** with Manhattan distance heuristic.
*   Always calculates the shortest optimal path to the Rabbit.
*   Moves every turn (unless in Human mode).

### Visualizations
The system logs performance data to `resources/data/` and generates plots in `resources/train/` or `resources/play/`:
*   **Success Rate:** Rolling average of Survival + Eating Carrots.
*   **Efficiency:** Steps taken to find a carrot.
*   **Total Reward:** Cumulative score per episode.
import random
import setup
import qlearn
import config as cfg
import os
import heapq

def pick_random_location(world):
    while 1:
        x = random.randrange(world.width)
        y = random.randrange(world.height)
        cell = world.get_cell(x, y)
        if not (cell.wall or len(cell.agents) > 0):
            return cell

class Carrot(setup.Agent):
    def __init__(self):
        self.image_file = cfg.carrot_img
    
    def update(self):
        pass

class Hunter(setup.Agent):
    def __init__(self, filename):
        self.cell = None
        self.hunterWin = 0
        self.image_file = cfg.hunter_img
        
        self.move = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        with open(filename, "r") as f:
            lines = f.readlines()
        lines = [x.rstrip() for x in lines]
        self.fh = len(lines)
        self.fw = max([len(x) for x in lines])
        self.grid_list = [[1 for x in range(self.fw)] for y in range(self.fh)]

        for y in range(self.fh):
            line = lines[y]
            for x in range(min(self.fw, len(line))):
                t = 1 if (line[x] == 'X') else 0
                self.grid_list[y][x] = t
        print ('hunter init success......')

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def astar_move(self, target):
        if self.cell == target: return

        start = (self.cell.y, self.cell.x)
        goal = (target.y, target.x)
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        best_move = None

        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                curr = current
                path = []
                while curr in came_from:
                    path.append(curr)
                    curr = came_from[curr]
                path.reverse()
                if len(path) > 0:
                    next_y, next_x = path[0]
                    best_move = self.world.grid[next_y][next_x]
                break

            for i in range(4):
                ny, nx = current[0] + self.move[i][0], current[1] + self.move[i][1]
                # boundary Check
                if nx < 0 or ny < 0 or nx >= self.world.width or ny >= self.world.height: continue
                if self.grid_list[ny][nx] == 1: continue

                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get((ny, nx), float('inf')):
                    came_from[(ny, nx)] = current
                    g_score[(ny, nx)] = tentative_g
                    f = tentative_g + self.heuristic((ny, nx), goal)
                    f_score[(ny, nx)] = f
                    heapq.heappush(open_set, (f, (ny, nx)))

        if best_move:
            self.cell = best_move
        else:
            valid_moves = []
            for i in range(4):
                dx, dy = self.move[i]
                nx, ny = self.cell.x + dx, self.cell.y + dy
                if 0 <= nx < self.world.width and 0 <= ny < self.world.height:
                     if not self.world.get_cell(nx, ny).wall:
                         valid_moves.append(i)
            if valid_moves:
                self.go_direction(random.choice(valid_moves))

    def update(self):
        rabbit_cell = None
        for a in self.world.agents:
            if isinstance(a, Rabbit):
                rabbit_cell = a.cell
                break
        if rabbit_cell and self.cell != rabbit_cell:
            self.astar_move(rabbit_cell)

class Rabbit(setup.Agent):
    def __init__(self, brain_file=None, metrics=None):
        self.ai = None
        self.ai = qlearn.QLearn(actions=range(4), alpha=0.1, gamma=0.9, epsilon=0.1)
        self.hunterWin = 0
        self.rabbitWin = 0
        self.lastState = None
        self.lastAction = None
        self.image_file = cfg.rabbit_img
        self.skip_turn = False 
        self.metrics = metrics 
        
        if brain_file and os.path.exists(brain_file):
            self.ai.load_brain(brain_file)
        else:
            print('No brain loaded, starting fresh.')

    def _check_collision_and_die(self, state, reward):
        caught = False
        hunter_agent = None
        
        # check if agent is an instance of Hunter class
        for agent in self.cell.agents:
            if isinstance(agent, Hunter):
                self.hunterWin += 1
                reward = cfg.CAUGHT_BY_HUNTER
                caught = True
                hunter_agent = agent
                break
        
        if caught:
            if self.lastState is not None:
                self.ai.learn(self.lastState, self.lastAction, state, reward)
            
            if self.metrics:
                self.metrics.update_step(reward)
                self.metrics.record_outcome('died')
            
            self.lastState = None
            
            self.cell = pick_random_location(self.world)
            if hunter_agent:
                hunter_agent.cell = pick_random_location(self.world)
                
            self.skip_turn = True 
            
            if hasattr(self.world, 'display') and self.world.display:
                self.world.display.redraw()
            return True
        return False

    def update(self):
        if self.skip_turn:
            self.skip_turn = False
            return

        state = self.calculate_state()
        reward = cfg.MOVE_REWARD

        if self._check_collision_and_die(state, reward): return

        found_carrot = False
        target_carrot = None
        for agent in self.cell.agents:
            if isinstance(agent, Carrot):
                found_carrot = True
                target_carrot = agent
                break

        if found_carrot:
            self.rabbitWin += 1
            total_reward = reward + cfg.EAT_CARROT
            target_carrot.cell = pick_random_location(self.world)
            
            if self.metrics:
                self.metrics.update_step(total_reward)
                self.metrics.record_outcome('carrot')
            reward = total_reward 
        else:
            if self.metrics:
                self.metrics.update_step(reward)

        if self.lastState is not None:
            self.ai.learn(self.lastState, self.lastAction, state, reward)

        action = self.ai.choose_action(state)
        
        dx, dy = [(0, -1), (1, 0), (0, 1), (-1, 0)][action]
        next_x = self.cell.x + dx
        next_y = self.cell.y + dy
        
        if 0 <= next_x < self.world.width and 0 <= next_y < self.world.height:
            self.lastState = state
            self.lastAction = action
            self.go_direction(action)
        else:
            self.lastState = state
            self.lastAction = action

        if self._check_collision_and_die(state, reward): return

    def calculate_state(self):
        # immediate surroundings (8 neighbors)
        def cell_value(cell):
            if cell.wall: return 1
            return 0

        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        surroundings = [cell_value(self.world.get_relative_cell(self.cell.x + d[0], self.cell.y + d[1])) for d in dirs]

        # radar, search for the hunter
        hunter_dx, hunter_dy = 0, 0
        closest_dist = 9999
        
        for agent in self.world.agents:
             if isinstance(agent, Hunter):
                 dx = agent.cell.x - self.cell.x
                 dy = agent.cell.y - self.cell.y
                 dist = abs(dx) + abs(dy)
                 if dist < closest_dist:
                     closest_dist = dist
                     hunter_dx = -1 if dx < 0 else (1 if dx > 0 else 0)
                     hunter_dy = -1 if dy < 0 else (1 if dy > 0 else 0)
        
        # rader, search the carrot
        carrot_dx, carrot_dy = 0, 0
        for agent in self.world.agents:
            if isinstance(agent, Carrot):
                dx = agent.cell.x - self.cell.x
                dy = agent.cell.y - self.cell.y
                carrot_dx = -1 if dx < 0 else (1 if dx > 0 else 0)
                carrot_dy = -1 if dy < 0 else (1 if dy > 0 else 0)
                break 
        
        return tuple(surroundings + [hunter_dx, hunter_dy, carrot_dx, carrot_dy])
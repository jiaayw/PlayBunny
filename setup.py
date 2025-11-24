# coding:utf-8

import time
import tkinter as tk
import random
import config as cfg

class Cell:
    def __init__(self):
        self.wall = False

    # def color(self):
    #     if self.wall:
    #         return cfg.wall_color
    #     else:
    #         return 'white'

    def load(self, data):
        if data == 'X':
            self.wall = True
        else:
            self.wall = False

    def __getattr__(self, key):
        if key == 'neighbors':
            opts = [self.world.get_next_grid(self.x, self.y, dir) for dir in range(self.world.directions)]
            next_states = tuple(self.world.grid[y][x] for (x, y) in opts)
            return next_states
        raise AttributeError(key)


class Agent:
    def __setattr__(self, key, value):
        if key == 'cell':
            old = self.__dict__.get(key, None)
            if old is not None:
                old.agents.remove(self)
            if value is not None:
                value.agents.append(self)
        self.__dict__[key] = value

    def go_direction(self, dir):
        target = self.cell.neighbors[dir]
        if getattr(target, 'wall', False):
            return False
        self.cell = target
        return True


class World:
    def __init__(self, cell=None, directions=cfg.directions, filename=None):
        if cell is None:
            cell = Cell
        self.Cell = cell
        self.directions = directions
        self.filename = filename

        self.grid = None
        self.agents = []
        self.step = 0

        self.height = None
        self.width = None
        self.get_file_size(filename)

        self.rabbitWin = None
        self.hunterWin = None
        
        self.reset()
        self.load(filename)
        
        # Initialize display LAST
        self.display = make_display(self)

    def get_file_size(self, filename):
        if filename is None:
            raise Exception("world file not exist!")

        with open(filename, "r") as f:
            data = f.readlines()

        if self.height is None:
            self.height = len(data)

        if self.width is None:
            self.width = max(len(x.rstrip()) for x in data)

    def reset(self):
        self.grid = [[self.make_cell(i, j) for i in range(self.width)] for j in range(self.height)]
        self.agents = []
        self.step = 0

    def make_cell(self, x, y):
        c = self.Cell()
        c.x = x
        c.y = y
        c.world = self
        c.agents = []
        return c

    def get_cell(self, x, y):
        return self.grid[y][x]

    def get_relative_cell(self, x, y):
        # Keep wrapping for Vision (optional), or make strict. 
        # Currently keeping as is for "calculate_state" logic.
        return self.grid[y % self.height][x % self.width]

    def load(self, f):
        if not hasattr(self.Cell, 'load'):
            return

        if isinstance(f, str):
            f = open(f, "r")

        with f:
            lines = f.readlines()

        lines = [x.rstrip() for x in lines]
        fh = len(lines)
        fw = max(len(x) for x in lines)

        if fh > self.height: fh = self.height
        start_y = (self.height - fh) // 2
        if fw > self.width: fw = self.width
        start_x = (self.width - fw) // 2

        self.reset()
        for j in range(fh):
            line = lines[j]
            for i in range(min(fw, len(line))):
                self.grid[start_y + j][start_x + i].load(line[i])

    def update(self, rabbit_win=None, hunter_win=None):
        for a in self.agents:
            a.update()
        
        if self.display:
            self.display.redraw()
            self.display.update()

        if rabbit_win:
            self.rabbitWin = rabbit_win
        if hunter_win:
            self.hunterWin = hunter_win
        self.display.update()
        self.step += 1

    def get_next_grid(self, x, y, dir):
        dx = 0
        dy = 0
        if self.directions == 8:
            dx, dy = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)][dir]
        elif self.directions == 4:
            dx, dy = [(0, -1), (1, 0), (0, 1), (-1, 0)][dir]
        
        x2 = x + dx
        y2 = y + dy

        # --- OPTIMIZATION: STRICT BOUNDARY CHECK ---
        # Prevents wrapping around the screen (teleporting)
        if x2 < 0 or x2 >= self.width or y2 < 0 or y2 >= self.height:
            return x, y
        
        return x2, y2

    def add_agent(self, agent, x=None, y=None, cell=None, dir=None):
        self.agents.append(agent)
        if cell is not None:
            x = cell.x
            y = cell.y
        if x is None:
            x = random.randrange(self.width)
        if y is None:
            y = random.randrange(self.height)
        if dir is None:
            dir = random.randrange(self.directions)

        agent.cell = self.grid[y][x]
        agent.dir = dir
        agent.world = self


# GUI display
class TkinterDisplay:
    def __init__(self, size=cfg.grid_width):
        self.activated = False
        self.paused = False
        self.title = ''
        self.updateEvery = 1
        self.root = None
        self.speed = cfg.speed
        self.bg = None
        self.size = size
        self.frameWidth = 0
        self.frameHeight = 0
        self.world = None
        self.canvas = None # Use Canvas instead of Image Label
        self.image_cache = {} # <--- 1. Initialize Cache Dictionary

    def activate(self):
        if self.root is None:
            self.root = tk.Tk()

        for c in self.root.winfo_children():
            c.destroy()

        self.activated = True
        self.frameWidth  = self.world.width * self.size
        self.frameHeight = self.world.height * self.size
        self.root.geometry(f"{self.frameWidth}x{self.frameHeight}")

        # --- OPTIMIZATION: Use Canvas for rendering ---
        self.canvas = tk.Canvas(self.root, width=self.frameWidth, height=self.frameHeight, bg='white')
        self.canvas.pack()
        
        self.redraw()
        self.root.bind("<Escape>", self.quit)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

    def quit(self, event=None):
        self.activated = False
        try:
            self.root.destroy()
        except tk.TclError:
            pass
        finally:
            self.root = None

    def update(self):
        if not self.activated:
            return
        if self.world.step % self.updateEvery != 0 and not self.paused:
            return
        
        self.set_title(self.title)
        try:
            self.root.update()
        except tk.TclError:
            self.activated = False
        
        if self.speed > 0:
            time.sleep(float(1)/self.speed)

    def make_title(self, world):
        text = 'step: %d' % world.step
        extra = []
        if world.rabbitWin:
            extra.append('rabbitWin=%d' % world.rabbitWin)
        if world.hunterWin:
            extra.append('hunterWin=%d' % world.hunterWin)
        if world.display.paused:
            extra.append('paused')
        if world.display.speed > 0:
            extra.append('speed=%dm/s' % world.display.speed)

        if len(extra) > 0:
            text += ' [%s]' % ', '.join(extra)
        return text

    def set_title(self, title):
        if not self.activated:
            return
        self.title = title
        title += ' %s' % self.make_title(self.world)
        if self.root.title() != title:
            self.root.title(title)

    def pause(self, event=None):
        self.paused = not self.paused
        while self.paused:
            self.update()

    def redraw(self):
        if not self.activated:
            return
        
        # Clear canvas
        try:
            self.canvas.delete("all")

            if hasattr(cfg, 'wall_img') and cfg.wall_img not in self.image_cache:
                try:
                    self.image_cache[cfg.wall_img] = tk.PhotoImage(file=cfg.wall_img)
                except:
                    self.image_cache[cfg.wall_img] = None

        # Draw only necessary items
            for y in range(self.world.height):
                for x in range(self.world.width):
                    cell = self.world.grid[y][x]

                    if len(cell.agents) == 0 and not cell.wall:
                        continue

                # If empty and no wall, skip drawing (black background)
                    x1 = x * self.size
                    y1 = y * self.size
                    x2 = x1 + self.size
                    y2 = y1 + self.size

                    if cell.wall:
                        # Try to draw image
                        if hasattr(cfg, 'wall_img') and self.image_cache.get(cfg.wall_img):
                             self.canvas.create_image(x1 + self.size/2, y1 + self.size/2, image=self.image_cache[cfg.wall_img])
                        
                    if len(cell.agents) > 0:
                            agent = cell.agents[-1]
                            if hasattr(agent, 'image_file') and agent.image_file:
                                # 2. Load Image if not in cache
                                if agent.image_file not in self.image_cache:
                                    try:
                                        # Load the image
                                        photo = tk.PhotoImage(file=agent.image_file)
                                        self.image_cache[agent.image_file] = photo
                                    except Exception as e:
                                        print(f"Error loading image: {e}")
                                        self.image_cache[agent.image_file] = None # Mark as failed
                            
                                photo = self.image_cache[agent.image_file]
                                if photo:
                                    # Center the image in the cell
                                    center_x = x * self.size + (self.size / 2)
                                    center_y = y * self.size + (self.size / 2)
                                    self.canvas.create_image(center_x, center_y, image=photo)
                                else:
                                    # Fallback to square if image failed
                                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='black', outline="")
                            else:
                                # Normal Square Agent
                                self.canvas.create_rectangle(x1, y1, x2, y2, fill='black', outline="")
        except tk.TclError:
            self.activated = False

    
def make_display(world):
    d = TkinterDisplay()
    d.world = world
    return d
"""
Pac-Man clone.
"""

import random
import sturm

with open('glutton.maze') as f:
    maze = f.read().splitlines()[1:]

def main():
    with sturm.cbreak_mode():
        run()

dbg_log = []
dbg = dbg_log.append

def run():
    grid = [list(line) for line in maze]
    glutton = Agent('<', find_glutton(maze))
    glutton.place_on(grid)
    ghosts = [make_ghost(grid) for _ in range(4)]
    while True:
        sturm.render(view(grid), [(' ', x) for x in dbg_log])
        dbg_log[:] = []
        key = sturm.get_key(0.1)
        if key == sturm.esc: break
        elif key == 'left':  glutton.face('>', left)
        elif key == 'right': glutton.face('<', right)
        elif key == 'up':    glutton.face('V', up)
        elif key == 'down':  glutton.face('^', down)
        glutton.act(grid)
        for ghost in ghosts:
            ghost.act(grid)

left    = -1,  0
right   =  1,  0
up      =  0, -1
down    =  0,  1
stopped =  0,  0

headings = (left, right, up, down)

def find_glutton(maze):
    for y, line in enumerate(maze):
        if 'P' in line:
            return line.index('P'), y
    assert False

def make_ghost(grid):
    while True:
        x, y = (random.randint(0, len(grid[0])-1),
                random.randint(0, len(grid)-1))
        if grid[y][x] in '.':
            ghost = Ghost((x, y))
            ghost.place_on(grid)
            return ghost

class Agent(object):
    def __init__(self, glyph, p):
        self.p = p
        self.v = stopped
        self.heading = stopped
        self.glyph = glyph

    def place_on(self, grid):
        x, y = self.p
        grid[y][x] = self.glyph

    def face(self, glyph, heading):
        self.glyph = glyph
        self.heading = heading

    def act(self, grid):
        self.move(grid, self.heading) or self.move(grid, self.v)

    def move(self, grid, (dx, dy)):
        x, y = self.p
        x2, y2 = (x+dx) % len(grid[0]), (y+dy) % len(grid)
        if grid[y2][x2] in ' .o':
            self.step(grid, x2, y2)
            self.v = dx, dy
            return True
        else:
            return False

    def step(self, grid, x2, y2):
        x, y = self.p
        grid[y2][x2] = self.glyph
        grid[y][x] = ' '
        self.p = x2, y2

class Ghost(Agent):
    def __init__(self, p):
        Agent.__init__(self, 'G', p)
        self.upon = '.'
        self.heading = random.choice(headings)

    def act(self, grid):
        if random.random() < 0.1:
            self.heading = random.choice(headings)
        Agent.act(self, grid)

    def step(self, grid, x2, y2):
        x, y = self.p
        grid[y2][x2], grid[y][x], self.upon = self.glyph, self.upon, grid[y2][x2]
        self.p = x2, y2

def view(grid):
    for row in grid:
        for i, c in enumerate(row):
            yield color(c)
            sep = ' -'[i+1<len(row) and is_wall(c) and is_wall(row[i+1])]
            yield color(sep)
        yield '\n'

def is_wall(c): return c not in ' .o<>V^G'

def color(c):
    return block if is_wall(c) else sturm.yellow(c) if c in '<>V^' else c

block = sturm.on_blue(' ')

if __name__ == '__main__':
    main()

"""
A Pac-Man clone.
"""

import random, time
import sturm

with open('glutton.maze') as f:
    maze = f.read().splitlines()[1:]

def main():
    with sturm.cbreak_mode():
        run()

dbg_log = []
dbg = dbg_log.append

tick_interval = 1./10

def run():
    grid = [list(line) for line in maze]
    glutton = Agent('<', find_glutton(maze))
    glutton.place_on(grid)
    ghosts = [make_ghost(grid) for _ in range(4)]
    for _ in ticking():
        sturm.render(view(grid, ghosts),
                     [(' ', x) for x in dbg_log])
        dbg_log[:] = []
        key = sturm.get_key(tick_interval)
        if key == sturm.esc: break
        elif key == 'left':  glutton.face('>', left)
        elif key == 'right': glutton.face('<', right)
        elif key == 'up':    glutton.face('V', up)
        elif key == 'down':  glutton.face('^', down)
        glutton.act(grid)
        for ghost in ghosts:
            ghost.act(grid)

def ticking():
    tick = time.time()
    while True:
        yield
        now = time.time()
        tick = max(now, tick + tick_interval)
        time.sleep(tick - now)

left    = -1,  0
right   =  1,  0
up      =  0, -1
down    =  0,  1
stopped =  0,  0

headings = (left, right, up, down)

def find_glutton(maze):
    return next(find(maze, 'P'))

def make_ghost(grid):
    return Ghost(random.choice(list(find(grid, '.'))))

def find(grid, glyph):
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c == glyph:
                yield x, y

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
        self.heading = random.choice(headings)

    def act(self, grid):
        if random.random() < 0.1:
            self.heading = random.choice(headings)
        Agent.act(self, grid)

    def step(self, grid, x2, y2):
        self.p = x2, y2

def view(grid, ghosts):
    rows = [list(row) for row in grid]
    for ghost in ghosts:
        x, y = ghost.p
        rows[y][x] = 'G'
    for row in rows:
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

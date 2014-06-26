"""
Pac-Man clone.
"""

import sturm

with open('glutton.maze') as f:
    maze = f.read().splitlines()[1:]

def main():
    with sturm.cbreak_mode():
        run()

def run():
    grid = [list(line) for line in maze]
    x, y = find_glutton(maze)
    glutton = Agent((x, y))
    grid[y][x] = glutton.glyph
    while True:
        sturm.render(view(grid))
        key = sturm.get_key(0.1)
        if key == sturm.esc: break
        elif key == 'left':  glutton.face('>', left)
        elif key == 'right': glutton.face('<', right)
        elif key == 'up':    glutton.face('V', up)
        elif key == 'down':  glutton.face('^', down)
        glutton.act(grid)

left    = -1,  0
right   =  1,  0
up      =  0, -1
down    =  0,  1
stopped =  0,  0

def find_glutton(maze):
    for y, line in enumerate(maze):
        if 'P' in line:
            return line.index('P'), y
    assert False

class Agent(object):
    def __init__(self, p):
        self.p = p
        self.v = stopped
        self.heading = stopped
        self.glyph = '<'
    def face(self, glyph, heading):
        self.glyph = glyph
        self.heading = heading
    def act(self, grid):
        self.move(grid, self.heading) or self.move(grid, self.v)
    def move(self, grid, (dx, dy)):
        x, y = self.p
        x2, y2 = x+dx, y+dy
        if grid[y2][x2] in ' .o': # XXX bounds
            grid[y2][x2] = self.glyph
            grid[y][x] = ' '
            self.p = x2, y2
            self.v = dx, dy
            return True
        else:
            return False

def view(grid):
    for row in grid:
        for i, c in enumerate(row):
            yield color(c)
            sep = ' -'[i+1<len(row) and is_wall(c) and is_wall(row[i+1])]
            yield color(sep)
        yield '\n'

def is_wall(c): return c not in ' .o<>V^'

def color(c):
    return block if is_wall(c) else sturm.yellow(c) if c in '<>V^' else c

block = sturm.on_blue(' ')

if __name__ == '__main__':
    main()

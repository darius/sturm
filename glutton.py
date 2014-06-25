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
        if key == sturm.esc:
            break
        elif key == 'left':
            glutton.toggle_motion('>', left)
        elif key == 'right':
            glutton.toggle_motion('<', right)
        elif key == 'up':
            glutton.toggle_motion('V', up)
        elif key == 'down':
            glutton.toggle_motion('^', down)
        glutton.move(grid)

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
        self.glyph = '<'
    def toggle_motion(self, glyph, v):
        self.glyph = glyph
        self.v = stopped if self.v == v else v
    def move(self, grid):
        x, y = self.p
        dx, dy = self.v
        x2, y2 = x+dx, y+dy
        if grid[y2][x2] in ' .o': # XXX bounds
            grid[y2][x2] = self.glyph
            grid[y][x] = ' '
            self.p = x2, y2
            
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

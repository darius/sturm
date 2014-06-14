"""
https://github.com/darius/sketchbook/blob/master/misc/sokoban.py
refactored, extracting the terminal stuff into a module.

You move yourself (shown as 'i' or 'I') around a 2-d grid. You can
push one crate at a time (each shown as 'o' or '@'). You win when
every crate is on a target square: an empty target appears as '.',
while one with a crate on it is '@'. (You are shown as 'I' when on a
target yourself.) Nothing can move through a wall ('#'). These simple
rules yield an elegant game with scope for a tremendous variety of
puzzles, from easy to AI-complete.

Other console Sokobans display the game a little differently: with
different symbols and a squeezed aspect ratio. I insert spaces between
squares to make them more nearly, y'know, square.

Some other Sokoban implementations you might enjoy:
http://eloquentjavascript.net/chapter13.html (by Marijn Haverbeke)
http://aurelio.net/projects/sedsokoban/ (by Aurelio Marinho Jargas)
http://code.google.com/p/cleese/source/browse/trunk/experimental/necco/kernel/soko.py
(runs without a regular OS, by Dave Long)
"""

import sturm

def main(level_collection, name=''):
    grids = [parse(level) for level in level_collection.split('\n\n')]
    with sturm.cbreak_mode():
        play(grids, name)

# We represent a grid as a list of characters, including the newlines,
# with every line the same length (which we call the width of the
# grid). Thus moving up or down from some square means a displacement
# by that same width, whatever the starting square.

def parse(grid_string):
    lines = grid_string.splitlines()
    assert all(len(line) == len(lines[0]) for line in lines)
    return list(grid_string)

def unparse(grid):
    return ' '.join(grid).replace('\n ', '\n')

def up   (width): return -width
def down (width): return  width
def left (width): return -1
def right(width): return  1
directions = dict(h    = left, j    = down, k  = up, l     = right,
                  left = left, down = down, up = up, right = right)

def play(grids, name='', level=0):
    "The UI to a sequence of Sokoban levels."
    trails = [[] for _ in grids] # The past history for undo for each level.
    while True:
        grid, trail = grids[level], trails[level]

        def frame():
            yield "Move with the arrow keys or HJKL. U to undo."
            yield "N/P for next/previous level; Q to quit."
            yield ""
            yield "Level {} {:^50} Move {}".format(level+1, name, len(trail))
            yield ""
            yield unparse(grid)
            if won(grid):
                yield ""
                yield "Done!"

        sturm.render('\n'.join(frame()) + '\n')
        key = sturm.get_key().lower()
        if   key == 'q':
            break
        elif key == 'n':
            level = (level + 1) % len(grids)
        elif key == 'p':
            level = (level - 1) % len(grids)
        elif key == 'u':
            if trail: grids[level] = trail.pop()
        elif key in directions:
            previously = grid[:]
            push(grid, directions[key])
            if grid != previously: trail.append(previously)

def won(grid): return 'o' not in grid

def push(grid, direction):
    "Update grid, trying to move the player in the direction."
    i = grid.index('i' if 'i' in grid else 'I')
    d = direction(grid.index('\n')+1)
    move(grid, 'o@', i+d, i+d+d) # First push any neighboring crate.
    move(grid, 'iI', i, i+d)     # Then move the player.

def move(grid, thing, here, there):
    "Move thing from here to there if possible."
    # N.B. `there` is always in bounds when `grid[here] in thing`
    # because our grids have '#'-borders, while `thing` is never a '#'.
    if grid[here] in thing and grid[there] in ' .':
        lift(grid, here)
        drop(grid, there, thing)

def lift(grid, i):
    "Remove any thing (crate or player) from position i."
    grid[i] = ' .'[grid[i] in '.@I']

def drop(grid, i, thing):
    "Into a clear square, put thing."
    grid[i] = thing['.' == grid[i]]

# The above two functions each index a string with a boolean value.
# False and True act like 0 and 1, so 'xy'[False] == 'x' and
# 'xy'[True] == 'y'.


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        # Levels from Microban, by David Skinner, from
        # http://sneezingtiger.com/sokoban/levels.html
        # "A good set for beginners and children."
        filename = 'sokoban/microban'
    elif len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        print("Usage: python %s [filename]" % sys.argv[0])

    with open(filename) as f:
        name = f.readline().rstrip('\n')
        collection = f.read()
    main(collection, name)

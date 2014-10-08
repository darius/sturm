"""
A Snake game.
"""

import random, time
import sturm

nrows, ncols = 20, 20
 
def main():
    with sturm.cbreak_mode():
        run()

dbg_log = []
dbg = dbg_log.append

def run():
    global tick_interval
    tick_interval = 1./4

    body = [(10,10), (11,10), (12,10)]
    heading = down
    def face(new_heading):
        return heading if new_heading == negate(heading) else new_heading

    def empties():
        return [(x, y)
                for y in range(1, nrows-1)
                for x in range(1, ncols-1)
                if (x, y) not in body]
    target_x, target_y = random.choice(empties())
    won = False

    for _ in ticking():
        lengthen = False
        grid = map(list,
                   ['#'*ncols] + (['#%*s#' % (ncols-2, '')] * (nrows-2)) + ['#'*ncols])
        grid[target_y][target_x] = '@'
        for x, y in body:
            if grid[y][x] == '@':
                lengthen = True
                targets = empties()
                if not targets:
                    won = True
                else:
                    target_x, target_y = random.choice(targets)
                    tick_interval *= .9
            if grid[y][x] not in ' @':
                raise Exception('Lose')
            grid[y][x] = '*'
        def view():
            for row in grid:
                for i, c in enumerate(row):
                    yield c
                yield '\n'

        sturm.render(view(), [(' ', x) for x in dbg_log])
        dbg_log[:] = []
        if won: break

        key = sturm.get_key(tick_interval)
        if   key == 'Q':     break
        elif key == 'left':  heading = face(left)
        elif key == 'right': heading = face(right)
        elif key == 'up':    heading = face(up)
        elif key == 'down':  heading = face(down)

        if not lengthen: body.pop(0)
        body.append(add(body[-1], heading))

def negate((x, y)):        return (-x, -y)
def add((x, y), (dx, dy)): return (x+dx, y+dy)

def ticking():
    tick = time.time()
    while True:
        yield
        now = time.time()
        tick = max(now, tick + tick_interval)
        #dbg(str(tick - now))
        time.sleep(tick - now)

left    = -1,  0
right   =  1,  0
up      =  0, -1
down    =  0,  1
stopped =  0,  0

headings = (left, right, up, down)

if __name__ == '__main__':
    main()

"""
Type something in while a stopwatch counts up, showing your typing speed.
"""

import time

import sturm

def main(argv):
    with sturm.cbreak_mode():
        interact()
    return 0

def show(t, body):
    cps = (len(body)-1) / t if t and body else 0
    sturm.render('%3d secs  %3d wpm' % (t, round(60/5 * cps)),
                 '   (Hit Esc to quit.)\n\n',
                 body, sturm.cursor)
    
def interact():
    show(0, "(Start typing...)")
    strokes = sturm.get_key()
    start = time.time()
    while True:
        show(time.time() - start, strokes)
        key = sturm.get_key(timeout=0.2)
        if key is None:
            continue
        elif key == sturm.esc:
            break
        elif key == 'backspace':
            strokes = strokes[:-1]
        elif len(key) == 1:   # an ordinary key, not special like PgUp
            strokes += key

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

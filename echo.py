"""
To check how sturm interprets your keystrokes.
"""

import sturm

def main():
    with sturm.cbreak_mode():
        run()

def run():
    strokes = []
    while True:
        sturm.render(("Hit some keys; hit esc to quit.\n\n",
                      repr(strokes), sturm.cursor))
        key = sturm.get_key()
        if key == sturm.esc:
            break
        strokes.append(key)

if __name__ == '__main__':
    main()

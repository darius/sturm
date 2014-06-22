"""
To check how sturm interprets your keystrokes.
We quit on Q instead of the escape key because there are still
unmapped keys with escape sequences.
"""

import textwrap

import sturm

def main():
    with sturm.cbreak_mode():
        run()

def run():
    strokes = []
    while True:
        lines = textwrap.wrap(' '.join(strokes), sturm.COLS)
        sturm.render("Hit some keys; or hit capital Q to quit.\n\n",
                     '\n'.join(lines), sturm.cursor)
        key = sturm.get_key()
        if key == 'Q':
            break
        strokes.append(repr(key))

if __name__ == '__main__':
    main()

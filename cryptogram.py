"""
A UI for cryptogram puzzles.
Incomplete in many ways.
"""

import itertools, string
import sturm

def main():
    with sturm.cbreak_mode():
        puzzle('nggnpx ng qnja')

def puzzle(cryptogram):
    def my(): pass        # A hack to get a mutable-nonlocal variable.
    my.cursor = 0
    code = ''.join(c for c in cryptogram if c.isalpha())
    assert code
    decoder = {c: ' ' for c in set(code)}

    def erase():          jot(' ')
    def jot(letter):      decoder[code[my.cursor]] = letter
    def shift_by(offset): my.cursor = (my.cursor + offset) % len(code)

    def shift_to_space():
        if ' ' in decoder.values():
            while True:
                shift_by(1)
                if ' ' == decoder[code[my.cursor]]:
                    break

    def view():
        # Assume 1 line, for now.
        yield '\n'
        pos = itertools.count(0)
        for c in cryptogram:
            if c.isalpha() and next(pos) == my.cursor: yield sturm.cursor
            yield decoder.get(c, ' ')
        yield '\n'
        yield ''.join(' -'[c.isalpha()] for c in cryptogram) + '\n'
        yield cryptogram + '\n\n'

    while True:
        sturm.render(view())
        key = sturm.get_key()
        if   key == sturm.esc:
            break
        elif key in string.ascii_letters:
            jot(key)
            shift_by(1)
        elif key == 'right':
            shift_by(1)
        elif key == 'left':
            shift_by(-1)
        elif key == '\t':
            shift_to_space()
        elif key == 'backspace':
            shift_by(-1)
            erase()
        elif key == 'del':
            erase()
            shift_by(1)

if __name__ == '__main__':
    main()

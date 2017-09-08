"""
A UI for cryptogram puzzles.
"""

import collections, commands, itertools, random, string, sys
import sturm
from sturm import ctrl

def main(argv):
    if   len(argv) == 1: make_cryptogram = lambda: random_encrypt(fortune())
    elif len(argv) == 2: make_cryptogram = lambda: argv[1]
    else:
        print("Usage: python %s [cryptogram]" % sys.argv[0])
        sys.exit(1)
    with sturm.cbreak_mode():
        puzzle(make_cryptogram())

alphabet = string.ascii_lowercase

def random_encrypt(text):
    values = list(alphabet); random.shuffle(values)
    code = dict(zip(alphabet, values))
    return ''.join(code.get(c, c) for c in text.lower())

def fortune():
    while True:
        text = shell_run('fortune')
        lines = text.splitlines()
        # Will it fit? TODO: cleaner to actually try to render it.
        if 2 + 4*len(lines) < sturm.ROWS-1 and max(map(len, lines)) < sturm.COLS:
            return text

def shell_run(command):
    err, output = commands.getstatusoutput(command)
    if err:
        print(output)
        sys.exit(1)
    return output

def puzzle(cryptogram):
    def my(): pass        # A hack to get a mutable-nonlocal variable.
    my.cursor = 0         # TODO: simpler now to track line# and column#?
    code = ''.join(c for c in cryptogram if c.isalpha())
    assert code
    decoder = {c: ' ' for c in set(code)}
    lines = map(clean, cryptogram.splitlines())

    def jot(letter):      decoder[code[my.cursor]] = letter
    def shift_by(offset): my.cursor = (my.cursor + offset) % len(code)

    def shift_to_space(offset):
        if ' ' in decoder.values():
            while True:
                shift_by(offset)
                if ' ' == decoder[code[my.cursor]]:
                    break

    def shift_line(offset):
        my.cursor = line_starts[(line_number(my.cursor) + offset) % len(lines)]
    def line_number(pos):
        return next(i for i, start in enumerate(line_starts) # TODO: use binary search
                    if start <= pos < line_starts[i+1])
    line_starts = running_sum(sum(c.isalpha() for c in line)
                              for line in lines)

    def view(show_cursor=True):
        counts = collections.Counter(v for v in decoder.values() if v != ' ')
        letters_left = ''.join(' ' if c in counts else c for c in alphabet)
        clashes = set(v for v,n in counts.items() if 1 < n)
        pos = itertools.count(0)

        yield sturm.green(("Free: ", letters_left, '\n'))
        for line in lines:
            yield '\n'
            for c in line:
                if show_cursor and c.isalpha() and next(pos) == my.cursor:
                    yield sturm.cursor
                yield decoder.get(c, c)
            yield '\n'
            yield ''.join(' -'[c.isalpha()] for c in line) + '\n'
            for c in line:
                color = (sturm.red if decoder.get(c) in clashes
                         else sturm.green if c == code[my.cursor]
                         else sturm.unstyled)
                yield color(c)
            yield '\n'

    while True:
        sturm.render(view())
        key = sturm.get_key()
        if   key == ctrl('X'): break
        elif key == 'home':    my.cursor = 0
        elif key == 'end':     my.cursor = len(code)-1
        elif key == 'left':    shift_by(-1)
        elif key == 'right':   shift_by( 1)
        elif key == 'up':      shift_line(-1)
        elif key == 'down':    shift_line( 1)
        elif key == '\t':      shift_to_space( 1)
        elif key == 'shift-tab': shift_to_space(-1)
        elif key == 'backspace':
            shift_by(-1)
            jot(' ')
        elif key == 'del':
            jot(' ')
            shift_by(1)
        elif key in string.ascii_letters + ' ':
            jot(key)
            shift_by(1)
    # So the shell prompt after exit doesn't overwrite the middle:
    sturm.render(view(show_cursor=False))

def clean(s):
    "Expand tabs; blank out other control characters."
    r = ''
    for c in s:
        if c == '\t':
            while True:
                r += ' '
                if len(r) % 8 == 0: break
        elif ord(c) < 32:
            r += ' '
        else:
            r += c
    return r

def running_sum(ns):
    result = [0]
    for n in ns:
        result.append(result[-1] + n)
    return result

if __name__ == '__main__':
    main(sys.argv)

"""
A UI for cryptogram puzzles.
"""

import collections, commands, itertools, random, string, sys
import sturm
from sturm import ctrl

def main(argv):
    if   len(argv) == 1: cryptogram = random_encrypt(fortune())
    elif len(argv) == 2: cryptogram = argv[1]
    else:
        print("Usage: python %s [cryptogram]" % sys.argv[0])
        sys.exit(1)
    with sturm.cbreak_mode():
        puzzle(cryptogram)

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
    cryptogram = cryptogram.upper()
    lines = map(clean, cryptogram.splitlines())
    code_lines = filter(None, [''.join(c for c in line if c.isalpha())
                               for line in lines])
    line_starts = running_sum(map(len, code_lines))
    code = ''.join(code_lines)
    assert code
    decoder = {c: ' ' for c in set(code)}

    def jot(letter):      decoder[code[my.cursor]] = letter
    def shift_by(offset): my.cursor = (my.cursor + offset) % len(code)

    def shift_to_space(offset):
        if ' ' in decoder.values():
            while True:
                shift_by(offset)
                if ' ' == decoder[code[my.cursor]]:
                    break

    def shift_to_code(offset, letter):
        if letter in code:
            while True:
                shift_by(offset)
                if letter == code[my.cursor]:
                    break

    def shift_line(offset):
        my.cursor = line_starts[(line_number(my.cursor) + offset)
                                % (len(line_starts)-1)]
    def line_number(pos):
        return next(i for i, start in enumerate(line_starts) # TODO: use binary search
                    if start <= pos < line_starts[i+1])

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
        elif key in alphabet or key == ' ':
            jot(key)
            shift_by(1)
        elif key.isupper() and len(key) == 1:
            shift_to_code(1, key)

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

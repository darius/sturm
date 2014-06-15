"""
A UI for cryptogram puzzles.
Incomplete in many ways.
"""

import collections, commands, itertools, random, string, sys
import sturm

def main(argv):
    if   len(argv) == 1:
        make_cryptogram = lambda: random_encrypt(fortune())
    elif len(argv) == 2:
        make_cryptogram = lambda: argv[1]
    else:
        print("Usage: python %s [cryptogram]" % sys.argv[0])
        sys.exit(1)
    with sturm.cbreak_mode():
        puzzle(make_cryptogram())

def random_encrypt(text):
    text = text.lower()
    keys = string.ascii_lowercase
    values = list(keys); random.shuffle(values)
    code = dict(zip(keys, values))
    return ''.join(code.get(c, c) for c in text)

def fortune():
    while True:
        text = shell_run('fortune')
        lines = text.splitlines()
        # Will it fit? TODO: cleaner to actually try to render it.
        if 5 * len(lines) < sturm.ROWS and max(map(len, lines)) < sturm.COLS:
            return text

def shell_run(command):
    err, output = commands.getstatusoutput(command)
    if err:
        print(output)
        sys.exit(1)
    return output

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

    def find_clashes():
        counts = collections.Counter(v for v in decoder.values() if v != ' ')
        return set(v for v,n in counts.items() if 1 < n)

    def view():
        clashes = find_clashes()
        pos = itertools.count(0)
        for line in cryptogram.splitlines():
            line = line.replace('\t', ' ') # XXX formatting hack
            yield '\n'
            for c in line:
                if c.isalpha() and next(pos) == my.cursor: yield sturm.cursor
                yield decoder.get(c, c)
            yield '\n'
            yield ''.join(' -'[c.isalpha()] for c in line) + '\n'
            for c in line:
                yield sturm.red(c) if decoder.get(c) in clashes else c
            yield '\n'

    while True:
        sturm.render(view())
        key = sturm.get_key()
        if   key == sturm.esc:
            break
        elif key == 'right': shift_by(1)
        elif key == 'left':  shift_by(-1)
        elif key == '\t':    shift_to_space()
        elif key == 'home':  my.cursor = 0
        elif key == 'end':   my.cursor = len(code)-1
        elif key == 'backspace':
            shift_by(-1)
            erase()
        elif key == 'del':
            erase()
            shift_by(1)
        elif key in string.ascii_letters + ' ':
            jot(key)
            shift_by(1)

if __name__ == '__main__':
    main(sys.argv)

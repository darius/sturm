"""
Animate matching a set of literal patterns against a string.
"""

import sturm

def main(argv):
    if len(argv) == 1:
        string = 'cats are fat'
        patterns = 'rat cat capsize catalog'.split()
    elif len(argv) == 2:
        print("Usage: python %s [string pattern1 pattern2...]" % argv[0])
        return 1
    else:
        string = argv[1]
        patterns = argv[2:]
    with sturm.cbreak_mode():
        animate(string, patterns)
    return 0

def animate(string, patterns):
    i = 0
    computation = [sorted(set(patterns))]
    while True:
        update(computation, i, string)
        sturm.render((string[:i], sturm.cursor, string[i:], '\n\n',
                      view(computation, i)))
        key = sturm.get_key()
        if   key == sturm.esc:     break
        elif key == 'left':        i = max(0, i-1)
        elif key in (' ','right'): i = min(i+1, len(string))

def update(computation, i, string):
    if i < len(computation): return
    patterns, ch = computation[i-1], string[i-1]
    computation.append(sorted(set(pattern[1:] for pattern in patterns
                                  if pattern.startswith(ch))))

def view(computation, i):
    for pattern in computation[i]:
        yield ' '*i, pattern or sturm.green('match!'), '\n'
            

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

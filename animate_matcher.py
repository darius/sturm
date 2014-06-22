"""
Animate matching a set of literal patterns against a string.
"""

import sturm

def main():
    with sturm.cbreak_mode():
        run(['rat', 'cat', 'capsize', 'catalog'], 'cats are fat')

def run(patterns, string):
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
    return ((' '*i, pattern or sturm.green('match!'), '\n')
            for pattern in computation[i])

if __name__ == '__main__':
    main()

"""
A crude human interface for SAT solving -- I want to see if it can
make a fun puzzle game.

Adapted from https://github.com/darius/sketchbook/blob/master/sat/ttypuzzle.py
"""

import string

from sat import sat, dimacs
import sturm

# Some problems from http://toughsat.appspot.com/
filenames = ['sat/trivial.dimacs',
             'sat/factoring6.dimacs',
             'sat/factoring2.dimacs',
             'sat/subsetsum_random.dimacs']

def main():
    games = [Game(problem) for _,problem in map(dimacs.load, filenames)]
    with sturm.cbreak_mode():
        play(games)

instructions = """\
To win, put a * in every column. (Columns with no *'s are yellow.)
Flip O's and *'s in a row by typing its key (listed on the left and right edges).
Press the spacebar to mark/unmark the last row you flipped (as a memory aid).
Press Tab to cycle to the next game, Esc to quit."""

def play(games):
    level = 0
    while True:
        game = games[level]
        sturm.render((instructions, "\n\n",
                      game.view(), "\n",
                      "You win!" if game.is_solved() else ""))
        key = sturm.get_key()
        if key == sturm.esc:
            break
        elif key == '\t':
            level = (level + 1) % len(games)
        elif key == ' ':
            game.toggle_mark()
        else:
            v = game.variable_of_name(key)
            if v is not None:
                game.flip(v)

class Game(object):

    def __init__(self, problem):
        variables = sat.problem_variables(problem)
        names = '1234567890' + string.ascii_uppercase
        self.problem   = problem
        self.env       = {v: False for v in variables}
        self.names     = dict(zip(names, variables))
        self.variables = dict(zip(variables, names))
        self.last_flip = None   # The variable last flipped
        self.marks     = set()  # Variables currently marked

    def variable_of_name(self, name):
        return self.names.get(name.upper())

    def is_solved(self):
        return sat.is_satisfied(self.problem, self.env)

    def clause_is_satisfied(self, clause):
        return any(self.env.get(abs(literal)) == (0 < literal)
                   for literal in clause)

    def flip(self, v):
        self.env[v] = not self.env[v]
        self.last_flip = v

    def toggle_mark(self):
        if self.last_flip is not None:
            if self.last_flip in self.marks:
                self.marks.remove(self.last_flip)
            else:
                self.marks.add(self.last_flip)

    def view(self):

        def present(v, clause):
            pos, neg = v in clause, -v in clause
            mark = 'O*'[self.env[v] == pos] if pos or neg else '.'
            color = satisfied if self.clause_is_satisfied(clause) else unsatisfied
            return color(mark)

        for v in self.variables:
            v_color = row_true if self.env[v] else row_false
            if v in self.marks: v_color = S.compose(S.underlined, v_color)
            name = v_color(self.variables[v])
            yield name, ' '
            for clause in self.problem:
                yield present(v, clause)
            yield ' ', name, '\n'


S = sturm

bg          = S.on_black
row_true    = S.compose(bg, S.red)
row_false   = S.compose(bg, S.white)
satisfied   = S.compose(bg, S.blue)
unsatisfied = S.compose(bg, S.bold, S.yellow)


if __name__ == '__main__':
    main()

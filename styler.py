"""
Let's interactively tweak styles and colors in a mockup.
TODO:
 - save designs to a file or something
 - load the mockup from elsewhere
 - highlight currently-active styles/colors
 - load saved designs
 - undo
"""

import sturm

def main():
    with sturm.cbreak_mode():
        run()
    dump()

def dump():
    print()
    print('styles = {}')
    for thing in mockup:
        if isinstance(thing, Cell):
            thing.dump()

def run():
    pos = 0
    things = [thing for thing in mockup if isinstance(thing, Cell)]
    while True:
        sturm.render(('\n', view(mockup, pos), '\n\n',
                      '   '.join(k+' '+v
                                 for k,v in sorted(style_map.items())), '\n\n',
                      ' '.join(colors), '\n\n',
                      "Right/left or tab/shift-tab to navigate; Esc to quit."))
        key = sturm.get_key()
        if   key == sturm.esc:   break
        elif key in lefts:       pos = (pos - 1) % len(things)
        elif key in rights:      pos = (pos + 1) % len(things)
        elif key in styles:      things[pos].toggle(styles[key])
        elif key in backgrounds: things[pos].background(backgrounds[key])
        elif key in foregrounds: things[pos].foreground(foregrounds[key])

lefts  = 'left', 'shift-tab'
rights = 'right', '\t'

style_map = {'!': 'bold',     '_': 'underlined',
             '*': 'blinking', 'space': 'inverted'}
styles = {k.replace('space', ' '): getattr(sturm, name)
          for k,name in style_map.items()}

colors = 'blacK Red Green Yellow Blue Magenta Cyan White Default'.split()
color_map = {next(char for char in name if char.isupper()): name.lower()
             for name in colors}
backgrounds = {char: getattr(sturm, 'on_'+name)
               for char, name in color_map.items()}
foregrounds = {char.lower(): getattr(sturm, 'fg_default' if name == 'default' else name)
               for char, name in color_map.items()}

class Cell(object):
    def __init__(self, text):
        self.text = text
        self.styles = set()
        self.fg = sturm.fg_default
        self.bg = sturm.on_default

    def toggle(self, style):
        if style in self.styles:
            self.styles.remove(style)
        else:
            self.styles.add(style)

    def foreground(self, color):
        self.fg = color

    def background(self, color):
        self.bg = color

    def render(self):
        scene = self.fg(self.bg(self.text))
        for style in self.styles:
            scene = style(scene)
        yield scene

    def dump(self):
        print('styles[%r] = %s' % (self.text, self.export()))

    def export(self):
        expr = repr(self.text)
        expr = uncall(self.bg, expr)
        expr = uncall(self.fg, expr)
        for style in self.styles:
            expr = uncall(style, expr)
        return expr

def uncall(style, expr):
    return 'sturm.%s(%s)' % (style.__name__, expr)

## x = Cell('hey')
## x.toggle(sturm.underlined)
## x.dump()
#. styles['hey'] = sturm.underlined(sturm.fg_default(sturm.on_default('hey')))

def view(things, point):
    pos = 0
    for thing in things:
        if isinstance(thing, Cell):
            if pos == point: yield sturm.cursor
            pos += 1
            yield thing.render()
        else:
            yield thing

mockup = (' ', Cell('  . '), ' ', Cell('  2 '), ' ', Cell('  4 '), ' ', Cell('  8 '), '\n\n',
          ' ', Cell(' 16 '), ' ', Cell(' 32 '), ' ', Cell(' 64 '), ' ', Cell('128 '), '\n\n',
          ' ', Cell('256 '), ' ', Cell('512 '), ' ', Cell('1024'), ' ', Cell('2048'), '\n\n',)

if __name__ == '__main__':
    main()

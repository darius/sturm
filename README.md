An excessively-minimal terminal-UI module. This won't run under
Windows except with Cygwin.

The most standard way to code a console app like this is with curses,
but curses kind of earns its name. And there are better libraries now,
but I'm not familiar with them yet. (Soon!) Here we use
http://en.wikipedia.org/wiki/ANSI_escape_code and raw or cbreak mode
http://en.wikipedia.org/wiki/Seventh_Edition_Unix_terminal_interface#Input_modes

Thanks to https://github.com/thomasballinger/curtsies for ideas and
discussion. (Curtsies is considerably more complete and useful and I
don't expect this library to ever grow up to compete with it.)

There's some influence too from https://github.com/gwk/gloss which
looks very nice.

Thanks to Dave Long for helpful discussion of the key-reading
code.

## To Use

`import sturm`. The other `.py` files here are examples.

## Bugs

On my system if I hold down an arrow key for auto-repeat, get_key()
may return a bare escape character. Presumably the OS claims the rest
of the escape sequence isn't available yet. Argh.

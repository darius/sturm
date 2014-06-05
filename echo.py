import sturm

def main():
    with sturm.cbreak_mode():
        run()

def run():
    strokes = []
    while True:
        sturm.render(repr(strokes) + '\n')
        key = sturm.get_key()
        if key == 'q':
            break
        strokes.append(key)

main()

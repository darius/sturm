"""
Produce all the dictionary words that can go into an anagram of
the input text. Then take the user's choice of a word and show the
anagrams using it.

Adapted from https://github.com/darius/languagetoys

Bare start; needs lots of polish, etc..
"""

import heapq, re, string, textwrap
from itertools import permutations

from pdist import cPw
import sturm

# Configure me by editing these constants:
dict_filename = 'wordlist.txt'

def main(argv):
    source = ' '.join(argv[1:]).lower()
    global dictionary, dictionary_prefixes
    dictionary, dictionary_prefixes = load(dict_filename, source)
    with sturm.cbreak_mode():
        sturm.render('Collecting words...')
        run(collect_words(source))

def collect_words(source):
    return [(word,rest)
            for _,word,rest in sorted((word[:1].isupper(), word, rest)
                                      for name,rest in gen_anagram_words(source)
                                      for word in dictionary[name])]
    
def run(words):
    lines = [line.split() for line in textwrap.wrap(' '.join(word for word,_ in words),
                                                    sturm.COLS-1)]
    pos = 0
    while True:
        sturm.render(view_words(lines, pos))
        key = sturm.get_key()
        if   key == sturm.esc: return
        elif key == '\n':      run_anagrams(words[pos])
        elif key == 'left':    pos = (pos - 1) % len(words)
        elif key in ('right','\t'): pos = (pos + 1) % len(words)

def view_words(lines, pos):
    i = 0
    for y, line in enumerate(lines):
        if y == sturm.ROWS-1: break
        for x, word in enumerate(line):
            if x: yield ' '
            if i == pos: yield sturm.cursor
            yield word
            i += 1
        yield '\n'

def run_anagrams((word, rest)):
    anagrams = []

    def interact(timeout):
        sturm.render(view_anagrams(anagrams))
        key = sturm.get_key(timeout)
        return key != sturm.esc

    for anagram in extend((word,), '', rest, ''):
        for words in cross_product([dictionary[p] for p in anagram[1:]]):
            words = [anagram[0]] + words
            anagrams.append(best_permutation(words))
            if not interact(0): return
    anagrams.append((0, ('--done--',)))
    while interact(None):
        pass

def view_anagrams(anagrams):
    y = 0
    for score,words in heapq.nlargest(sturm.ROWS-1, anagrams):
#        if y == sturm.ROWS-1: break
        yield ' '.join(words)
        yield '\n'
        y += 1

def cross_product(lists):
    if not lists:
        yield []
    else:
        for xs in cross_product(lists[1:]):
            for x in lists[0]:
                yield [x] + xs

def best_permutation(words):
    return max(map(bigram_score, permutations(words)))

cache = {}

def bigram_score(words):
    P = 1
    prev = '<S>'
    for word in words:
        key = prev + ' ' + word
        if key not in cache:
            if 100000 < len(cache):
                cache.clear()   # Keep memory use bounded
            cache[key] = cPw(word, prev)
        P *= cache[key]
        prev = word
    return P, words

def pigeonhole(word):
    "Two words have the same pigeonhole iff they're anagrams of each other."
    return ''.join(sorted(word))

def load(filename, subject=None):
    "Read in a word-list, one word per line. Prune it wrt subject."
    pigeonholes = {}
    prefixes = set()
    identity = ''.join(map(chr, range(256)))
    nonalpha = ''.join(set(identity) - set(string.ascii_lowercase))
    usable = usable_pattern(subject)
    def add(word):
        if not usable(word): return
        canon = word.lower().translate(identity, nonalpha)
        hole = pigeonhole(canon)
        pigeonholes.setdefault(hole, []).append(word)
        for i in range(1, len(hole)+1):
            prefixes.add(hole[:i])
    for line in open(filename):
        add(line.rstrip('\n'))
    # 'a' and 'I' happen not to be in my wordlist file:
    if 'a' not in pigeonholes: add('a')
    if 'i' not in pigeonholes: add('I')
    return pigeonholes, prefixes

def usable_pattern(subject):
    """Return a predicate that accepts words that could be part of an
    anagram of subject. (But a None subject could be anything.) This
    is to prune the dictionary to speed things up a bit."""
    if subject is None:
        return lambda word: True
    alphabet = set(extract_letters(subject))
    pattern = re.compile('([%s]|\W)+$' % ''.join(alphabet), re.I)
    return pattern.match

dictionary, dictionary_prefixes = None, None
## dictionary, dictionary_prefixes = load(dict_filename)

## pt = pigeonhole
## pt('hel') in dictionary_prefixes, pt('hel') in dictionary
#. (True, False)
## pt('hello') in dictionary_prefixes, pt('hello') in dictionary
#. (True, True)

def gen_anagram_words(s):
    "Generate the pigeonhole names possible in anagrams of s."
    bag = extract_letters(s)
    return gen_names('', bag) if bag else ()

def gen_names(wp, rest):
    for letter, others in each_distinct_letter(rest):
        wp1 = wp + letter
        if wp1 in dictionary_prefixes:
            if wp1 in dictionary:
                if not others or any(extend((), '', others, '')):
                    yield wp1, others
            if others:
                for result in gen_names(wp1, others):
                    yield result

def extend(acc, wp, rest, bound):
    """Generate all the anagrams of the nonempty bag 'rest' that
    extend acc with a word starting with wp, the remainder of wp
    being lexicographically >= bound. As with gen_anagrams(), each
    anagram is sorted and they appear in sorted order."""
    for letter, others in each_distinct_letter(rest):
        if bound[:1] <= letter:
            wp1 = wp + letter
            if wp1 in dictionary_prefixes:
                bound1 = bound[1:] if bound[:1] == letter else ''
                if not bound1 and wp1 in dictionary:
                    acc1 = acc + (wp1,)
                    if others:
                        for result in extend(acc1, '', others, wp1):
                            yield result
                    else:
                        yield acc1
                if others:
                    for result in extend(acc, wp1, others, bound1):
                        yield result

def extract_letters(s):
    return make_bag(c for c in s.lower() if c.isalpha())

def make_bag(letters):
    return ''.join(sorted(letters))

def each_distinct_letter(bag):
    """Generate (letter, bag-minus-one-of-that-letter) for each
    different letter in the bag."""
    prefix = ''
    for i, letter in enumerate(bag):
        if 0 == i or letter != bag[i-1]:
            yield letter, bag[:i] + bag[i+1:]

## list(each_distinct_letter('eehlloo'))
#. [('e', 'ehlloo'), ('h', 'eelloo'), ('l', 'eehloo'), ('o', 'eehllo')]

if __name__ == '__main__':
    import sys
    main(sys.argv)

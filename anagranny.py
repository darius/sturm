"""
Produce all the dictionary words that can go into an anagram of
the input text. Then take the user's choice of a word and show the
anagrams using it.

Adapted from https://github.com/darius/languagetoys

Bare start; needs lots of polish, etc..
"""

import re, string, time
from itertools import permutations, izip_longest

from anagrams.pdist import cPw
import sturm

# Configure me by editing these constants:
dict_filename = 'anagrams/wordlist.txt'

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
    nrows, ncols = sturm.ROWS-1, sturm.COLS-1
    words_width = max(len(word) for word,_ in words) # N.B. assumes >=1 word

    def view():
        grams_pane = anagrams.top(nrows)
        for r, (word, gram) in enumerate(izip_longest(words_pane, grams_pane, fillvalue='')):
            if page+r == pos: yield sturm.cursor
            yield word.ljust(words_width), ' ', ' '.join(gram), '\n'
        if anagrams.done:
            yield ' '*words_width, ' ', '--done--'

    pos, new_pos = None, 0
    while True:
        if pos != new_pos % len(words):
            pos = new_pos % len(words)
            page = (pos // nrows) * nrows
            words_pane = [word for word,_ in words[page:page+nrows]]
            anagrams = Anagrams(gen_anagrams(words[pos]))
        sturm.render(view())
        key = sturm.get_key(None if anagrams.done else 0)
        if   key is None:          anagrams.grow()
        elif key == sturm.esc:     return
        elif key == 'up':          new_pos = pos - 1
        elif key in ('down','\t'): new_pos = pos + 1
        elif key == 'pgup':        new_pos = ((pos // nrows) - 1) * nrows
        elif key == 'pgdn':        new_pos = ((pos // nrows) + 1) * nrows

class Anagrams(object):
    def __init__(self, gen):
        self.gen = gen
        self.done = False
        self.results = []
    def grow(self):
        start = time.time()
        for result in self.gen:
            self.results.append(result)
            if start + 0.05 < time.time():
                break
        else:
            self.done = True
            return
        self.results.sort(reverse=True)
    def top(self, n):
        return [gram for _,gram in self.results[:n]]

def gen_anagrams((word, rest)):
    for anagram in extend((word,), '', rest, ''):
        for words in cross_product([dictionary[p] for p in anagram[1:]]):
            words = [anagram[0]] + words
            yield best_permutation(words)

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
    pattern = re.compile(r'([%s]|\W)+$' % ''.join(alphabet), re.I)
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

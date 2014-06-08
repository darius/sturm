"""
Helper for anagranny.
Adapted from https://github.com/darius/languagetoys
"""

from itertools import permutations
from math import log

from pdist import Pw, cPw

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

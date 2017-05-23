# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
import string
import regex
import functools

# TODO:
# - detokenizer

MULTI = ',-/.:'
PUNCTS = set(string.punctuation)
NONWORDS = regex.compile(r'([\p{P}\p{S}\p{Z}\p{M}\p{C}\n ])', flags=regex.I)
EMAIL = regex.compile(r'([a-z\d\.-]+@[a-z\d\.-]+)', flags=regex.I)
URL = regex.compile(r'(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))'
                    r'([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?')
TWITTER = regex.compile(r'[@#][a-z\d]+', flags=regex.I)
DOMAIN = regex.compile(r'[a-z0-9]([a-z0-9-]+\.){1,}[a-z0-9]+')
ABBR = regex.compile(r'(?:[A-Z]\.)+')
NUM = regex.compile(r'((?:\d+[\.,:])+\d+)', flags=regex.I)


@functools.lru_cache(maxsize=65536)
def find_entities(token):
    if not token:
        return

    match = None
    if token[0] in '@#':
        match = TWITTER.search(token)
        if match: yield match.group()
    elif '@' in token:
        match = EMAIL.search(token)
        if match: yield match.group()
    elif '://' in token:
        match = URL.search(token)
        if match: yield match.group()
    elif '.' in token:
        for pattern in [ABBR, NUM, DOMAIN]:
            match = pattern.search(token)
            if match: yield match.group()
    elif ',' in token or ':' in token:
        match = NUM.search(token)
        if match: yield match.group()


def extract_entities(text):
    ents = set()
    for token in regex.split(r'\s+', text):
        for ent in find_entities(token):
            ents.add(ent)

    entities = {}
    for i, e in enumerate(sorted(ents, key=len, reverse=True)):
        eid = ' ENT{0} '.format(i)
        entities[eid] = e.strip()
        text = text.replace(e, eid)

    return (text, entities)


CONTRACTIONS = regex.compile(r" ' (s|m|d|ll|re|ve) ", flags=regex.I)


def fix(text, sep='￭'):
    text = CONTRACTIONS.sub(r' {sep}\1 '.format(sep=sep), text)
    text = text.replace(" n ' t ", " n't ")
    return text


EMPTY = 0
SPACE = 1
PUNCT = 2
OTHER = 3

ADD_PREV = ((OTHER, EMPTY), (OTHER, SPACE), (OTHER, PUNCT), (PUNCT, EMPTY),
            (PUNCT, SPACE))
ADD_NEXT = ((EMPTY, OTHER), (SPACE, OTHER), (EMPTY, PUNCT), (PUNCT, PUNCT),
            (PUNCT, OTHER))
ADD_BOTH = ((OTHER, OTHER), (PUNCT, OTHER))


def check(text, mode=None):
    char = None
    if mode == 'pre' and text:
        char = text[-1]
    elif mode == 'nex' and text:
        char = text[0]

    if char == None:
        return EMPTY
    elif char == ' ':
        return SPACE
    elif char in PUNCTS:
        return PUNCT
    return OTHER


def tokenizer(text, aggressive=True, separator='￭'):
    psep = ' {0}'.format(separator)
    nsep = '{0} '.format(separator)

    text, entities = extract_entities(text)
    text = NONWORDS.sub(r' \1 ', text)
    text = fix(text)

    tokens = []
    parts = [''] + text.split() + ['']

    for pre, cur, nex in zip(parts, parts[1:], parts[2:]):
        if not cur in PUNCTS:
            tokens.append(' {cur} '.format(cur=cur))
            continue

        _aggressive = aggressive
        if aggressive is True and cur in MULTI:
            _aggressive = False

        (p, n) = (check(pre, 'pre'), check(nex, 'nex'))

        if (p, n) in ADD_NEXT:
            tokens.append('{cur}{nsep}'.format(cur=cur, nsep=nsep))
        elif (p, n) in ADD_PREV:
            tokens.append('{psep}{cur}'.format(cur=cur, psep=psep))
        elif (p, n) in ADD_BOTH:
            if _aggressive:
                tokens.append('{psep}{cur}{nsep}'
                              .format(cur=cur, psep=psep, nsep=nsep))
            else:
                tokens.append('{psep}{cur}'.format(cur=cur, psep=psep))
        else:
            tokens.append('{cur}'.format(cur=cur))

    text = ' '.join(tokens)
    for eid, ent in entities.items():
        text = text.replace(eid, ent)

    return text.split()


if __name__ == '__main__':
    for line in sys.stdin:
        print(' '.join(tokenizer(line.strip(), aggressive=True)))

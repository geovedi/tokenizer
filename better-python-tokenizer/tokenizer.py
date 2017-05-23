# -*- coding: utf-8 -*-

from __future__ import unicode_literals


import sys
import string
import regex

# TODO:
# - language specific handling abbreviations and contractions
# - detokenizer

PUNCTS = set(string.punctuation)
PUNCTS_PATTERN = regex.compile(r'([^\p{P}]+|[\p{S}\p{P}])', flags=regex.I)
EMAIL = regex.compile(r'([a-z\d\.-]+@[a-z\d\.-]+)', flags=regex.I)
URL = regex.compile(r'([a-z\d]+:\/\/\S+)', flags=regex.I)
DOMAIN = regex.compile(r'^[a-z0-9]([a-z0-9-]+\.){1,}[a-z0-9]+\Z')

def extract_entities(text):
    ents = set()
    for token in regex.split(r'\s+', text):
        if not token:
            continue
        if token[0] in '@#':
            # twitter user and hashtag
            ents.add(token)
        elif '@' in token:
            # could be email?
            match = EMAIL.search(token)
            if match:
                ents.add(match.group())
        elif '://' in token:
            # url
            match = URL.search(token)
            if match:
                ents.add(match.group())
        elif len(token.split('.')) >= 2:
            match = DOMAIN.search(token)
            if match:
                ents.add(match.group())

    entities = {}
    for i, e in enumerate(sorted(ents, key=len, reverse=True)):
        eid = 'ENT_{0}'.format(i)
        entities[eid] = e
        text = text.replace(e, eid)

    return (text, entities)


CONTRACTIONS = regex.compile(r"('(s|m|d|ll|re|ve)\W)|(n't\W)", flags=regex.I)

def handle_contractions(text, sep='￭'):
    text = CONTRACTIONS.sub(r' {sep}\1'.format(sep=sep), text)
    return text


EMPTY = 0
SPACE = 1
PUNCT = 2
OTHER = 3

ADD_PREV = ((OTHER, EMPTY), (OTHER, SPACE), (OTHER, PUNCT), (PUNCT, EMPTY), (PUNCT, SPACE))
ADD_NEXT = ((EMPTY, OTHER), (SPACE, OTHER), (EMPTY, PUNCT), (PUNCT, PUNCT))
ADD_BOTH = ((OTHER, OTHER), (PUNCT, OTHER), (PUNCT, OTHER))

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

MWE_PUNCTS = ',-/.:\''

def tokenizer(text, aggressive=False, separator='￭'):
    psep = ' {0}'.format(separator)
    nsep = '{0} '.format(separator)

    # pre-processing
    text, entities = extract_entities(text)
    text = handle_contractions(text)

    tokens = []
    parts = [''] + list(filter(None, PUNCTS_PATTERN.split(text))) + ['']

    for pre, cur, nex in zip(parts, parts[1:], parts[2:]):
        if cur in PUNCTS:
            _aggressive = aggressive
            if not cur in MWE_PUNCTS and aggressive is True:
                _aggressive = False

            (p, n) = (check(pre, 'pre'), check(nex, 'nex'))

            # abbreviations?
            if cur == '.' and (len(pre.strip()) == 1 or len(nex.strip()) == 1) and (p == OTHER or n == OTHER):
                tokens.append('{cur}'.format(cur=cur))
                continue

            if (p, n) in ADD_NEXT:
                tokens.append('{cur}{nsep}'.format(cur=cur, nsep=nsep))
            elif (p, n) in ADD_PREV:
                tokens.append('{psep}{cur}'.format(cur=cur, psep=psep))
            elif (p, n) in ADD_BOTH and _aggressive:
                tokens.append(
                    '{psep}{cur}{nsep}'.format(cur=cur, psep=psep, nsep=nsep))
            else:
                tokens.append('{cur}'.format(cur=cur))
        else:
            tokens.append('{cur}'.format(cur=cur))

    # post-processing
    text = ''.join(tokens)
    for eid, ent in entities.items():
        text = text.replace(eid, ent)

    return text.split()


if __name__ == '__main__':
    for line in sys.stdin:
        print(' '.join(tokenizer(line.strip(), aggressive=True)))


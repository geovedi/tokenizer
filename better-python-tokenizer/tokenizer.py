import string
import regex as re

PUNCTS = set(string.punctuation)
PUNCTS_PATTERN = re.compile(r'([^\p{P}]+|\p{S}|\p{P})')
EMAIL = re.compile(r'([a-z\d\.-]+@[a-z\d\.-]+)', re.I)
TWEET = re.compile(r'([@#][a-z\d]+)', re.I)
URL = re.compile(r'([a-z\d]+:\/\/\S+)', re.I)
DOMAIN = re.compile(r'(([a-z\d]+|[a-z\d][-])+[a-z\d]+){1,63}\.'
                    '([a-z]{2,3}\.[a-z]{2}|[a-z]{2,6})', re.I)


def extract_entities(text):
    ents = set()
    for token in re.split(r'\s+', text):
        for pattern in [EMAIL, TWEET, URL, DOMAIN]:
            match = pattern.search(token)
            if match:
                ents.add(match.group())
    entities = {}
    for i, e in enumerate(sorted(ents, key=len, reverse=True)):
        eid = 'ENT_{0}'.format(i)
        entities[eid] = e
        text = text.replace(e, eid)
    return (text, entities)


EMPTY = 0
SPACE = 1
PUNCT = 2
OTHER = 3

ADD_PREV = ((OTHER, EMPTY), (OTHER, SPACE), (OTHER, PUNCT), (PUNCT, PUNCT),
            (PUNCT, EMPTY), (PUNCT, SPACE))

ADD_NEXT = ((EMPTY, OTHER), (SPACE, OTHER), (PUNCT, OTHER), (EMPTY, PUNCT))


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


def tokenize(text, aggressive=False, separator='￭'):
    psep = ' {0}'.format(separator)
    nsep = '{0} '.format(separator)

    # pre-processing
    text, entities = extract_entities(text)

    tokens = []
    parts = [''] + list(filter(None, PUNCTS_PATTERN.split(text))) + ['']

    for pre, cur, nex in zip(parts, parts[1:], parts[2:]):
        if cur in PUNCTS:
            _aggressive = aggressive
            if not cur in ',-/.:' and aggressive is True:
                _aggressive = False

            (p, n) = (check(pre, 'pre'), check(nex, 'nex'))

            if (p, n) in ADD_NEXT:
                tokens.append('{cur}{nsep}'.format(cur=cur, nsep=nsep))
            elif (p, n) in ADD_PREV:
                tokens.append('{psep}{cur}'.format(cur=cur, psep=psep))
            elif (p, n) == (OTHER, OTHER) and _aggressive:
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

# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
from collections import OrderedDict
import regex as re


class Tokenizer(object):
    PUNCTUATIONS = set('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')

    SPLITTER = re.compile(r'(\w+|\s|[^\w\s])', flags=re.S | re.M | re.V0)
    EMAIL = re.compile(r'([a-z\d\.-]+@[a-z\d\.-]+[a-z])', flags=re.I)
    URL = re.compile(
        r'(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))'
        r'([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?',
        flags=re.I)
    DOMAIN = re.compile(r'[a-z0-9]([a-z0-9-]+\.){1,}[a-z0-9]+', flags=re.I)
    TWITTER = re.compile(r'[@#][a-z\d_]+', flags=re.I)
    ABBR = re.compile(r'(?:[A-Z]\.){1,}|(Prof|[Dd]r|[Rr]ev)\.')
    NUM = re.compile(r'((?:\d+[\.,:—-])+\d+)', flags=re.I)
    MONEY = re.compile(r'((?:US|S|AU)\$|(?:AU|CA)D|[\$£¥€]|R[ps]\.?)(\s?\d+)')
    CONTRACTIONS = re.compile(
        r"(?<=\w+)('(s|m|d|ll|re|ve)|n't)(?<![^\w])", flags=re.I)

    REPLACETABLE = OrderedDict({
        '“': '"',
        '”': '"',
        '’': "'",
        '‘': "'",
        '—': ' — ',
        '–': ' — ',
        '…': '...',
        '—': ' — ',
        '̶': ' — ',
        '♫': ' ♫ ',
        '♪': ' ♪ ',
        'â\u0082Ź': '€',
        'â ?? Ź': '€',
        'â\u0080\u008B': '',
        'â\u0080˘': '•',
        'â\u0084˘': '™',
        'â\u0096ş': '►',
        'â\u0087§': '⇧',
        'Âť': '»',
        'Â°': '°',
        'ĂŠ': 'é',
        'ĂŽ': 'î',
        'ĂŞ': 'ê',
        'Ăź': 'ü',
        'Â(C)': '©',
        'Â (C)': '©',
        'Ë\u0098': '•',
        'Ă\u0089': 'É',
        '¡¯': "'",
        'Î\u009C': 'µ',
        'Ă\u00AD': 'í',
        'Ă\u0091': 'Ñ',
        'Ă\u0097': '×',
        '\u00ad': '',
        '\u0080': '',
        '\u0093': '',
        '\uFEFF': '',
        '\u200B': '',
        '\u200E': '',
        '\u008B': '',
        '\u0082': '',
    })

    def __init__(self, joiner='￭'):
        self.joiner = joiner

    def _preprocess(self, text):
        text = self.MONEY.sub(r'\1 \2', text)
        for pat, rep in self.REPLACETABLE.items():
            text = text.replace(pat, rep)
        return text

    def _protect(self, text):
        protected = OrderedDict()
        protected['PIPE'] = '|||'

        for i, chunk in enumerate(self.CONTRACTIONS.finditer(text)):
            protected['CONT{0}'.format(i)] = self.joiner + chunk.group()

        for i, chunk in enumerate(self.EMAIL.finditer(text)):
            protected['EMAIL{0}'.format(i)] = chunk.group()

        for i, chunk in enumerate(self.URL.finditer(text)):
            protected['URL{0}'.format(i)] = chunk.group()

        for i, chunk in enumerate(self.DOMAIN.finditer(text)):
            protected['DOMAIN{0}'.format(i)] = chunk.group()

        for i, chunk in enumerate(self.TWITTER.finditer(text)):
            protected['TWITTER{0}'.format(i)] = chunk.group()

        for i, chunk in enumerate(self.ABBR.finditer(text)):
            protected['ABBR{0}'.format(i)] = chunk.group()

        for i, chunk in enumerate(self.NUM.finditer(text)):
            protected['NUM{0}'.format(i)] = chunk.group()

        for pat, rep in protected.items():
            if rep.startswith(self.joiner):
                text = text.replace(rep[1:], ' ' + pat)
            text = text.replace(rep, pat)

        return (text, protected)

    def _add_joiner(self, tokens, protected):
        tokens = list(filter(None, tokens))
        new_tokens = []

        tokens = [' '] + tokens + [' ']
        for pre, tok, nex in zip(tokens, tokens[1:], tokens[2:]):
            if tok in self.PUNCTUATIONS:
                if pre != ' ':
                    tok = self.joiner + tok

                if nex != ' ':
                    tok = tok + self.joiner

            new_tokens.append(tok)

        text = ' '.join(new_tokens)
        for pat, rep in protected.items():
            text = text.replace(pat, rep)

        return text.split()

    def tokenize(self, text):
        text = self._preprocess(text)
        text, protected = self._protect(text)
        return self._add_joiner(self.SPLITTER.split(text), protected)


if __name__ == '__main__':
    tokenize = Tokenizer().tokenize
    for line in sys.stdin:
        print(' '.join(tokenize(line.strip())))

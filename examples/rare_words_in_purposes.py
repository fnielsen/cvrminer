"""Rare words in company purposes.

This script requires the `dasem` module

"""

from __future__ import print_function

from os import write

import signal

from six import b

from nltk import WordPunctTokenizer

from dasem.fullmonty import Word2Vec
from dasem.text import Decompounder

from cvrminer.cvrmongo import CvrMongo
from cvrminer.text import PurposeProcessor
from cvrminer.virksomhed import Virksomhed

# Ignore broken pipe errors
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

decompounder = Decompounder()
purpose_processor = PurposeProcessor()
w2v = Word2Vec()
word_tokenizer = WordPunctTokenizer()

n = 1
cvr_mongo = CvrMongo()
for company in cvr_mongo.iter_companies():
    virksomhed = Virksomhed(company)
    purposes = virksomhed.formaal
    for purpose in purposes:
        cleaned_purpose = purpose_processor.clean(purpose)
        words = word_tokenizer.tokenize(cleaned_purpose)
        for word in words:
            word = word.lower()
            if word not in w2v.model:
                phrase = decompounder.decompound_word(word)
                for subphrase in phrase.split(' '):
                    if subphrase not in w2v.model:
                        write(1, subphrase.encode('utf-8') + b('\n'))

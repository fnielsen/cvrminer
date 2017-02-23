"""Cleaned company purposes."""

from __future__ import print_function

from os import write

import signal

from six import b

from cvrminer.cvrmongo import CvrMongo
from cvrminer.text import PurposeProcessor
from cvrminer.virksomhed import Virksomhed


# Ignore broken pipe errors
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

purpose_processor = PurposeProcessor()

n = 1
cvr_mongo = CvrMongo()
for company in cvr_mongo.iter_companies():
    virksomhed = Virksomhed(company)
    purposes = virksomhed.formaal
    for purpose in purposes:
        # write(1, "-" * 80 + '\n')
        # write(1, purpose.encode('utf-8') + b('\n'))
        cleaned_purpose = purpose_processor.clean(purpose)
        write(1, cleaned_purpose.encode('utf-8') + b('\n'))

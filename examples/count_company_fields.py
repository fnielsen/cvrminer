"""Count company fields.

Usage:
  count_company_fields

Describe:
  Iterate over all companies in the Mongo database and return
  the number of unique fields

"""


from __future__ import print_function

from collections import Counter

from cvrminer.cvrmongo import CvrMongo
from cvrminer.virksomhed import Virksomhed


cvr_mongo = CvrMongo()
counts = Counter()
for n, company in enumerate(cvr_mongo.iter_companies()):
    counts += Virksomhed(company).count_fields()
    if not n % 100:
        print("{:6}: {}".format(n, len(counts)))

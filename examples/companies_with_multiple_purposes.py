ur"""Companies with multiple purposes.

An example is 31862132

"Selskabets form\xe5l er at eje kapitalandele og likvide midler"

"Selskabets form\xe5l er formueadministration"

"""

from __future__ import print_function, unicode_literals

from cvrminer.cvrmongo import CvrMongo
from cvrminer.virksomhed import Virksomhed

n = 1
cvr_mongo = CvrMongo()
for company in cvr_mongo.iter_companies():
    virksomhed = Virksomhed(company)
    purposes = virksomhed.formaal
    if len(purposes) > 1:
        print('-' * 80)
        for purpose in purposes:
            print(purpose)
        n += 1

print('Total number of companies with multiple purposes {}'.format(n))

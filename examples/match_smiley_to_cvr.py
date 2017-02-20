"""Print match and missing match between smiley and CVR."""


from __future__ import print_function

from cvrminer.cvrmongo import CvrMongo
from cvrminer.smiley import Smiley


cvr_mongo = CvrMongo()

smiley = Smiley()
cvrs = smiley.all_cvrs()

n_missing = 0
n_ok = 0
for cvr in sorted(cvrs):
    company = cvr_mongo.get_company(cvr)
    if company:
        n_ok += 1
        print('cvr {} ok'.format(cvr))
    else:
        n_missing += 1
        print('cvr {} missing'.format(cvr))


print("Missing: {}; Ok: {}.".format(n_missing, n_ok))

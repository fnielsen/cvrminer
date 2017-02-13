"""Company name of smiley companies."""

from cvrminer.cvrmongo import CvrMongo
from cvrminer.virksomhed import Virksomhed

cvr_mongo = CvrMongo()
for company in cvr_mongo.iter_smiley_companies():
    print(Virksomhed(company).nyeste_navn)

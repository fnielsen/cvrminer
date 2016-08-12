"""CVR miner.


JSON file structure
-------------------
_id : ID of some form
_index : 
_source : Actual data
_type: 'virksomhed', 'produktionsenhed', 'deltager' or 'meta'
fields

The 'meta' type appear only once and with the entry: 
    {"_index":"cvr-permanent-prod-20151209",
     "_type":"meta",
     "_id":"1",
     "_score":1,
     "_source":{
       "NewestRetrievedFileTimestampForBeskaeftigelse":
         "2016-05-07T08:59:23.373+02:00"}}


Virksomheder
------------
aarsbeskaeftigelse


"""

import json

from pprint import pprint


JSONL_FILENAME = 'cvr-permanent.json'
# $ wc cvr-permanent.json 
#    4721004   127333568 42796650397 cvr-permanent.json


def print_types(filename=JSONL_FILENAME):
    """Print entry types from JSON file.

    Iterate over entire file and print distinct entry types.

    This should produce:

    virksomhed
    produktionsenhed
    deltager
    meta

    Parameters
    ----------
    filename : str
        Filename for JSONL file

    """
    types = set()
    for line in open(filename):
        obj = json.loads(line)
        type_ = obj['_type']
        if type_ not in types:
            print(type_)
            types.add(type_)


def print_source_fields(filename=JSONL_FILENAME):
    """Print field values from _source fields in JSON file.

    This could produce:

    (u'Vrvirksomhed',)
    (u'VrproduktionsEnhed',)
    (u'Vrdeltagerperson',)
    (u'NewestRetrievedFileTimestampForBeskaeftigelse',)

    """
    fields_set = set()
    for line in open(filename):
        obj = json.loads(line)
        fields = tuple(obj['_source'].keys())
        if fields not in fields_set:
            print(fields)
            fields_set.add(fields)


def pretty_print(filename=JSONL_FILENAME):
    """Pretty print JSON lines."""
    for line in open('cvr-permanent.json'):
        obj = json.loads(line)
        pprint(obj)


def main():
    pretty_print()


if __name__ == '__main__':
    main()

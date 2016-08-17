"""CVR miner.

Handles JSONL files from CVR in Erhvervsstyrelsen with information about 
companies, places and participants.

Command-line usage
------------------

    $ python -m cvrminer.cvrfile


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

"""

import csv

import json

from pprint import pprint

from .virksomhed import Virksomhed

JSONL_FILENAME = 'cvr-permanent.json'
# $ wc cvr-permanent.json 
#    4721004   127333568 42796650397 cvr-permanent.json


class CvrFile(object):

    """CVR file.

    Examples
    --------
    >>> for item in CvrFile():
    ...     print(str(item['_type']))
    ...     break
    'virksomhed'

    """

    def __init__(self, filename=JSONL_FILENAME):
        self.filename = filename
        self.fid = open(filename)
        self.line_number = 0

    def __iter__(self):
        return self

    def __next__(self):
        """Return data from line in JSONL file.

        Returns
        -------
        obj : dict
            JSON decoded data object from line in file

        """
        line = self.fid.readline()
        self.line_number += 1
        try:
            data = json.loads(line)
        except ValueError:
            raise ValueError(
                "No JSON object could be decoded in line {}: {}".format(
                    self.line_number, line))
        return data
        
    next = __next__

    def __str__(self):
        """Return human readable representation of object."""
        return "<CvrFile(filename={})>".format(self.filename)

    __repr__ = __str__

    def iter_virksomhed_features(self):
        """Yield features for virksomheder.

        Yields
        ------
        features : OrderedDict
            Features in an ordered dictionary

        """
        for n, obj in enumerate(self):
            if 'Vrvirksomhed' not in obj['_source']:
                    continue
            virksomhed = Virksomhed(obj)
            features = virksomhed.features()
            yield features
    
    def write_virksomhed_features_file(
            self, filename='virksomheder-features.csv'):
        """Write feature file for virksomheder in the fille.

        Parameters
        ----------
        filename : str
            Filename for comma-separated output file.
        
        """
        with open(filename, 'w') as csvfile:
            csv_writer = csv.writer(csvfile)
            header = None
            for n, features in enumerate(self.iter_virksomhed_features()):
                if not header:
                    header = features.keys()
                    csv_writer.writerow(header)
                values = [unicode(value).encode('utf-8')
                          for value in features.values()]
                csv_writer.writerow(values)


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
    for obj in CvrFile(filename):
        type_ = obj['_type']
        if type_ not in types:
            print(type_)
            types.add(type_)


def print_source_fields(self):
    """Print field values from _source fields in JSON file.

    This could produce:

    (u'Vrvirksomhed',)
    (u'VrproduktionsEnhed',)
    (u'Vrdeltagerperson',)
    (u'NewestRetrievedFileTimestampForBeskaeftigelse',)

    """
    fields_set = set()
    for obj in CvrFile(filename=filename):
        fields = tuple(obj['_source'].keys())
        if fields not in fields_set:
            print(fields)
            fields_set.add(fields)


def pretty_print(filename=JSONL_FILENAME):
    """Pretty print JSON lines."""
    for obj in CvrFile(filename=filename):
        pprint(obj)


def main():
    pretty_print()


if __name__ == '__main__':
    main()

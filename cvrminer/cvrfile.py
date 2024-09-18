"""CVR miner.

Usage:
  cvrminer.cvrfile show-file [<filename>]
  cvrminer.cvrfile write-virksomhed-features-file

Description:
  Handles JSONL files from CVR in Erhvervsstyrelsen (Danish Business Authority)
  with information about companies, places and participants.

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

Example:
  $ python -m cvrminer.cvrfile show-file

"""

import csv

from gzip import open as gzip_open

import json

from os.path import expanduser, join

from pprint import pprint

from .virksomhed import Virksomhed

JSONL_FILENAME = join(expanduser('~'), 'cvrminer_data',
                      'cvr-permanent.json.gz')
# $ wc cvr-permanent.json
#    4721004   127333568 42796650397 cvr-permanent.json


class CvrFile(object):
    """CVR file."""

    def __init__(self, filename=JSONL_FILENAME):
        """Set up file for reading.

        Parameters
        ----------
        filename : str
            Filename for JSONL file with CVR data.

        """
        self.filename = filename
        if filename.endswith('.gz'):
            self.fid = gzip_open(filename, mode='rt')
        else:
            try:
                self.fid = open(filename)
            except IOError:
                self.fid = gzip_open(filename + '.gz', mode='rt')
        self.line_number = 0

    def __iter__(self):
        """Return iterator."""
        return self

    def __next__(self):
        """Return data from line in NDJSON file.

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

    def iter_virksomhed(self):
        """Yield virksomhed.

        Yields
        ------
        virksomhed : virksomhed.Virksomhed
            Object representing a virksomhed

        """
        for n, obj in enumerate(self, start=1):
            if 'Vrvirksomhed' not in obj['_source']:
                continue
            virksomhed = Virksomhed(obj['_source']['Vrvirksomhed'])
            yield virksomhed

    def iter_virksomhed_features(self):
        """Yield features for virksomheder.

        Yields
        ------
        features : OrderedDict
            Features in an ordered dictionary

        """
        for n, virksomhed in enumerate(self.iter_virksomhed(), start=1):
            try:
                features = virksomhed.features()
            except Exception as err:
                raise err("Error in line {} with {}.".format(
                    n, virksomhed))
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
                values = features.values()
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


def print_source_fields(filename=JSONL_FILENAME):
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
    """Handle command-line interface.

    This will pretty print the JSONL file.

    """
    from docopt import docopt

    arguments = docopt(__doc__)

    if arguments['show-file']:
        if arguments['<filename>']:
            pretty_print(arguments['<filename>'])
        else:
            pretty_print()

    elif arguments['write-virksomhed-features-file']:
        cvr_file = CvrFile()
        cvr_file.write_virksomhed_features_file()

    else:
        assert False


if __name__ == '__main__':
    main()

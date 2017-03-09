"""cvrmongofeatures.

Usage:
  cvrmongofeatures get-all-company-field-names [options]

Options:
  --debug             Debug messages.
  -h --help           Help message
  -o --output=<file>  Output filename, default output to stdout
  --verbose           Verbose messages.

"""


from __future__ import absolute_import

from collections import Counter

import logging

import os
from os import write

import signal

from six import b

from .cvrmongo import CvrMongo
from .virksomhed import Virksomhed


class CvrMongoFeatures(object):
    """Feature extractor based on data in Mongo database."""

    def __init__(self):
        """Setup database."""
        self.logger = logging.getLogger(__name__ + '.CvrMongoFeatures')
        self.logger.addHandler(logging.NullHandler())

        self.logger.info('Setup of connection to Mongo database.')
        self.cvr_mongo = CvrMongo()

    def count_all_company_field_names(self):
        """Count company fields.

        Returns
        -------
        counts : collections.Counter
            Counter object with counts of field occurrences.

        """
        counts = Counter()
        for n, company in enumerate(self.cvr_mongo.iter_companies()):
            counts += Virksomhed(company).count_fields()
            if not n % 100:
                self.logger.debug("Counted {:6}: {}".format(n, len(counts)))
        return counts

    def get_all_company_field_names(self):
        """Return company field names for all companies.

        Returns
        -------
        names : list
            List with string for company fields.

        """
        return sorted(self.count_all_company_field_names().keys())


def main():
    """Handle command-line interface."""
    from docopt import docopt

    arguments = docopt(__doc__)

    logging_level = logging.WARN
    if arguments['--debug']:
        logging_level = logging.DEBUG
    elif arguments['--verbose']:
        logging_level = logging.INFO

    logger = logging.getLogger()
    logger.setLevel(logging_level)
    logging_handler = logging.StreamHandler()
    logging_handler.setLevel(logging_level)
    logging_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging_handler.setFormatter(logging_formatter)
    logger.addHandler(logging_handler)

    # Ignore broken pipe errors
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    if arguments['--output']:
        output_filename = arguments['--output']
        output_file = os.open(output_filename, os.O_RDWR | os.O_CREAT)
    else:
        # stdout
        output_file = 1

    if arguments['get-all-company-field-names']:
        cvr_mongo_features = CvrMongoFeatures()
        names = cvr_mongo_features.get_all_company_field_names()
        for name in names:
            write(output_file, name + b('\n'))


if __name__ == '__main__':
    main()

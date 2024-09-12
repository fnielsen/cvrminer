"""cvrmongo - Interface to CVR information a Mongo database.

Usage:
  cvrmongo [options] build-database
  cvrmongo [options] count-companies
  cvrmongo [options] get-all-company-purposes
  cvrmongo [options] get-company <cvr-nummer>
  cvrmongo [options] get-company-purposes <cvr-nummer>

Options:
  --debug             Debug messages.
  -h --help           Help message
  --oe=encoding       Output encoding [default: utf-8]
  -o --output=<file>  Output filename, default output to stdout
  --verbose           Verbose messages.

Examples:
  $ python -m cvrminer.cvrmongo get-company 33628234

"""


from __future__ import absolute_import, division, print_function

import logging

import os
from os import write

from pprint import pprint

from six import b

import signal

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from .cvrfile import CvrFile
from .smiley import Smiley


class CvrMongo(object):
    """Mongo database interface for CVR data."""

    def __init__(self):
        """Set up variables."""
        self.client = MongoClient()
        self.db = self.client.cvrminer
        self.db.companies.create_index('cvrNummer', unique=True)

    def count_companies(self):
        """Return number of companies in database.

        Returns
        -------
        count : int
            Number of companies in the database.

        """
        return self.db.companies.count()

    def insert_one_company(self, company):
        """Insert one company in the companies collection.

        Parameters
        ----------
        company : dict
            Dictionary with company information.

        """
        self.db.companies.insert_one(company)

    def insert_many_companies(self, companies):
        """Insert one company in the companies collection.

        Parameters
        ----------
        companies : iterable
            Iterable of dictionary with company information.

        """
        self.db.companies.insert_many(companies)

    def iter_companies(self):
        """Yield companies.

        Yields
        ------
        company : dict
            Company data as dictionary.

        """
        for company in self.db.companies.find():
            yield company

    def iter_smiley_companies(self):
        """Yield companies that is in the Smiley database.

        Yields
        ------
        company : dict
            Company data as dictionary.

        """
        smiley = Smiley()
        smiley_cvrs = smiley.all_cvrs()
        for company in self.iter_companies():
            if company['cvrNummer'] in smiley_cvrs:
                yield company

    def get_company(self, cvr_nummer):
        """Return company data from CVR.

        Parameters
        ----------
        cvr_nummer : int
            CVR number.

        Returns
        -------
        company : dict or None
            Dictionary with company data.

        """
        data = self.db.companies.find_one({'cvrNummer': int(cvr_nummer)})
        return data


def main():
    """Handle command-line interface."""
    from docopt import docopt
    from .virksomhed import Virksomhed

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

    if arguments['--output']:
        output_filename = arguments['--output']
        output_file = os.open(output_filename, os.O_RDWR | os.O_CREAT)
    else:
        # stdout
        output_file = 1
    output_encoding = arguments['--oe']

    # Ignore broken pipe errors
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    if arguments['build-database']:
        logger.info('Building database.')

        cvr_mongo = CvrMongo()
        cvr_file = CvrFile()

        for n, virksomhed in enumerate(cvr_file.iter_virksomhed()):
            try:
                cvr_mongo.insert_one_company(virksomhed.data)
            except DuplicateKeyError:
                pass
            if not n % 1000:
                logger.debug('Inserted {} companies'.format(n))

    elif arguments['count-companies']:
        cvr_mongo = CvrMongo()
        print(cvr_mongo.count_companies())

    elif arguments['get-all-company-purposes']:
        cvr_mongo = CvrMongo()
        for company_data in cvr_mongo.iter_companies():
            virksomhed = Virksomhed(company_data)
            for purpose in virksomhed.formaal:
                write(output_file, purpose.encode(output_encoding) + b('\n'))

    elif arguments['get-company']:
        cvr_nummer = int(arguments['<cvr-nummer>'])
        cvr_mongo = CvrMongo()
        pprint(cvr_mongo.get_company(cvr_nummer))

    elif arguments['get-company-purposes']:
        cvr_nummer = int(arguments['<cvr-nummer>'])
        cvr_mongo = CvrMongo()
        company_data = cvr_mongo.get_company(cvr_nummer)
        if company_data is not None:
            virksomhed = Virksomhed(company_data)
            for purpose in virksomhed.formaal:
                write(output_file, purpose.encode(output_encoding) + b('\n'))

    else:
        assert False


if __name__ == '__main__':
    main()

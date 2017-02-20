"""smiley.

Usage:
  cvrminer.smiley build-sqlite-database [options]
  cvrminer.smiley query [options] [<query>]

Options:
  -h --help           Help message.
  --oe=<encoding>     Output encoding [default: utf-8].
  -o --output=<file>  Output filename, default output to stdout.
  -v --verbose        Verbose messaging.
  --debug             Debug messages.

Examples:
  $ python -m cvrminer.smiley query 'postnr="2800"' 2> /dev/null | wc
      363    4243  118597

References:
  http://www.findsmiley.dk/Statistik/Smiley_data/

"""

from __future__ import absolute_import, division, print_function

import logging

import os
from os import write
from os.path import join, split

import signal

import sys

import sqlite3

from zipfile import ZipFile

from db import DB

from pandas import read_csv, read_excel

import requests

from .config import data_directory

from .utils import make_data_directory


SMILEY_CSV_FILENAME = 'SmileyStatus.csv'

SMILEY_SQLITE_FILENAME = 'SmileyStatus.db'

SMILEY_ZIP_FILENAME = 'smileystatus.zip'

SMILEY_URL = ('https://www.foedevarestyrelsen.dk/_layouts/15/sdata/'
              'smileystatus.zip')


class Smiley(object):
    """Smiley.

    References
    ----------
    http://www.findsmiley.dk/Statistik/Smiley_data/

    """

    def __init__(self, logging_level=logging.WARN):
        """Initialize logger."""
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())
        self.logger.setLevel(logging_level)

        self._db = None

    def full_filename(self, filename):
        """Return full path filename for file."""
        return join(data_directory(), 'smiley', filename)

    def download(self):
        """Download remote Smiley data to local directory."""
        directory = join(data_directory(), 'smiley')
        self.logger.info('Making directory {}'.format(directory))
        make_data_directory(directory)

        url = SMILEY_URL
        filename = split(url)[-1]
        full_filename = self.full_filename(filename)

        self.logger.info('Downloading {} to local file {}'.format(
            url, full_filename))
        response = requests.get(url, stream=True)
        with open(full_filename, 'wb') as f:
            for chunk in response.iter_content():
                if chunk:
                    f.write(chunk)

    def read_csv_file(self, filename=SMILEY_CSV_FILENAME):
        """Read CSV file with smiley status.

        Parameters
        ----------
        filename : str
            Filename for the CSV file.

        Returns
        -------
        df : pandas.DataFrame
            Dataframe with smiley status information.

        """
        full_filename = self.full_filename(filename)
        return read_csv(full_filename, index_col=0, encoding='utf-8')

    def read_zipped_xls_file(self):
        """Read zip XLS file with smiley status.

        Returns
        -------
        df : pandas.DataFrame
            Dataframe with smiley status information.

        """
        full_filename = self.full_filename(SMILEY_ZIP_FILENAME)
        with ZipFile(full_filename) as f:
            namelist = f.namelist()
            if len(namelist) == 1:
                df = read_excel(f.open(namelist[0]))
            else:
                raise IOError('Multiple files in {}'.format(full_filename))
        return df

    @property
    def db(self):
        """Return a db.py instance with Smiley data."""
        if self._db is not None and hasattr(self._db.tables, 'smiley'):
            return self._db

        full_filename = self.full_filename(SMILEY_SQLITE_FILENAME)
        try:
            self._db = DB(filename=full_filename, dbtype='sqlite')
            if not hasattr(self._db.tables, 'smiley'):
                raise
        except:
            self.build_sqlite_database()
            self._db = DB(filename=full_filename, dbtype='sqlite')
        return self._db

    def build_sqlite_database(
            self, sqlite_filename=SMILEY_SQLITE_FILENAME,
            csv_filename=SMILEY_CSV_FILENAME, if_exists='replace'):
        """Build SQLite database with Smiley data.

        This will try to setup a sqlite database with smiley information from
        the zipped xls file distributed from the homepage.

        Parameters
        ----------
        sqlite_filename : str, optional
            Filename of the SQLite file.
        csv_filename : str, optional
            Filename of CSV file.
        if_exists : bool, optional
            Determines whether the database tables should be overwritten
            (replace) [default: replace]

        """
        full_filename = self.full_filename(sqlite_filename)
        self.logger.info('Building "{full_filename}" sqlite file'.format(
            full_filename=full_filename))

        try:
            df = self.read_zipped_xls_file()
        except:
            df = self.read_csv_file(filename=csv_filename)

        table = 'smiley'
        with sqlite3.connect(full_filename) as connection:
            self.logger.info('Writing "{table}" table'.format(table=table))
            df.to_sql(table, con=connection, if_exists=if_exists)

    def all_cvrs(self):
        """Return set of all cvr.

        Returns
        -------
        values : set of int
            Set of integers representing CVR numbers.

        """
        values = self.db.query('select cvrnr from smiley').values[:, 0]
        values = set([int(value) for value in values if value.is_integer()])
        return values

    def where(self, expression=None):
        if expression is None:
            query = 'select * from smiley;'
        else:
            query = 'select * from smiley where ' + expression
        return self.db.query(query)


def main():
    """Handle command-line interface."""
    from docopt import docopt

    logging.basicConfig()

    arguments = docopt(__doc__)

    encoding = sys.stdout.encoding
    if not encoding:
        # In Python2 sys.stdout.encoding is set to None for piped output
        encoding = 'utf-8'

    logging_level = logging.WARN
    if arguments['--verbose']:
        logging_level = logging.INFO
    if arguments['--debug']:
        logging_level = logging.DEBUG

    if arguments['--output']:
        output_filename = arguments['--output']
        output_file = os.open(output_filename, os.O_RDWR | os.O_CREAT)
    else:
        # stdout
        output_file = 1
    output_encoding = arguments['--oe']

    # Ignore broken pipe errors
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    smiley = Smiley(logging_level=logging_level)

    if arguments['build-sqlite-database']:
        smiley.build_sqlite_database()

    elif arguments['query']:
        query = arguments['<query>']
        df = smiley.where(query)
        write(output_file, df.to_csv(index=False, encoding=output_encoding))


if __name__ == '__main__':
    main()

"""smiley.

Usage:
  cvrminer.smiley build-sqlite-database [options]

Options:
  -h --help     Help message
  -v --verbose  Verbose messaging
  --debug

"""

from __future__ import absolute_import, division, print_function

import logging

from os.path import join

import sys

import sqlite3

from db import DB

from pandas import read_csv

from .config import data_directory


SMILEY_CSV_FILENAME = 'SmileyStatus.csv'

SMILEY_SQLITE_FILENAME = 'SmileyStatus.db'


class Smiley(object):

    def __init__(self, logging_level=logging.WARN):
        
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())
        self.logger.setLevel(logging_level)

        self._db = None

    def full_filename(self, filename):
        """Return full path filename for file."""
        return join(data_directory(), 'smiley', filename)

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

        table = 'smiley'
        with sqlite3.connect(full_filename) as connection:
            df = self.read_csv_file(filename=csv_filename)
            self.logger.info('Writing "{table}" table'.format(table=table))
            df.to_sql(table, con=connection, if_exists=if_exists)
    
    
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

    smiley = Smiley()

    if arguments['build-sqlite-database']:
        smiley.build_sqlite_database()


if __name__ == '__main__':
    main()

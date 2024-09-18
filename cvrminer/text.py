"""text.

Usage:
  text clean-purpose [options] <purpose>

Options:
  --debug             Debug messages.
  -h --help           Help message
  --ie=encoding     Input encoding [default: utf-8]
  --oe=encoding       Output encoding [default: utf-8]
  -o --output=<file>  Output filename, default output to stdout
  --verbose           Verbose messages.

"""


import codecs

import logging

import os
from os import write
from os.path import join, split

import re

import signal

from six import b, text_type


class PurposeProcessor(object):
    """Text processor for company purpose."""

    def __init__(self):
        """Set up pattern and logger."""
        self.logger = logging.getLogger(__name__ + '.PurposeProcessor')
        self.logger.addHandler(logging.NullHandler())

        self.ignore_pattern = re.compile(
            r"""
            Selskabets\sform\xe5l\ser\sat\sdrive|
            Selskabets\sform\xe5l\ser|
            og\sdermed\sbesl\xe6gtet\svirksomhed|
            \.$
            """,
            flags=re.VERBOSE)

        self.stop_words = self.read_stop_words()
        stop_words = sorted(self.stop_words, key=len, reverse=True)
        regex = '|'.join((re.escape(word) for word in stop_words))
        regex = r'\b(?:' + regex + r')\b'
        self.stop_words_pattern = re.compile(regex, flags=re.UNICODE)

    def clean(self, text):
        """Return cleaned purpose text.

        Parameters
        ----------
        text : str
           String with purpose

        Returns
        -------
        cleaned : str
           String with cleaned purpose

        Description
        -----------
        Remove the following fragments:

        "Selskabets formaal er at drive"
        "Selskabets formaal er"
        "og anden dermed beslaegtet virksomhed"
        "dermed beslaegtet virksomhed"
        "hermed beslaegtet virksomhed"

        """
        cleaned = self.stop_words_pattern.sub('', text).strip()
        return cleaned

    def read_stop_words(self):
        """Read purpose stop words from data file.

        Returns
        -------
        stop_words : list of str
            List with stop words

        Examples
        --------
        >>> purpose_processor = PurposeProcessor()
        >>> stop_words = purpose_processor.read_stop_words()
        >>> 'dermed' in stop_words
        True

        """
        filename = join(split(__file__)[0], 'data', 'purpose_stop_words.txt')
        self.logger.info('Reading stop words from {}'.format(filename))

        stop_words = []
        with codecs.open(filename, encoding='utf-8') as fid:
            for line in fid:
                stop_words.append(line.strip())
        return stop_words


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

    if arguments['--output']:
        output_filename = arguments['--output']
        output_file = os.open(output_filename, os.O_RDWR | os.O_CREAT)
    else:
        # stdout
        output_file = 1
    output_encoding = arguments['--oe']
    input_encoding = arguments['--ie']

    # Ignore broken pipe errors
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    if arguments['clean-purpose']:
        purpose = arguments['<purpose>']
        if not isinstance(purpose, text_type):
            purpose = purpose.decode(input_encoding)
        processor = PurposeProcessor()
        cleaned_purpose = processor.clean(purpose)
        write(output_file, cleaned_purpose.encode(output_encoding) + b('\n'))


if __name__ == '__main__':
    main()

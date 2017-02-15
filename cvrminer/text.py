u"""text.

Usage:
  text clean-purpose <purpose>

Example:
  $ python -m cvrminer.text clean-purpose "Selskabets formål er handel"
  handel

"""

import re

from six import u


class PurposeProcessor(object):
    """Text processor for company purpose."""

    def __init__(self):
        """Setup pattern."""
        self.ignore_pattern = re.compile(
            u"""
            Selskabets\sform\xe5l\ser\sat\sdrive|
            Selskabets\sform\xe5l\ser|
            og\sdermed\sbesl\xe6gtet\svirksomhed|
            \.$
            """,
            flags=re.UNICODE | re.VERBOSE)

        self.stop_words = set(re.split('\s+', u("""
            af anden at
            besl\xe6gtet
            dermed efter forbindelse herunder i inden og om
            samt til virksomhed
        """).strip(), flags=re.UNICODE | re.DOTALL))

        regex = '|'.join(self.stop_words)
        regex = r'\b(?:' + regex + r')\b'
        self.stop_words_pattern = re.compile(regex, flags=re.UNICODE)

    def clean(self, text):
        u"""Clean purpose text.

        Parameters
        ----------
        text : str
           String with purpose

        Description
        -----------
        Remove the following fragments:

        "Selskabets formal er at drive"
        "Selskabets formål er"
        "og anden dermed beslægtet virksomhed"
        "dermed beslægtet virksomhed"
        "hermed beslægtet virksomhed"

        """
        return self.stop_words_pattern.sub(
            '', self.ignore_pattern.sub('', text)).strip()


def main():
    """Handle command-line interface."""
    from docopt import docopt

    arguments = docopt(__doc__)

    if arguments['clean-purpose']:
        purpose = arguments['<purpose>'].decode('utf-8')
        processor = PurposeProcessor()
        cleaned_purpose = processor.clean(purpose)
        print(cleaned_purpose)


if __name__ == '__main__':
    main()

"""cvrminer.

Usage:
  cvrminer pretty-print <xbrl_filename>

Options:
  -h --help

Try `python -m cvrminer.cvrfile` or `python -m cvrminer.xbrler`.

"""


from __future__ import absolute_import, division, print_function

from .xbrler import pretty_print


def main():
    """Handle command-line interface."""
    from docopt import docopt

    arguments = docopt(__doc__)

    if arguments['pretty-print']:

        pretty_print(arguments['<xbrl_filename>'])


if __name__ == "__main__":
    main()

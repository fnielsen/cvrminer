"""cvrminer.

Usage:
  python -m cvrminer

Options:
  -h --help

No functionality presently implemented here. Try `python -m cvrminer.cvrfile`
instead.

"""


from __future__ import absolute_import, division, print_function


def main():
    """Handle command-line interface."""
    from docopt import docopt

    arguments = docopt(__doc__)

if __name__ == "__main__":
    main()

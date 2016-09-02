"""xbrler - handling of XBRL.

Usage:
  xbrl print [options] (<filename>|<filename>...)

Options:
  --tag=<tag> -t=<tag>   Tag [default: NameOfReportingEntity]

Examples:
  $ python -m cvrminer.xbrler print X-997873F3-20150219_165208_342.xml
  RESULTPARTNER ApS

"""

from __future__ import print_function

import sys

from lxml import etree

from six import print_


def print_tag_value(filename, tag='NameOfReportingEntity'):
    """Print value for a specified tag.

    Prints the values from a name from specified field.

    Possible tags are
    - NameOfReportingEntity
    - NameAndSurnameOfAuditor
    - DateOfGeneralMeeting
    - PlaceOfSignatureOfStatement
    - and many others

    Parameters
    ----------
    filename : str
        Filename of XBRL XML file.
    tag : str
        Tag to print.

    """
    tree = etree.fromstring(open(filename, 'rb').read())
    elements = [element for element in tree.findall('.//')]
    for element in elements:
        if element.tag.endswith(tag):
            print_(element.text)


def print_name_and_surname_of_auditor(filename):
    """Print name of auditor.

    Prints the name from the 'NameAndSurnameOfAuditor' field.

    Parameters
    ----------
    filename : str
        Filename of XBRL XML file.

    """
    print_tag_value(filename, tag='NameAndSurnameOfAuditor')


def main():
    """Handle command-line arguments."""
    from docopt import docopt

    arguments = docopt(__doc__)

    filenames = arguments['<filename>']
    if type(filenames) == str:
        filenames = [filenames]

    for filename in filenames:
        try:
            print_tag_value(filename,
                            arguments['--tag'])
        except etree.XMLSyntaxError as err:
            print_(err, file=sys.stderr)


if __name__ == '__main__':
    main()

"""wikidata.

Usage:
  cvrminer.wikidata cvr-to-q <cvr>

Examples:
  $ python -m cvrminer.wikidata cvr-to-q 10007127
  Q45576

"""

from __future__ import absolute_import, division, print_function

import requests


HEADERS = {'user-agent': 'cvrminer'}


def cvr_to_q(cvr):
    """Convert CVR to Wikidata ID.

    Parameters
    ----------
    cvr : str or int
        CVR identifier.

    Returns
    -------
    q : str or None
        Strings with Wikidata IDs. None is returned if the CVR is not found.

    Examples
    --------
    >>> cvr_to_q("10007127") == 'Q45576'
    True

    >>> cvr_to_q(10007127) == 'Q45576'
    True

    """
    query = 'select ?company where {{ ?company wdt:P1059 "{cvr}" }}'.format(
        cvr=cvr)

    url = 'https://query.wikidata.org/sparql'
    params = {'query': query, 'format': 'json'}
    response = requests.get(url, params=params, headers=HEADERS)
    try:
        data = response.json()
    except:
        return None

    qs = [item['company']['value'][31:]
          for item in data['results']['bindings']]
    if len(qs) > 0:
        return qs[0]
    else:
        return None


def main():
    """Handle command-line interface."""
    from docopt import docopt

    arguments = docopt(__doc__)

    if arguments['cvr-to-q']:
        q = cvr_to_q(arguments['<cvr>'])
        print(q)


if __name__ == '__main__':
    main()

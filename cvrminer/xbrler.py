"""xbrler - handling of XBRL.

Usage:
  xbrl print [options] (<filename>|<filename>...)
  xbrl search [options] 

Options:
  --tag=<tag> -t=<tag>     Tag [default: NameOfReportingEntity]
  --from_date=<from_date>  Date in ISO format, e.g., "2014-09-01"
  --pretty                 Pretty printing
  --size=<size>            Integer for the requested number of results
  --to_date=<to_date>      Date in ISO format, e.g., "2014-09-01"

Examples:
  $ With a file from the sample dataset
  $ python -m cvrminer.xbrler print X-997873F3-20150219_165208_342.xml
  RESULTPARTNER ApS

  $ python3 -m cvrminer.xbrler search --from_date=2016-08-31 \
       --to_date=2016-09-01 --size=1000 | wc
  716   17184  366077

References:
  http://datahub.virk.dk/dataset/regnskabsdata-fra-selskaber-sample 

"""

from __future__ import print_function

import json

from pprint import pprint

import sys

from lxml import etree

import requests

from six import print_


USER_AGENT = 'cvrminerbot, https://github.com/fnielsen/cvrminer/'

HEADERS_FOR_JSON = {
    'User-agent': USER_AGENT,
    'accept': "application/json; charset=utf-8",
    'content-type': "application/json"
}

SEARCH_URL = "http://distribution.virk.dk/offentliggoerelser/_search"


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


def _flatten_search_result(result):
    """Flatten the nested search result.

    http://distribution.virk.dk/offentliggoerelser/_search

    Parameters
    ----------
    result : dict
        Dictionary with search item result.

    Returns
    -------
    result_output : dict
        Flatten dictionary.

    See also
    --------
    search_for_regnskaber.

    """
    assert result['offentliggoerelsestype'] == 'regnskab'
    result_output = {}
    
    simple_fields = [
        'cvrNummer', 'indlaesningsId', 'indlaesningsTidspunkt',
        'offentliggoerelsesTidspunkt', 'omgoerelse',
        'regNummer', 'sagsNummer', 'sidstOpdateret'
    ]
    for field in simple_fields:
        result_output[field] = result[field]

    regnskabsperiode = result['regnskab']['regnskabsperiode']
    result_output['slutDato'] = regnskabsperiode['slutDato']
    result_output['startDato'] = regnskabsperiode['startDato']

    for dokument in result['dokumenter']:
        if dokument['dokumentMimeType'] == 'application/xml':
            result_output['dokumentType'] = dokument['dokumentType']
            result_output['dokumentUrl'] = dokument['dokumentUrl']
            break
    else:
        result_output['dokumentType'] = None
        result_output['dokumentUrl'] = None
    return result_output
    

def search_for_regnskaber(from_date=None, to_date=None, size=10):
    """Search virk.dk search API for regnskaber.

    This function will require Internet access as the API at
    http://distribution.virk.dk/offentliggoerelser/_search is queried.

    The returned fields are:

    - cvrNummer
    - dokumentType
    - dokumentUrl
    - indlaesningsId
    - indlaesningsTidspunkt
    - offentliggoerelsesTidspunkt
    - omgoerelse
    - regNummer
    - sagsNummer
    - sidstOpdateret
    - slutDato
    - startDato

    There are unusual cases, e.g., CVR 32147569 is a German company
    (HERMLE NORDIC FILIAL AF MASCHINENFABRIK BERTHOLD HERMLE AGTYSKLAND)
    with the report in German and on XML file.

    Parameters
    ----------
    from_date : str
        ISO date for from date on offentliggoerelsesTidspunkt
    to_date : str
        ISO date for to date on offentliggoerelsesTidspunkt
    size : int
        Number of returned items

    Returns
    -------
    result_output : list of dict
        List of flatten dictionaries with search results.

    See also
    --------
    flatten_search_result

    References
    ----------
    http://datahub.virk.dk/dataset/system-til-system-adgang-til-regnskabsdata

    """
    # Build query
    data = {}
    data['query'] = {}
    if size is not None:
        data['size'] = size
    if from_date is not None or to_date is not None:
        range_value = {}
        if from_date is not None:
            range_value['from'] = from_date
        if to_date is not None:
            range_value['to'] = to_date
        range_value = {
            'offentliggoerelse.offentliggoerelsesTidspunkt':
            range_value
        }
        data['query']['range'] = range_value
            
    # Query Erhvervsstyrelsen API
    response = requests.post(SEARCH_URL, data=json.dumps(data),
                             headers=HEADERS_FOR_JSON)
    response_data = response.json()

    # Fix result format
    if 'hits' not in response_data:
        return []
    else:
        return [_flatten_search_result(hit['_source'])
                for hit in response_data['hits']['hits']]

    
def main():
    """Handle command-line arguments."""
    from docopt import docopt

    arguments = docopt(__doc__)

    if arguments['print']:
        
        filenames = arguments['<filename>']
        if type(filenames) == str:
            filenames = [filenames]

        for filename in filenames:
            try:
                print_tag_value(filename,
                                arguments['--tag'])
            except etree.XMLSyntaxError as err:
                print_(err, file=sys.stderr)

    elif arguments['search']:
        
        regnskaber = search_for_regnskaber(
            from_date=arguments['--from_date'],
            to_date=arguments['--to_date'],
            size=arguments['--size'])

        for regnskab in regnskaber:
            if arguments['--pretty']:
                pprint(regnskab)
            else:
                print_(regnskab)

                
if __name__ == '__main__':
    main()

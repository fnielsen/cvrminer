r"""xbrler - handling of XBRL.

Usage:
  xbrler pretty-print <filename>
  xbrler print-tag-value [options] (<filename>|<filename>...)
  xbrler print-tag-values [options] (<filename>|<filename>...)
  xbrler print-tags (<filename>|<filename>...)
  xbrler search [options]
  xbrler regnskabsdata1000-print-tag-value [options]

Options:
  --cvr=<cvr>
  --tag=<tag> -t=<tag>     Tag [default: NameOfReportingEntity]
  --from_date=<from_date>  Date in ISO format, e.g., "2014-09-01"
  --pretty                 Pretty printing
  --size=<size>            Integer for the requested number of results
  --to_date=<to_date>      Date in ISO format, e.g., "2014-09-01"

Examples:
  $ With a file from the sample dataset
  $ python -m cvrminer.xbrler print-tag-value \
       X-997873F3-20150219_165208_342.xml
  RESULTPARTNER ApS

  $ python3 -m cvrminer.xbrler search --from_date=2016-08-31 \
       --to_date=2016-09-01 --size=1000 | wc
  716   17184  366077

References:
  http://datahub.virk.dk/dataset/regnskabsdata-fra-selskaber-sample

"""

from __future__ import print_function

from collections import defaultdict

import json

import logging

from os.path import join, sep, split

from pprint import pprint

import sys

from zipfile import ZipFile

from lxml import etree

import requests

from six import print_

from .config import data_directory
from .utils import make_data_directory


USER_AGENT = 'cvrminerbot, https://github.com/fnielsen/cvrminer/'

HEADERS_FOR_JSON = {
    'User-agent': USER_AGENT,
    'accept': "application/json; charset=utf-8",
    'content-type': "application/json"
}

SEARCH_URL = "http://distribution.virk.dk/offentliggoerelser/_search"

REGNSKABSDATA1000_URL = ('http://datahub.virk.dk/sites/default/files/'
                         'storage/1000_digitale_aarsrapporter.zip')


def extract_tags(filename_or_file):
    """Extract tags.

    Parameters
    ----------
    filename_or_file : str or file-like
        Filename of XBRL XML file.

    Returns
    -------
    tags : list of str
        List of tags

    """
    if hasattr(filename_or_file, 'read'):
        f = filename_or_file
    else:
        f = open(filename_or_file, 'rb')
    tree = etree.fromstring(f.read())
    elements = [element for element in tree.findall('.//')]
    tags = [element.tag for element in elements]
    return tags


def extract_tag_value(filename_or_file, tag='NameOfReportingEntity'):
    """Extract value for a specified tag.

    Extract the value from a name from specified field.

    Possible tags are
    - NameOfReportingEntity
    - NameAndSurnameOfAuditor
    - DateOfGeneralMeeting
    - PlaceOfSignatureOfStatement
    - and many others

    Parameters
    ----------
    filename_or_file : str or file
        Filename of XBRL XML file.
    tag : str or None
        Tag to extract.

    Returns
    -------
    value : str
        Value of element text

    """
    values = extract_tag_values(filename_or_file, tag=tag)
    if values:
        return values
    else:
        return None


def extract_tag_values(filename_or_file, tag='NameOfReportingEntity'):
    """Extract value for a specified tag.

    Extract the value from a name from specified field.

    Possible tags are
    - NameOfReportingEntity
    - NameAndSurnameOfAuditor
    - DateOfGeneralMeeting
    - PlaceOfSignatureOfStatement
    - and many others

    Parameters
    ----------
    filename_or_file : str or file
        Filename of XBRL XML file.
    tags : str or None
        Tag to extract.

    Returns
    -------
    value : list
        List of string with values of element text

    """
    if hasattr(filename_or_file, 'read'):
        f = filename_or_file
    else:
        f = open(filename_or_file, 'rb')
    tree = etree.fromstring(f.read())
    elements = [element for element in tree.findall('.//')]
    values = []
    for element in elements:
        if element.tag.endswith(tag):
            values.append(element.text)
    return values


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
    print_(extract_tag_value(filename, tag=tag))


def print_tag_values(filename, tag='NameOfReportingEntity'):
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
    values = extract_tag_values(filename, tag=tag)
    for value in values:
        print_(value)


def print_name_and_surname_of_auditor(filename):
    """Print name of auditor.

    Prints the name from the 'NameAndSurnameOfAuditor' field.

    Parameters
    ----------
    filename : str
        Filename of XBRL XML file.

    """
    print_tag_value(filename, tag='NameAndSurnameOfAuditor')


def pretty_print(filename_or_file):
    """Pretty print XBRL file."""
    if hasattr(filename_or_file, 'read'):
        f = filename_or_file
    else:
        f = open(filename_or_file, 'rb')
    tree = etree.fromstring(f.read())
    print_(etree.tostring(tree, pretty_print=True))


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

    result_output['dokumentType'] = None
    result_output['dokumentUrlPdf'] = None
    result_output['dokumentUrlXml'] = None
    for dokument in result['dokumenter']:
        if dokument['dokumentMimeType'] == 'application/xml':
            result_output['dokumentUrlXml'] = dokument['dokumentUrl']
            result_output['dokumentType'] = dokument['dokumentType']
        elif dokument['dokumentMimeType'] == 'application/pdf':
            result_output['dokumentUrlPdf'] = dokument['dokumentUrl']
            result_output['dokumentType'] = dokument['dokumentType']
        elif dokument['dokumentMimeType'] == 'application/zip':
            # May be "dukomentType=IFRS_EXTENSION"
            pass
        else:
            # assert False
            # This should be logged
            pass

    return result_output


def search_for_regnskaber(from_date=None, to_date=None, cvr=None, size=10):
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
    with the report in German and no XML file.

    Parameters
    ----------
    from_date : str
        ISO date for from date on offentliggoerelsesTidspunkt
    to_date : str
        ISO date for to date on offentliggoerelsesTidspunkt
    cvr : str or int
        CVR identifier.
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
    data['query'] = {'bool': {'must': []}}
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
        data['query']['bool']['must'].append({'range': range_value})
    if cvr is not None:
        data['query']['bool']['must'].append({'term': {'cvrNummer': cvr}})

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


class Regnskabsdata1000(object):
    """Interface to Regnskabsdata sample.

    References
    ----------
    http://datahub.virk.dk/dataset/regnskabsdata-fra-selskaber-sample

    """

    def __init__(self, logging_level=logging.WARN):
        """Set up logger."""
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())
        self.logger.setLevel(logging_level)

    @property
    def zip_filename(self):
        """Return full filename of zip file with XBRL."""
        filename = split(REGNSKABSDATA1000_URL)[-1]
        full_filename = self.full_filename(filename)
        return full_filename

    def full_filename(self, filename):
        """Return filename with full filename path.

        Parameters
        ----------
        filename : str
            String with filename.

        Returns
        -------
        full_filename : str
            String with filename with path prepended.

        """
        if sep in filename:
            return filename
        else:
            return join(data_directory(), 'regnskabsdata1000',
                        filename)

    def download(self, url=REGNSKABSDATA1000_URL, filename=None):
        """Download remote data to local directory.

        Parameters
        ----------
        url : str
            String with URL to zip file.
        filename : str
            String with local filename.

        """
        if filename is None:
            filename = split(url)[-1]
        full_filename = self.full_filename(filename)
        directory = split(full_filename)[0]
        self.logger.info('Making directory {}'.format(directory))
        make_data_directory(directory)

        self.logger.info('Downloading {} to local file {}'.format(
            url, full_filename))
        response = requests.get(url, stream=True)
        with open(full_filename, 'wb') as f:
            for chunk in response.iter_content():
                if chunk:
                    f.write(chunk)

    def iter_files(self, return_filenames=False):
        """Return iterable of XML content of XBRL files.

        Parameters
        ----------
        return_filenames : bool, optional
            Return the filenames too (f, name).

        Yields
        ------
        file : file-like
            XML file-like object.
        name : str
            Filename. This element is only returned if return_filenames is
            True.

        """
        self.logger.debug('Reading from {}'.format(self.zip_filename))
        zip_file = ZipFile(self.zip_filename)
        for name in zip_file.namelist():
            if name.endswith('.xml'):
                with zip_file.open(name) as f:
                    if return_filenames:
                        yield f, name
                    else:
                        yield f

    def tag_matrix(self):
        """Return tag matrix.

        It can be converted to a Pandas DataFrame with:

        df = DataFrame(matrix).T.fillna(0)

        then the tags from the XBRL file are the columns and the rows are
        files.

        Returns
        -------
        matrix : dict of dicts
            Tag matrix as dictionary of dictionary.

        """
        matrix = {}
        for f, filename in self.iter_files(return_filenames=True):
            try:
                tags = extract_tags(f)
            except Exception:
                self.logger.error('Could not parse {}'.format(filename))
                tags = []
            matrix[filename] = defaultdict(int)
            for tag in tags:
                matrix[filename][tag] += 1

        return matrix


def main():
    """Handle command-line arguments."""
    from docopt import docopt

    arguments = docopt(__doc__)

    if arguments['pretty-print']:

        pretty_print(arguments['<filename>'][0])

    elif arguments['print-tag-value']:

        filenames = arguments['<filename>']
        if isinstance(filenames, str):
            filenames = [filenames]

        for filename in filenames:
            try:
                print_tag_value(filename,
                                arguments['--tag'])
            except etree.XMLSyntaxError as err:
                print_(err, file=sys.stderr)

    elif arguments['print-tag-values']:

        filenames = arguments['<filename>']
        if isinstance(filenames, str):
            filenames = [filenames]

        for filename in filenames:
            try:
                print_tag_values(filename,
                                 arguments['--tag'])
            except etree.XMLSyntaxError as err:
                print_(err, file=sys.stderr)

    elif arguments['print-tags']:

        filenames = arguments['<filename>']
        if isinstance(filenames, str):
            filenames = [filenames]

        for filename in filenames:
            try:
                tags = extract_tags(filename)
                print_(u",".join(tags))
            except etree.XMLSyntaxError as err:
                print_(err, file=sys.stderr)

    elif arguments['search']:

        regnskaber = search_for_regnskaber(
            cvr=arguments['--cvr'],
            from_date=arguments['--from_date'],
            to_date=arguments['--to_date'],
            size=arguments['--size'])

        for regnskab in regnskaber:
            if arguments['--pretty']:
                pprint(regnskab)
            else:
                print_(regnskab)

    elif arguments['regnskabsdata1000-print-tag-value']:

        rd = Regnskabsdata1000()

        for f in rd.iter_files():
            try:
                print_tag_value(f, arguments['--tag'])
            except etree.XMLSyntaxError as err:
                print_(err, file=sys.stderr)

    else:
        # Something is wrong with command-line parsing if we end here
        assert False


if __name__ == '__main__':
    main()

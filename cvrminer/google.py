"""google.

Usage:
  cvrminer.google get-archive-texts
  cvrminer.google get-archive-websites
  cvrminer.google interactive-query-and-save

References
----------
.. [1] https://developers.google.com/places/web-service/details

"""

from __future__ import print_function

from builtins import input

import configparser

from datetime import datetime

import json

from os.path import expanduser, isfile, join

import requests


# https://developers.google.com/places/web-service/details
GOOGLE_PLACE_DETAIL_URL = ("https://maps.googleapis.com/"
                           "maps/api/place/details/json")

# https://developers.google.com/places/web-service/search
GOOGLE_PLACE_SEARCH_URL = ("https://maps.googleapis.com/"
                           "maps/api/place/findplacefromtext/json")

GOOGLE_PLACE_ARCHIVE_FILENAME = join(expanduser('~'), 'cvrminer_data',
                                     'google-place.ndjson')

CONFIG_FILENAMES = [
    join(expanduser('~'), 'cvrminer.cfg'),
    join(expanduser('~'), 'python.cfg')
]


class GoogleError(Exception):
    """Exception for Google API."""
    pass


class GooglePlaceArchive(object):
    """Interface for archive of Google Place responses."""

    def __init__(self):
        """Set up index and file."""
        self.place_id_index = {}
        self.last_line = -1
        self.make_index()

        self.file = open(GOOGLE_PLACE_ARCHIVE_FILENAME, 'a+')

    def append(self, data):
        """Append downloaded data to file.

        Parameters
        ----------
        data : dict
            Data to be written as a JSON line to a file.

        """
        place_id = data['result']['place_id']
        self.file.write(json.dumps(data) + '\n')
        self.last_line += 1
        self.place_id_index[place_id] = self.last_line

    def has_place_id(self, place_id):
        """Test if place identifier is downloaded."""
        return place_id in self.place_id_index

    def make_index(self):
        """Make index of downloaded Place identifiers."""
        if isfile(GOOGLE_PLACE_ARCHIVE_FILENAME):
            for n, line in enumerate(open(GOOGLE_PLACE_ARCHIVE_FILENAME, 'r')):
                data = json.loads(line)
                place_id = data['result']['place_id']
                self.place_id_index[place_id] = n
                self.last_line = n

    def texts(self):
        """Iterate over text in reviews.

        Yields
        ------
        text : str
            Text from reviews.

        """
        for line in self.file:
            data = json.loads(line)
            for review in data['result']['reviews']:
                yield review['text']

    def websites(self):
        """Iterate over websites.

        Yields
        ------
        website : str
            String with website address.

        """
        for line in self.file:
            data = json.loads(line)
            if 'website' in data['result']:
                yield data['result']['website']


class GooglePlaceApi(object):
    """Interface to Google Place API."""

    def __init__(self):
        """Set up API key."""
        self.key = self.get_key_from_config_file()

    def get_key_from_config_file(self):
        """Read and return API key from config file.

        Returns
        -------
        key : str
            Google API key.

        """
        config = configparser.ConfigParser()
        for filename in CONFIG_FILENAMES:
            try:
                config.read(filename)
                key = config['google']['key']
                break
            except (IOError, KeyError):
                continue
        else:
            raise GoogleError("Could not find Google API key in: "
                              ", ".join(CONFIG_FILENAMES))
        return key

    def search_places(self, query, language='da'):
        """Search for places with Google Place API.

        Parameters
        ----------
        query : str
            Query to Google Place API.

        Returns
        -------
        place_ids : list of str
            List of strings with place-IDs.

        """
        search_response = requests.get(
            GOOGLE_PLACE_SEARCH_URL,
            params=dict(key=self.key, inputtype='textquery',
                        language=language, input=query))
        search_data = search_response.json()
        print(search_data)
        place_ids = [candidate['place_id']
                     for candidate in search_data['candidates']]
        return place_ids

    def get_place_details(self, place_id, language='da'):
        """Get details about place from Google Place API.

        Parameters
        ----------
        place_id : str
            String with place_id.

        Returns
        -------
        place_details : dict
            Place details in a nested structure.

        """
        detail_response = requests.get(
            GOOGLE_PLACE_DETAIL_URL,
            params=dict(key=self.key, language=language,
                        placeid=place_id))
        place_details = detail_response.json()
        place_details['datetime'] = datetime.now().isoformat()
        return place_details


class GooglePlaceApiAndArchive(object):
    """API and Archive for Google Place search and details."""

    def __init__(self):
        """Initialize API and archive."""
        self.api = GooglePlaceApi()
        self.archive = GooglePlaceArchive()

    def search_and_save(self, query, update=False):
        """Search for place and store place details.

        Parameters
        ----------
        query : str
            Query to Google Place search.

        """
        place_ids = self.api.search_places(query)
        print(place_ids)
        if len(place_ids) > 0:
            place_id = place_ids[0]
            if not self.archive.has_place_id(place_id) or update:
                place_details = self.api.get_place_details(place_ids)
                self.archive.append(place_details)


def main():
    """Handle command-line interface."""
    from docopt import docopt

    arguments = docopt(__doc__)

    if arguments['interactive-query-and-save']:
        api_and_archive = GooglePlaceApiAndArchive()
        while True:
            try:
                query = input('query> ')
            except KeyboardInterrupt:
                break
            api_and_archive.search_and_save(query)

    elif arguments['get-archive-texts']:
        archive = GooglePlaceArchive()
        for text in archive.texts():
            print(text.replace('\n', ' '))

    elif arguments['get-archive-websites']:
        archive = GooglePlaceArchive()
        for text in archive.websites():
            print(text)


if __name__ == '__main__':
    main()

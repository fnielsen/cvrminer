"""Virksomhed."""

from collections import OrderedDict

from re import findall

from numpy import nan


class Virksomhed(object):
    
    """Encapsulate a single 'virksomhed' from CVR."""

    def __init__(self, data):
        """Initial raw data storage.

        Parameters
        ----------
        data : dist
            Nested structure corresponding to JSON file from CVR dump.
        
        """
        self.data = data
        
    @property
    def antal_ansatte(self):
        """Return 'antal ansatte'.

        Taken as the first number from the 'intervalKodeAntalAnsatte' field 
        from the nyesteAarsbeskaeftigelse.

        """
        try: 
            value = self.data['_source']['Vrvirksomhed']['virksomhedMetadata'][
                'nyesteAarsbeskaeftigelse']['intervalKodeAntalAnsatte']
            numbers = findall('\d+', value)
            return int(numbers[0])
        except: 
            return nan

    @property
    def antal_penheder(self):
        """Return number of P-enheder."""
        values = self.data['_source']['Vrvirksomhed']['penheder']
        return len(values)

    @property
    def reklamebeskyttet(self):
        """Return 'reklamebeskyttet'."""
        value = self.data['_source']['Vrvirksomhed']['reklamebeskyttet']
        return value

    @property
    def sidste_virksomhedsstatus(self):
        """Return last virksomhedsstatus."""
        virksomhedsstatus = self.data['_source']['Vrvirksomhed'][
            'virksomhedsstatus']
        if len(virksomhedsstatus) == 0:
            return 'NORMAL'
        else:
            return virksomhedsstatus[-1]['status']

    @property
    def cvr_nummer(self):
        """Return CVR number."""
        value = self.data['_source']['Vrvirksomhed']['cvrNummer']
        return value

    @property
    def virksomhedsform(self):
        """Return 'virksomhedsform'.

        Possible values are 'Interessentskab', 'Enkeltmandsvirksomhed',

        """
        try:
            value = self.data['_source']['Vrvirksomhed']['virksomhedMetadata'][
                'nyesteVirksomhedsform']['langBeskrivelse']
            return value
        except:
            return nan

    def features(self):
        """Return set of features for a virksomhed.

        Returns
        -------
        features : OrderedDict
            Ordered dictionary with feature names and feature values

        """
        return OrderedDict([
            ('cvr_nummer', self.cvr_nummer),
            ('antal_ansatte', self.antal_ansatte),
            ('antal_penheder', self.antal_penheder),
            ('reklamebeskyttet', self.reklamebeskyttet),
            ('sidste_virksomhedsstatus', self.sidste_virksomhedsstatus),
            ('virksomhedsform', self.virksomhedsform),
        ])

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

    def __str__(self):
        """Return human readable string for object.
        
        Returns
        -------
        readable : str
            String showing object

        """
        return "<Virksomhed(CVR={})>".format(self.cvr_nummer)

    __repr__ = __str__

    @property
    def antal_penheder(self):
        """Return number of P-enheder."""
        value = self.data['_source']['Vrvirksomhed']['virksomhedMetadata'][
            'antalPenheder']
        return value

    @property
    def branche_ansvarskode(self):
        """Return 'brancheAnsvarskode'.

        This fields is often None, sometimes 65 and seldom other values (99,
        97 and 0). The returned value is of type str.

        Returns
        -------
        kode : str

        """
        value = self.data['_source']['Vrvirksomhed']['brancheAnsvarskode']
        return str(value)
    
    @property
    def cvr_nummer(self):
        """Return CVR number."""
        value = self.data['_source']['Vrvirksomhed']['cvrNummer']
        return value

    @property
    def nyeste_antal_ansatte(self):
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
    def nyeste_virksomhedsform(self):
        """Return 'virksomhedsform'.

        Possible values are 'Interessentskab', 'Enkeltmandsvirksomhed',

        """
        try:
            value = self.data['_source']['Vrvirksomhed']['virksomhedMetadata'][
                'nyesteVirksomhedsform']['langBeskrivelse']
            return value
        except:
            return nan

    @property
    def nyeste_virksomhedsstatus(self):
        """Return last virksomhedsstatus."""
        virksomhedsstatus = self.data['_source']['Vrvirksomhed'][
            'virksomhedMetadata']['nyesteVirksomhedsstatus']['langbeskrivelse']
        return virksomhedsstatus

    @property
    def reklamebeskyttet(self):
        """Return 'reklamebeskyttet'."""
        value = self.data['_source']['Vrvirksomhed']['reklamebeskyttet']
        return value

    @property
    def sammensat_status(self):
        """Return 'sammensatStatus'."""
        value = self.data['_source']['Vrvirksomhed'][
            'virksomhedMetadata']['sammensatStatus']
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
    def stiftelsesdato(self):
        value = self.data['_source']['Vrvirksomhed']['virksomhedMetadata'][
            'stiftelsesDato']
        return value

    @property
    def stiftelsesaar(self):
        date = self.stiftelsesdato
        try:
            year = int(date[:4])
        except:
            year = nan
        return year
    
    def features(self):
        """Return set of features for a virksomhed.

        Returns
        -------
        features : OrderedDict
            Ordered dictionary with feature names and feature values

        """
        return OrderedDict([
            ('cvr_nummer', self.cvr_nummer),
            ('antal_penheder', self.antal_penheder),
            ('branche_ansvarskode', self.branche_ansvarskode),
            ('nyeste_antal_ansatte', self.nyeste_antal_ansatte),
            ('nyeste_virksomhedsform', self.nyeste_virksomhedsform),
            ('reklamebeskyttet', self.reklamebeskyttet),
            ('sammensat_status', self.sammensat_status),
            ('sidste_virksomhedsstatus', self.sidste_virksomhedsstatus),
            ('stiftelsesaar', self.stiftelsesaar),
        ])

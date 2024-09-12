"""Virksomhed.

Usage:
  cvrminer.virksomhed field-counts <cvr>

Examples:
  $ python -m cvrminer.virksomhed field-counts 33628234

"""


from __future__ import absolute_import, division, print_function

from collections import Counter, OrderedDict

from re import findall

from six import u

from numpy import nan

from six import integer_types, text_type


class Virksomhed(object):
    """Encapsulate a single 'virksomhed' from CVR.

    Attributes
    ----------
    data : dict
        Virksomhed data from CVR file.

    """

    def __init__(self, data):
        """Initialize raw data storage.

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
        """Return number of P-enheder.

        Returns
        -------
        antal : int
            Number of p-enheder from the 'antalPenhder field.

        """
        value = self.data['virksomhedMetadata'][
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
            The Branch-ansvarskode as a string. If the field is None then the
            string 'None' is returned.

        """
        value = self.data['brancheAnsvarskode']
        return str(value)

    @property
    def cvr_nummer(self):
        """Return CVR number."""
        value = self.data['cvrNummer']
        return value

    @property
    def formaal(self):
        """Return formaal, i.e., purposes.

        Returns
        -------
        formaal : list of str
            List of strings

        """
        formaal = []
        for attribute in self.data['attributter']:
            if attribute['type'] == u('FORM\xc5L'):
                values = attribute['vaerdier']
                for value in values:
                    formaal.append(value['vaerdi'])
                break
        return formaal

    @property
    def foerste_deltager_navn(self):
        """Return gender of first deltager.

        Returns
        -------
        name : str
            If the name cannot be extracted then the an empty string is
            returned.

        """
        try:
            name = self.data['deltagerRelation'][0][
                'deltager']['navne'][0]['navn']
        except (KeyError, IndexError, TypeError):
            name = ''
        return name

    @property
    def nyeste_antal_ansatte(self):
        """Return 'antal ansatte'.

        Taken as the first number from the 'intervalKodeAntalAnsatte' field
        from the nyesteAarsbeskaeftigelse.

        """
        try:
            value = self.data['virksomhedMetadata'][
                'nyesteAarsbeskaeftigelse']['intervalKodeAntalAnsatte']
            numbers = findall(r'\d+', value)
            return int(numbers[0])
        except Exception:
            return nan

    @property
    def nyeste_navn(self):
        """Return 'nyesteNavn'.

        If the ['virksomhedMetadata']['nyesteNavn']['navn'] field cannot be
        accessed the an empty string is returned.

        """
        try:
            value = self.data['virksomhedMetadata']['nyesteNavn']['navn']
        except TypeError:
            # 'nyesteNavn' may be None
            value = ''
        return value

    @property
    def nyeste_virksomhedsform(self):
        """Return 'virksomhedsform'.

        Possible values are 'Interessentskab', 'Enkeltmandsvirksomhed',

        """
        try:
            value = self.data['virksomhedMetadata'][
                'nyesteVirksomhedsform']['langBeskrivelse']
            return value
        except Exception:
            return nan

    @property
    def nyeste_statuskode(self):
        """Return newest 'statuskode' from 'nyestestatus.

        Return
        ------
        statuskode : int
            Integer for 'statuskode'

        """
        try:
            statuskode = self.data[
                'virksomhedMetadata']['nyesteStatus']['statuskode']
            return str(statuskode)
        except Exception:
            return 'None'

    @property
    def reklamebeskyttet(self):
        """Return 'reklamebeskyttet'."""
        value = self.data['reklamebeskyttet']
        return value

    @property
    def sammensat_status(self):
        """Return 'sammensatStatus'."""
        value = self.data['virksomhedMetadata']['sammensatStatus']
        return value

    @property
    def sidste_virksomhedsstatus(self):
        """Return last virksomhedsstatus.

        Returns
        -------
        virksomhedsstatus : string
            Last 'virksomhedsstatus'. If the length of list of
            'virksomhedstatus' is zero an empty string is returned.

        """
        virksomhedsstatus = self.data['virksomhedsstatus']
        if len(virksomhedsstatus) == 0:
            return ''
        else:
            return virksomhedsstatus[-1]['status']

    @property
    def stiftelsesdato(self):
        """Return stiftelsesdato.

        Returns
        -------
        date : str
            Stiftelsesdato from 'virksomhedMetadata' as a string.

        """
        value = self.data['virksomhedMetadata']['stiftelsesDato']
        return value

    @property
    def stiftelsesaar(self):
        """Return year part of stiftelsesdato.

        Returns
        -------
        year : int
            Integer for year of stiftelsesdato. NaN is returned if the year
            cannot be converted from the date.

        """
        date = self.stiftelsesdato
        try:
            year = int(date[:4])
        except Exception:
            year = nan
        return year

    @property
    def nyeste_hovedbranche_branchekode(self):
        """Return branchekode.

        Returns
        -------
        branchekode : str or None
            Field of operation. None if not possible to decode.

        """
        try:
            branchekode = self.data[
                'virksomhedMetadata']['nyesteHovedbranche']['branchekode']
            return branchekode
        except Exception:
            return None

    @property
    def nyeste_hovedbranche_branchetekst(self):
        """Return newest 'branchetekst'.

        Returns
        -------
        branchetekst : str or None

        """
        try:
            branchetekst = self.data[
                'virksomhedMetadata']['nyesteHovedbranche']['branchetekst']
            return branchetekst
        except Exception:
            return None

    def count_fields(self):
        """Return counts for occurrence of fields.

        Returns
        -------
        counts : collections.Counter
            Dictionary (Counter) with keys a '.'-separated field names and
            values as the number of times the field occurs.

        Examples
        --------
        >>> virksomhed = Virksomhed({'cvrNummer': 33628234})
        >>> virksomhed.count_fields()
        Counter({'cvrNummer': 1})

        """
        def _process_field(field, value):
            if isinstance(value, list):
                for element in value:
                    for returned_field in _process_field(field, element):
                        yield returned_field
            elif isinstance(value, dict):
                for key, dict_value in value.items():
                    for returned_field in _process_field(
                            field + '.' + key, dict_value):
                        yield returned_field
            elif isinstance(value, integer_types):
                yield field
            elif isinstance(value, text_type):
                yield field
            elif value is None:
                pass
            elif field == '._id':
                pass
            else:
                # Unhandle type
                assert False

        # Need to remove initial '.'
        counts = Counter((field[1:]
                          for field in _process_field('', self.data)))

        return counts

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
            ('nyeste_hovedbranche_branchekode',
             self.nyeste_hovedbranche_branchekode),
            ('nyeste_hovedbranche_branchetekst',
             self.nyeste_hovedbranche_branchetekst),
            ('nyeste_statuskode', self.nyeste_statuskode),
            ('stiftelsesaar', self.stiftelsesaar),
        ])


def main():
    """Handle command-line interface."""
    from docopt import docopt
    from . import cvrmongo

    arguments = docopt(__doc__)

    if arguments['field-counts']:
        cvr = arguments['<cvr>']

        cvr_mongo = cvrmongo.CvrMongo()
        virksomhed = Virksomhed(cvr_mongo.get_company(cvr))
        counts = virksomhed.count_fields()
        for field, count in counts.items():
            print("{:3} {}".format(count, field))


if __name__ == '__main__':
    main()

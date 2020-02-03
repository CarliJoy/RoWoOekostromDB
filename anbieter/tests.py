from django.test import TestCase

from anbieter.models import Anbieter, HomepageKriterium


class MappingTestCase(TestCase):
    def test_anbieter_mapping(self):
        """
        Test that all mapping point to correct fields
        """
        for field in set(Anbieter.FIELD_NAME_MAPPING.values()):
            if field is None:
                continue
            else:
                Anbieter._meta.get_field(field)

    def test_homepage_kriterium_mapping(self):
        """
        Test that all mapping point to correct fields
        """
        for field in set(HomepageKriterium.FIELD_NAME_MAPPING.values()):
            HomepageKriterium._meta.get_field(field)

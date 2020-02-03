from django.test import TestCase

from anbieter.conv_helpers import conv_ee_anteil, conv_zertifikat_string
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


class TestConverstations(TestCase):
    def test_conv_ee_anteil(self):
        self.assertIsNone(conv_ee_anteil("k.A."))
        self.assertEqual(conv_ee_anteil("-4%"), 0)
        self.assertEqual(conv_ee_anteil(0.4), 40)
        self.assertEqual(conv_ee_anteil("101%"), 100)

    def test_conv_zertifikat_string(self):
        string_test_cases = [
            "TÜV Süd-Verbund",
            "PurepowerTrue",
            "OKPower plus",
            "TÜV SÜD EE01",
            "OK-Power",
            "TÜV Nord-Geprüfter Ökostrom",
            "TÜV SÜD",
            "EKOenergie",
            "TÜV Nord",
            "TÜV Rheinland",
            "TÜV Süd",
            "Verbund",
            "RenewablePLUS",
            "OK-Power Plus",
            "FirstClimate-Naturstrom Wasser und Wald",
            "Ecotopten",
            "FirstClimate-Naturstrom",
            "watergreen",
            "TÜV Nord-Freiwillige Zertifizierung",
            "Grüner Strom Gold",
            "KlimaInvest-Ökostrom",
            "KlimaInvest-ÖkostromRE",
            "OK Power",
            "OKPower?",
            "TÜV Süd EE",
            "Grüner Strom",
            "EcoTopTen",
            "TÜV NORD",
            "ASEW",
            "Klima Invest",
            "OKPower",
        ]
        none_test_cases = ["x", "?"]

        for test_case in string_test_cases:
            self.assertIsInstance(conv_zertifikat_string(test_case), str)

        for test_case in none_test_cases:
            self.assertIsNone(conv_zertifikat_string(test_case))

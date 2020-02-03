import unicodedata
from logging import getLogger
from typing import Dict, Union, Optional

from django.core import validators
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from polymorphic.models import PolymorphicModel
from requests.structures import CaseInsensitiveDict

from anbieter.conv_helpers import (
    conv_bool,
    conv_plz_number,
    conv_phone_str,
    conv_ee_anteil,
    conv_zertifikate_string,
    conv_none_to_empty_str,
)
from anbieter.exceptions import ConversationError
from helpers.model_fields import PostleitzahlField

EE_ANTEIL_RANGE_MSG = "Der EEG Anteil kann nur zwischen 0% und 100% liegen."

logger = getLogger("anbieter.models")


class Zertifizierung(models.Model):
    name = models.CharField("Name", unique=True, max_length=64)
    kommentar = models.TextField("Kommentar")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "anbieter_zertifizierung"


class HomepageKriterium(models.Model):
    FIELD_NAME_MAPPING = {
        "ID": "id",
        "Kategorie": "kategorie",
        "Teaser": "teaser",
        "Text": "text",
        "Link": "link",
        "Linktitel": "linktitel",
        "Methoden": "methoden",
        "Methodenlink": "methoden_link",
        "Profil": "profil",
        "Strommix": "strommix",
        "Empfehlung": "empfehlung",
    }

    FIELD_CONTENT_MAPPER = {
        "Profil": CaseInsensitiveDict({"true": True, "false": False, "": None}),
        "Strommix": CaseInsensitiveDict({"true": True, "false": False, "": None}),
        "Empfehlung": CaseInsensitiveDict({"yes": "Y", "maybe": "M", "no": "N"}),
    }

    id = models.CharField(
        "ID",
        validators=[
            validators.RegexValidator("[a-z][A-Z]*", "Nur Buchstaben sind als ID erlaubt")
        ],
        max_length=16,
        primary_key=True,
    )
    kategorie = models.CharField("Kategorie", max_length=16, blank=True)
    teaser = models.TextField("Teaser")
    text = models.TextField("Text", blank=True)
    link = models.URLField("Link", blank=True, null=True)
    linktitel = models.CharField("Linktitel", blank=True, max_length=128)
    methoden = models.TextField("Methoden")
    methoden_link = models.TextField("Methodenlink", blank=True)
    profil = models.BooleanField("Profil")
    strommix = models.BooleanField(
        "Strommix",
        null=True,
        choices=((None, "?"), (True, "Vorhanden"), (False, "Fehlt")),
    )
    empfehlung = models.CharField(
        "Empfehlung", max_length=1, choices=(("Y", "yes"), ("N", "no"), ("M", "maybe"))
    )

    @classmethod
    def csv_data_to_obj_data(cls, data: Dict[str, str]) -> Dict[str, Union[str, bool]]:
        """
        Convert CSV Data to obj data that can be used to create or update
        an object
        :param data: the csv data
        :return: converted dictionary ready to be read in object
        :exception ConversationError - if failed to convert
        """
        result: Dict[str, Union[str, bool]] = {}
        for csv_field, csv_val in data.items():
            key = csv_field
            val = csv_val
            val_mapper = cls.FIELD_CONTENT_MAPPER.get(key, None)
            if val_mapper is not None:
                try:
                    val = val_mapper[val]
                except KeyError as e:
                    raise ConversationError(
                        f"Could not convert '{val}' for field {key} "
                        f"- seems to invalid. Only {val_mapper.keys()} "
                        f"are valid values."
                    )
            try:
                result[cls.FIELD_NAME_MAPPING[key]] = val
            except KeyError:
                raise ConversationError(f"Could not corresponding field for" f" '{key}'")
        return result

    @classmethod
    def get_for_excel_table(cls, id: Optional[str]):
        def strip_accents(s):
            return "".join(
                c
                for c in unicodedata.normalize("NFD", str(s))
                if unicodedata.category(c) != "Mn"
            )

        if id is None:
            return None
        else:
            try:
                cls.objects.get(id__iexact=strip_accents(id))
            except cls.DoesNotExist:
                logger.error(f"Did not find HomepageKriterium '{id}'")
                return None

    def __str__(self):
        return self.id

    class Meta:
        db_table = "anbieter_kriterium"


class Anbieter(PolymorphicModel):
    FIELD_NAME_MAPPING = CaseInsensitiveDict(
        {
            "Firmenname": "name",
            "Erneuerbare Energien 2": "ee_anteil",
            "KategorieÜberarbeitung": None,  # set automatically
            "Kennzeichnung Link": "kennzeichnung_link",
            "Adresse": "strasse",
            "PLZ": "plz",
            "Stadt": "stadt",
            "URL": "homepage",
            "Kontakt (nur für relevante Anbieter)": "email",
            "Telefon": "telefon",
            "Fragebogen": "fragebogen",
            "RoWo-Kriterien": "rowo_kriterium",
            "Kriterium-Websuche": "homepage_kriterium",
            "A": None,
            "B": None,
            "C": None,
            "D": None,
            "Begründung": "begruendung",
            "Eigene Anlagen/Anteile an Anlagen": "eigene_anlagen",
            "Zertifizierung": "zertifizierung",  # Many to many needs special handling
            "Bemerkung": "bemerkung",
            "Grüner Strom": "gruener_strom",
            "OK Power": "ok_power",
            "RoWo-Anbieterprofil": "rowo_profil",
        }
    )
    FIELD_FUNCTION_MAPPING = {
        "fragebogen": lambda x: str(x).replace("None", ""),
        "bemerkung": conv_none_to_empty_str,
        "telefon": conv_phone_str,
        "homepage_kriterium": HomepageKriterium.get_for_excel_table,
        "email": conv_none_to_empty_str,
        "eigene_anlagen": conv_bool,
        "ok_power": conv_bool,
        "begruendung": conv_none_to_empty_str,
        "kennzeichnung_link": conv_none_to_empty_str,
        "rowo_kriterium": None,
        "ee_anteil": conv_ee_anteil,
        "name": None,
        "zertifizierung": conv_zertifikate_string,
        "gruener_strom": conv_bool,
        "rowo_profil": conv_none_to_empty_str,
        "strasse": conv_none_to_empty_str,
        "homepage": conv_none_to_empty_str,
        "plz": conv_plz_number,
        "stadt": conv_none_to_empty_str,
    }

    MAX_EE_KATEGORIE = 101
    EE_KATEGORIEN = (
        (1, "Kategorie 1, 0% - 0.99%"),
        (5, "Kategorie 2, 1% - 4.99%"),
        (10, "Kategorie 3, 5% - 9.99%"),
        (20, "Kategorie 4, 10% - 19.99%"),
        (30, "Kategorie 5, 20% - 29.99%"),
        (40, "Kategorie 6, 30% - 39.99%"),
        (50, "Kategorie 7, 40% - 49.99%"),
        (60, "Kategorie 8, 50% - 59.99%"),
        (70, "Kategorie 9, 60% - 69.99%"),
        (80, "Kategorie 10, 70% - 79.99%"),
        (90, "Kategorie 11, 80% - 89.99%"),
        (100, "Kategorie 12, 90% - 99.99%"),
        (101, "Kategorie 13 100%"),
    )

    name = models.CharField("Firmenname", max_length=256, unique=True)
    ee_anteil = models.DecimalField(
        verbose_name="Anteil Erneuerbare Energien " "(laut Strommix von Lichtblick)",
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            validators.MinValueValidator(0, EE_ANTEIL_RANGE_MSG),
            validators.MaxLengthValidator(100, EE_ANTEIL_RANGE_MSG),
        ],
    )
    ee_kategorie = models.PositiveSmallIntegerField(
        choices=EE_KATEGORIEN, editable=False, null=True,
    )
    strasse = models.CharField(
        "Straße", max_length=128, help_text="Straßenname mit Hausnummer", blank=True
    )
    plz = PostleitzahlField("PLZ", blank=True, max_length=16)
    stadt = models.CharField("Stadt", max_length=128, blank=True)
    homepage = models.URLField("Homepage", blank=True)
    kennzeichnung_link = models.URLField("Link der Kennzeichnung", blank=True)
    fragebogen = models.CharField(
        choices=((val, val) for val in ["", "x", "(x)", "k.A."]), max_length=5
    )
    rowo_kriterium = models.CharField(
        "RoWo Kriterium",
        choices=(
            (
                "X",
                "X - Überregionale Anbieter mit 100% Ökostrom, Beiträgen zu "
                "Förderung der Energiewende und ohne erkennbare Verflechtungen mit "
                "Unternehmen die mit Kohle oder Atomstrom handeln oder "
                "entsprechende Kraftwerke besitzen",
            ),
            (
                "XX",
                "XX - Alternative Anbieter mit eher Vermittelnder / Beratender "
                "Funktion (z.B. regionale Direktvermarktung aus kleinstanlagen, "
                "Mietstromangebote, u.ä.), mit 100% Ökostrom",
            ),
            ("R", "R - Regionale Anbieter die den X oder XX Kriterien entsprechen"),
            (
                "RC",
                "RC - Regionale Anbieter die keinen erkennbare, "
                "zusätzlichen Beitrag zur Energiewende leisten",
            ),
            (
                "D",
                "D - Betreiber von Anlagen aus denen Strom Bezogen produzieren "
                "oder verkaufen Strom aus Kohl-Atomenergie",
            ),
            (
                "C",
                "C - Große, überregionale Anbieter die keinen erkennbare "
                "(auch keine eigenen EE Anlagen) zusätzlichen Beitrag zur "
                "Energiewende leisten",
            ),
            (
                "B",
                "B - Eigentumsrechtliche Verflechtungen oder oder Verkauf von "
                "nicht regenerativen Energien eines, "
                "am Anbieter, beteiligten Unternehmens (Grund in Spalte "
                "Begründung angegeben)",
            ),
            ("A", "A - keine 100% Ökostrom"),
            (
                "0",
                "0 - Sonstiger Stromanbieter mit Ökostromtarif (Keine Bewertung"
                " über die ROBIN WOOD Kriterien da es sich um keinen klassischen"
                " Stromanbieter / Stromkenneichung fehlt / Informationen fehlen "
                "(z.B. keine Internetpräsenz) oder sonstige Gründe",
            ),
            ("", "? - noch nicht geprüft"),
        ),
        default="",
        max_length=3,
    )
    homepage_kriterium = models.ForeignKey(
        HomepageKriterium,
        verbose_name="Kriterium-Websuche",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        "Kontakt", blank=True, help_text="Nur für relevante Anbieter benötigt"
    )
    eigene_anlagen = models.BooleanField("Eigene Anlagen (oder Anteile)", blank=True)
    eigene_anlagen_kommentar = models.TextField(
        "Weitere Informationen über Anlagen", blank=True
    )
    telefon = PhoneNumberField("Telefon", blank=True)
    begruendung = models.TextField("Begründung", blank=True)
    anlagen = models.BooleanField("Eigene Anlagen", default=False, blank=True)
    zertifizierung = models.ManyToManyField(
        Zertifizierung,
        verbose_name="Zertifizierung(en)",
        blank=True,
        db_table="anbieter_zertifizierungen",
    )
    bemerkung = models.TextField("Bemerkung", blank=True)
    gruener_strom = models.BooleanField("Grüner Strom Label", blank=True)
    ok_power = models.BooleanField("OK Power Label", blank=True)
    rowo_profil = models.URLField("RoWo-Anbieterprofil", blank=True)

    def __str__(self):
        return self.name

    def _select_correct_category(self) -> None:
        """
        Selects the correct ee_kategorie if given, will be called by save
        automatically
        """
        if self.ee_anteil is None:
            self.ee_kategorie = None
        else:
            for max_percent, name in self.EE_KATEGORIEN:
                if self.ee_anteil < max_percent:
                    self.ee_kategorie = max_percent
                    break
            else:
                logger.warning(f"Invalid percentage value {self.ee_anteil} for {self}")

    @classmethod
    def csv_data_to_obj_data(
        cls, data: Dict[str, str]
    ) -> Dict[str, Union[str, bool, float]]:
        """
        Convert CSV Data to obj data that can be used to create or update
        an object
        :param data: the csv data
        :return: converted dictionary ready to be read in object
        :exception ConversationError - if failed to convert
        """
        result: Dict[str, Union[str, bool]] = {}
        for csv_field, csv_val in data.items():
            key = csv_field
            try:
                target_key = cls.FIELD_NAME_MAPPING[key]
            except KeyError:
                raise ConversationError(f"Could not corresponding field for" f" '{key}'")
            if target_key is None:
                continue
            convert_func = cls.FIELD_FUNCTION_MAPPING.get(target_key, None)
            if convert_func is None:
                result[target_key] = csv_val
            else:
                result[target_key] = convert_func(csv_val)
            if target_key == "eigene_anlagen" and result[target_key]:
                if str(csv_val).lower().strip() != "x":
                    result["eigene_anlagen_kommentar"] = csv_val
        return result

    def save(self, *args, **kwargs):
        """
        Make save object make sure the correct category is selected
        """
        self._select_correct_category()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "anbieter"

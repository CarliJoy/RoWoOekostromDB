from collections.abc import Iterable
from functools import cached_property
from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.base import ModelBase
from django.db.models.functions import Now
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import classproperty
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from .field_helper import generate_unique_code, upload_to_power_plants
from .fields import (
    CharField,
    FileField,
    FloatField,
    HiddenPositiveIntegerField,
    IntegerField,
    PercentField,
    TextField,
    YesNoField,
    is_percentage,
)
from .layouts import Alert, Header, Label, PercentChecker, Section, State, StateLabels


class AnbieterBase(models.Model):
    name = models.CharField(max_length=255, unique=True)

    street = models.CharField(max_length=255, db_default="", blank=True)
    city = models.CharField(max_length=255, db_default="", blank=True)
    plz = models.CharField(max_length=255, db_default="", blank=True)
    phone = models.CharField(max_length=255, db_default="", blank=True)
    fax = models.CharField(max_length=255, db_default="", blank=True)
    note = models.TextField(db_default="", blank=True, help_text="Interne Notizen")
    mail = models.EmailField(max_length=255, db_default="", blank=True)
    homepage = models.URLField(max_length=1024, db_default="", blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name

    @property
    def extra(self) -> str:
        return ""

    @property
    def details(self) -> str:
        result: str = format_html(
            "<p><h5>{}</h5>Scraped as: <q>{}</q><br />",
            self.__class__.__name__,
            self.name,
        )
        if self.street or self.city or self.plz:
            result += format_html(
                "<strong>Address</strong>: {}, {}, {} <br />",
                self.street,
                self.city,
                self.plz,
            )
        if self.phone or self.fax or self.mail:
            result += mark_safe("<strong>Kontakt</strong>:")
            if self.phone:
                result += format_html(
                    " 📞 <a href='tel:{}'>{}</a> ", self.phone, self.phone
                )
            if self.fax:
                result += format_html(" 📠 {} ", self.fax)
            if self.mail:
                result += format_html(
                    " 📧 <a href='mailto:{}'>{}</a> ", self.mail, self.mail
                )
            result += "<br />"
        if self.homepage:
            result += format_html(
                "Homepage: <a href='{}' target='_blank'>{}</a> <br />",
                self.homepage,
                self.homepage,
            )
        if self.extra:
            result += self.extra + "<br />"
        return mark_safe(result + "</p>")


class ScrapeBase(AnbieterBase):
    scrape_date = models.DateTimeField()

    class Meta:
        abstract = True


class Oekotest(ScrapeBase):
    tarif = models.CharField(max_length=255, db_default="")
    tarif_url = models.URLField(max_length=512, db_default="")
    bewertung = models.CharField(max_length=255, db_default="")

    class Meta:
        verbose_name_plural = "Scrape: Ökopower"

    @property
    def extra(self) -> str:
        return format_html(
            "Bewertung: <a href='{}' target='_blank'>Tarif {} -> {}</a>",
            self.tarif_url,
            self.tarif,
            self.bewertung,
        )


class OkPower(ScrapeBase):
    tarif = models.CharField(max_length=255, db_default="")
    tarif_url = models.URLField(max_length=512, db_default="")
    cert_info = models.CharField(max_length=255, db_default="")

    class Meta:
        verbose_name_plural = "Scrape: OkPower"

    @property
    def extra(self) -> str:
        result = format_html("{}: {}", self.tarif, self.cert_info)
        if self.tarif_url:
            # wir kombinieren hier f string und format_html,
            # damit wir result nicht doppelt escapen
            result = format_html(
                f"<a href='{{}}' target='_blank'>{result}</a>", self.tarif_url
            )
        return result


class Rowo2019(ScrapeBase):
    kennzeichnung_url = models.URLField(
        max_length=1024, db_default="", verbose_name="Link Stromkennzeichnung"
    )

    class Meta:
        verbose_name_plural = "Scrape: RoWo 2019"


class Stromauskunft(ScrapeBase):
    portal_url = models.URLField(max_length=512, db_default="")

    class Meta:
        verbose_name_plural = "Scrape: Stromauskunft"

    @property
    def extra(self):
        return format_html("<a href='{}' target='_blank'>Quelle</a>'", self.portal_url)


class Verivox(ScrapeBase):
    portal_url = models.URLField(max_length=512, db_default="")

    class Meta:
        verbose_name_plural = "Scrape: Verivox"

    @property
    def extra(self):
        return format_html("<a href='{}' target='_blank'>Quelle</a>", self.portal_url)


KRITERIUM = {
    True: "Erfüllt",
    False: "Nicht erfüllt",
    None: "?",
}

STATUS_CHOICES = {
    0: "0 - Nicht geprüft",
    4: "4 - Existenz geprüft",
    8: "8 - Ökostrom geprüft",
    16: "16 - Ökostrom Anteil geprüft",
    32: "32 - EE Anteil geprüft",
    64: "64 - Zusätzlichkeit geprüft",
    128: "128 - Unabhängigkeit geprüft ",
    256: "256 - Kein Geld Atom/Kohl geprüft",
    512: "512 - Fragebogen versendet",
    1024: "1024 - Fragebogen zurück erhalten",
    2048: "2048 - Fragebogen eingearbeitet",
    4096: "4096 - Prüfung beendet",
}


class Anbieter(AnbieterBase):
    slug_id = models.SlugField(unique=True, default=None, max_length=255)
    active = models.BooleanField(
        db_default=True, default=True, help_text="Gibt es den Anbieter noch?"
    )
    german_wide = models.BooleanField(
        db_default=True, verbose_name="🇩🇪", help_text="Deutschlandweiter Anbieter"
    )
    kennzeichnung_url = models.URLField(
        max_length=1024,
        db_default="",
        verbose_name="Link Stromkennzeichnung",
        blank=True,
    )
    rowo_2019 = models.OneToOneField(
        Rowo2019, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    oekotest = models.OneToOneField(
        Oekotest, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    ok_power = models.OneToOneField(
        OkPower, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    stromauskunft = models.OneToOneField(
        Stromauskunft, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    verivox = models.OneToOneField(
        Verivox, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    status = models.PositiveIntegerField(
        db_default=0,
        choices=STATUS_CHOICES,
    )
    mutter = models.ForeignKey(
        "Anbieter",
        on_delete=models.SET_NULL,
        db_default=None,
        null=True,
        blank=True,
        verbose_name="Mutter Firma",
        related_name="children",
    )
    sells_from = models.ForeignKey(
        "Anbieter",
        on_delete=models.SET_NULL,
        db_default=None,
        null=True,
        blank=True,
        verbose_name="Verkauft Strom von",
        related_name="sellers",
    )
    ee_anteil = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[is_percentage],
        verbose_name="EE Anteil [%]",
        help_text="Anteil Erneuerbare Energien in Prozent",
    )
    nur_oeko = models.BooleanField(
        null=True,
        db_default=None,
        blank=True,
        choices=KRITERIUM,
        verbose_name="100% Ökostrom",
        help_text=(
            "Der Anbieter verkauft ausschließlich Strom aus erneuerbaren Quellen "
            "über direkte Lieferverträge mit Erzeugerkraftwerken oder Zwischenhändlern."
        ),
    )
    unabhaengigkeit = models.BooleanField(
        null=True,
        db_default=None,
        blank=True,
        choices=KRITERIUM,
        verbose_name="Unabhängigkeit",
        help_text=(
            "Der Anbieter ist nicht direkt mit Konzernen verbunden, "
            "die Atom- oder Kohlekraftwerke betreiben oder Strom aus diesen Quellen handeln."
        ),
    )
    zusaetzlichkeit = models.BooleanField(
        null=True,
        db_default=None,
        blank=True,
        choices=KRITERIUM,
        verbose_name="Zusätzlichkeit",
        help_text=(
            "Der Anbieter fördert die Energiewende durch Strombezug aus Neuanlagen "
            "und/oder feste Investitionsprogramme."
        ),
    )
    money_for_ee_only = models.BooleanField(
        null=True,
        db_default=None,
        blank=True,
        choices=KRITERIUM,
        verbose_name="💰 Kein Geld für Kohle und Atom",
        help_text=(
            "Der Anbieter bezieht Strom von Anlagen mit geringen Verflechtungen "
            "mit Kohle- oder Atomkonzernen. "
            "Neuinvestitionen in Kohle- und Atomkraftwerke sind nicht zulässig."
        ),
    )
    begruendung = models.TextField(
        blank=True,
        verbose_name="Notiz/Begründung Intern",
        help_text="Interne Begründung/Notizen zum Anbieter und deren Bewertung",
    )
    begruendung_extern = models.TextField(
        blank=True,
        verbose_name="Begründung für Homepage",
        help_text="Zusatzbegründung für Bewertung für Homepage",
    )
    north_data = models.URLField(
        max_length=1024,
        db_default="",
        verbose_name="North Data Profil",
        blank=True,
    )
    wikipedia = models.URLField(
        max_length=1024,
        db_default="",
        verbose_name="Wikipedia Eintrag",
        blank=True,
    )

    last_updated = models.DateTimeField(
        auto_now=True, null=True, editable=False, db_default=Now()
    )
    created_at = models.DateTimeField(
        auto_now_add=True, null=True, editable=False, db_default=Now()
    )

    class Meta:
        verbose_name_plural = "Anbieter"

    def save(self, *args, **kwargs) -> None:
        if not self.slug_id:
            self.slug_id = slugify(self.name)
        super().save(*args, **kwargs)
        # Ensure SurveyAccess and initial CompanySurvey2024 exist
        if not SurveyAccess.objects.filter(anbieter=self).exists():
            survey = CompanySurvey2024.objects.create(anbieter=self, revision=1)
            SurveyAccess.objects.create(
                anbieter=self, survey=survey, code=generate_unique_code()
            )

    def clean(self):
        """
        Ensure no duplicate names are created
        """
        super().clean()
        try:
            obj = AnbieterName.objects.get(name=self.name)
        except AnbieterName.DoesNotExist:
            return
        if obj.anbieter != self:
            raise ValidationError(
                f"{self.name} ist bereits für {obj.anbieter} in Benutzung."
            )

    @classproperty
    def kriterien_fields(cls) -> tuple[str, ...]:
        return (
            "nur_oeko",
            "unabhaengigkeit",
            "zusaetzlichkeit",
            "money_for_ee_only",
        )

    @classproperty
    def active_count(cls) -> int:
        return Anbieter.objects.filter(active=True).count()

    @cached_property
    def parent(self) -> "Anbieter":
        if self.mutter is not None:
            return self.mutter.parent
        if self.sells_from is not None:
            return self.sells_from.parent
        return self

    @property
    def has_parent(self) -> bool:
        return self.parent != self

    @property
    def ist_empfohlen(self) -> bool:
        # empfehle erstmal alles was nicht nicht empfohlen ist
        anbieter = self.parent
        for field in self.kriterien_fields:
            if getattr(anbieter, field) is False:
                return False
        return True

    def get_nicht_erfuellte_kriterien_iter(self) -> Iterable[str]:
        anbieter = self.parent
        for field in self.kriterien_fields:
            if getattr(anbieter, field) is False:
                yield self._meta.get_field(field).help_text

    @property
    def nicht_erfuellte_kriterien(self) -> tuple[str, ...]:
        return tuple(self.get_nicht_erfuellte_kriterien_iter())

    @property
    def homepage_notizen(self) -> tuple[str, ...]:
        if not self.has_parent:
            # no parent
            if self.begruendung_extern:
                return (self.begruendung_extern,)
            return tuple()

        anbieter = self.parent
        result: list[str] = []
        if anbieter.begruendung_extern:
            result.append(f"{anbieter}: {anbieter.begruendung_extern}")
        if self.begruendung_extern:
            result.append(f"{self}: {anbieter.begruendung_extern}")
        return tuple(result)

    @property
    def code_2024(self) -> str:
        return self.survey_access.code


class UmfrageVersendung2024(Anbieter):
    anbieter = models.OneToOneField(
        Anbieter,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        editable=False,
    )
    sent_date = models.DateTimeField(null=True, blank=True)
    mail_status = models.BooleanField(
        null=True,
        db_default=None,
        blank=True,
        choices={
            True: "Sent",
            None: "Not sent",
            False: "Sent failed",
        },
        verbose_name="📤 State",
        help_text="Status des Mail versand",
    )
    mail_details = models.TextField(help_text="i.e. Fehlermeldung aus Mail Versand")

    class Meta:
        verbose_name_plural = "Umfrage: Mailversand"


class AnbieterName(models.Model):
    name = models.CharField(max_length=255, unique=True)
    anbieter = models.ForeignKey(
        Anbieter, on_delete=models.PROTECT, related_name="names"
    )
    rowo_2019 = models.ForeignKey(
        Rowo2019, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    oekotest = models.ForeignKey(
        Oekotest, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    ok_power = models.ForeignKey(
        OkPower, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    stromauskunft = models.ForeignKey(
        Stromauskunft, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    verivox = models.ForeignKey(
        Verivox, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )

    class Meta:
        verbose_name_plural = "Anbieter: Namessammlung"

    def __str__(self) -> str:
        return self.name


class TemplateNames(models.TextChoices):
    HOMEPAGE_TEXT_EXPORT = "HP_EXPORT", "Homepage Text"
    SURVEY2024_SUBJECT = "SURVEY_2024_SUBJECT", "Umfrage 2024 Betreff"
    SURVEY2024_TXT = "SURVEY_2024_TXT", "Umfrage 2024 Text"
    SURVEY2024_HTML = "SURVEY_2024_HTML", "Umfrage 2024 Html"


class Template(models.Model):
    name = models.CharField(
        unique=True, max_length=64, choices=TemplateNames, blank=False
    )
    template = models.TextField()

    def __str__(self) -> str:
        return TemplateNames(self.name).label


class KeepOrderModelBase(ModelBase):
    def __new__(
        cls, name: str, bases: list[type], attrs: dict[str, Any], **kwargs
    ) -> type:
        field_order = tuple(
            k for k, v in attrs.items() if not k.startswith("_") and not callable(v)
        )
        klass = super().__new__(cls, name, bases, attrs, **kwargs)
        klass._field_order = field_order
        return klass


class CompanySurvey2024(models.Model, metaclass=KeepOrderModelBase):
    created = models.DateTimeField(auto_now_add=True, null=True)
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE, editable=False)
    revision = HiddenPositiveIntegerField(default=1)

    state_labels = StateLabels(
        {
            State.start: Alert(
                "info",
                "Bitte vergessen Sie nicht am Ende zu Speichern. <br />"
                "Sie können dies auch mit Zwischenständen tun.",
            ),
            State.saved_with_warning: Alert(
                "warning",
                "Bitte überprüfen Sie ihre Daten. Einige schein logische Fehler zu enthalten.",
            ),
            State.saved: Alert("success", "Erfolgreich gespeichert."),
            State.unchanged: Alert("info", "Nicht gespeichert, da keine Änderungen."),
            State.error: Alert(
                "danger", "Konnte nicht speichern, Eingabefehler gefunden."
            ),
            State.view_old: Alert("warning", "Das ist eine alte Revision!"),
        }
    )

    header_contact = Header("Kontaktinformationen")

    section_client_contact = Section(
        "Kund*innen Kontakt",
        "Bitte geben Sie die Kontaktinformationen für Kunden*innen an",
    )
    name = CharField("Vollständiger Firmenname")

    street = CharField("Straße")
    plz = CharField("PLZ")
    city = CharField("Ort")
    phone = CharField("Telefon")
    fax = CharField("Fax")
    mail = CharField("E-Mail")
    homepage = CharField("Homepage", max_length=1024)

    section_rowo_contact = Section(
        "ROBIN WOOD Ansprechpartner*in",
        "Für eventuelle Rückfragen zu Ihren Antworten, geben Sie bitte hier eine Ansprechperson an [optional]",
    )
    contact_name = CharField("Name")
    contact_position = CharField("Position/Funktion")
    contact_mail = CharField("E-Mail")
    contact_phone = CharField("Telefon")
    contact_label = Label(
        "<p>Ihr Kontakt bei ROBIN WOOD: <br />"
        '<a href="mailto:oekostrom@robinwood.de">📧 Florian Kubitz</a> (Vorstandssprecher) '
        '<a href="tel:+494038089216">📞040 380 892-16</a></p>'
    )

    # Organisationsstruktur und Verflechtungen
    header_orga = Header("Organisationsstruktur und Verflechtungen")

    section_service = Section(
        "Versorgungsgebiet",
        (
            "Liefern sie Strom für Haushaltskunden ins gesamte Bundesgebiet oder "
            "nur in ein begrenzetes Gebiet?"
        ),
    )
    service_germany = YesNoField("Bundesweit")
    service_area = TextField(
        verbose_name="Gebiet Stromversorgung",
        help_text=(
            "Falls sie nur bestimmte Gebiete beliefern, geben Sie bitte hier eine Liste "
            "der PLZ an, welche sie beliefern."
        ),
    )

    section_name = Section(
        "Identifikation",
        "Welchen Namen, Rechtsform und Handelsregisternummer hat ihr Unternehmen?",
    )
    legal_form = models.CharField(
        max_length=20,
        choices=[
            ("eG", "Genossenschaft (eG)"),
            ("SCE", "SCE (Europäische Genossenschaft)"),
            ("EK", "Einzelunternehmen (e.K., e.Kfm., e.Kfr.)"),
            ("GmbH", "Gesellschaft mit beschränkter Haftung (GmbH)"),
            ("GmbHCoKG", "GmbH & Co. KG"),
            ("GmbHCoOHG", "GmbH & Co. OHG"),
            ("UG", "Unternehmergesellschaft (haftungsbeschränkt) (UG)"),
            ("AG", "Aktiengesellschaft (AG)"),
            ("AGCoKG", "AG & Co. KG"),
            ("UGCoKG", "UG & Co. KG"),
            ("KG", "Kommanditgesellschaft (KG)"),
            ("OHG", "Offene Handelsgesellschaft (OHG)"),
            ("GbR", "Gesellschaft bürgerlichen Rechts (GbR)"),
            ("PartG", "Partnerschaftsgesellschaft (PartG)"),
            ("KGaA", "Kommanditgesellschaft auf Aktien (KGaA)"),
            ("SE", "Europäische Gesellschaft (SE)"),
            ("EWIV", "EWIV (Europäische Wirtschaftliche Interessenvereinigung)"),
            ("Stille", "Stille Gesellschaft"),
            ("Stiftung", "Stiftung"),
            ("Verein", "Verein (e.V.)"),
        ],
        blank=True,
        verbose_name="Rechtsform",
        help_text="Rechtsform ihres Unternehmens.",
    )
    register_id = CharField(
        "Handelsregisternummer", "Handelsregisternummer falls zutreffend"
    )

    section_orga = Section(
        "Organisationsstruktur",
        (
            "Eigentümer- und Organisationsstruktur Ihres Unternehmens "
            "(z.B. Anteilseigner, Hauptaktionär*in, Leitung des operativen Geschäfts)"
        ),
    )
    ownership_structure = TextField(
        verbose_name="Eigentümer- und Organisationsstruktur",
    )
    company_connections = TextField(
        verbose_name="Unternehmensverbindungen",
        help_text="Mit welchen anderen Unternehmen sind Sie ggf. verbunden (quer und horizontal)?",
    )

    section_no_ee_connection = Section(
        "Verbindungen zu fossilen oder Atomkonzernen",
        (
            "Bezieht und verkauft Ihr Unternehmen oder ein mit Ihnen verbundenes Unternehmen "
            "Strom aus fossilen Energiequellen oder Atomenergie?"
        ),
    )
    sells_fossil_or_nuclear_energy = YesNoField(
        verbose_name="Verbindung zu fossiler oder Atomenergie",
    )
    explanation_fossil_nuclear = TextField(
        verbose_name="Erläuterung",
        help_text="Erläuterungen zu Strom aus fossilen/Atomenergie, falls zutreffend.",
    )

    section_commodities = Section(
        "Rohstoffhandel",
        (
            "Handelt Ihr Unternehmen oder ein mit Ihnen verbundenes Unternehmen mit "
            "Öl, Kohle, Atomtechnologien und/oder fossilem Gas?"
        ),
    )
    trades_commodities = YesNoField(
        verbose_name="fossiler Rohstoffhandel",
    )
    commodities_extent = TextField(
        verbose_name="Umfang des Rohstoffhandels",
        help_text="In welchem Umfang handelt Ihr Unternehmen mit diesen Rohstoffen?",
    )

    section_renewable_gas_invest = Section(
        "Investitionen Erneuerbares Gas",
        "Investiert Ihr Unternehmen in dem Aufbau von erneuerbarer Gas-Infrastruktur?",
    )
    invests_renewable_gas = YesNoField(
        verbose_name="Investitionen in erneuerbare Gas-Infrastruktur",
    )
    explanation_investments = TextField(
        verbose_name="Erläuterungen zu Investitionen",
        help_text="Erläutern Sie, wie in erneuerbare Gas-Infrastruktur investiert wird.",
    )

    # Strom und Erzeugungsanlagen
    header_energy = Header("Strom und Erzeugungsanlagen")

    section_mix = Section(
        "Strommix letztes Kalenderjahr",
        (
            "Mit welchem Strommix haben Sie Ihre Kund*innen im letzten Kalenderjahr beliefert? "
            "Bitte geben Sie jeweils den Anteil in Prozent an."
        ),
    )
    hydro_power = PercentField("Wasserkraft")
    solar_power = PercentField("Solarenergie")
    biomass_power = PercentField("Biomasse")
    wind_power = PercentField("Windkraft")
    geothermal_power = PercentField("Erdwärme")
    other_power = PercentField("Sonstige Energiequellen")
    checker_power_source = PercentChecker(
        "hydro_power",
        "solar_power",
        "biomass_power",
        "wind_power",
        "geothermal_power",
        "other_power",
    )

    other_power_explanation = TextField(
        verbose_name="Erläuterung ",
        help_text="Erläuterungen zu 'Sonstiges Energiequellen' im Strommix, falls zutreffend.",
    )

    section_source = Section(
        "Bezugsquellen", "Worüber beziehen Sie Strom (jeweils in Prozent)?"
    )
    power_from_exchange = PercentField("Strombörse")
    power_from_plants = PercentField(
        "direkt aus Erzeugungsanlagen",
        help_text="Stroms bezogen direkt von Erzeugungsanlagen (im Inland oder Ausland)",
    )
    power_from_traders = PercentField("andere Stromhändler")
    power_from_own_plants = PercentField("eigenen Anlagen")
    checker_power_from = PercentChecker(
        "power_from_exchange",
        "power_from_plants",
        "power_from_traders",
        "power_from_own_plants",
    )

    section_plant_location = Section(
        "Standort der Anlagen",
        (
            "Wie viel des von Ihnen im letzten Kalenderjahr verkauften Stroms stammte "
            "aus Anlagen mit dem Standort:"
        ),
    )
    regional_plants_percent = PercentField("ihre Region")
    national_plants_percent = PercentField("Deutschland")
    international_plants_percent = PercentField("Europäisches Ausland")
    checker_power_region = PercentChecker(
        "regional_plants_percent",
        "national_plants_percent",
        "international_plants_percent",
    )

    section_plant_age = Section(
        "Anlagenalter",
        (
            "Wie viel Prozent des von Ihnen im letzten Kalenderjahr verkauften Stroms "
            "stammt aus Anlagen folgenden Alters?"
        ),
    )
    plant_age_0_3 = PercentField("bis 3 Jahre")
    plant_age_4_6 = PercentField("4-6 Jahre")
    plant_age_7_10 = PercentField("7-10 Jahre")
    plant_age_11_15 = PercentField("11-15 Jahre")
    plant_age_16_20 = PercentField("16-20 Jahre")
    plant_age_21_plus = PercentField("über 21 Jahre")
    checker_plant_age = PercentChecker(
        "plant_age_0_3",
        "plant_age_4_6",
        "plant_age_7_10",
        "plant_age_11_15",
        "plant_age_16_20",
        "plant_age_21_plus",
    )

    section_plant_ee_saved = Section(
        "EEG Anlagen Altanlagen",
        (
            "Wie viel Prozent des von Ihnen im letzten Kalenderjahr verkauften Stroms "
            "stammt jeweils aus Anlagen die aus der EGG Förderung gefallen sind, welche"
        ),
    )

    plant_ee_saved_owned = PercentField(
        "weiterbetrieben", help_text="Anlagen die schon vorher in ihren Besitz waren"
    )
    plant_ee_saved_new = PercentField(
        "neu erworben",
        help_text="Anlagen die sie nach Ende oder kurz vor Ende der EEG Förderung erworben haben",
    )
    plant_ee_saved_trade = PercentField(
        "direkt Verträge",
        help_text=(
            "Anlagen außerhalb der Förderung die Sie nicht besitzen aber "
            "mit denen sie einen direkten Liefervertrag abgeschlossen haben"
        ),
    )
    checker_ee_saved = PercentChecker(
        "plant_ee_saved_owned", "plant_ee_saved_new", "plant_ee_saved_trade"
    )

    section_file_upload = Section(
        "Stromzukauf von Fremdanlagen",
        (
            "<p>Wenn Sie Strom von Erzeugungsanlagen zukaufen: "
            "Aus welchen Erzeugungsanlagen haben Sie im letzten Kalenderjahr Strom bezogen?</p>"
            "<p>Bitte schicken Sie uns eine Tabelle mit folgenden Informationen"
            "   (im Excel- oder LibreOffice-Format):</p>"
            "<ul>"
            "<li>Name</li>"
            "<li>Besitzer</li>"
            "<li>Adresse + Kontakt des Besitzers</li>"
            "<li>Eigentümerstruktur</li>"
            "<li>Anlagen Typ</li>"
            "<li>Leistung</li>"
            "<li>Standort</li>"
            "<li>Datum Inbetriebnahme,</li>"
            "<li>wie viel MWh Sie von der Anlage bezogen haben</li>"
            "<li>selbst initiiert/gefördert?, </li>"
            "<li>Stromerzeugungs-Anlagen-Kennzeichnung der BeNetzA.</li>"
            "</ul>"
        ),
    )
    power_plants_file = FileField(
        "Erzeugungsanlagen Tabelle",
        "Bitte laden Sie die Tabelle hoch.",
        upload_to=upload_to_power_plants,
    )
    criteria_for_third_party_suppliers = TextField(
        verbose_name="Kriterien für Fremdanbieter",
        help_text="Nach welchen Kriterien wählen Sie Fremdanbieter von Strom aus?",
    )

    # Förderung der Energiewende
    header_promotion = Header("Förderung der Energiewende")

    section_new_plant = Section(
        "Neuanlagen",
        "Haben Sie in den letzten 5 Jahren Erneuerbare Energien-Anlagen errichtet?",
    )
    built_renewable_plants = YesNoField("Neuanlagen errichtet")
    built_plant_count = IntegerField(
        verbose_name="Anzahl", help_text="Anzahl der errichteten Neuanlagen"
    )
    built_plant_capacity_kw = IntegerField(
        verbose_name="Installierte Leistung",
        unit="kW",
        help_text="Installierte Leistung der errichteten Anlagen",
    )

    section_plant_planned = Section(
        "geplante Anlangen",
        "Haben Sie in den letzten 5 Jahren Erneuerbare Energien-Anlagen geplant?",
    )
    planned_renewable_plants = YesNoField("Geplante Anlagen")
    planned_plant_count = IntegerField(
        verbose_name="Anzahl", help_text="Anzahl der geplanten Anlagen"
    )
    planned_plant_capacity_kw = IntegerField(
        verbose_name="Leistung",
        unit="kW",
        help_text="Installierte Leistung der geplanten Anlagen",
    )

    section_investment = Section(
        "Anlagen Investitionen",
        (
            "Wie viel Prozent Ihres Umsatzes haben Sie in den letzten 5 Jahren zur "
            "Errichtung und Planung von Anlagen verwendet?"
        ),
    )
    revenue_investment_percent = PercentField(
        verbose_name="Anteil an Umsatz",
    )

    section_tech_invest = Section(
        "Technologie Investitionen",
        (
            "Investieren Sie in Technologien, die den Verbrauch und die Erzeugung "
            "von Erneuerbaren Energien zusammenbringen, z.B. Speicher oder SmartGrids?"
        ),
    )
    invests_in_renewable_tech = YesNoField("Investitionen")
    investment_details = TextField(
        verbose_name="Details der Investitionen",
        help_text="Erläutern Sie, wie und worin sie investieren.",
    )

    section_customer_support = Section(
        "Unterstützung von Kund*innen",
        "Unterstützen Sie Kund*innen bei der Anschaffung von PV, Wärmepumpen oder ähnlichen Anlagen?",
    )
    supports_customers_with_renewable = YesNoField(
        verbose_name="Unterstützung Anschaffung",
    )
    support_customer_details = TextField(
        verbose_name="Details",
        help_text="Falls ja, erläutern Sie, wie und wofür die Unterstützung erfolgt.",
    )

    section_energy_transition_support = Section(
        "Förderbeitrag zur Energiewende",
        "Fördern Sie die Energiewende mit einem festen Betrag pro kWh?",
    )
    supports_energy_transition_per_kwh = YesNoField("Erhebung Förderbeitrag")

    support_per_kwh = FloatField(
        verbose_name="Höhe Förderbetrag",
        unit="€-ct/kWh",
    )

    section_support_spending = Section(
        "Verwendung des Förderbeitrages",
        "Wofür wird der oben genannte Förderbetrag verwendet?",
    )
    support_spending_new_plants = YesNoField(
        verbose_name="Neuanlagen", help_text="Verwendung für den Bau neuer Anlagen?"
    )
    support_spending_tech = YesNoField(
        verbose_name="Technologie",
        help_text="Verwendet das Unternehmen Fördermittel für Technologien?",
    )
    support_spending_emobility = YesNoField(
        verbose_name="E-Mobilität",
        help_text="Verwendung für Maßnahmen im Bereich der E-Mobilität?",
    )
    support_spending_other = YesNoField(
        verbose_name="Sonstige Maßnahmen",
        help_text="Verwendung sonstige Maßnahmen zur Förderung der Energiewende?",
    )
    support_spending_details = TextField(
        verbose_name="Details",
        help_text="Optionale weitere Ausführungen zur Verwendung des Förderbeitrags.",
    )

    section_support_other = Section(
        "Sonstige Förderung",
        "Fördern Sie Energiewende durch sonstige weitere Maßnahmen?",
    )
    support_other = TextField(
        "Sonstige Förderungen",
    )

    # Zum Schluss
    header_final = Header("Allgemeines zum Unternehmen")
    section_final = Section(
        "Statistiken",
        (
            "Bitte helfen sie unseren Leser*innen ein genaueres Bild von ihrem Unternehmen zu bekommen. "
            "Alle Angaben sind natürlich freiwillig."
        ),
    )
    num_employees = IntegerField(
        verbose_name="Mitarbeiteranzahl",
        help_text="Wie viele Mitarbeiter*innen hat Ihr Unternehmen?",
    )
    num_private_customers = IntegerField(
        verbose_name="Anzahl privater Kund*innen",
        help_text="Wie viele private Kund*innen versorgen Sie zur Zeit?",
    )
    num_business_customers = IntegerField(
        verbose_name="Anzahl gewerblicher Kund*innen",
        help_text="Wie viele gewerbliche Kund*innen versorgen Sie zur Zeit?",
    )
    total_mwh_sold_2023 = IntegerField(
        verbose_name="Verkaufter Strom in 2023",
        unit="MWh",
        help_text="Wie viele Megawattstunden Strom hat Ihr Unternehmen im Jahr 2023 verkauft?",
    )

    class Meta:
        unique_together = ["anbieter", "revision"]
        verbose_name = "Umfrage Revision"
        verbose_name_plural = "Umfrage: Revisionen"

    def __str__(self) -> str:
        # TODO Edit with Anbieter Name
        return f"Umfrage {self.anbieter.name}"

    def get_absolute_url(self) -> str:
        url = SurveyAccess.objects.get(anbieter=self.anbieter).get_absolute_url()
        return f"{url}&rev={self.revision}"


class SurveyAccess(models.Model):
    anbieter = models.OneToOneField(
        Anbieter, on_delete=models.CASCADE, related_name="survey_access"
    )
    survey = models.ForeignKey(
        CompanySurvey2024,
        help_text="Survey of the current revision",
        on_delete=models.CASCADE,
    )
    code = models.CharField(max_length=32, unique=True, default=generate_unique_code)
    current_revision = models.IntegerField(default=1, db_index=True)
    changed = models.DateTimeField(null=True)
    access_count = models.IntegerField(default=0)
    last_access = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Umfrage Zugang"
        verbose_name_plural = "Umfrage: Zugänge"

    def __str__(self) -> str:
        return f"{self.anbieter.name} (Rev {self.current_revision})"

    def get_absolute_url(self) -> str:
        return f'{reverse("survey_update", kwargs={"code": self.code})}?view=1'

    def increment_access_count(self) -> None:
        self.access_count += 1
        self.last_access = timezone.now()
        self.save()

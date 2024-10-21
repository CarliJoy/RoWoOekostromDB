# Generated by Django 5.1.2 on 2024-10-21 00:34
# noqa

from django.db import migrations, models

import anbieter.fields


class Migration(migrations.Migration):
    dependencies = [
        ("anbieter", "0013_make_slug_unique"),
    ]

    operations = [
        migrations.CreateModel(
            name="CompanySurvey2024",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "service_germany",
                    anbieter.fields.YesNoField(
                        blank=True,
                        choices=[(True, "Ja"), (False, "Nein"), (None, "?")],
                        null=True,
                        verbose_name="Bundesweit",
                    ),
                ),
                (
                    "service_area",
                    anbieter.fields.TextField(
                        blank=True,
                        help_text=(
                            "Falls sie nur bestimmte Gebiete beliefern, "
                            "geben Sie bitte hier eine Liste der PLZ an, welche sie beliefern."
                        ),
                        verbose_name="Gebiet Stromversorgung",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        default="Ökostrom GmbH",
                        max_length=256,
                        verbose_name="Vollständiger Name",
                    ),
                ),
                (
                    "legal_form",
                    models.CharField(
                        blank=True,
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
                            (
                                "EWIV",
                                "EWIV (Europäische Wirtschaftliche Interessenvereinigung)",
                            ),
                            ("Stille", "Stille Gesellschaft"),
                            ("Stiftung", "Stiftung"),
                            ("Verein", "Verein (e.V.)"),
                        ],
                        help_text="Rechtsform ihres Unternehmens.",
                        max_length=20,
                        verbose_name="Rechtsform",
                    ),
                ),
                (
                    "register_id",
                    models.CharField(
                        blank=True,
                        help_text="Handelsregisternummer falls zutreffend",
                        max_length=256,
                        verbose_name="Handelsregisternummer",
                    ),
                ),
                (
                    "ownership_structure",
                    anbieter.fields.TextField(
                        blank=True, verbose_name="Eigentümer- und Organisationsstruktur"
                    ),
                ),
                (
                    "company_connections",
                    anbieter.fields.TextField(
                        blank=True,
                        help_text="Mit welchen anderen Unternehmen sind Sie ggf. verbunden (quer und horizontal)?",
                        verbose_name="Unternehmensverbindungen",
                    ),
                ),
                (
                    "sells_fossil_or_nuclear_energy",
                    anbieter.fields.YesNoField(
                        blank=True,
                        choices=[(True, "Ja"), (False, "Nein"), (None, "?")],
                        null=True,
                        verbose_name="Verbindung zu fossiler oder Atomenergie",
                    ),
                ),
                (
                    "explanation_fossil_nuclear",
                    anbieter.fields.TextField(
                        blank=True,
                        help_text="Erläuterungen zu Strom aus fossilen/Atomenergie, falls zutreffend.",
                        verbose_name="Erläuterung",
                    ),
                ),
                (
                    "trades_commodities",
                    anbieter.fields.YesNoField(
                        blank=True,
                        choices=[(True, "Ja"), (False, "Nein"), (None, "?")],
                        null=True,
                        verbose_name="fossiler Rohstoffhandel",
                    ),
                ),
                (
                    "commodities_extent",
                    anbieter.fields.TextField(
                        blank=True,
                        help_text="In welchem Umfang handelt Ihr Unternehmen mit diesen Rohstoffen?",
                        verbose_name="Umfang des Rohstoffhandels",
                    ),
                ),
                (
                    "invests_renewable_gas",
                    anbieter.fields.YesNoField(
                        blank=True,
                        choices=[(True, "Ja"), (False, "Nein"), (None, "?")],
                        null=True,
                        verbose_name="Investitionen in erneuerbare Gas-Infrastruktur",
                    ),
                ),
                (
                    "explanation_investments",
                    anbieter.fields.TextField(
                        blank=True,
                        help_text="Erläutern Sie, wie in erneuerbare Gas-Infrastruktur investiert wird.",
                        verbose_name="Erläuterungen zu Investitionen",
                    ),
                ),
                (
                    "hydro_power",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="Wasserkraft",
                    ),
                ),
                (
                    "solar_power",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="Solarenergie",
                    ),
                ),
                (
                    "biomass_power",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="Biomasse",
                    ),
                ),
                (
                    "wind_power",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="Windkraft",
                    ),
                ),
                (
                    "geothermal_power",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="Erdwärme",
                    ),
                ),
                (
                    "other_power",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="Sonstige Energiequellen",
                    ),
                ),
                (
                    "other_power_explanation",
                    anbieter.fields.TextField(
                        blank=True,
                        help_text="Erläuterungen zu 'Sonstiges Energiequellen' im Strommix, falls zutreffend.",
                        verbose_name="Erläuterung ",
                    ),
                ),
                (
                    "power_from_exchange",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="Strombörse",
                    ),
                ),
                (
                    "power_from_plants",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        help_text="Stroms bezogen direkt von Erzeugungsanlagen (im Inland oder Ausland)",
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="direkt aus Erzeugungsanlagen",
                    ),
                ),
                (
                    "power_from_traders",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="andere Stromhändler",
                    ),
                ),
                (
                    "power_from_own_plants",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="eigenen Anlagen",
                    ),
                ),
                (
                    "regional_plants_percent",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="ihre Region",
                    ),
                ),
                (
                    "national_plants_percent",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="Deutschland",
                    ),
                ),
                (
                    "international_plants_percent",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="Europäisches Ausland",
                    ),
                ),
                (
                    "plant_age_0_3",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="bis 3 Jahre",
                    ),
                ),
                (
                    "plant_age_4_6",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="4-6 Jahre",
                    ),
                ),
                (
                    "plant_age_7_10",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="7-10 Jahre",
                    ),
                ),
                (
                    "plant_age_11_15",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="11-15 Jahre",
                    ),
                ),
                (
                    "plant_age_16_20",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="16-20 Jahre",
                    ),
                ),
                (
                    "plant_age_21_plus",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="über 21 Jahre",
                    ),
                ),
                (
                    "plant_ee_saved_owned",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        help_text="Anlagen die schon vorher in ihren Besitz waren",
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="weiterbetrieben",
                    ),
                ),
                (
                    "plant_ee_saved_new",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        help_text="Anlagen die sie nach Ende oder kurz vor Ende der EEG Förderung erworben haben",
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="neu erworben",
                    ),
                ),
                (
                    "plant_ee_saved_trade",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        help_text=(
                            "Anlagen außerhalb der Förderung die Sie nicht besitzen aber "
                            "deren Strom einkaufen aber mit denen sie einen direkten Liefervertrag"
                            " oder ähnlichen abgeschlossen haben"
                        ),
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="direkt Verträge",
                    ),
                ),
                (
                    "power_plants_file",
                    models.FileField(
                        blank=True,
                        help_text="Bitte laden Sie die Tabelle hoch.",
                        upload_to="uploads/",
                        verbose_name="Erzeugungsanlagen Tabelle",
                    ),
                ),
                (
                    "criteria_for_third_party_suppliers",
                    anbieter.fields.TextField(
                        blank=True,
                        help_text="Nach welchen Kriterien wählen Sie Fremdanbieter von Strom aus?",
                        verbose_name="Kriterien für Fremdanbieter",
                    ),
                ),
                (
                    "built_renewable_plants",
                    anbieter.fields.YesNoField(
                        blank=True,
                        choices=[(True, "Ja"), (False, "Nein"), (None, "?")],
                        null=True,
                        verbose_name="Neuanlagen errichtet",
                    ),
                ),
                (
                    "built_plant_count",
                    anbieter.fields.IntegerField(
                        blank=True,
                        help_text="Anzahl der errichteten Neuanlagen",
                        null=True,
                        verbose_name="Anzahl",
                    ),
                ),
                (
                    "built_plant_capacity_kw",
                    anbieter.fields.IntegerField(
                        blank=True,
                        help_text="Installierte Leistung der errichteten Anlagen",
                        null=True,
                        verbose_name="Installierte Leistung",
                    ),
                ),
                (
                    "planned_renewable_plants",
                    anbieter.fields.YesNoField(
                        blank=True,
                        choices=[(True, "Ja"), (False, "Nein"), (None, "?")],
                        null=True,
                        verbose_name="Geplante Anlagen",
                    ),
                ),
                (
                    "planned_plant_count",
                    anbieter.fields.IntegerField(
                        blank=True,
                        help_text="Anzahl der geplanten Anlagen",
                        null=True,
                        verbose_name="Anzahl",
                    ),
                ),
                (
                    "planned_plant_capacity_kw",
                    anbieter.fields.IntegerField(
                        blank=True,
                        help_text="Installierte Leistung der geplanten Anlagen",
                        null=True,
                        verbose_name="Leistung",
                    ),
                ),
                (
                    "revenue_investment_percent",
                    anbieter.fields.PercentField(
                        blank=True,
                        decimal_places=1,
                        max_digits=6,
                        null=True,
                        validators=[anbieter.fields.is_percentage],
                        verbose_name="Anteil an Umsatz",
                    ),
                ),
                (
                    "invests_in_renewable_tech",
                    anbieter.fields.YesNoField(
                        blank=True,
                        choices=[(True, "Ja"), (False, "Nein"), (None, "?")],
                        null=True,
                        verbose_name="Investitionen",
                    ),
                ),
                (
                    "investment_details",
                    anbieter.fields.TextField(
                        blank=True,
                        help_text="Erläutern Sie, wie und worin sie investieren.",
                        verbose_name="Details der Investitionen",
                    ),
                ),
                (
                    "supports_customers_with_renewable",
                    anbieter.fields.YesNoField(
                        blank=True,
                        choices=[(True, "Ja"), (False, "Nein"), (None, "?")],
                        null=True,
                        verbose_name="Unterstützung Anschaffung",
                    ),
                ),
                (
                    "support_customer_details",
                    anbieter.fields.TextField(
                        blank=True,
                        help_text="Falls ja, erläutern Sie, wie und wofür die Unterstützung erfolgt.",
                        verbose_name="Details",
                    ),
                ),
                (
                    "supports_energy_transition_per_kwh",
                    anbieter.fields.YesNoField(
                        blank=True,
                        choices=[(True, "Ja"), (False, "Nein"), (None, "?")],
                        null=True,
                        verbose_name="Erhebung Förderbeitrag",
                    ),
                ),
                (
                    "support_per_kwh",
                    anbieter.fields.FloatField(
                        blank=True, null=True, verbose_name="Höhe Förderbetrag"
                    ),
                ),
                (
                    "support_spending_new_plants",
                    anbieter.fields.YesNoField(
                        blank=True,
                        choices=[(True, "Ja"), (False, "Nein"), (None, "?")],
                        help_text="Verwendung für den Bau neuer Anlagen?",
                        null=True,
                        verbose_name="Neuanlagen",
                    ),
                ),
                (
                    "support_spending_tech",
                    anbieter.fields.YesNoField(
                        blank=True,
                        choices=[(True, "Ja"), (False, "Nein"), (None, "?")],
                        help_text="Verwendet das Unternehmen Fördermittel für Technologien?",
                        null=True,
                        verbose_name="Technologie",
                    ),
                ),
                (
                    "support_spending_emobility",
                    anbieter.fields.YesNoField(
                        blank=True,
                        choices=[(True, "Ja"), (False, "Nein"), (None, "?")],
                        help_text="Verwendung für Maßnahmen im Bereich der E-Mobilität?",
                        null=True,
                        verbose_name="E-Mobilität",
                    ),
                ),
                (
                    "support_spending_other",
                    anbieter.fields.YesNoField(
                        blank=True,
                        choices=[(True, "Ja"), (False, "Nein"), (None, "?")],
                        help_text="Verwendung sonstige Maßnahmen zur Förderung der Energiewende?",
                        null=True,
                        verbose_name="Sonstige Maßnahmen",
                    ),
                ),
                (
                    "support_spending_details",
                    anbieter.fields.TextField(
                        blank=True,
                        help_text="Optionale weitere Ausführungen zur Verwendung des Förderbeitrags.",
                        verbose_name="Details",
                    ),
                ),
                (
                    "support_other",
                    anbieter.fields.TextField(
                        blank=True, verbose_name="Sonstige Förderungen"
                    ),
                ),
                (
                    "num_employees",
                    anbieter.fields.IntegerField(
                        blank=True,
                        help_text="Wie viele Mitarbeiter*innen hat Ihr Unternehmen?",
                        null=True,
                        verbose_name="Mitarbeiteranzahl",
                    ),
                ),
                (
                    "num_private_customers",
                    anbieter.fields.IntegerField(
                        blank=True,
                        help_text="Wie viele private Kund*innen versorgen Sie zur Zeit?",
                        null=True,
                        verbose_name="Anzahl privater Kund*innen",
                    ),
                ),
                (
                    "num_business_customers",
                    anbieter.fields.IntegerField(
                        blank=True,
                        help_text="Wie viele gewerbliche Kund*innen versorgen Sie zur Zeit?",
                        null=True,
                        verbose_name="Anzahl gewerblicher Kund*innen",
                    ),
                ),
                (
                    "total_kwh_sold_2023",
                    anbieter.fields.IntegerField(
                        blank=True,
                        help_text="Wie viele Kilowattstunden Strom hat Ihr Unternehmen im Jahr 2023 verkauft?",
                        null=True,
                        verbose_name="Verkaufter Strom in 2023",
                    ),
                ),
            ],
        ),
    ]

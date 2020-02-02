from django.conf import settings

# Url to a CSV file that contains the Robin Wood Criteria for the Homepage
ROWO_CRITERIA_URL = getattr(
    settings,
    "ROWO_CRITERIA_URL",
    "https://raw.githubusercontent.com/Robin-Wood/rowo-drupal-module/master/criteria.csv",
)


# Url to a excel file that contains the current list of engery providers
ROWO_PROVIDER_EXCEL_URL = getattr(settings, "ROWO_PROVIDER_EXCEL_URL", None)

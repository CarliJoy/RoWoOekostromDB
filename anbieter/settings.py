from django.conf import settings

ROWO_CRITERIA_URL = getattr(
    settings,
    "ROWO_CRITERIA_URL",
    "https://raw.githubusercontent.com/Robin-Wood/rowo-drupal-module/master/criteria.csv",
)

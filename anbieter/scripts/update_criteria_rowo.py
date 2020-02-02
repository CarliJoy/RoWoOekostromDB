import csv

import requests

from anbieter.models import HomepageKriterium
from anbieter.settings import ROWO_CRITERIA_URL


def run():
    request = requests.get(ROWO_CRITERIA_URL)
    content = request.content.decode("UTF8").splitlines()
    reader = csv.DictReader(content, delimiter=";")
    for row in reader:
        data = HomepageKriterium.csv_data_to_obj_data(row)
        HomepageKriterium.objects.update_or_create(id=data["id"], defaults=data)

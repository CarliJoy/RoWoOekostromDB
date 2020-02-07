import csv
from logging import getLogger
from pathlib import Path
from typing import List

import requests
from django.conf import settings

from anbieter.models import HomepageKriterium
from anbieter.settings import ROWO_CRITERIA_URL

DEFAULT_LOCAL_CSV_PATH = Path(settings.BASE_DIR) / "downloads" / "homepagekrit.csv"
logger = getLogger("anbieter.script.update_criteria_rowo")


def get_rowo_homepage_kriterium_online() -> List[str]:
    request = requests.get(ROWO_CRITERIA_URL)
    DEFAULT_LOCAL_CSV_PATH.write_bytes(request.content)
    logger.info("Downloaded current Robin Wood Homepagekriterium")
    return request.content.decode("UTF8").splitlines()


def get_rowo_home_kriterium_file(filepath: Path = DEFAULT_LOCAL_CSV_PATH):
    if filepath.exists():
        logger.info("Using cached version")
        return filepath.read_text("UTF8").splitlines()
    else:
        logger.info("Cache is empty.")
        return get_rowo_homepage_kriterium_online()


def run(*args):
    """
    Read and import Robin Wood Homepage Kriterium file
    :param args: if use_cache is given, the cached file will be used
    :return:
    """
    if "use_cache" in args:
        content = get_rowo_home_kriterium_file()
    else:
        content = get_rowo_homepage_kriterium_online()
    reader = csv.DictReader(content, delimiter=";")
    for row in reader:
        data = HomepageKriterium.csv_data_to_obj_data(row)
        HomepageKriterium.objects.update_or_create(id=data["id"], defaults=data)

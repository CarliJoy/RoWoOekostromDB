from logging import getLogger
from pathlib import Path
from pprint import pprint
from typing import List, Dict

import requests
from django.conf import settings
from django.db import IntegrityError
from openpyxl import load_workbook

from anbieter.conv_helpers import ZERTIFIKATE
from anbieter.exceptions import ConfigurationError
from anbieter.models import Zertifizierung, Anbieter
from anbieter.scripts import update_criteria_rowo
from anbieter.settings import ROWO_PROVIDER_EXCEL_URL
from anbieter.typing import XLSX_ROW

DEFAULT_LOCAL_XLSX_PATH = Path(settings.BASE_DIR) / "downloads" / "anbieter.xlsx"
logger = getLogger("anbieter.scripts.update_providers_from_excel")


def create_or_get_zertifizierung() -> Dict[str, Zertifizierung]:
    result = {}
    for zertifikat in ZERTIFIKATE:
        result[zertifikat] = Zertifizierung.objects.get_or_create(name=zertifikat)[0]
    return result


def run(*args):
    """
    Retrieve the current version of the robin wood provider list
    :param *args if use_cache given, the file won't be downloaded again
    :return:
    """
    # Make sure the homepage criteria are up to date
    update_criteria_rowo.run(*args)
    if ROWO_PROVIDER_EXCEL_URL is None:
        raise ConfigurationError(
            "Could not perform update as ROWO_PROVIDER_EXCEL_URL is not defined. "
            "Think about adding it to your local.py!"
        )
    download_excel_file: bool = True
    if "use_cache" in args:
        if DEFAULT_LOCAL_XLSX_PATH.exists():
            download_excel_file = False
            logger.info("Using cached Excel file")
        else:
            logger.info("Cached Excel does not exist.")
    if download_excel_file:
        with DEFAULT_LOCAL_XLSX_PATH.open("wb") as f:
            request = requests.get(ROWO_PROVIDER_EXCEL_URL)
            f.write(request.content)
        logger.info("Downloaded new version of excel file")
    wb = load_workbook(DEFAULT_LOCAL_XLSX_PATH, read_only=True, data_only=True)
    db_zertifikate = create_or_get_zertifizierung()
    sheet = wb.worksheets[0]
    values = list(sheet.values)
    header: List[str] = values[0]
    for row in values[1:]:
        row_data: XLSX_ROW = {}
        for col_count, col_val in enumerate(row):
            if col_count > len(header):
                break
            row_data[header[col_count]] = col_val
        data = Anbieter.csv_data_to_obj_data(row_data)
        zertifizierung = data.pop("zertifizierung")
        try:
            anbieter: Anbieter = Anbieter.objects.update_or_create(
                name=data["name"], defaults=data
            )[0]
        except IntegrityError:
            pprint(data)
            raise
        for zertifikat_str in zertifizierung:
            if zertifikat_str is not None:
                anbieter.zertifizierung.add(db_zertifikate[zertifikat_str])

from tempfile import NamedTemporaryFile
from typing import List, Dict

import requests
from openpyxl import load_workbook

from anbieter.conv_helpers import ZERTIFIKATE
from anbieter.exceptions import ConfigurationError
from anbieter.models import Zertifizierung
from anbieter.settings import ROWO_PROVIDER_EXCEL_URL
from anbieter.typing import XLSX_ROW


def create_or_get_zertifizierung() -> Dict[str, Zertifizierung]:
    result = {}
    for zertifikat in ZERTIFIKATE:
        result[zertifikat] = Zertifizierung.objects.get_or_create(name=zertifikat)[0]
    return result


def run():
    """
    Retrieve the current version of the robin wood provider list
    :return:
    """
    if ROWO_PROVIDER_EXCEL_URL is None:
        raise ConfigurationError(
            "Could not perform update as ROWO_PROVIDER_EXCEL_URL is not defined. "
            "Think about adding it to your local.py!"
        )

    with NamedTemporaryFile(suffix=".xlsx", prefix="rowo_liste_") as f:
        # keep file only as long as not loaded
        request = requests.get(ROWO_PROVIDER_EXCEL_URL)
        f.write(request.content)
        wb = load_workbook(f.name, read_only=True, data_only=True)
    sheet = wb.worksheets[0]
    values = list(sheet.values)
    header: List[str] = values[0]
    data: List[XLSX_ROW] = []
    for row in values[1:]:
        row_data: XLSX_ROW = {}
        for col_count, col_val in enumerate(row):
            if col_count > len(header):
                break
            row_data[header[col_count]] = col_val
        print(row_data)
        data.append(row_data)

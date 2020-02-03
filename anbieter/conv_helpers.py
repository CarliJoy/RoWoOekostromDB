from typing import Optional, Union

ZERTIFIKAT_MAPPING = {
    "asew": "ASEW",
    "ecotopten": "EcoTopTen",
    "ekoenergie": "EKOenergy",
    "firstclimate naturstrom": "First Climate Naturstrom BASIS",
    "firstclimate naturstrom wasser und wald": "First Climate Naturstrom WASSER UND WALD",
    "grüner strom": "Grüner Strom",
    "grüner strom gold": "Grüner Strom Gold",
    "klima invest": "KlimaINVEST Ökostrom",
    "klimainvest ökostrom": "KlimaINVEST Ökostrom",
    "klimainvest ökostromre": "KlimaINVEST Ökostrom RE",
    "ok power": "ok-power",
    "ok power plus": "ok-power plus",
    "okpower": "ok-power",
    "okpower plus": "ok-power plus",
    "okpower?": "ok-power",
    "purepowertrue": "purepowerTRUE (TÜV SÜD - EE01)",
    "renewableplus": "RenewablePLUS",
    "tüv nord": "TÜV NORD",
    "tüv nord freiwillige zertifizierung": "TÜV NORD - Freiwillige Zertifizierung gemäß VdTÜV Standard 1304",
    "tüv nord geprüfter ökostrom": "TÜV NORD",
    "tüv rheinland": "TÜV Rheinland",
    "tüv süd": "TÜV SÜD",
    "tüv süd ee": "TÜV SÜD",  # Unklar ob EE01 oder EE02 - daher ohne Zusatz
    "tüv süd ee01": "TÜV SÜD - EE01",
    "tüv süd verbund": "TÜV SÜD EE+ - Verbund",
    "verbund": "TÜV SÜD EE+ - Verbund",
    "watergreen": "ASEW Watergreen",
}

ZERTIFIKATE = list(
    sorted(
        list(set(ZERTIFIKAT_MAPPING.values()))
        + [
            "TÜV NORD - Zertifizierung gemäß TN-Standard A75-S026-1",
            "TÜV SÜD - EE02",
            "KlimaINVEST Ökostrom PLUS ",
            "ASEW Watergreen+",
            "ASEW Energreen",
        ]
    )
)


def conv_phone_str(input_str: Optional[str]) -> Optional[str]:
    SPECIAL1 = "Stromio Kundenservice (Festnetz) 0800 58 58 224 (mobil) 0211 777 957 10"
    if input_str is None or len(str(input_str).strip()) == 0:
        return None
    elif input_str[0] in ("0", "+"):
        # Seems to be valid
        return input_str
    elif input_str[0].isdigit():
        # Forgot 0 of telefon number
        return "0" + input_str
    elif str(input_str).strip().lower() == SPECIAL1.lower():
        return "0800 58 58 224"
    else:
        return None


def conv_zertifikat_string(input_str: Optional[str]) -> Optional[str]:
    """
    Convert the zertifikat string to easier
    :param input_str:
    :exception KeyError if conversation not found
    """
    if input_str is None:
        return None
    else:
        conv_str = str(input_str).strip().lower().replace("-", " ")
    if conv_str in ("?", "", "x"):
        return None
    return ZERTIFIKAT_MAPPING[conv_str]


def conv_ee_anteil(input_value: Optional[Union[str, float, int]]) -> Optional[float]:
    """
    Converts the number of the percentage column to the correct percentage if
    possible. Numbers will be forced to be between 0% and 100%
    """
    if input_value is None:
        return None
    if isinstance(input_value, int) or isinstance(input_value, float):
        number = float(input_value)
    else:
        try:
            number = float(str(input_value.replace("%", "")))
            if "%" in input_value:
                number = number / 100
        except ValueError:
            return None
    if number < 0:
        return 0
    elif number > 1:
        return 100
    else:
        return number * 100

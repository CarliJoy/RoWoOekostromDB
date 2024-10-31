import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .models import CompanySurvey2024


def generate_unique_code() -> str:
    return uuid.uuid4().hex[:32]


def upload_to_power_plants(instance: "CompanySurvey2024", filename: str) -> str:
    # Retrieve the associated SurveyAccess code and revision
    from .models import SurveyAccess

    survey_access = SurveyAccess.objects.get(anbieter=instance.anbieter)
    code = survey_access.code
    revision = instance.revision
    return f"{code}/{revision}/{filename}"


def get_fill_status(values: dict[str, Any]) -> float:
    fields = {f for f in values if not f.startswith("_")}
    fields -= {
        "id",
        "created",
        "anbieter_id",
        "revision",
        "name",
        "mail",
        "homepage",
    }
    filled = sum(bool(values.get(f)) for f in fields)
    return filled / len(fields) * 100

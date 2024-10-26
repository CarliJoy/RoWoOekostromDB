import uuid
from typing import TYPE_CHECKING

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

from typing import Any

from django.core.exceptions import ValidationError
from django.db import models

MAX_PERCENTAGE = 100


def is_percentage(value: float | None) -> None:
    if value is None or (0 <= value <= MAX_PERCENTAGE):
        return
    raise ValidationError(
        f"Value must be between 0 and 100 or not set. Got '{value}'.",
        code="invalid",
        params={"value": value},
    )


JA_NEIN_CHOICE = (
    (True, "Ja"),
    (False, "Nein"),
    (None, "?"),
)


class PercentField(models.DecimalField):
    def __init__(
        self, verbose_name: str = "", help_text: str = "", **kwargs: Any
    ) -> None:
        kwargs.setdefault("blank", True)
        kwargs.setdefault("null", True)
        kwargs.setdefault("max_digits", 6)
        kwargs.setdefault("decimal_places", 1)
        kwargs.setdefault("validators", (is_percentage,))
        super().__init__(verbose_name=verbose_name, help_text=help_text, **kwargs)


class YesNoField(models.BooleanField):
    def __init__(
        self, verbose_name: str = "", help_text: str = "", **kwargs: Any
    ) -> None:
        kwargs.setdefault("blank", True)
        kwargs.setdefault("null", True)
        kwargs.setdefault("choices", JA_NEIN_CHOICE)
        super().__init__(verbose_name=verbose_name, help_text=help_text, **kwargs)


class TextField(models.TextField):
    def __init__(
        self, verbose_name: str = "", help_text: str = "", **kwargs: Any
    ) -> None:
        kwargs.setdefault("blank", True)
        super().__init__(verbose_name=verbose_name, help_text=help_text, **kwargs)


class IntegerField(models.IntegerField):
    def __init__(
        self, verbose_name: str = "", unit: str = "", help_text: str = "", **kwargs: Any
    ) -> None:
        kwargs.setdefault("blank", True)
        kwargs.setdefault("null", True)
        if unit:
            verbose_name = f"{verbose_name} [{unit}]"
        super().__init__(verbose_name=verbose_name, help_text=help_text, **kwargs)


class FloatField(models.FloatField):
    def __init__(
        self, verbose_name: str = "", unit: str = "", help_text: str = "", **kwargs: Any
    ) -> None:
        kwargs.setdefault("blank", True)
        kwargs.setdefault("null", True)
        if unit:
            verbose_name = f"{verbose_name} [{unit}]"
        super().__init__(verbose_name=verbose_name, help_text=help_text, **kwargs)

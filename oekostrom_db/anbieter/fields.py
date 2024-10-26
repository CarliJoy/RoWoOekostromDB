from typing import Any

from crispy_forms.bootstrap import AppendedText, InlineRadios
from crispy_forms.layout import Field
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import forms, widgets

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

    # def formfield(self, **kwargs) -> forms.Field:
    #     result = super().formfield(**kwargs)
    #     result.widget.attrs['style']='text-align: right; padding-right: 1rem;'
    #     return result

    def bootstrap_field(self, name: str) -> AppendedText:
        return AppendedText(name, "%")


class YesNoField(models.BooleanField):
    def __init__(
        self, verbose_name: str = "", help_text: str = "", **kwargs: Any
    ) -> None:
        kwargs.setdefault("blank", True)
        kwargs.setdefault("null", True)
        kwargs.setdefault("choices", JA_NEIN_CHOICE)
        super().__init__(verbose_name=verbose_name, help_text=help_text, **kwargs)

    def formfield(self, **kwargs) -> forms.Field:
        kwargs["widget"] = widgets.RadioSelect
        return super().formfield(**kwargs)
        #
        # # result.widget.attrs['style']='text-align: right; padding-right: 1rem;'
        # return result

    def bootstrap_field(self, name: str) -> AppendedText:
        return InlineRadios(name)


class CharField(models.CharField):
    def __init__(self, verbose_name: str = "", help_text: str = "", **kwargs: Any):
        kwargs.setdefault("blank", True)
        kwargs.setdefault("max_length", 256)
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
        self._unit = unit
        super().__init__(verbose_name=verbose_name, help_text=help_text, **kwargs)

    def bootstrap_field(self, name: str) -> AppendedText:
        if self._unit:
            return AppendedText(name, self._unit)
        return Field(name)


class FloatField(models.FloatField):
    def __init__(
        self, verbose_name: str = "", unit: str = "", help_text: str = "", **kwargs: Any
    ) -> None:
        kwargs.setdefault("blank", True)
        kwargs.setdefault("null", True)
        self._unit = unit
        super().__init__(verbose_name=verbose_name, help_text=help_text, **kwargs)

    def bootstrap_field(self, name: str) -> AppendedText:
        if self._unit:
            return AppendedText(name, self._unit)
        return Field(name)

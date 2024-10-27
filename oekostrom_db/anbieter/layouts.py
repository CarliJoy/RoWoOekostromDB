from enum import StrEnum
from typing import Literal

from crispy_forms.layout import HTML


class LayoutElement(HTML):
    def __init__(self) -> None:
        super().__init__(self.__html__())

    def __html__(self) -> str:
        raise NotImplementedError()


class Nothing(LayoutElement):
    def __html__(self) -> str:
        return ""


class Header(LayoutElement):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__()

    def __html__(self) -> str:
        return f"<h2 class='kampagne-full-forderung-headline'>{self.name}</h2>"


class Label(LayoutElement):
    def __init__(self, content: str) -> None:
        self.content = content
        super().__init__()

    def __html__(self) -> str:
        return f"<span>{self.content}</span>"


class Section(LayoutElement):
    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        super().__init__()

    def __html__(self) -> str:
        desc = ""
        if self.description:
            desc = f"<div class='forderung-text'>{self.description}</div>"
        return (
            f"<div class='kampagne-full-forderung-wrapper mobile-padding-1 mb-3'>"
            f"<div class='forderung-nummer'><span>?</span></div>"
            f"<div class='forderung-titel'>{self.name}</div>{desc}</div>"
        )


AlertType = Literal["primary", "secondary", "success", "danger", "warning", "info"]


class Alert(LayoutElement):
    def __init__(self, type_: AlertType, content: str) -> None:
        self.type = type_
        self.content = content
        super().__init__()

    def __html__(self) -> str:
        return (
            f'<div class="alert alert-{self.type} mt-3" role="alert">'
            f"{self.content}</div>"
        )


class State(StrEnum):
    start = "start"
    saved = "saved"
    unchanged = "unchanged"
    saved_with_warning = "saved_with_warning"
    error = "error"
    view_only = "view_only"
    view_old = "view_old"


HUNDERT_PERCENT = 100
ALMOST_HUNDERT_PERCENT = 99


class PercentChecker:
    def __init__(self, *fields: str) -> None:
        self.fields = fields

    def check(self, field_values: dict[str, float]) -> tuple[LayoutElement, bool]:
        total = 0
        fields_set = 0
        for field in self.fields:
            if field in field_values and field_values[field]:
                fields_set += 1
                total += field_values.get(field)
        if not fields_set:
            return Nothing(), True
        if total > HUNDERT_PERCENT:
            return Alert(
                "danger",
                f"Die Summe der Prozente ist {total:.1f}%. Sie sollte kleiner-gleich 100% sein.",
            ), False
        if total == HUNDERT_PERCENT:
            return Alert("success", "Die Summe der Prozente ist genau 100%"), True
        if total >= ALMOST_HUNDERT_PERCENT:
            return Alert(
                "success",
                f"Die Summe der Prozente ist {total:.1f}% und damit fast genau 100%.",
            ), True
        return Alert(
            "warning", f"Die Summe der Prozente ist {total:.1f}%. Das ist zu wenig."
        ), False


class StateLabels(dict[State, Alert]): ...

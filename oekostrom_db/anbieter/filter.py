from typing import Literal

from django.contrib.admin import SimpleListFilter
from django.db.models import Q


class SurveyStatusFilter(SimpleListFilter):
    # Human-readable title for the filter
    title = "Umfragerückmeldung"

    # The parameter that will be used in the URL query
    parameter_name = "survey_status"

    def lookups(self, request, model_admin):  # noqa: ARG002
        """Define the filter options."""
        return [
            ("unanswered", "📭 nicht beantworted"),
            ("answered", "📬 beantwortet"),
        ]

    def queryset(self, request, queryset):  # noqa: ARG002
        """Filter the queryset based on the selected option."""
        answered = Q(survey_access__current_revision__gt=1)
        if self.value() == "unanswered":
            return queryset.exclude(answered)
        if self.value() == "answered":
            return queryset.filter(answered)
        return queryset  # No filtering for "all"


class EmpfohlenFilter(SimpleListFilter):
    # Human-readable title for the filter
    title = "Empfohlen (👍)"

    # The parameter that will be used in the URL query
    parameter_name = "empfohlen"

    def lookups(self, request, model_admin):  # noqa: ARG002
        """Define the filter options."""
        return [
            ("ja", "ja"),
            ("nein", "nein"),
        ]

    def queryset(self, request, queryset):  # noqa: ARG002
        """Filter the queryset based on the selected option."""

        queryset = queryset.select_related("mutter", "sells_from")

        def empfohlen_for(prefix_: Literal["mutter", "sells_from", "self"]) -> Q:
            extra_q: dict[str, bool] = {}

            if prefix_ == "self":
                prefix = ""
            else:
                prefix = f"{prefix_}__"
                extra_q = {f"{prefix_}__isnull": False}

            return Q(
                Q(**extra_q, **{f"{prefix}survey_access__current_revision__gt": 1})
                & ~Q(**{f"{prefix}nur_oeko": False})
                & ~Q(**{f"{prefix}unabhaengigkeit": False})
                & ~Q(**{f"{prefix}zusaetzlichkeit": False})
                & ~Q(**{f"{prefix}money_for_ee_only": False})
            )

        empfohlen = (
            empfohlen_for("mutter")
            | empfohlen_for("sells_from")
            | empfohlen_for("self")
        )

        if self.value() == "ja":
            return queryset.filter(empfohlen)

        if self.value() == "nein":
            return queryset.exclude(empfohlen)

        return queryset  # No filtering for "all"

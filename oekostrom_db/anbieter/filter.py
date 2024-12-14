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
        empfohlen = Q(
            Q(survey_access__current_revision__gt=1)
            & ~Q(nur_oeko=False)
            & ~Q(unabhaengigkeit=False)
            & ~Q(zusaetzlichkeit=False)
            & ~Q(money_for_ee_only=False)
        )

        if self.value() == "ja":
            return queryset.filter(empfohlen)

        if self.value() == "nein":
            return queryset.exclude(empfohlen)

        return queryset  # No filtering for "all"
